import logging
import os
import re

from collections import namedtuple

import db.card_repository
import db.mtga_card_repository
import importer.deck_helper
import importer.draft_helper
import importer.mtga_log_helper

from db.connector import get_session

LOG_FOLDER = os.path.join('logs', 'mtga')
LEAGUE_FORMAT_REGEX = re.compile(r'^(\w+)_(\w+)_(\d+)$')
CARDS_IN_PACK = 15
MIN_PICKS_TO_SAVE = 15

PickOptions = namedtuple('PickOptions', [
    'user',
    'expansion',
    'format',
    'draft_id',
    'pack_number',
    'pick_number',
    'pack_card_names'
])
PickResult = namedtuple('PickResult', ['draft_id', 'pack_number', 'pick_number', 'card_name'])


def maybe_get_league_info(session, blob):
    try:
        blob = blob[0]
        if blob['CurrentEventState'] != 'Completed':
            return None

        league_status = blob['ModuleInstanceData']['WinLossGate']
        match = LEAGUE_FORMAT_REGEX.match(blob['InternalEventName'])

        return importer.deck_helper.DeckData(
            format=match.group(1),
            expansion=match.group(2),
            deck_name=blob['Id'],
            maindeck_card_names=get_card_names(session, blob['CourseDeck']['mainDeck']),
            sideboard_card_names=get_card_names(session, blob['CourseDeck']['sideboard']),
            match_record=(league_status['CurrentWins'], league_status['CurrentLosses'],),
        )
    except KeyError as e:
        return None

def maybe_get_draft_pack(session, blob):
    try:
        blob = blob[0]
        if blob['draftStatus'] != 'Draft.PickNext':
            return None
        
        match = LEAGUE_FORMAT_REGEX.match(blob['eventName'])
        return PickOptions(
            user=blob['playerId'],
            expansion=match.group(2),
            format=match.group(1),
            draft_id=blob['draftId'],
            pack_number=int(blob['packNumber']),
            pick_number=int(blob['pickNumber']),
            pack_card_names=[get_card_name(session, int(i)) for i in blob['draftPack']],
        )

    except KeyError as e:
        return None

def maybe_get_draft_pick(session, blob):
    try:
        blob = blob[0]
        if blob['method'] != 'Draft.MakePick':
            return None
        blob = blob['params']
        
        return PickResult(
            draft_id=blob['draftId'],
            pack_number=int(blob['packNumber']),
            pick_number=int(blob['pickNumber']),
            card_name=get_card_name(session, int(blob['cardId'])),
        )

    except KeyError as e:
        return None

def aggregate_draft_info(packs, picks, cards_in_pack=CARDS_IN_PACK, min_picks_to_save=MIN_PICKS_TO_SAVE):
    all_drafts = []
    last_pick_time = None
    pack_index = 0
    pick_index = 0
    current_pick_number = 0
    current_draft_picks = []
    while True:
        if pack_index >= len(packs) or pick_index >= len(picks):
            break

        (pack_time, pack) = packs[pack_index]
        (pick_time, pick) = picks[pick_index]

        if pack.pack_number > pick.pack_number or pack.pick_number > pick.pick_number:
            pick_index += 1
            continue
        if pack.pack_number < pick.pack_number or pack.pick_number < pick.pick_number:
            pack_index += 1
            continue


        next_pick_number = pack.pack_number * cards_in_pack + pack.pick_number + 1
        if next_pick_number < current_pick_number and len(current_draft_picks) >= min_picks_to_save:
            all_drafts.append(importer.draft_helper.DraftData(
                draft_time=last_pick_time,
                user=pack.user,
                draft_name=f'{pack.draft_id}:{last_pick_time}',
                picks=current_draft_picks,
            ))
            current_draft_picks = []

        current_pick_number = next_pick_number
        last_pick_time = pick_time

        assert pick.card_name in pack.pack_card_names
        assert pick.draft_id in pack.draft_id

        current_draft_picks.append(importer.draft_helper.PickInfo(
            expansion=pack.expansion,
            pick_number=current_pick_number,
            pack_card_names=pack.pack_card_names,
            pick=pick.card_name,
        ))

        pick_index += 1
        pack_index += 1

    if len(current_draft_picks) >= min_picks_to_save:
        all_drafts.append(importer.draft_helper.DraftData(
            draft_time=last_pick_time,
            user=pack.user,
            draft_name=f'{pack.draft_id}:{last_pick_time}',
            picks=current_draft_picks,
        ))
        current_draft_picks = []

    return all_drafts


def get_card_names(session, board_blob):
    names = []
    for d in board_blob:
        names += d['quantity'] * [get_card_name(session, int(d['id'])), ]
    return names

def get_card_name(session, mtga_card_id):
    mtga_card = db.mtga_card_repository.get_mtga_card(session, mtga_card_id)
    return db.card_repository.get_card_by_id(session, mtga_card.primary_card_id).name


if __name__ == '__main__':
    session = get_session()

    pack_info = []
    pick_info = []
    for filename in os.listdir(LOG_FOLDER):
        decks_data = []
        with open(os.path.join(LOG_FOLDER, filename)) as f:
            logging.info(f'Loading MTGA data from {filename}')
            blobs = importer.mtga_log_helper.get_all_log_blobs(f)

            for (time, blob) in blobs:
                maybe_league_info = maybe_get_league_info(session, blob)
                if maybe_league_info is not None:
                    decks_data.append(maybe_league_info)

                maybe_pack_info = maybe_get_draft_pack(session, blob)
                if maybe_pack_info is not None:
                    pack_info.append((time, maybe_pack_info))

                maybe_pick_info = maybe_get_draft_pick(session, blob)
                if maybe_pick_info is not None:
                    pick_info.append((time, maybe_pick_info))

        decks_by_expansion = {}
        for deck in decks_data:
            if deck.expansion not in decks_by_expansion:
                decks_by_expansion[deck.expansion] = []
            decks_by_expansion[deck.expansion].append(deck)
        for (expansion, decks) in decks_by_expansion.items():
            importer.deck_helper.add_decks_data(session, decks_data, [expansion,])
            session.commit()

    for draft_data in aggregate_draft_info(pack_info, pick_info):
        importer.draft_helper.add_draft_data(session, draft_data)
    session.commit()