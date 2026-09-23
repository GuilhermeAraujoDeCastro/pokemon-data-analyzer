from pokedata.analysis import (
    average_stat_by_type,
    correlation_matrix,
    fastest_type,
    find_outliers,
    height_hp_correlation,
    most_common_type_by_generation,
    rarest_type_combination,
    stat_total_distribution_by_generation,
    top_n_by_stat,
    type_combination_counts,
    weight_defense_correlation,
)
from pokedata.dataset import build_dataframe
from pokedata.generations import add_generation_column


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


def test_weight_defense_correlation_is_nan_without_warning_when_constant(recwarn):
    # peso constante -> desvio padrao 0 -> correlacao NaN (matematicamente
    # correto), sem soltar RuntimeWarning do numpy no meio do relatorio.
    df = make_df([
        mon("a", "rock", weight_kg=10, defense=20),
        mon("b", "rock", weight_kg=10, defense=40),
    ])
    import math
    result = weight_defense_correlation(df)

    assert math.isnan(result)
    assert len(recwarn) == 0


def test_height_hp_correlation_perfect_positive():
    df = make_df([
        mon("a", "rock", height_m=1, hp=10),
        mon("b", "rock", height_m=2, hp=20),
        mon("c", "rock", height_m=3, hp=30),
    ])
    assert height_hp_correlation(df) == 1.0


def make_gen_df():
    df = make_df([
        mon("bulbasaur", "grass", speed=45),
        mon("ivysaur", "grass", speed=60),
        mon("charmander", "fire", speed=65),
        mon("chikorita", "grass", speed=32),
    ])
    df.loc[0, "id"] = 1    # geracao 1
    df.loc[1, "id"] = 2    # geracao 1
    df.loc[2, "id"] = 4    # geracao 1
    df.loc[3, "id"] = 152  # geracao 2
    return add_generation_column(df)


def test_most_common_type_by_generation():
    result = most_common_type_by_generation(make_gen_df())

    assert result[1] == "grass"  # 2 grass x 1 fire na geracao 1
    assert result[2] == "grass"


def test_stat_total_distribution_by_generation_has_one_row_per_generation():
    result = stat_total_distribution_by_generation(make_gen_df())

    assert set(result.index) == {1, 2}
    assert result.loc[1, "count"] == 3
    assert result.loc[2, "count"] == 1


def test_correlation_matrix_is_symmetric_with_ones_on_diagonal():
    # todas as stats variam entre as linhas -- uma coluna constante teria
    # desvio padrao 0 e a correlacao dela viraria NaN (matematicamente
    # correto, mas atrapalharia esse teste especifico).
    df = make_df([
        mon("a", "rock", hp=10, attack=20, defense=30, special_attack=1, special_defense=2, speed=5, height_m=1, weight_kg=10),
        mon("b", "rock", hp=20, attack=40, defense=60, special_attack=2, special_defense=4, speed=15, height_m=2, weight_kg=20),
        mon("c", "rock", hp=30, attack=60, defense=90, special_attack=3, special_defense=6, speed=25, height_m=3, weight_kg=30),
    ])
    matrix = correlation_matrix(df)

    assert (matrix.values.diagonal() == 1.0).all()
    assert matrix.loc["hp", "attack"] == matrix.loc["attack", "hp"]


def test_find_outliers_flags_value_far_from_the_rest():
    df = make_df([
        mon("comum1", "normal", hp=50),
        mon("comum2", "normal", hp=52),
        mon("comum3", "normal", hp=48),
        mon("comum4", "normal", hp=51),
        mon("extremo", "normal", hp=500),
    ])
    outliers = find_outliers(df, "hp")

    assert list(outliers["name"]) == ["extremo"]
