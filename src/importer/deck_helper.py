import logging

from collections import namedtuple

import db.card_repository
import db.deck_repository

from db.model import Deck, DeckCard, Match

DeckData = namedtuple('DeckData', [
    'format',
    'expansion',
    'deck_name',
    'maindeck_card_names',
    'sideboard_card_names',
    'match_record',
])


def add_decks_data(session, decks, expansions):
    all_card_names = set()
    for deck_data in decks:
        for n in deck_data.maindeck_card_names + deck_data.sideboard_card_names:
            all_card_names.add(n)

    cards_by_name = get_cards_by_name(session, all_card_names, expansions)
    for deck_data in decks:
        add_deck_data(session, deck_data, cards_by_name)

def get_primary_cards_for_decks(decks, cards):
    return ({card.multiverse_id: count for (card, count) in zip(cards, deck_card_counts) if card.is_primary() and count > 0} for deck_card_counts in decks)

def get_cards_by_name(session, names, expansions):
    return {name: db.card_repository.get_card_from_first_expansion(session, expansions, name) for name in names}

def deck_exists(session, name):
    return db.deck_repository.get_deck(session, name) is not None

def add_deck_data(session, deck_data, cards_by_name):
    if deck_exists(session, deck_data.deck_name):
        logging.debug(f'Skipping import of {deck_data.deck_name}')
        return

    deck = Deck(
        name=deck_data.deck_name,
        format=deck_data.format.lower(),
        expansion=deck_data.expansion.upper(),
    )
    session.add(deck)
    session.flush()

    add_cards(session, deck, deck_data.maindeck_card_names, cards_by_name, True)
    add_cards(session, deck, deck_data.sideboard_card_names, cards_by_name, False)

    for ignored in range(deck_data.match_record[0]):
        session.add(Match(deck=deck.id, wins=1, losses=0))
    for ignored in range(deck_data.match_record[1]):
        session.add(Match(deck=deck.id, wins=0, losses=1))

def add_cards(session, deck, card_names, cards_by_name, is_maindeck):
    for card_name in card_names:
        card = cards_by_name[card_name]
        if card is None:
            print(f'{card_name}, {deck.name}, {deck.expansion}')
        if not card.is_primary():
            continue
        session.add(DeckCard(deck=deck.id, card_multiverse_id=card.multiverse_id, in_maindeck=is_maindeck))