import datetime
import io

import importer.flooey_importer


def test_extract_picks():
    packs_blob = [
        {
            'picks': [
                {
                    'cards': [
                        'Goblin Electromancer', 
                        'Dimir Informant', 
                        'Undercity Uprising', 
                        'Skyknight Legionnaire', 
                        'Sonic Assault', 
                        'Bartizan Bats', 
                        'Luminous Bonds', 
                        'Torch Courier', 
                        'Wary Okapi', 
                        'Direct Current', 
                        'Sunhome Stalwart', 
                        'Justice Strike', 
                        'Rampaging Monument', 
                        'Aurelia, Exemplar of Justice', 
                        'Golgari Guildgate',
                    ], 
                    'pick': 'Aurelia, Exemplar of Justice',
                }, 
            ], 
            'productCode': 'ABC',
        }, 
        {
            'picks': [
                {
                    'cards': [
                        'Erstwhile Trooper', 
                        'Never Happened', 
                        'Golgari Guildgate',
                    ], 
                    'pick': 'Golgari Guildgate',
                }, 
                {
                    'cards': [
                        'Douser of Lights', 
                        'Wary Okapi',
                    ], 
                    'pick': 'Wary Okapi',
                }, 
                {
                    'cards': [
                        'Wary Okapi',
                    ], 
                    'pick': 'Wary Okapi',
                }
          ], 
          'productCode': 'GRN',
        }
    ]

    expected = [
        importer.draft_helper.PickInfo(
            expansion='ABC',
            pick_number=1,
            pack_card_names=[
                'Goblin Electromancer', 
                'Dimir Informant', 
                'Undercity Uprising', 
                'Skyknight Legionnaire', 
                'Sonic Assault', 
                'Bartizan Bats', 
                'Luminous Bonds', 
                'Torch Courier', 
                'Wary Okapi', 
                'Direct Current', 
                'Sunhome Stalwart', 
                'Justice Strike', 
                'Rampaging Monument', 
                'Aurelia, Exemplar of Justice', 
                'Golgari Guildgate',
            ],
            pick='Aurelia, Exemplar of Justice',
        ),
        importer.draft_helper.PickInfo(
            expansion='GRN',
            pick_number=28,
            pack_card_names=['Erstwhile Trooper', 'Never Happened', 'Golgari Guildgate',],
            pick='Golgari Guildgate',
        ),
        importer.draft_helper.PickInfo(
            expansion='GRN',
            pick_number=29,
            pack_card_names=['Douser of Lights', 'Wary Okapi'],
            pick='Wary Okapi',
        ),
        importer.draft_helper.PickInfo(
            expansion='GRN',
            pick_number=30,
            pack_card_names=['Wary Okapi',],
            pick='Wary Okapi',
        ),
    ]

    assert expected == importer.flooey_importer.extract_picks(packs_blob)

def test_extract_individual_draft():
    draft_blob = {
        "Draft": {
            "event": "3622", 
            "packs": [
                {
                    'picks': [
                        {
                            'cards': [
                                'Rampaging Monument', 
                                'Aurelia, Exemplar of Justice', 
                                'Golgari Guildgate',
                            ], 
                            'pick': 'Aurelia, Exemplar of Justice',
                        }, 
                        {
                            'cards': [
                                'Douser of Lights', 
                                'Terror',
                            ], 
                            'pick': 'Terror',
                        }, 
                    ], 
                    'productCode': 'ABC',
                }, 
                {
                    'picks': [
                        {
                            'cards': [
                                'Wary Okapi',
                            ], 
                            'pick': 'Wary Okapi',
                        }
                  ], 
                  'productCode': 'GRN',
                }
            ],
            "time": "1970-01-01 00:00:01"
        }, 
        "Format": "GRN-GRN-GRN"
    }


    expected = importer.draft_helper.DraftData(
        draft_time=datetime.datetime(1970, 1, 1, 0, 0, 1),
        user=None,
        draft_name=f'GRN-GRN-GRN-3622-{datetime.datetime(1970, 1, 1, 0, 0, 1).timestamp()}',
        picks=[
            importer.draft_helper.PickInfo(
                expansion='ABC',
                pick_number=13,
                pack_card_names=[
                    'Rampaging Monument', 
                    'Aurelia, Exemplar of Justice', 
                    'Golgari Guildgate',
                ],
                pick='Aurelia, Exemplar of Justice',
            ),
            importer.draft_helper.PickInfo(
                expansion='ABC',
                pick_number=14,
                pack_card_names=['Douser of Lights', 'Terror',],
                pick='Terror',
            ),
            importer.draft_helper.PickInfo(
                expansion='GRN',
                pick_number=30,
                pack_card_names=['Wary Okapi',],
                pick='Wary Okapi',
            ),
        ]
    )

    assert expected == importer.flooey_importer.extract_individual_draft(draft_blob)
