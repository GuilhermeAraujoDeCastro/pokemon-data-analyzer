from pokedata.dataset import build_dataframe
from pokedata.html_report import build_html_report, export_html_report

SAMPLE_RECORDS = [
    {"id": 1, "name": "bulbasaur", "type_1": "grass", "type_2": "poison",
     "hp": 45, "attack": 49, "defense": 49, "special_attack": 65,
     "special_defense": 65, "speed": 45, "height_m": 0.7, "weight_kg": 6.9},
    {"id": 25, "name": "pikachu", "type_1": "electric", "type_2": None,
     "hp": 35, "attack": 55, "defense": 40, "special_attack": 50,
     "special_defense": 50, "speed": 90, "height_m": 0.4, "weight_kg": 6.0},
]


def make_df():
    return build_dataframe(SAMPLE_RECORDS)


def test_build_html_report_contains_key_numbers():
    html = build_html_report(make_df())

    assert "<html" in html
    assert "bulbasaur" in html or "Bulbasaur" in html
    assert "pikachu" in html


def test_build_html_report_without_charts_dir_shows_placeholder():
    html = build_html_report(make_df())
    assert "Rode com --charts-dir" in html


def test_build_html_report_embeds_svg_when_charts_dir_has_them(tmp_path):
    (tmp_path / "distribuicao_tipos.svg").write_text("<svg><circle/></svg>", encoding="utf-8")

    html = build_html_report(make_df(), charts_dir=tmp_path)

    assert "<circle/>" in html


def test_export_html_report_writes_file(tmp_path):
    output = tmp_path / "relatorio.html"
    export_html_report(make_df(), output)

    assert output.exists()
    assert "<html" in output.read_text(encoding="utf-8")
