import datetime
import logging

from collections import namedtuple

import db.card_repository
import db.draft_repository
import db.user_repository

from db.model import User, Draft, Pack, PackCard, Pick


TIME_FORMATS = (
    '%Y-%m-%d %I:%M:%S %p',
    '%Y-%m-%d %H:%M:%S',
    '%m/%d/%Y %I:%M:%S %p',
    '%m/%d/%Y %H:%M:%S',
    '%Y/%m/%d %I:%M:%S %p',
    '%Y/%m/%d %H:%M:%S',
)
OUTPUT_TIME_FORMAT = '%Y%m%d%H%M%S'


__PickInfo = namedtuple('PickInfo', ['expansion', 'pick_number', 'pack_card_names', 'pick'])
__PickInfo_Arena = namedtuple('PickInfo', ['pick_number', 'pack_cards', 'pick'])
DraftData = namedtuple('DraftData', ['draft_time', 'user', 'draft_name', 'picks'])

class PickInfo(__PickInfo):
    def get_cards_from_db(self, session):
        for card_name in self.pack_card_names:
            db_card = db.card_repository.get_card_by_approximate_name(session, self.expansion, card_name)
            is_pick = card_name == self.pick
            yield (db_card, is_pick)

class PickInfo_Arena(__PickInfo_Arena):
    def get_cards_from_db(self, session):
        assert False, 'Not yet implemented'


def add_draft_data(session, draft_data):
    if draft_exists(session, draft_data.draft_name):
        logging.info(f'Skipping import of {draft_data.draft_name}')
        return
    
    logging.info(f'Loading {draft_data.draft_name} into database')

    draft = initialize_draft(session, draft_data.draft_time, draft_data.user, draft_data.draft_name)
    session.flush()
    for p in draft_data.picks:
        add_pack(session, draft, p)

def initialize_draft(session, draft_time, username, name):
    user = get_or_add_user(session, username)

    draft = Draft(start_time=draft_time, name=name, user=user.id)
    session.add(draft)

    return draft

def get_or_add_user(session, username):
    if username is None:
        username = ''
    user = db.user_repository.get_user(session, username)

    if user is None:
        logging.debug(f'Adding user {username}')
        user = User(username=username)
        session.add(user)
        session.flush()

    return user

def add_pack(session, draft, pick_info):
    pack = Pack(draft=draft.id, pick_number=pick_info.pick_number)
    session.add(pack)

    picked = False
    for (card, is_pick) in pick_info.get_cards_from_db(session):
        pack_card = PackCard(pack=pack.id, card_multiverse_id=card.multiverse_id)
        session.add(pack_card)

        if is_pick and not picked:
            session.flush()
            session.add(Pick(pack_card=pack_card.id))
            picked = True

    assert picked, 'No cards were picked'

def draft_exists(session, name):
    return db.draft_repository.get_draft(session, name) is not None

def extract_time(time_str):
    for possible_format in TIME_FORMATS:
        try:
            return datetime.datetime.strptime(time_str, possible_format)
        except ValueError:
            pass
    raise ValueError(f'Unsupported time format: {time_str}')