import datetime
import json
import logging
import os

import importer.draft_helper

from db.connector import get_session


FLOOEY_LOG_DIR = os.path.join('raw_data_from_contributor', 'draft_logs')
CARDS_IN_PACK = 15


def import_flooey_log(session, filename):
    with open(filename) as f:
        all_data = extract_all_draft_data(f)
    for draft_data in all_data:
        importer.draft_helper.add_draft_data(session, draft_data)

def extract_all_draft_data(file):
    return [extract_individual_draft(draft_blob) for draft_blob in json.load(file)]

def extract_individual_draft(blob):
    draft_info = blob['Draft']
    draft_time = importer.draft_helper.extract_time(draft_info['time'])

    return importer.draft_helper.DraftData(
        draft_time=draft_time,
        user=None,
        draft_name=f'{blob["Format"]}-{draft_info["event"]}-{draft_time.timestamp()}',
        picks=extract_picks(draft_info['packs']),
    )

def extract_picks(blob):
    pick_infos = []
    for (pack_number, pack) in enumerate(blob):
        expansion = pack['productCode']
        for pick in pack['picks']:
            pick_infos.append(importer.draft_helper.PickInfo(
                expansion=expansion,
                pick_number=pack_number * CARDS_IN_PACK + (CARDS_IN_PACK - len(pick['cards'])) + 1,
                pack_card_names=pick['cards'],
                pick=pick['pick'],
            ))
    return pick_infos


if __name__ == '__main__':
    session = get_session()
    for filename in os.listdir(FLOOEY_LOG_DIR):
        logging.info(f'Importing draft from {filename}')
        full_path = os.path.join(FLOOEY_LOG_DIR, filename)
        import_flooey_log(session, filename=full_path)
    session.commit()