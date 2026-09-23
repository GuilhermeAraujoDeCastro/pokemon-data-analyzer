"""Gera um relatorio HTML autocontido (CSS inline, SVGs dos graficos
embutidos direto no HTML) a partir do dataset. Pra virar PDF: abra o HTML
no navegador e use Imprimir -> Salvar como PDF -- nao compensa puxar uma
biblioteca so' pra isso.
"""
from pathlib import Path

from pokedata.analysis import (
    fastest_type,
    find_outliers,
    rarest_type_combination,
    top_n_by_stat,
    weight_defense_correlation,
)

CHART_FILES = [
    "distribuicao_tipos.svg",
    "velocidade_media_por_tipo.svg",
    "peso_vs_defesa.svg",
    "top_ataque.svg",
    "correlacao.svg",
]

STYLE = """
body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #222; }
h1 { border-bottom: 3px solid #4a90d9; padding-bottom: .5rem; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #ddd; }
.chart { margin: 1.5rem 0; }
.chart svg { max-width: 100%; height: auto; }
.stat { display: inline-block; background: #f2f6fc; border-radius: 8px; padding: .8rem 1.2rem; margin: .3rem; }
"""


def _table_rows(df, columns):
    return "".join(
        "<tr>" + "".join(f"<td>{row[c]}</td>" for c in columns) + "</tr>"
        for _, row in df.iterrows()
    )


def _embed_svg(path):
    path = Path(path)
    if not path.exists():
        return ""
    return f'<div class="chart">{path.read_text(encoding="utf-8")}</div>'


def build_html_report(df, charts_dir=None):
    combo, combo_count = rarest_type_combination(df)
    type_name, avg_speed = fastest_type(df)
    correlation = weight_defense_correlation(df)
    outliers = find_outliers(df, "hp")

    charts_html = ""
    if charts_dir:
        charts_dir = Path(charts_dir)
        charts_html = "".join(_embed_svg(charts_dir / f) for f in CHART_FILES)

    outliers_html = (
        "<p>Nenhum outlier de HP nesse dataset.</p>"
        if outliers.empty
        else "<table><tr><th>Pokemon</th><th>HP</th></tr>" + _table_rows(outliers, ["name", "hp"]) + "</table>"
    )

    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Relatorio Pokemon</title>
<style>{STYLE}</style>
</head>
<body>
<h1>Extrator e Analisador de Dados Pokemon</h1>
<div class="stat"><strong>Total de Pokemon:</strong> {len(df)}</div>
<div class="stat"><strong>Combinacao mais rara:</strong> {combo} ({combo_count})</div>
<div class="stat"><strong>Tipo mais rapido:</strong> {type_name} ({avg_speed:.1f})</div>
<div class="stat"><strong>Correlacao peso/defesa:</strong> {correlation:.3f}</div>

<h2>Outliers de HP (fora da curva)</h2>
{outliers_html}

<h2>Top 10 em ataque</h2>
<table><tr><th>Pokemon</th><th>Ataque</th></tr>{_table_rows(top_n_by_stat(df, "attack", 10), ["name", "attack"])}</table>

<h2>Graficos</h2>
{charts_html or "<p>Rode com --charts-dir apontando pra uma pasta com os SVGs gerados.</p>"}
</body>
</html>"""


def export_html_report(df, output_path, charts_dir=None):
    Path(output_path).write_text(build_html_report(df, charts_dir), encoding="utf-8")
