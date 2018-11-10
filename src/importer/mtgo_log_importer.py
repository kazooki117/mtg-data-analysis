import os
import logging
import re
import datetime

import importer.draft_helper

from db.connector import get_session


PACK_X_PICK_Y_REGEX = re.compile(r'Pack (\d+) pick (\d+):')
EXPANSION_REGEX = re.compile(r'------ (...) ------')
PICK_INDICATOR = '--> '
TIME_REGEX = re.compile(r'Time:\W+(.+)')
TIME_FORMAT = '%m/%d/%Y %I:%M:%S %p'
USER_LIST_REGEX = re.compile(r'Players:')
CARDS_IN_PACK = 15


LOG_DIR = 'logs'

def import_MTGO_log(session, filename, draft_name):
    with open(filename) as f:
        draft_data = extract_draft_data(f, draft_name)
    importer.draft_helper.add_draft_data(session, draft_data)

def extract_draft_data(file, draft_name):
    (draft_time, user) = get_draft_info(file)
    picks = get_draft_picks(file)
    return importer.draft_helper.DraftData(
        draft_time=draft_time,
        user=user,
        draft_name=draft_name,
        picks=picks,
    )

def get_draft_info(file):
    draft_time = _maybe_get_draft_time(file)
    logging.debug(f'Importing draft with time {draft_time}')
    user = _maybe_get_user(file)
    logging.debug(f'User is {user}')
    return (draft_time, user)

def get_draft_picks(file):
    picks = []
    while True:
        expansion_abbreviation = _maybe_get_next_pack_expansion(file)
        if expansion_abbreviation is None:
            logging.debug('No more packs')
            break
        logging.debug(f'Next pack is {expansion_abbreviation}')

        while True:
            result = _get_next_pack_cards(file)
            if result is None:
                break
            pick_number, pack_card_names, pick = result

            logging.debug(f'Pick {pick_number} sees {pack_card_names} and takes {pick}')
            picks.append(importer.draft_helper.PickInfo(
                expansion=expansion_abbreviation,
                pick_number=pick_number,
                pack_card_names=pack_card_names,
                pick=pick,
            ))
            if len(pack_card_names) == 1:
                break
    return picks

def _maybe_get_draft_time(file):
    while True:
        next_line = file.readline()
        match = TIME_REGEX.match(next_line)
        if match:
            try:
                return datetime.datetime.strptime(match.group(1), TIME_FORMAT)
            except ValueError:
                return None

def _maybe_get_user(file):
    while not USER_LIST_REGEX.match(file.readline()):
        pass

    user = None
    while True:
        next_line = file.readline()
        if next_line == '\n':
            return user
        elif next_line.startswith(PICK_INDICATOR):
            user = next_line[len(PICK_INDICATOR):].strip()

def _maybe_get_next_pack_expansion(file):
    while True:
        line = file.readline()
        if len(line) == 0:
            return None

        match = EXPANSION_REGEX.match(line)
        if match:
            return match.group(1)

def _get_next_pack_cards(file):
    while True:
        next_line = file.readline()
        if next_line == '':
            return None
        match = PACK_X_PICK_Y_REGEX.match(next_line)
        if match:
            pack_number = int(match.group(1))
            pick_in_pack = int(match.group(2))
            pick_number = (pack_number - 1) * CARDS_IN_PACK + pick_in_pack
            break

    pack_card_names = []
    while True:
        line = file.readline()
        if line == '' or line == '\n':
            return pick_number, pack_card_names, pick

        if line.startswith(PICK_INDICATOR):
            pick = line[len(PICK_INDICATOR):].strip()
            pack_card_names.append(pick)
        else:
            pack_card_names.append(line.strip())


if __name__ == '__main__':
    session = get_session()
    for filename in os.listdir(LOG_DIR):
        if importer.draft_helper.draft_exists(session, filename):
            logging.info(f'Skipping import of {filename}')
            continue
        
        logging.info(f'Importing draft from {filename}')
        full_path = os.path.join(LOG_DIR, filename)
        import_MTGO_log(session, filename=full_path, draft_name=filename)
    session.commit()
    