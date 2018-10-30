import json
import os
import logging
import re

import db.expansion_repository
import db.card_repository

from db.model import Expansion, Card
from db.connector import getSession


JSON_FOLDER = 'sets'
UNICODE_REPLACEMENTS = {
  u'\u2212': '-',
  u'\u2014': '-',
  u'\u2022': '*',
}

def normalizeStringForDb(s):
  for (k, v) in UNICODE_REPLACEMENTS.items():
    s = s.replace(k, v)
  return s

def convertBlobToExpansion(blob):
  name = blob['name']
  lastLandSlot = max([int(c['number']) for c in blob['cards'] if c['type'].startswith('Basic Land')])
  return Expansion(
    name=name,
    max_booster_number=lastLandSlot,
    abbreviation=blob['code'],
  )

def convertBlobToCard(blob, expansionId):
  name = normalizeStringForDb(blob['name'])
  parsedNumber = re.match('(\\d+)(\\D*)', blob['number'])
  number = int(parsedNumber.group(1))
  face = None if parsedNumber.group(2) == '' else parsedNumber.group(2)

  c = Card(
    expansion=expansionId,
    name=name,
    number=number,
    type=normalizeStringForDb(blob['type']),
    rarity=blob['rarity'],
  )
  if 'manaCost' in blob: c.mana_cost = blob['manaCost']
  if 'text' in blob: c.text = normalizeStringForDb(blob['text'])
  if 'power' in blob and blob['power'] != '*': c.power = int(blob['power'])
  if 'toughness' in blob and blob['toughness'] != '*': c.toughness = int(blob['toughness'])
  if 'loyalty' in blob: c.loyalty = int(blob['loyalty'])
  if face != '': c.face = face

  return c

def getOrPersistExpansion(session, expansion):
  existing = db.expansion_repository.get_expansion(session, expansion.name)
  if existing is not None:
    return existing

  logging.info('Adding expansion {expansion.name}')
  session.add(expansion)
  return expansion

def getOrPersistCard(session, card):
  existing = db.card_repository.get_card(session=session, expansion_id=card.expansion, number=card.number, face=card.face)
  if existing is not None:
    return existing

  logging.debug('Adding card {name}'.format(name=card.name,))
  session.add(card)
  return card

def addFromJson(session, blob):
  expansion = getOrPersistExpansion(session, convertBlobToExpansion(blob))
  session.flush()
  for cardBlob in blob['cards']:
    getOrPersistCard(session, convertBlobToCard(cardBlob, expansion.id))
  session.commit()

if __name__ == '__main__':
  session = getSession()
  for filename in os.listdir(JSON_FOLDER):
    if not filename.lower().endswith('.json'):
      continue
    with open(os.path.join(JSON_FOLDER, filename)) as f:
      addFromJson(session, json.load(f))