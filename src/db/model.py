import re

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SimplePrinterBase(object):
    def __repr__(self):
        attributes = {k: v for (k, v) in self.__dict__.items() if k != '_sa_instance_state'}
        return f'{type(self).__name__}<{attributes}>'

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
