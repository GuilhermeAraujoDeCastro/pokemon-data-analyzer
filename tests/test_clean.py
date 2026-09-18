import json
from pathlib import Path

from pokedata.clean import clean_all, clean_pokemon_record

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_clean_pokemon_record_extracts_types_and_stats():
    raw = load_fixture("bulbasaur_response.json")
    clean = clean_pokemon_record(raw)

    assert clean["id"] == 1
    assert clean["name"] == "bulbasaur"
    assert clean["type_1"] == "grass"
    assert clean["type_2"] == "poison"
    assert clean["hp"] == 45
    assert clean["attack"] == 49
    assert clean["defense"] == 49
    assert clean["special_attack"] == 65
    assert clean["special_defense"] == 65
    assert clean["speed"] == 45


def test_clean_pokemon_record_converts_height_and_weight_units():
    # A PokeAPI manda altura em decimetros e peso em hectogramas.
    raw = load_fixture("bulbasaur_response.json")
    clean = clean_pokemon_record(raw)

    assert clean["height_m"] == 0.7
    assert clean["weight_kg"] == 6.9


def test_clean_pokemon_record_handles_single_type():
    raw = load_fixture("pikachu_response.json")
    clean = clean_pokemon_record(raw)

    assert clean["type_1"] == "electric"
    assert clean["type_2"] is None


def test_clean_all_processes_multiple_records():
    raw_records = [load_fixture("bulbasaur_response.json"), load_fixture("pikachu_response.json")]
    cleaned = clean_all(raw_records)

    assert len(cleaned) == 2
    assert [c["name"] for c in cleaned] == ["bulbasaur", "pikachu"]
