import logging
import re
import time

FILENAME = 'output_log.txt'

LOG_START_REGEX = re.compile(r'^\[UnityCrossThreadLogger\]([\d:/ -]+(AM|PM)?)$')
SLEEP_TIME = 0.25

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

    def append_line(self, line):
        match = LOG_START_REGEX.match(line)
        if match:
            self.handle_blob()
            self.cur_log_time = match.group(1)
        else:
            self.buffer.append(line)

    def handle_blob(self):
        if len(self.buffer) == 0:
            return
        if self.cur_log_time is None:
            self.buffer = []
            return


        full_log = ''.join(self.buffer)
        # logging.info(f'At {self.cur_log_time} parsed buffer of size {len(self.buffer)} ({len(full_log)} characters)')
        logging.info(f'At {self.cur_log_time} read {full_log}')
        self.buffer = []




follower = Follower()
with open(FILENAME) as f:
    while True:
        last_position = f.tell()
        line = f.readline()
        if line:
            follower.append_line(line)
        else:
            # logging.info('Seeking back')
            f.seek(last_position)
            time.sleep(SLEEP_TIME)
