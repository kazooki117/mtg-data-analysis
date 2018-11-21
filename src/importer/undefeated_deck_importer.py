import csv
import logging

import importer.deck_helper
from db.connector import get_session

def import_undefeated_decks(session, legend_filename, deck_filename, expansions, format):
    with open(legend_filename) as legend_file,\
         open(deck_filename) as deck_file:
        decks_data = get_decks_data(legend_file, deck_file, deck_filename)

    importer.deck_helper.add_decks_data(session, decks_data, expansions, format)

def get_decks_data(legend_file, deck_file, deck_name_prefix):
    card_names = read_legend(legend_file)
    decks = read_decks(deck_file)

    decks_data = []
    for (index, deck) in enumerate(decks):
        deck_name = f'{deck_name_prefix}-{index}'

        decks_data.append(importer.deck_helper.DeckData(
            deck_name=deck_name,
            maindeck_card_names=[name for (name, count) in zip(card_names, deck) for ignored in range(count)],
            sideboard_card_names=[],
            match_record=(3,0,),
        ))

    return decks_data

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
    import_undefeated_decks(
        session=session,
        legend_filename='raw_data_from_contributor/three_zero_trophy_hype/grn_3_0_raw_legend.csv',
        deck_filename='raw_data_from_contributor/three_zero_trophy_hype/grn_3_0_raw_deck.csv',
        expansions=('GRN',),
        format='draft',
    )
    session.commit()
