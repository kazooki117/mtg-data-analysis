import db.card_repository
import db.mtga_card_repository
import importer.mtga_mapping_importer

from unittest.mock import MagicMock, call, patch
from db.model import Card, MTGACard

def test_add_from_csv_multiple_cards():
    mock_session = MagicMock()
    input_data = (
        ('101', 'Shock'),
        ('102', 'Terror'),
        ('103', 'Revitalize'),
    )

    get_mtga_card = MagicMock()
    get_mtga_card.side_effect = (
        None,
        None,
        MTGACard(mtga_id=103, name='Revitalize', primary_card_id=3)
    )
    get_card_by_approximate_name = MagicMock()
    get_card_by_approximate_name.side_effect = (
        Card(id=1),
        Card(id=2),
    )
    with patch('db.mtga_card_repository.get_mtga_card', get_mtga_card), \
          patch('db.card_repository.get_card_by_approximate_name', get_card_by_approximate_name):
        importer.mtga_mapping_importer.add_from_csv(mock_session, 'ABC', input_data)

    assert get_mtga_card.call_args_list == [
        call(mock_session, 101),
        call(mock_session, 102),
        call(mock_session, 103),
    ]
    assert get_card_by_approximate_name.call_args_list == [
        call(mock_session, 'ABC', 'Shock'),
        call(mock_session, 'ABC', 'Terror'),
    ]
