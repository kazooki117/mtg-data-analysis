import json
import os
import logging
import re

import db.expansion_repository
import db.card_repository

from db.model import Expansion, Card
from db.connector import get_session


JSON_FOLDER = 'sets'
UNICODE_REPLACEMENTS = {
    u'\u2212': '-',
    u'\u2014': '-',
    u'\u2022': '*',
}

def normalize_string_for_db(s):
    for (k, v) in UNICODE_REPLACEMENTS.items():
        s = s.replace(k, v)
    return s

def convert_blob_to_expansion(blob):
    name = blob['name']
    last_land_slot = max([int(c['number']) for c in blob['cards'] if c['type'].startswith('Basic Land')])
    return Expansion(
        name=name,
        max_booster_number=last_land_slot,
        abbreviation=blob['code'],
    )

def convert_blob_to_card(blob, expansion_id):
    name = normalize_string_for_db(blob['name'])
    parsed_number = re.match('(\\d+)(\\D*)', blob['number'])
    number = int(parsed_number.group(1))
    face = None if parsed_number.group(2) == '' else parsed_number.group(2)

    c = Card(
        multiverse_id=blob['multiverseid'],
        expansion=expansion_id,
        name=name,
        number=number,
        type=normalize_string_for_db(blob['type']),
        rarity=blob['rarity'],
    )
    if 'manaCost' in blob: c.mana_cost = blob['manaCost']
    if 'text' in blob: c.text = normalize_string_for_db(blob['text'])
    if 'power' in blob and blob['power'] != '*': c.power = int(blob['power'])
    if 'toughness' in blob and blob['toughness'] != '*': c.toughness = int(blob['toughness'])
    if 'loyalty' in blob: c.loyalty = int(blob['loyalty'])
    if face != '': c.face = face

    return c

def get_or_persist_expansion(session, expansion):
    existing = db.expansion_repository.get_expansion(session, expansion.name)
    if existing is not None:
        return existing

    logging.info(f'Adding expansion {expansion}')
    session.add(expansion)
    return expansion

def get_or_persist_card(session, card):
    existing = db.card_repository.get_card(session=session, expansion_id=card.expansion, number=card.number, face=card.face)
    if existing is not None:
        return existing

    logging.debug(f'Adding card {card.name}')
    session.add(card)
    return card

def add_from_json(session, blob):
    expansion = get_or_persist_expansion(session, convert_blob_to_expansion(blob))
    session.flush()
    for cardBlob in blob['cards']:
        get_or_persist_card(session, convert_blob_to_card(cardBlob, expansion.id))
    session.commit()

if __name__ == '__main__':
    session = get_session()
    for filename in os.listdir(JSON_FOLDER):
        if not filename.lower().endswith('.json'):
            continue
        with open(os.path.join(JSON_FOLDER, filename)) as f:
            add_from_json(session, json.load(f))