import re

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SimplePrinterBase(object):
    def __repr__(self):
        attributes = {k: v for (k, v) in self.__dict__.items() if k != '_sa_instance_state'}
        return f'{type(self).__name__}<{attributes}>'

class Expansion(Base, SimplePrinterBase):
    __tablename__ = 'expansions'

    abbreviation = Column(String(3), nullable=False, primary_key=True)
    name = Column(String(255), nullable=False)
    max_booster_number = Column(Integer, nullable=False)

class Card(Base, SimplePrinterBase):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True)
    multiverse_id = Column(Integer, nullable=False)
    expansion = Column(String(3), ForeignKey('expansions.abbreviation'), nullable=False)
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
    user = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=True)

class Pack(Base, SimplePrinterBase):
    __tablename__ = 'packs'

    id = Column(Integer, primary_key=True)
    draft = Column(Integer, ForeignKey('drafts.id'), nullable=False)
    pick_number = Column(Integer, nullable=False)

class PackCard(Base, SimplePrinterBase):
    __tablename__ = 'pack_cards'

    id = Column(Integer, primary_key=True)
    pack = Column(Integer, ForeignKey('packs.id'), nullable=False)
    card_multiverse_id = Column(Integer, nullable=False)

class Pick(Base, SimplePrinterBase):
    __tablename__ = 'picks'

    id = Column(Integer, primary_key=True)
    pack_card = Column(Integer, ForeignKey('pack_cards.id'), nullable=False)

class Deck(Base, SimplePrinterBase):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    format = Column(String, nullable=False)
    expansion = Column(String(3), ForeignKey('expansions.abbreviation'), nullable=False)

class DeckCard(Base, SimplePrinterBase):
    __tablename__ = 'deck_cards'
    
    id = Column(Integer, primary_key=True)
    deck = Column(Integer, ForeignKey('decks.id'), nullable=False)
    card_multiverse_id = Column(Integer, nullable=False)
    in_maindeck = Column(Boolean, nullable=False)

class Match(Base, SimplePrinterBase):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    deck = Column(Integer, ForeignKey('decks.id'), nullable=False)
    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)

class Game(Base, SimplePrinterBase):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    match = Column(Integer, ForeignKey('matches.id'), nullable=False)
    is_win = Column(Boolean, nullable=False)
    game_in_match = Column(Integer, nullable=True)
    on_play = Column(Boolean, nullable=True)
    final_turn = Column(Integer, nullable=True)
    mulligans = Column(Integer, nullable=True)
    opponent_mulligans = Column(Integer, nullable=True)
    opponent_base_colors = Column(String(5), nullable=True)
    opponent_splashes = Column(String(5), nullable=True)