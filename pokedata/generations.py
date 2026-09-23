"""Mapeia o numero da Pokedex nacional pra geracao (1 a 9). As faixas sao
fixas por geracao desde que a Pokedex nacional existe, entao dá pra resolver
so' com o id, sem chamada de rede extra.
"""

RANGES = [
    (1, 151, 1),
    (152, 251, 2),
    (252, 386, 3),
    (387, 493, 4),
    (494, 649, 5),
    (650, 721, 6),
    (722, 809, 7),
    (810, 905, 8),
    (906, 1025, 9),
]


def generation_for_id(dex_id):
    """Devolve a geracao (int) do National Dex id, ou None se for um id fora
    das faixas conhecidas (forma regional/especial sem id proprio, etc.)."""
    for start, end, generation in RANGES:
        if start <= dex_id <= end:
            return generation
    return None


def add_generation_column(df):
    """Copia do DataFrame com uma coluna "generation" a mais, calculada a
    partir de "id"."""
    df = df.copy()
    df["generation"] = df["id"].apply(generation_for_id)
    return df
