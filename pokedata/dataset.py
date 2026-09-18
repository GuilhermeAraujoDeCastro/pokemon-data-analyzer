"""Monta o DataFrame a partir dos registros limpos, e le/grava esse dataset
em CSV.
"""
import pandas as pd

COLUMNS = [
    "id", "name", "type_1", "type_2",
    "hp", "attack", "defense", "special_attack", "special_defense", "speed",
    "height_m", "weight_kg",
]

SEM_SEGUNDO_TIPO = "Nenhum"


def build_dataframe(clean_records):
    """Monta o DataFrame a partir de uma lista de dicts ja limpos (veja
    clean.py). Pokemon de um tipo só ficam com type_2 = "Nenhum" em vez de
    vazio, pra value_counts()/groupby() nao ignorarem essas linhas (o pandas
    solta grupos com NaN por padrao)."""
    df = pd.DataFrame(clean_records, columns=COLUMNS)
    df["type_2"] = df["type_2"].fillna(SEM_SEGUNDO_TIPO)
    return df


def save_csv(df, path):
    df.to_csv(path, index=False)


def load_csv(path):
    df = pd.read_csv(path)
    if "type_2" in df.columns:
        df["type_2"] = df["type_2"].fillna(SEM_SEGUNDO_TIPO)
    return df
