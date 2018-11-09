import io
import datetime

import importer.mtgo_log_importer
import importer.draft_helper

def test_get_draft_info():
    sample_log_file = io.StringIO('\n'.join((
        "Event #: 421",
        "Time:    10/4/2018 1:23:45 PM",
        "Players:",
        "    Richard",
        "--> Garfield",
        "",
        "--: Legion Warboss",
        "",
    )))

    (draft_time, user) = importer.mtgo_log_importer.get_draft_info(sample_log_file)
    assert datetime.datetime(2018, 10, 4, 13, 23, 45) == draft_time
    assert 'Garfield' == user

def test_get_draft_picks():
    sample_log_file = io.StringIO('\n'.join((
        "--: Legion Warboss",
        "",
        "------ ABC ------ ",
        "",
        "Pack 1 pick 1:",
        "--> Legion Warboss",
        "    Dimir Guildgate",
        "",
        "--: Command the Storm",
        "",
        "Pack 1 pick 2:",
        "--> Command the Storm",
        "",
        "--: Vigorspore Wurm",
        "",
        "--: Piston-Fist Cyclops",
        "",
        "------ GRN ------ ",
        "",
        "Pack 2 pick 1:",
        "--> Piston-Fist Cyclops",
        "    Vigorspore Wurm",
        "",
        "--: Electrostatic Field",
        "",
        "Pack 2 pick 2:",
        "--> Electrostatic Field",
        "\n",
    )))

    expected = [
        importer.draft_helper.PickInfo(
            expansion='ABC',
            pick_number=1,
            pack_card_names=['Legion Warboss', 'Dimir Guildgate'],
            pick='Legion Warboss',
        ),
        importer.draft_helper.PickInfo(
            expansion='ABC',
            pick_number=2,
            pack_card_names=['Command the Storm'],
            pick='Command the Storm',
        ),
        importer.draft_helper.PickInfo(
            expansion='GRN',
            pick_number=16,
            pack_card_names=['Piston-Fist Cyclops', 'Vigorspore Wurm'],
            pick='Piston-Fist Cyclops',
        ),
        importer.draft_helper.PickInfo(
            expansion='GRN',
            pick_number=17,
            pack_card_names=['Electrostatic Field'],
            pick='Electrostatic Field',
        ),
    ]

    actual = importer.mtgo_log_importer.get_draft_picks(sample_log_file)

    assert expected == actual

def test_get_draft_picks_handles_skipped_picks():
    sample_log_file = io.StringIO('\n'.join((
        "--: Legion Warboss",
        "",
        "------ ABC ------ ",
        "",
        "Pack 1 pick 1:",
        "    Price of Fame",
        "--> Legion Warboss",
        "    Dimir Guildgate",
        "",
        "--: Command the Storm",
        "",
        "Pack 1 pick 3:",
        "--> Command the Storm",
        "\n",
    )))

    expected = [
        importer.draft_helper.PickInfo(
            expansion='ABC',
            pick_number=1,
            pack_card_names=['Price of Fame', 'Legion Warboss', 'Dimir Guildgate'],
            pick='Legion Warboss',
        ),
        importer.draft_helper.PickInfo(
            expansion='ABC',
            pick_number=3,
            pack_card_names=['Command the Storm'],
            pick='Command the Storm',
        ),
    ]

    actual = importer.mtgo_log_importer.get_draft_picks(sample_log_file)

    assert expected == actual

def test_get_draft_picks_handles_missed_last_pick():
    sample_log_file = io.StringIO('\n'.join((
        "--: Legion Warboss",
        "",
        "------ ABC ------ ",
        "",
        "Pack 1 pick 1:",
        "    Price of Fame",
        "--> Legion Warboss",
        "    Dimir Guildgate",
        "",
        "\n",
    )))

    expected = [
        importer.draft_helper.PickInfo(
            expansion='ABC',
            pick_number=1,
            pack_card_names=['Price of Fame', 'Legion Warboss', 'Dimir Guildgate'],
            pick='Legion Warboss',
        ),
    ]

    actual = importer.mtgo_log_importer.get_draft_picks(sample_log_file)

    assert expected == actual

def test_extract_draft_data():
    sample_log_file = io.StringIO('\n'.join((
        "Event #: 421",
        "Time:    10/4/2018 1:23:45 PM",
        "Players:",
        "--> Richard",
        "    Garfield",
        "",
        "--: Legion Warboss",
        "",
        "------ GRN ------ ",
        "",
        "Pack 1 pick 1:",
        "--> Legion Warboss",
        "    Dimir Guildgate",
        "",
        "--: Electrostatic Field",
        "",
        "Pack 1 pick 2:",
        "--> Electrostatic Field",
        "\n",
    )))

    expected = importer.draft_helper.DraftData(
        draft_time=datetime.datetime(2018, 10, 4, 13, 23, 45),
        user='Richard',
        draft_name='Foo draft',
        picks=[
            importer.draft_helper.PickInfo(
                expansion='GRN',
                pick_number=1,
                pack_card_names=['Legion Warboss', 'Dimir Guildgate'],
                pick='Legion Warboss',
            ),
            importer.draft_helper.PickInfo(
                expansion='GRN',
                pick_number=2,
                pack_card_names=['Electrostatic Field'],
                pick='Electrostatic Field',
            ),
        ],
    )

    assert expected == importer.mtgo_log_importer.extract_draft_data(sample_log_file, 'Foo draft')

    
