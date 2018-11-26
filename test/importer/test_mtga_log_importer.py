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
