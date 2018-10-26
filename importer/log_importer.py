import json
import os
import logging
import re
import datetime

from model import Expansion, Card, User, Draft, DraftSeat, Pack, PackCard, Pick
from db_connector import getSession


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


def importMTGOLog(session, filename):
  if draftExists(session, filename):
    logging.info(f'Skipping import of {filename}')
    return

  with open(filename) as f:
    draftTime = maybeGetDraftTime(f)
    logging.debug(f'Importing draft with time {draftTime}')
    user = maybeGetUser(f)
    logging.debug(f'User is {user}')
    draft, seat = initializeDraft(session, draftTime, user, filename)

    while True:
      expansionAbbreviation = maybeGetNextPackExpansion(f)
      if expansionAbbreviation is None:
        logging.debug('No more packs')
        break
      logging.debug(f'Next pack is {expansionAbbreviation}')
      expansion = queryExpansion(session, expansionAbbreviation)

      while True:
        pickNumber, packCardNames, pick = getNextPackCards(f)
        logging.debug(f'Pick {pickNumber} sees {packCardNames} and takes {pick}')
        addPack(session, seat, expansion, pickNumber, packCardNames, pick)

        if len(packCardNames) == 1:
          break

  session.commit()

def maybeGetDraftTime(file):
  while True:
    nextLine = file.readline()
    match = TIME_REGEX.match(nextLine)
    if match:
      try:
        return datetime.datetime.strptime(match.group(1), TIME_FORMAT)
      except ValueError:
        return None

def maybeGetUser(file):
  while not USER_LIST_REGEX.match(file.readline()):
    pass

  user = None
  while True:
    nextLine = file.readline()
    if nextLine == '\n':
      return user
    elif nextLine.startswith(PICK_INDICATOR):
      user = nextLine[len(PICK_INDICATOR):].strip()

def maybeGetNextPackExpansion(file):
  while True:
    line = file.readline()
    if len(line) == 0:
      return None

    match = EXPANSION_REGEX.match(line)
    if match:
      return match.group(1)

def getNextPackCards(file):
  while True:
    nextLine = file.readline()
    match = PACK_X_PICK_Y_REGEX.match(nextLine)
    if match:
      packNumber = int(match.group(1))
      pickInPack = int(match.group(2))
      pickNumber = packNumber * CARDS_IN_PACK + pickInPack
      break

  packCardNames = []
  while True:
    line = file.readline()
    if line == '\n':
      return pickNumber, packCardNames, pick

    if line.startswith(PICK_INDICATOR):
      pick = line[len(PICK_INDICATOR):].strip()
      packCardNames.append(pick)
    else:
      packCardNames.append(line.strip())

def initializeDraft(session, draftTime, username, name):
  draft = Draft(start_time=draftTime, name=name)
  session.add(draft)

  user = getOrAddUser(session, username)

  seat = DraftSeat(draft=draft.id, user=user.id)
  session.add(seat)

  return draft, seat

def getOrAddUser(session, username):
  if username is None:
    username = ''
  user = session.query(User).filter_by(username=username).one_or_none()

  if user is None:
    logging.debug(f'Adding user {username}')
    user = User(username=username)
    session.add(user)
    session.flush()

  return user

def addPack(session, seat, expansion, pickNumber, packCardNames, pick):
  pack = Pack(draft_seat=seat.id, pick_number=pickNumber, expansion=expansion.id)
  session.add(pack)

  picked = False
  for cardName in packCardNames:
    card = queryCard(session, expansion, cardName)
    packCard = PackCard(pack=pack.id, card=card.id)
    session.add(packCard)

    if cardName == pick and not picked:
      session.flush()
      session.add(Pick(user=seat.user, pick_number=pickNumber, pack_card=packCard.id))
      picked = True

  assert picked, 'No cards were picked'

def queryCard(session, expansion, cardName):
  if SPLIT_CARD_JOIN in cardName:
    cardName = cardName[:cardName.find(SPLIT_CARD_JOIN)]

  cardName = cardName.strip()

  result = session.query(Card).filter_by(expansion=expansion.id, name=cardName).scalar()
  if result:
    return result

  for suffix in SUFFIXES_TO_STRIP:
    result = session.query(Card).filter_by(expansion=expansion.id, name=f'{cardName}{suffix}').scalar()
    if result:
      return result

def queryExpansion(session, abbreviation):
  return session.query(Expansion).filter_by(abbreviation=abbreviation).scalar()

def draftExists(session, name):
  return session.query(Draft).filter_by(name=name).one_or_none() is not None


if __name__ == '__main__':
  session = getSession()
  for filename in os.listdir(LOG_DIR):
    importMTGOLog(session, os.path.join(LOG_DIR, filename))