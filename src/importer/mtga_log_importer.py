import os
import re

import importer.mtga_log_helper
import importer.deck_helper
import db.mtga_card_repository

from db.connector import get_session

LOG_FOLDER = os.path.join('logs', 'mtga')
LEAGUE_FORMAT_REGEX = re.compile(r'^(\w+)_(\w+)_(\d+)$')


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

def get_card_names(session, board_blob):
    names = []
    for d in board_blob:
        names += d['quantity'] * [get_card_name(session, d['id']), ]
    return names

def get_card_name(session, mtga_card_id):
    return db.mtga_card_repository.get_mtga_card(session, mtga_card_id).name


if __name__ == '__main__':
    session = get_session()
    for filename in os.listdir(LOG_FOLDER):
        # if filename != 'sample.htm':
            # continue
        with open(os.path.join(LOG_FOLDER, filename)) as f:
            print(filename)
            blobs = importer.mtga_log_helper.get_all_log_blobs(f)

            for (time, blob) in blobs:
                maybe_league_info = maybe_get_league_info(session, blob)
                if maybe_league_info is not None:
                    print(maybe_league_info)

                # print(time)
                # print(blob)
                # print()