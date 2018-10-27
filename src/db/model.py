import re

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SimplePrinterBase(object):
  def __repr__(self):
    return '{clazz}<{attributes}>'.format(
      clazz=type(self).__name__,
      attributes={k: v for (k, v) in self.__dict__.items() if k != '_sa_instance_state'},
    )

class Expansion(Base, SimplePrinterBase):
  __tablename__ = 'expansions'

  id = Column(Integer, primary_key=True)
  abbreviation = Column(String(255), nullable=False)
  name = Column(String(255), nullable=False)
  max_booster_number = Column(Integer, nullable=False)

class Card(Base, SimplePrinterBase):
  __tablename__ = 'cards'

  id = Column(Integer, primary_key=True)
  expansion = Column(Integer, ForeignKey('expansions.id'), nullable=False)
  name = Column(String(255), nullable=False)
  rarity = Column(String(255), nullable=False)
  number = Column(Integer, nullable=False)
  face = Column(String(255))
  mana_cost = Column(String(255))
  text = Column(String(1023))
  type = Column(String(255), nullable=False)
  power = Column(Integer)
  toughness = Column(Integer)
  loyalty = Column(Integer)

  def isSupertype(self, supertype):
    cardType = self.type
    if '-' in cardType:
      cardType = cardType[:cardType.index(' -')]
    return supertype in cardType

  def getColors(self):
    if self.mana_cost is None:
      return []
    return [color for color in 'WUBRG' if color in self.mana_cost]

  def isColor(self, color):
    return color.upper() in self.getColors()

  def isColorless(self):
    return self.mana_cost is None or not any([color in self.mana_cost for color in 'WUBRG'])

  def getConvertedCost(self):
    if self.mana_cost is None:
      return 0
    return sum([int(x) for x in re.findall('{(\\d+)}', re.sub('{X}', '', re.sub('{[CWUBRGP/]+}', '{1}', self.mana_cost)))])

  def getShortStr(self):
    otherStr = ''
    if self.loyalty is not None:
      otherStr = str(self.loyalty)
    elif self.power is not None:
      otherStr = '{power}/{toughness}'.format(power=self.power, toughness=self.toughness)
    if len(otherStr):
      otherStr += ' | '

    return '{name} | {mana_cost} | {type} | {other}{text}'.format(
      name=self.name,
      mana_cost=self.mana_cost,
      type=self.type,
      other=otherStr,
      text=('' if self.text is None else self.text).replace('\n', '\\n'),
    )

  def getSortKey(self, colors):
    return (
      not (self.isColorless() or any([self.isColor(c) for c in colors])),
      0 if self.isSupertype('Creature') else 2 if self.isSupertype('Land') else 1,
      self.getConvertedCost(),
      self.id,
    )

class User(Base, SimplePrinterBase):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True)
  username = Column(String(255), nullable=False)

class Draft(Base, SimplePrinterBase):
  __tablename__ = 'drafts'

  id = Column(Integer, primary_key=True)
  name = Column(String(255), nullable=False)
  start_time = Column(DateTime, nullable=True)

class DraftSeat(Base, SimplePrinterBase):
  __tablename__ = 'draft_seats'

  id = Column(Integer, primary_key=True)
  draft = Column(Integer, ForeignKey('drafts.id'), nullable=False)
  user = Column(Integer, ForeignKey('users.id'), nullable=False)
  seat_number = Column(Integer, nullable=True)

class Pack(Base, SimplePrinterBase):
  __tablename__ = 'packs'

  id = Column(Integer, primary_key=True)
  draft_seat = Column(Integer, ForeignKey('draft_seats.id'), nullable=False)
  pick_number = Column(Integer, nullable=False)
  expansion = Column(Integer, ForeignKey('expansions.id'), nullable=False)

class PackCard(Base, SimplePrinterBase):
  __tablename__ = 'pack_cards'

  id = Column(Integer, primary_key=True)
  pack = Column(Integer, ForeignKey('packs.id'), nullable=False)
  card = Column(Integer, ForeignKey('cards.id'), nullable=False)

class Pick(Base, SimplePrinterBase):
  __tablename__ = 'picks'

  id = Column(Integer, primary_key=True)
  user = Column(Integer, ForeignKey('users.id'), nullable=False)
  pick_number = Column(Integer, nullable=False)
  pack_card = Column(Integer, ForeignKey('pack_cards.id'), nullable=False)
