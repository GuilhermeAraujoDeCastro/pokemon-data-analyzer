"""Transforma o JSON bruto da PokeAPI num registro plano, pronto pra virar
uma linha de tabela. A PokeAPI devolve altura em decimetros e peso em
hectogramas (detalhe documentado da API, facil de passar batido); aqui ja
converte pra metros e quilos, que e' o que faz sentido pra analise.
"""

STATS_MAP = {
    "hp": "hp",
    "attack": "attack",
    "defense": "defense",
    "special-attack": "special_attack",
    "special-defense": "special_defense",
    "speed": "speed",
}


def clean_pokemon_record(raw):
    """Recebe o dict bruto de 1 Pokemon (formato da PokeAPI) e devolve um
    dict plano só com os campos que a analise usa."""
    types = [t["type"]["name"] for t in raw.get("types", [])]
    raw_stats = {s["stat"]["name"]: s["base_stat"] for s in raw.get("stats", [])}
    stats = {STATS_MAP[k]: v for k, v in raw_stats.items() if k in STATS_MAP}

    return {
        "id": raw["id"],
        "name": raw["name"],
        "type_1": types[0] if len(types) > 0 else None,
        "type_2": types[1] if len(types) > 1 else None,
        "hp": stats.get("hp"),
        "attack": stats.get("attack"),
        "defense": stats.get("defense"),
        "special_attack": stats.get("special_attack"),
        "special_defense": stats.get("special_defense"),
        "speed": stats.get("speed"),
        "height_m": raw["height"] / 10,
        "weight_kg": raw["weight"] / 10,
    }


def clean_all(raw_records):
    """Aplica clean_pokemon_record em cada item de uma lista de registros brutos."""
    return [clean_pokemon_record(r) for r in raw_records]
