from pokedata.charts import (
    charts_up_to_date,
    plot_average_speed_by_type,
    plot_correlation_heatmap,
    plot_top_n_by_stat,
    plot_type_distribution,
    plot_weight_vs_defense,
    write_charts_marker,
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


def test_plots_also_create_svg_version(tmp_path):
    output = tmp_path / "distribuicao.png"
    plot_type_distribution(make_df(), output)

    svg = output.with_suffix(".svg")
    assert svg.exists()
    assert svg.stat().st_size > 0


def test_plot_type_distribution_compare_mode(tmp_path):
    output = tmp_path / "distribuicao.png"
    other_df = make_df()

    plot_type_distribution(make_df(), output, compare_df=other_df, labels=("Kanto", "Johto"))

    assert output.exists()


def test_plot_weight_vs_defense_compare_mode(tmp_path):
    output = tmp_path / "peso_defesa.png"
    other_df = make_df()

    plot_weight_vs_defense(make_df(), output, compare_df=other_df, labels=("Kanto", "Johto"))

    assert output.exists()


def test_plot_correlation_heatmap_creates_file(tmp_path):
    output = tmp_path / "correlacao.png"
    plot_correlation_heatmap(make_df(), output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_charts_up_to_date_false_when_no_marker(tmp_path):
    assert charts_up_to_date(make_df(), tmp_path) is False


def test_charts_up_to_date_true_after_writing_marker(tmp_path):
    df = make_df()
    write_charts_marker(df, tmp_path)

    assert charts_up_to_date(df, tmp_path) is True


def test_charts_up_to_date_false_when_data_changes(tmp_path):
    df = make_df()
    write_charts_marker(df, tmp_path)

    changed = df.copy()
    changed.loc[0, "speed"] = 999

    assert charts_up_to_date(changed, tmp_path) is False
