import db.card_repository
import db.mtga_card_repository
import importer.deck_helper
import importer.mtga_log_importer

from unittest.mock import MagicMock, call, patch
from db.model import Card, MTGACard

def test_get_card_name(mocker):
    mocker.patch('db.mtga_card_repository.get_mtga_card').return_value = MTGACard(primary_card_id=101)
    mocker.patch('db.card_repository.get_card_by_id').return_value = Card(name='Shock')

    assert 'Shock' == importer.mtga_log_importer.get_card_name('my-session', 123)
    db.mtga_card_repository.get_mtga_card.assert_called_once_with('my-session', 123)
    db.card_repository.get_card_by_id.assert_called_once_with('my-session', 101)

def test_maybe_get_league_info():
    input_blob = [{
        "Id": "blob-id",
        "InternalEventName": "QuickDraft_M19_11232018",
        "PlayerId": "player-id",
        "ModuleInstanceData": {
            "HasPaidEntry": "Gem",
            "DraftInfo": {
                "DraftId": "player-id:QuickDraft_M19_11232018:Draft"
            },
            "DraftComplete": True,
            "HasGranted": True,
            "DeckSelected": True,
            "WinLossGate": {
                "MaxWins": 7,
                "MaxLosses": 3,
                "CurrentWins": 6,
                "CurrentLosses": 3,
                "ProcessedMatchIds": ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz0',]
            }
        },
        "CurrentEventState": "Completed",
        "CurrentModule": "Complete",
        "CardPool": [101, 102, 103, 104, 103, 102, 101],
        "CourseDeck": {
            "id": "deck-id",
            "name": "Draft Deck",
            "description": "",
            "format": "Limited",
            "resourceId": "00000000-0000-0000-0000-000000000000",
            "deckTileId": 104,
            "mainDeck": [
                {"id": "101", "quantity": 1},
                {"id": "102", "quantity": 2},
                {"id": "104", "quantity": 1},
            ],
            "sideboard": [
                {"id": "103", "quantity": 2},
                {"id": "101", "quantity": 1},
            ],
            "lastUpdated": "2018-11-25T19:56:56.2244",
            "lockedForUse": False,
            "lockedForEdit": False,
            "isValid": False
        }
    }]

    def mtga_cards_by_mtga_id(*args):
        return {
            ('my-session', 101): MTGACard(primary_card_id=201),
            ('my-session', 102): MTGACard(primary_card_id=202),
            ('my-session', 103): MTGACard(primary_card_id=203),
            ('my-session', 104): MTGACard(primary_card_id=204),
        }[args]

    def cards_by_id(*args):
        return {
            ('my-session', 201): Card(name='Abrade'),
            ('my-session', 202): Card(name='Banefire'),
            ('my-session', 203): Card(name='Char'),
            ('my-session', 204): Card(name='Disintegrate'),
        }[args]

    get_mtga_card = MagicMock(side_effect=mtga_cards_by_mtga_id)
    get_card_by_id = MagicMock(side_effect=cards_by_id)

    with patch('db.mtga_card_repository.get_mtga_card', get_mtga_card), \
          patch('db.card_repository.get_card_by_id', get_card_by_id):
        result = importer.mtga_log_importer.maybe_get_league_info('my-session', input_blob)

    assert result == importer.deck_helper.DeckData(
        format='QuickDraft',
        expansion='M19',
        deck_name='blob-id',
        maindeck_card_names=['Abrade', 'Banefire', 'Banefire', 'Disintegrate',],
        sideboard_card_names=['Char', 'Char', 'Abrade',],
        match_record=(6, 3),
    )

