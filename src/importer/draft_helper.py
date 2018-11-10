import logging

from collections import namedtuple

import db.card_repository
import db.draft_repository
import db.user_repository

from db.model import User, Draft, Pack, PackCard, Pick

PickInfo = namedtuple('PickInfo', ['expansion', 'pick_number', 'pack_card_names', 'pick'])
DraftData = namedtuple('DraftData', ['draft_time', 'user', 'draft_name', 'picks'])

def add_draft_data(session, draft_data):
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
    for card_name in pick_info.pack_card_names:
        card = db.card_repository.get_card_by_approximate_name(session, pick_info.expansion, card_name)
        pack_card = PackCard(pack=pack.id, card_multiverse_id=card.multiverse_id)
        session.add(pack_card)

        if card_name == pick_info.pick and not picked:
            session.flush()
            session.add(Pick(pack_card=pack_card.id))
            picked = True

    assert picked, 'No cards were picked'

def draft_exists(session, name):
    return db.draft_repository.get_draft(session, name) is not None
