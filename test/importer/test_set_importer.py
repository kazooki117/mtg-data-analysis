import db.expansion_repository
import db.card_repository
import importer.set_importer

from unittest.mock import MagicMock
from db.model import Expansion, Card

def test_normalizeStringForDb_ASCII_strings():
    assert 'Nicol Bolas, the Ravager' == importer.set_importer.normalizeStringForDb('Nicol Bolas, the Ravager')

def test_normalizeStringForDb_known_bad_characters():
    assert '-3: Destroy target creature' == importer.set_importer.normalizeStringForDb(u'\u22123: Destroy target creature')
    assert 'Creature - Dragon' == importer.set_importer.normalizeStringForDb(u'Creature \u2014 Dragon')
    assert '* Tap target creature' == importer.set_importer.normalizeStringForDb(u'\u2022 Tap target creature')

def test_convertBlobToExpansion():
    blob = {
        'name': 'Guilds of Ravnica',
        'code': 'GRN',
        'cards': [
            {
                'name': 'Direct Current',
                'number': '96',
                'type': 'Sorcery',
            },
            {
                'name': 'Island',
                'number': '261',
                'type': 'Basic Land — Island',
            },
            {
                'name': 'Forest',
                'number': '264',
                'type': 'Basic Land — Forest',
            },
            {
                'name': 'Impervious Greatwurm',
                'number': '273',
                'type': 'Creature — Wurm',
            }
        ]
    }

    actual = importer.set_importer.convertBlobToExpansion(blob)

    assert 'Guilds of Ravnica' == actual.name
    assert 264 == actual.max_booster_number
    assert 'GRN' == actual.abbreviation

def test_convertBlobToCard_basic_creatures():
    blob = {
        "manaCost": "{2}{R}",
        "name": "Fearless Halberdier",
        "number": "100",
        "power": "3",
        "rarity": "Common",
        "toughness": "2",
        "type": "Creature — Human Warrior",
    }

    actual = importer.set_importer.convertBlobToCard(blob, expansionId=123)

    assert 123 == actual.expansion
    assert 'Fearless Halberdier' == actual.name
    assert 'Common' == actual.rarity
    assert 100 == actual.number
    assert None == actual.face
    assert '{2}{R}' == actual.mana_cost
    assert None == actual.text
    assert 'Creature - Human Warrior' == actual.type
    assert 3 == actual.power
    assert 2 == actual.toughness
    assert None == actual.loyalty

def test_convertBlobToCard_variable_power_creatures():
    blob = {
        "artist": "Victor Adame Minguez",
        "cmc": 4,
        "colorIdentity": [
            "U",
            "R"
        ],
        "colors": [
            "Blue",
            "Red"
        ],
        "id": "ba12c18ec97e595c05a4da1cd951a42988e876f8",
        "imageName": "crackling drake",
        "layout": "normal",
        "manaCost": "{U}{U}{R}{R}",
        "multiverseid": 452913,
        "name": "Crackling Drake",
        "number": "163",
        "power": "*",
        "rarity": "Uncommon",
        "subtypes": [
            "Drake"
        ],
        "text": "Flying\nCrackling Drake's power is equal to the total number of instant and sorcery cards you own in exile and in your graveyard.\nWhen Crackling Drake enters the battlefield, draw a card.",
        "toughness": "4",
        "type": "Creature — Drake",
        "types": [
            "Creature"
        ],
        "watermark": "Izzet"
    }

    actual = importer.set_importer.convertBlobToCard(blob, expansionId=123)

    assert 123 == actual.expansion
    assert 'Crackling Drake' == actual.name
    assert 'Uncommon' == actual.rarity
    assert 163 == actual.number
    assert None == actual.face
    assert '{U}{U}{R}{R}' == actual.mana_cost
    assert "Flying\nCrackling Drake's power is equal to the total number of instant and sorcery cards you own in exile and in your graveyard.\nWhen Crackling Drake enters the battlefield, draw a card." == actual.text
    assert 'Creature - Drake' == actual.type
    assert None == actual.power
    assert 4 == actual.toughness
    assert None == actual.loyalty

def test_convertBlobToCard_planeswalkers():
    blob = {
        "loyalty": 5,
        "manaCost": "{3}{U}{R}",
        "name": "Ral, Izzet Viceroy",
        "number": "195",
        "rarity": "Mythic Rare",
        "text": "+1: Look at the top two cards of your library. Put one of them into your hand and the other into your graveyard.\n−3: Ral, Izzet Viceroy deals damage to target creature equal to the total number of instant and sorcery cards you own in exile and in your graveyard.\n−8: You get an emblem with \"Whenever you cast an instant or sorcery spell, this emblem deals 4 damage to any target and you draw two cards.\"",
        "type": "Legendary Planeswalker — Ral",
    }

    actual = importer.set_importer.convertBlobToCard(blob, expansionId=321)

    assert 321 == actual.expansion
    assert 'Ral, Izzet Viceroy' == actual.name
    assert 'Mythic Rare' == actual.rarity
    assert 195 == actual.number
    assert None == actual.face
    assert '{3}{U}{R}' == actual.mana_cost
    assert "+1: Look at the top two cards of your library. Put one of them into your hand and the other into your graveyard.\n-3: Ral, Izzet Viceroy deals damage to target creature equal to the total number of instant and sorcery cards you own in exile and in your graveyard.\n-8: You get an emblem with \"Whenever you cast an instant or sorcery spell, this emblem deals 4 damage to any target and you draw two cards.\"" == actual.text
    assert 'Legendary Planeswalker - Ral' == actual.type
    assert None == actual.power
    assert None == actual.toughness
    assert 5 == actual.loyalty

def test_getOrPersistExpansion_existing_expansion(mocker):
    get_expansion = mocker.patch('db.expansion_repository.get_expansion')
    get_expansion.return_value = Expansion(id=123)

    assert 123 == importer.set_importer.getOrPersistExpansion('my-session', Expansion(name='my-expansion')).id
    db.expansion_repository.get_expansion.assert_called_once_with('my-session', 'my-expansion')

def test_getOrPersistExpansion_new_expansion(mocker):
    get_expansion = mocker.patch('db.expansion_repository.get_expansion')
    get_expansion.return_value = None

    mock_session = MagicMock()
    input_expansion = Expansion(abbreviation='ABC', name='my-expansion', max_booster_number=321)

    assert input_expansion == importer.set_importer.getOrPersistExpansion(mock_session, input_expansion)
    db.expansion_repository.get_expansion.assert_called_once_with(mock_session, 'my-expansion')
    mock_session.add.assert_called_once_with(input_expansion)

def test_getOrPersistCard_existing_card(mocker):
    get_card = mocker.patch('db.card_repository.get_card')
    get_card.return_value = Card(id=123)

    assert 123 == importer.set_importer.getOrPersistCard('my-session', Card(expansion=42, number=100, face='A')).id
    db.card_repository.get_card.assert_called_once_with(session='my-session', expansion_id=42, number=100, face='A')

def test_getOrPersistCard_new_card(mocker):
    get_card = mocker.patch('db.card_repository.get_card')
    get_card.return_value = None

    mock_session = MagicMock()
    input_card = Card(expansion=42, number=100, face='A')

    assert input_card == importer.set_importer.getOrPersistCard(mock_session, input_card)
    db.card_repository.get_card.assert_called_once_with(session=mock_session, expansion_id=42, number=100, face='A')
    mock_session.add.assert_called_once_with(input_card)
