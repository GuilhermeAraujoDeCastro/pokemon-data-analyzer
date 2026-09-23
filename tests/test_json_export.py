import json

from pokedata.dataset import build_dataframe
from pokedata.json_export import build_report_dict, export_json

SAMPLE_RECORDS = [
    {"id": 1, "name": "bulbasaur", "type_1": "grass", "type_2": "poison",
     "hp": 45, "attack": 49, "defense": 49, "special_attack": 65,
     "special_defense": 65, "speed": 45, "height_m": 0.7, "weight_kg": 6.9},
    {"id": 25, "name": "pikachu", "type_1": "electric", "type_2": None,
     "hp": 35, "attack": 55, "defense": 40, "special_attack": 50,
     "special_defense": 50, "speed": 90, "height_m": 0.4, "weight_kg": 6.0},
]


def make_df():
    return build_dataframe(SAMPLE_RECORDS)


def test_build_report_dict_has_expected_shape():
    report = build_report_dict(make_df())

    assert report["summary"]["total"] == 2
    assert len(report["pokemon"]) == 2
    assert "weight_defense_correlation" in report["summary"]


def test_export_json_writes_both_files(tmp_path):
    export_json(make_df(), tmp_path)

    pokemon_path = tmp_path / "pokemon.json"
    report_path = tmp_path / "report.json"
    assert pokemon_path.exists()
    assert report_path.exists()

    pokemon_data = json.loads(pokemon_path.read_text(encoding="utf-8"))
    assert len(pokemon_data) == 2
    assert pokemon_data[0]["name"] == "bulbasaur"

    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    assert report_data["summary"]["total"] == 2
