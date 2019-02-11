import logging
import re
import time
import json

FILENAME = 'logs/mtga2/output_log.txt'

LOG_START_REGEX = re.compile(r'^\[(UnityCrossThreadLogger|Client GRE)\]([\d:/ -]+(AM|PM)?)')
JSON_START_REGEX = re.compile(r'[[{]')
SLEEP_TIME = 0.25
FOLLOW = False

import logging
logging.basicConfig(
    format='%(asctime)s,%(levelname)s,%(message)s',
    datefmt='%Y%m%d %H%M%S',
    level=logging.INFO,
)

class Follower:
    def __init__(self):
        self.buffer = []
        self.cur_log_time = None
        self.json_decoder = json.JSONDecoder()

    def append_line(self, line):
        match = LOG_START_REGEX.match(line)
        if match:
            self.handle_complete_log_entry()
            self.cur_logger, self.cur_log_time = (match.group(1), match.group(2))
        else:
            self.buffer.append(line)

    def handle_complete_log_entry(self):
        if len(self.buffer) == 0:
            return
        if self.cur_log_time is None:
            self.buffer = []
            return

        full_log = ''.join(self.buffer)
        self.handle_blob(full_log)

        self.buffer = []
        self.cur_logger = None
        self.cur_log_time = None

    def handle_blob(self, full_log):
        match = JSON_START_REGEX.search(full_log)
        if not match:
            return

        try:
            json_obj, end = self.json_decoder.raw_decode(full_log, match.start())
        except json.JSONDecodeError as e:
            logging.error(f'Ran into error {e}') #' when parsing {full_log} starting at {match.start()}')
            return

        logging.info(f'{self.cur_logger} logged at {self.cur_log_time}') # : {json_obj}')


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
