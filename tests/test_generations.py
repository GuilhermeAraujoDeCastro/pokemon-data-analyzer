from pokedata.dataset import build_dataframe
from pokedata.generations import add_generation_column, generation_for_id


def test_generation_for_id_first_and_last_of_gen1():
    assert generation_for_id(1) == 1
    assert generation_for_id(151) == 1


def test_generation_for_id_boundary_between_gens():
    assert generation_for_id(151) == 1
    assert generation_for_id(152) == 2


def test_generation_for_id_gen9():
    assert generation_for_id(906) == 9
    assert generation_for_id(1025) == 9


def test_generation_for_id_unknown_returns_none():
    assert generation_for_id(999999) is None


def test_add_generation_column():
    df = build_dataframe([
        {"id": 1, "name": "bulbasaur", "type_1": "grass", "type_2": "poison",
         "hp": 45, "attack": 49, "defense": 49, "special_attack": 65,
         "special_defense": 65, "speed": 45, "height_m": 0.7, "weight_kg": 6.9},
        {"id": 155, "name": "cyndaquil", "type_1": "fire", "type_2": None,
         "hp": 39, "attack": 52, "defense": 43, "special_attack": 60,
         "special_defense": 50, "speed": 65, "height_m": 0.5, "weight_kg": 7.9},
    ])

    result = add_generation_column(df)

    assert list(result["generation"]) == [1, 2]
    # nao deve alterar o DataFrame original
    assert "generation" not in df.columns
