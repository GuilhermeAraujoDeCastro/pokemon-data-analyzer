"""Monta o DataFrame, le/grava CSV, valida schema de um CSV externo e
filtra por geracao/tipo."""
import pandas as pd

from pokedata.generations import generation_for_id

COLUMNS = [
    "id", "name", "type_1", "type_2",
    "hp", "attack", "defense", "special_attack", "special_defense", "speed",
    "height_m", "weight_kg",
]

NUMERIC_COLUMNS = ["id", "hp", "attack", "defense", "special_attack", "special_defense", "speed", "height_m", "weight_kg"]

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


def validate_schema(df, source="CSV"):
    """Confere que um CSV externo (ex: editado a mao) tem as colunas certas
    e com tipo numerico onde precisa, com um erro claro em vez de deixar
    quebrar mais na frente numa conta ou grafico."""
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{source} sem as colunas obrigatorias: {', '.join(missing)}")

    nao_numericas = [c for c in NUMERIC_COLUMNS if not pd.api.types.is_numeric_dtype(df[c])]
    if nao_numericas:
        raise ValueError(f"{source} tem valor nao numerico nas colunas: {', '.join(nao_numericas)}")


def load_csv(path):
    df = pd.read_csv(path)
    validate_schema(df, source=str(path))
    if "type_2" in df.columns:
        df["type_2"] = df["type_2"].fillna(SEM_SEGUNDO_TIPO)
    return df


def filter_by_generation(df, generation):
    """So' as linhas cujo "id" cai na geracao pedida (1 a 9)."""
    return df[df["id"].apply(generation_for_id) == generation].reset_index(drop=True)


def filter_by_type(df, type_name):
    """So' as linhas onde o tipo (primario ou secundario) bate, sem
    diferenciar maiusculas/minusculas."""
    type_name = type_name.lower()
    mask = (df["type_1"].str.lower() == type_name) | (df["type_2"].str.lower() == type_name)
    return df[mask].reset_index(drop=True)
