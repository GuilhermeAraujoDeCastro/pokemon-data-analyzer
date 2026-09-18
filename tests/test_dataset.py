from pokedata.dataset import COLUMNS, build_dataframe, load_csv, save_csv

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
