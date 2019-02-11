import logging
import re
import time
import json

from db.connector import get_session
import importer.draft_helper

FILENAME = 'logs/mtga2/output_log.txt'

LOG_START_REGEX = re.compile(r'^\[(UnityCrossThreadLogger|Client GRE)\]([\d:/ -]+(AM|PM)?)')
JSON_START_REGEX = re.compile(r'[[{]')
SLEEP_TIME = 0.25
FOLLOW = False
CARDS_IN_PACK = 15

def getOverallPickNumber(pack_number, pick_number):
    return CARDS_IN_PACK * pack_number + pick_number + 1

class Follower:
    def __init__(self):
        self.buffer = []
        self.cur_log_time = None
        self.json_decoder = json.JSONDecoder()
        self.draft_data = None

    def append_line(self, line):
        match = LOG_START_REGEX.match(line)
        if match:
            self.handle_complete_log_entry()
            self.cur_logger, self.cur_log_time = (match.group(1), match.group(2))
            self.cur_log_time = importer.draft_helper.extract_time(self.cur_log_time)
        else:
            self.buffer.append(line)

    def handle_complete_log_entry(self):
        if len(self.buffer) == 0:
            return
        if self.cur_log_time is None:
            self.buffer = []
            return

        full_log = ''.join(self.buffer)
        self.__handle_blob(full_log)

        self.buffer = []
        self.cur_logger = None
        self.cur_log_time = None

    def __handle_blob(self, full_log):
        match = JSON_START_REGEX.search(full_log)
        if not match:
            return

        try:
            json_obj, end = self.json_decoder.raw_decode(full_log, match.start())
        except json.JSONDecodeError as e:
            logging.debug(f'Ran into error {e} when parsing at {self.cur_log_time}. Data was: {full_log}')
            return

        # logging.info(f'{self.cur_logger} logged at {self.cur_log_time}') # : {json_obj}')

        if 'draftStatus' in json_obj:
            self.__handle_draft_log(json_obj)
        elif 'method' in json_obj and json_obj['method'] == 'Draft.MakePick':
            self.__handle_draft_pick(json_obj)


    def __handle_draft_log(self, json_obj):
        draft_name = f'MTGA:{json_obj["draftId"]}:{self.cur_log_time.strftime("%Y%m%d%H%M%S")}'
        if json_obj['draftStatus'] == 'Draft.PickNext' and json_obj['packNumber'] == 0 and json_obj['pickNumber'] == 0:
            self.draft_data = importer.draft_helper.DraftData(
                draft_time=self.cur_log_time,
                user=json_obj['playerId'],
                draft_name=draft_name,
                picks=[]
            )
            logging.info(f'Initializing new draft {self.draft_data.draft_name}')

        if self.draft_data is None:
            logging.warning(f'Skipping data from draft already underway {draft_name}')
            return

        if json_obj['draftStatus'] == 'Draft.PickNext':
            self.draft_data.picks.append(importer.draft_helper.PickInfo_Arena(
                pick_number=getOverallPickNumber(pack_number=json_obj['packNumber'], pick_number=json_obj['pickNumber']),
                pack_cards=[int(x) for x in json_obj['draftPack']],
                pick=None,
            ))
        if json_obj['draftStatus'] == 'Draft.Complete':
            logging.warning(f'Should be saving draft data {self.draft_data}')
            self.draft_data = None

    def __handle_draft_pick(self, json_obj):
        inner_obj = json_obj['params']
        pick_number = getOverallPickNumber(pack_number=int(inner_obj['packNumber']), pick_number=int(inner_obj['pickNumber']))
        if self.draft_data is None or pick_number != self.draft_data.picks[-1].pick_number:
            logging.info(f'Skipping pick with missing pack data')
            return
        self.draft_data.picks[-1] = self.draft_data.picks[-1]._replace(pick=int(inner_obj['cardId']))


follower = Follower()
with open(FILENAME) as f:
    while True:
        last_position = f.tell()
        line = f.readline()
        if line:
            follower.append_line(line)
        else:
            follower.handle_complete_log_entry()
            if FOLLOW:
                # logging.info('Seeking back')
                f.seek(last_position)
                time.sleep(SLEEP_TIME)
            else:
                break
