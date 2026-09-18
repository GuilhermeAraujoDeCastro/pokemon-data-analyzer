from pokedata.analysis import (
    average_stat_by_type,
    fastest_type,
    rarest_type_combination,
    top_n_by_stat,
    type_combination_counts,
    weight_defense_correlation,
)
from pokedata.dataset import build_dataframe


def make_df(records):
    return build_dataframe(records)


def mon(name, type_1, type_2=None, hp=50, attack=50, defense=50,
        special_attack=50, special_defense=50, speed=50, height_m=1.0, weight_kg=50.0):
    return {
        "id": len(name), "name": name, "type_1": type_1, "type_2": type_2,
        "hp": hp, "attack": attack, "defense": defense,
        "special_attack": special_attack, "special_defense": special_defense,
        "speed": speed, "height_m": height_m, "weight_kg": weight_kg,
    }


def test_type_combination_counts_counts_each_combo():
    df = make_df([
        mon("a", "water"),
        mon("b", "water"),
        mon("c", "fire"),
    ])
    counts = type_combination_counts(df)

    assert counts["Water / Nenhum"] == 2
    assert counts["Fire / Nenhum"] == 1


def test_rarest_type_combination_finds_minimum():
    df = make_df([
        mon("a", "water"),
        mon("b", "water"),
        mon("c", "fire"),
    ])
    combo, count = rarest_type_combination(df)

    assert combo == "Fire / Nenhum"
    assert count == 1


def test_rarest_type_combination_breaks_ties_alphabetically():
    df = make_df([
        mon("a", "water"),
        mon("b", "fire"),
    ])
    combo, count = rarest_type_combination(df)

    # Empate 1 a 1: "Fire / Nenhum" vem antes de "Water / Nenhum" no alfabeto.
    assert combo == "Fire / Nenhum"
    assert count == 1


def test_average_stat_by_type_computes_mean_per_type():
    df = make_df([
        mon("a", "electric", speed=90),
        mon("b", "electric", speed=70),
        mon("c", "rock", speed=20),
    ])
    averages = average_stat_by_type(df, "speed")

    assert averages["electric"] == 80.0
    assert averages["rock"] == 20.0


def test_fastest_type_returns_highest_average():
    df = make_df([
        mon("a", "electric", speed=90),
        mon("b", "rock", speed=20),
    ])
    type_name, avg = fastest_type(df)

    assert type_name == "electric"
    assert avg == 90.0


def test_weight_defense_correlation_perfect_positive():
    df = make_df([
        mon("a", "rock", weight_kg=10, defense=20),
        mon("b", "rock", weight_kg=20, defense=40),
        mon("c", "rock", weight_kg=30, defense=60),
        mon("d", "rock", weight_kg=40, defense=80),
    ])
    correlation = weight_defense_correlation(df)

    assert correlation == 1.0


def test_weight_defense_correlation_is_weaker_when_unrelated():
    perfect = make_df([
        mon("a", "rock", weight_kg=10, defense=20),
        mon("b", "rock", weight_kg=20, defense=40),
        mon("c", "rock", weight_kg=30, defense=60),
        mon("d", "rock", weight_kg=40, defense=80),
    ])
    unrelated = make_df([
        mon("a", "rock", weight_kg=10, defense=10),
        mon("b", "rock", weight_kg=20, defense=90),
        mon("c", "rock", weight_kg=30, defense=10),
        mon("d", "rock", weight_kg=40, defense=90),
    ])

    assert weight_defense_correlation(unrelated) < weight_defense_correlation(perfect)


def test_top_n_by_stat_returns_correct_count_and_order():
    df = make_df([
        mon("lento", "rock", speed=10),
        mon("medio", "rock", speed=50),
        mon("rapido", "rock", speed=99),
    ])
    top2 = top_n_by_stat(df, "speed", 2)

    assert list(top2["name"]) == ["rapido", "medio"]
    assert len(top2) == 2
