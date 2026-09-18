from pokedata.charts import (
    plot_average_speed_by_type,
    plot_top_n_by_stat,
    plot_type_distribution,
    plot_weight_vs_defense,
)
from pokedata.dataset import build_dataframe

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
    {
        "id": 95, "name": "onix", "type_1": "rock", "type_2": "ground",
        "hp": 35, "attack": 45, "defense": 160, "special_attack": 30,
        "special_defense": 45, "speed": 70, "height_m": 8.8, "weight_kg": 210.0,
    },
]


def make_df():
    return build_dataframe(SAMPLE_RECORDS)


def test_plot_type_distribution_creates_file(tmp_path):
    output = tmp_path / "distribuicao.png"
    plot_type_distribution(make_df(), output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_plot_average_speed_by_type_creates_file(tmp_path):
    output = tmp_path / "velocidade.png"
    plot_average_speed_by_type(make_df(), output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_plot_weight_vs_defense_creates_file(tmp_path):
    output = tmp_path / "peso_defesa.png"
    plot_weight_vs_defense(make_df(), output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_plot_top_n_by_stat_creates_file(tmp_path):
    output = tmp_path / "top_ataque.png"
    plot_top_n_by_stat(make_df(), "attack", output, n=2)
    assert output.exists()
    assert output.stat().st_size > 0
