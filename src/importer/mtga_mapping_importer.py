import os
import csv
import logging

import db.card_repository

from db.model import Card, MTGACard
from db.connector import get_session

MAPPING_FOLDER = 'mtga_mappings'

def add_from_csv(session, expansion, reader):
    add_cards(session, expansion, [get_mtga_card(row) for row in reader])
    session.commit()

def get_mtga_card(row):
    (mtga_id, name) = row
    return MTGACard(mtga_id=mtga_id, name=name)

def add_cards(session, expansion, mtga_cards):
    for mtga_card in mtga_cards:
        if session.query(MTGACard).filter_by(mtga_id=mtga_card.mtga_id).one_or_none() is None:
            logging.debug(f'Adding card {mtga_card.name}')

            card = db.card_repository.get_card_by_approximate_name(session, expansion, mtga_card.name)
            mtga_card.primary_card_id = card.id
            session.add(mtga_card)


if __name__ == '__main__':
    session = get_session()
    for filename in os.listdir(MAPPING_FOLDER):
        if not filename.lower().endswith('.csv'):
            continue
        with open(os.path.join(MAPPING_FOLDER, filename)) as f:
            add_from_csv(session, filename.upper()[:-4], csv.reader(f))
