import importer.set_importer

from db.model import Expansion, Card

def test_normalizeStringForDb_doesNothingForASCIIStrings():
  assert 'Nicol Bolas, the Ravager' == importer.set_importer.normalizeStringForDb('Nicol Bolas, the Ravager')

def test_normalizeStringForDb_replacesKnownBadCharacters():
  assert '-3: Destroy target creature' == importer.set_importer.normalizeStringForDb(u'\u22123: Destroy target creature')
  assert 'Creature - Dragon' == importer.set_importer.normalizeStringForDb(u'Creature \u2014 Dragon')
  assert '* Tap target creature' == importer.set_importer.normalizeStringForDb(u'\u2022 Tap target creature')

def test_convertBlobToExpansion_usesTheLastBasicAsMaxCardNumber():
  jsonBlob = {
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

  actual = importer.set_importer.convertBlobToExpansion(jsonBlob)

  assert 'Guilds of Ravnica' == actual.name
  assert 264 == actual.max_booster_number
  assert 'GRN' == actual.abbreviation

def test_convertBlobToCard_handlesBasicCreatures():
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

def test_convertBlobToCard_handlesVariablePowerCreatures():
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

def test_convertBlobToCard_handlesPlaneswalkers():
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

