import sqlite3

from pokedata.dataset import build_dataframe
from pokedata.sql_export import export_to_sqlite

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


def test_export_to_sqlite_creates_table_with_correct_row_count(tmp_path):
    df = build_dataframe(SAMPLE_RECORDS)
    db_path = tmp_path / "pokemon.db"

    export_to_sqlite(df, db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM pokemon")
        assert cursor.fetchone()[0] == 2


def test_export_to_sqlite_replaces_existing_table(tmp_path):
    df = build_dataframe(SAMPLE_RECORDS)
    db_path = tmp_path / "pokemon.db"

    export_to_sqlite(df, db_path)
    export_to_sqlite(df.head(1), db_path)  # exporta de novo, com menos linhas

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM pokemon")
        assert cursor.fetchone()[0] == 1
