import json
import os
import logging
import re

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
  lastLandSlot = max([int(c['number']) for c in blob['cards'] if c['type'].startswith('Basic Land')])
  return Expansion(
    name=name,
    max_booster_number=lastLandSlot,
    abbreviation=blob['code'],
  )

def getOrAddExpansion(session, blob):
  name = blob['name']
  s = session.query(Expansion).filter_by(name=name).one_or_none()
  if s is None:
    logging.info('Adding expansion %s' % (name,))
    session.add(convertBlobToExpansion(blob))
    session.commit()
    return session.query(Expansion).filter_by(name=name).one_or_none()
  return s

def getOrAddCard(session, blob, expansionId):
  name = normalizeStringForDb(blob['name'])
  parsedNumber = re.match('(\\d+)(\\D*)', blob['number'])
  number = int(parsedNumber.group(1))
  face = None if parsedNumber.group(2) == '' else parsedNumber.group(2)
  c = session.query(Card).filter_by(expansion=expansionId, number=number, face=face).one_or_none()
  if c is None:
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

    logging.info('Adding card {name}'.format(name=c.name,))
    session.add(c)
  return c

def addFromJson(session, blob):
  s = getOrAddExpansion(session, blob)
  for cardBlob in blob['cards']:
    getOrAddCard(session, cardBlob, expansionId=s.id)
  session.commit()

if __name__ == '__main__':
  session = getSession()
  for filename in os.listdir(JSON_FOLDER):
    if not filename.lower().endswith('.json'):
      continue
    with open(os.path.join(JSON_FOLDER, filename)) as f:
      addFromJson(session, json.load(f))