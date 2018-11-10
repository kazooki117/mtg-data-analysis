import csv

import db.card_repository

from db.connector import get_session


def foo(session, legend_file, deck_file, expansions):
    (names, decks) = get_card_names_and_counts(legend_file, deck_file)
    cards = get_cards_from_names(session, names, expansions)
    return get_primary_cards_for_decks(decks, cards)

def get_primary_cards_for_decks(decks, cards):
    return ({card.multiverse_id: count for (card, count) in zip(cards, deck_card_counts) if card.is_primary()} for deck_card_counts in decks)

def get_card_names_and_counts(legend_file, deck_file):
    names = read_legend(legend_file)
    decks = read_decks(deck_file)
    return (names, decks)

def get_cards_from_names(session, names, expansions):
    return (db.card_repository.get_card_from_first_expansion(session, expansions, name) for name in names)

def read_decks(file):
    counts = []
    first = True
    for row in csv.reader(file):
        if first:
            first = False
            continue

        counts.append([int(x) for x in row[1:]])

    return counts

def read_legend(file):
    names = []
    first = True
    for row in csv.reader(file):
        if first:
            first = False
            continue

        names.append(row[1])

    return names


if __name__ == '__main__':
    session = get_session()
    with open('raw_data_from_contributor/three_zero_trophy_hype/grn_3_0_raw_legend.csv') as legend_file,\
         open('raw_data_from_contributor/three_zero_trophy_hype/grn_3_0_raw_deck.csv') as deck_file:
        
        result = foo(session, legend_file, deck_file, expansions=('GRN',))
    print(result)
