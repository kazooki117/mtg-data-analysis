import json
import os
import logging
import re
import datetime

from db.model import Expansion, Card, User, Draft, Pack, PackCard, Pick
from db.connector import get_session


SEATS = 8
PACK_X_PICK_Y_REGEX = re.compile(r'Pack (\d+) pick (\d+):')
EXPANSION_REGEX = re.compile(r'------ (...) ------')
PICK_INDICATOR = '--> '
TIME_REGEX = re.compile(r'Time:\W+(.+)')
TIME_FORMAT = '%m/%d/%Y %I:%M:%S %p'
USER_LIST_REGEX = re.compile(r'Players:')
CARDS_IN_PACK = 15

SPLIT_CARD_JOIN = '/'
SUFFIXES_TO_STRIP = (' (a)', ' (b)')

LOG_DIR = 'logs'


def import_MTGO_log(session, filename):
    if draft_exists(session, filename):
        logging.info(f'Skipping import of {filename}')
        return
    
    logging.info(f'Importing draft from {filename}')

    with open(filename) as f:
        draft_time = maybe_get_draft_time(f)
        logging.debug(f'Importing draft with time {draft_time}')
        user = maybe_get_user(f)
        logging.debug(f'User is {user}')
        draft = initialize_draft(session, draft_time, user, filename)

        while True:
            expansion_abbreviation = maybe_get_next_pack_expansion(f)
            if expansion_abbreviation is None:
                logging.debug('No more packs')
                break
            logging.debug(f'Next pack is {expansion_abbreviation}')
            expansion = query_expansion(session, expansion_abbreviation)

            while True:
                pick_number, pack_card_names, pick = get_next_pack_cards(f)
                logging.debug(f'Pick {pick_number} sees {pack_card_names} and takes {pick}')
                add_pack(session, draft, expansion, pick_number, pack_card_names, pick)

                if len(pack_card_names) == 1:
                    break

    session.commit()

def maybe_get_draft_time(file):
    while True:
        next_line = file.readline()
        match = TIME_REGEX.match(next_line)
        if match:
            try:
                return datetime.datetime.strptime(match.group(1), TIME_FORMAT)
            except ValueError:
                return None

def maybe_get_user(file):
    while not USER_LIST_REGEX.match(file.readline()):
        pass

    user = None
    while True:
        next_line = file.readline()
        if next_line == '\n':
            return user
        elif next_line.startswith(PICK_INDICATOR):
            user = next_line[len(PICK_INDICATOR):].strip()

def maybe_get_next_pack_expansion(file):
    while True:
        line = file.readline()
        if len(line) == 0:
            return None

        match = EXPANSION_REGEX.match(line)
        if match:
            return match.group(1)

def get_next_pack_cards(file):
    while True:
        next_line = file.readline()
        match = PACK_X_PICK_Y_REGEX.match(next_line)
        if match:
            pack_number = int(match.group(1))
            pick_in_pack = int(match.group(2))
            pick_number = pack_number * CARDS_IN_PACK + pick_in_pack
            break

    pack_card_names = []
    while True:
        line = file.readline()
        if line == '\n':
            return pick_number, pack_card_names, pick

        if line.startswith(PICK_INDICATOR):
            pick = line[len(PICK_INDICATOR):].strip()
            pack_card_names.append(pick)
        else:
            pack_card_names.append(line.strip())

def initialize_draft(session, draft_time, username, name):
    user = get_or_add_user(session, username)

    draft = Draft(start_time=draft_time, name=name, user=user.id)
    session.add(draft)

    return draft

def get_or_add_user(session, username):
    if username is None:
        username = ''
    user = session.query(User).filter_by(username=username).one_or_none()

    if user is None:
        logging.debug(f'Adding user {username}')
        user = User(username=username)
        session.add(user)
        session.flush()

    return user

def add_pack(session, draft, expansion, pick_number, pack_card_names, pick):
    pack = Pack(draft=draft.id, pick_number=pick_number)
    session.add(pack)

    picked = False
    for card_name in pack_card_names:
        card = query_card(session, expansion, card_name)
        pack_card = PackCard(pack=pack.id, card_multiverse_id=card.multiverse_id)
        session.add(pack_card)

        if card_name == pick and not picked:
            session.flush()
            session.add(Pick(pack_card=pack_card.id))
            picked = True

    assert picked, 'No cards were picked'

def query_card(session, expansion, card_name):
    if SPLIT_CARD_JOIN in card_name:
        card_name = card_name[:card_name.find(SPLIT_CARD_JOIN)]

    card_name = card_name.strip()

    result = session.query(Card).filter_by(expansion=expansion.abbreviation, name=card_name).scalar()
    if result:
        return result

    for suffix in SUFFIXES_TO_STRIP:
        result = session.query(Card).filter_by(expansion=expansion.abbreviation, name=f'{card_name}{suffix}').scalar()
        if result:
            return result

def query_expansion(session, abbreviation):
    return session.query(Expansion).filter_by(abbreviation=abbreviation).scalar()

def draft_exists(session, name):
    return session.query(Draft).filter_by(name=name).one_or_none() is not None


if __name__ == '__main__':
    session = get_session()
    for filename in os.listdir(LOG_DIR):
        import_MTGO_log(session, os.path.join(LOG_DIR, filename))