def test_maybe_get_league_info_skips_in_progress_drafts():
    input_blob = [{
        "Id": "blob-id",
        "InternalEventName": "QuickDraft_M19_11232018",
        "PlayerId": "player-id",
        "ModuleInstanceData": {
            "HasPaidEntry": "Gem",
            "DraftInfo": {
                "DraftId": "player-id:QuickDraft_M19_11232018:Draft"
            },
            "DraftComplete": True,
            "HasGranted": True,
            "DeckSelected": True,
            "WinLossGate": {
                "MaxWins": 7,
                "MaxLosses": 3,
                "CurrentWins": 6,
                "CurrentLosses": 2,
                "ProcessedMatchIds": ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz0',]
            }
        },
        "CurrentEventState": "ReadyToMatch",
        "CurrentModule": "WinLossGate",
        "CardPool": [101, 102, 103, 104, 103, 102, 101],
        "CourseDeck": {
            "id": "deck-id",
            "name": "Draft Deck",
            "description": "",
            "format": "Limited",
            "resourceId": "00000000-0000-0000-0000-000000000000",
            "deckTileId": 104,
            "mainDeck": [
                {"id": "101", "quantity": 1},
                {"id": "102", "quantity": 2},
                {"id": "104", "quantity": 1},
            ],
            "sideboard": [
                {"id": "103", "quantity": 2},
                {"id": "101", "quantity": 1},
            ],
            "lastUpdated": "2018-11-25T19:56:56.2244",
            "lockedForUse": False,
            "lockedForEdit": False,
            "isValid": False
        }
    }]

    assert None == importer.mtga_log_importer.maybe_get_league_info('my-session', input_blob)

def test_maybe_get_draft_pack():
    input_blob = [{
        "playerId": "player-id",
        "eventName": "QuickDraft_M19_11232018",
        "draftId": "player-id:QuickDraft_M19_11232018:Draft",
        "draftStatus": "Draft.PickNext",
        "packNumber": 3,
        "pickNumber": 13,
        "draftPack": [
            "101",
            "102",
            "103",
        ],
        "pickedCards": ["104"],
        "requestUnits": 0.0
    }]

    def mtga_cards_by_mtga_id(*args):
        return {
            ('my-session', 101): MTGACard(primary_card_id=201),
            ('my-session', 102): MTGACard(primary_card_id=202),
            ('my-session', 103): MTGACard(primary_card_id=203),
            ('my-session', 104): MTGACard(primary_card_id=204),
        }[args]

    def cards_by_id(*args):
        return {
            ('my-session', 201): Card(name='Abrade'),
            ('my-session', 202): Card(name='Banefire'),
            ('my-session', 203): Card(name='Char'),
            ('my-session', 204): Card(name='Disintegrate'),
        }[args]

    get_mtga_card = MagicMock(side_effect=mtga_cards_by_mtga_id)
    get_card_by_id = MagicMock(side_effect=cards_by_id)

    with patch('db.mtga_card_repository.get_mtga_card', get_mtga_card), \
          patch('db.card_repository.get_card_by_id', get_card_by_id):
        result = importer.mtga_log_importer.maybe_get_draft_pack('my-session', input_blob)

    assert result == importer.mtga_log_importer.PickOptions(
        user='player-id',
        expansion='M19',
        format='QuickDraft',
        draft_id='player-id:QuickDraft_M19_11232018:Draft',
        pack_number=3,
        pick_number=13,
        pack_card_names=['Abrade', 'Banefire', 'Char'],
    )

def test_maybe_get_draft_pick():
    input_blob = [{
        "jsonrpc": "2.0",
        "method": "Draft.MakePick",
        "params": {
            "draftId": "player-id:QuickDraft_M19_11232018:Draft",
            "cardId": "103",
            "packNumber": "1",
            "pickNumber": "5"
        },
        "id": "166"
    }]

    def mtga_cards_by_mtga_id(*args):
        return {
            ('my-session', 103): MTGACard(primary_card_id=203),
        }[args]

    def cards_by_id(*args):
        return {
            ('my-session', 203): Card(name='Char'),
        }[args]

    get_mtga_card = MagicMock(side_effect=mtga_cards_by_mtga_id)
    get_card_by_id = MagicMock(side_effect=cards_by_id)

    with patch('db.mtga_card_repository.get_mtga_card', get_mtga_card), \
          patch('db.card_repository.get_card_by_id', get_card_by_id):
        result = importer.mtga_log_importer.maybe_get_draft_pick('my-session', input_blob)

    assert result == importer.mtga_log_importer.PickResult(
        draft_id='player-id:QuickDraft_M19_11232018:Draft',
        pack_number=1,
        pick_number=5,
        card_name='Char',
    )

def test_aggregate_draft_info():
    assert False, 'Test not yet implemented'