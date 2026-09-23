import pandas as pd
import pytest

from pokedata.dataset import (
    COLUMNS,
    build_dataframe,
    filter_by_generation,
    filter_by_type,
    load_csv,
    save_csv,
    validate_schema,
)

SAMPLE_RECORDS = [
    {
        "id": 1, "name": "bulbasaur", "type_1": "grass", "type_2": "poison",
        "hp": 45, "attack": 49, "defense": 49, "special_attack": 65,
        "special_defense": 65, "speed": 45, "height_m": 0.7, "weight_kg": 6.9,
    },
    {
        "id": 25, "name": "pikachu", "type_1": "electric", "type_2": None,
        "hp": 35, "attack": 55, "defense": 40, "special_attack": 50,
        "special_defense": 50, "speed": 90, "height_m": 0.4, "weight_kg": 6.0,
    },
]


def test_build_dataframe_has_expected_columns():
    df = build_dataframe(SAMPLE_RECORDS)
    assert list(df.columns) == COLUMNS


def test_build_dataframe_fills_missing_type2():
    df = build_dataframe(SAMPLE_RECORDS)
    pikachu = df[df["name"] == "pikachu"].iloc[0]
    assert pikachu["type_2"] == "Nenhum"


def test_build_dataframe_keeps_real_type2():
    df = build_dataframe(SAMPLE_RECORDS)
    bulbasaur = df[df["name"] == "bulbasaur"].iloc[0]
    assert bulbasaur["type_2"] == "poison"


def test_save_and_load_csv_roundtrip(tmp_path):
    df = build_dataframe(SAMPLE_RECORDS)
    csv_path = tmp_path / "pokemon.csv"

    save_csv(df, csv_path)
    loaded = load_csv(csv_path)

    assert list(loaded["name"]) == ["bulbasaur", "pikachu"]
    assert list(loaded["type_2"]) == ["poison", "Nenhum"]
    assert int(loaded.loc[loaded["name"] == "pikachu", "speed"].iloc[0]) == 90


def test_validate_schema_passes_for_valid_dataframe():
    validate_schema(build_dataframe(SAMPLE_RECORDS))  # nao deve lancar


def test_validate_schema_raises_when_column_missing():
    df = build_dataframe(SAMPLE_RECORDS).drop(columns=["defense"])

    with pytest.raises(ValueError, match="defense"):
        validate_schema(df)


def test_validate_schema_raises_when_stat_is_not_numeric():
    df = build_dataframe(SAMPLE_RECORDS)
    df["speed"] = df["speed"].astype(str)
    df.loc[0, "speed"] = "muito rapido"

    with pytest.raises(ValueError, match="speed"):
        validate_schema(df)


def test_load_csv_raises_clear_error_for_broken_csv(tmp_path):
    csv_path = tmp_path / "quebrado.csv"
    pd.DataFrame({"id": [1], "name": ["bulbasaur"]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError):
        load_csv(csv_path)


def test_filter_by_generation():
    df = build_dataframe(SAMPLE_RECORDS)  # ids 1 e 25, ambos geracao 1
    filtered = filter_by_generation(df, 1)

    assert list(filtered["name"]) == ["bulbasaur", "pikachu"]
    assert filter_by_generation(df, 2).empty


def test_filter_by_type_matches_primary_or_secondary():
    df = build_dataframe(SAMPLE_RECORDS)  # bulbasaur e grass/poison, pikachu e electric

    assert list(filter_by_type(df, "poison")["name"]) == ["bulbasaur"]
    assert list(filter_by_type(df, "ELECTRIC")["name"]) == ["pikachu"]
    assert filter_by_type(df, "fire").empty
