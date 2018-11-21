import io

import importer.undefeated_deck_importer
import importer.deck_helper

def test_read_legend():
    sample_legend_file = io.StringIO('\n'.join((
        'Card Code,Card Name',
        'GRN30Decks[{_1}]._scale,Blade Instructor',
        'GRN30Decks[{_2}]._scale,Bounty Agent',
        'GRN30Decks[{_3}]._scale,Candlelight Vigil',
    )))

    card_names = importer.undefeated_deck_importer.read_legend(sample_legend_file)
    
    expected = [
        'Blade Instructor',
        'Bounty Agent',
        'Candlelight Vigil',
    ]

    assert expected == card_names

def test_read_decks():
    sample_decks_file = io.StringIO('\n'.join((
        'Serial,GRN30Decks[{_1}]._scale,GRN30Decks[{_2}]._scale,GRN30Decks[{_3}]._scale',
        '2,0,1,0',
        '3,1,0,2',
        '4,0,1,1',
    )))

    decks = importer.undefeated_deck_importer.read_decks(sample_decks_file)
    
    expected = [
        [0, 1, 0],
        [1, 0, 2],
        [0, 1, 1],
    ]

    assert expected == decks


def test_get_decks_data():
    sample_legend_file = io.StringIO('\n'.join((
        'Card Code,Card Name',
        'GRN30Decks[{_1}]._scale,Terror',
        'GRN30Decks[{_2}]._scale,Shock',
        'GRN30Decks[{_3}]._scale,Clone',
    )))

    sample_decks_file = io.StringIO('\n'.join((
        'Serial,GRN30Decks[{_1}]._scale,GRN30Decks[{_2}]._scale,GRN30Decks[{_3}]._scale',
        '2,0,2,1',
        '3,1,1,1',
        '4,0,4,0',
    )))

    decks = importer.undefeated_deck_importer.get_decks_data(sample_legend_file, sample_decks_file, 'deckprefix.txt', format='my-custom-draft', expansion='ABC')
    
    expected = [
        importer.deck_helper.DeckData(
            format='my-custom-draft',
            expansion='ABC',
            deck_name='deckprefix.txt-0',
            maindeck_card_names=['Shock', 'Shock', 'Clone',],
            sideboard_card_names=[],
            match_record=(3,0,),
        ),
        importer.deck_helper.DeckData(
            format='my-custom-draft',
            expansion='ABC',
            deck_name='deckprefix.txt-1',
            maindeck_card_names=['Terror', 'Shock', 'Clone',],
            sideboard_card_names=[],
            match_record=(3,0,),
        ),
        importer.deck_helper.DeckData(
            format='my-custom-draft',
            expansion='ABC',
            deck_name='deckprefix.txt-2',
            maindeck_card_names=['Shock', 'Shock', 'Shock', 'Shock',],
            sideboard_card_names=[],
            match_record=(3,0,),
        ),
    ]

    assert expected == decks
