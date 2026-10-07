#!/usr/bin/env python3
"""Analisador de Dados Pokemon.

Busca dados de Pokemon (na PokeAPI ao vivo, ou de um CSV ja salvo), organiza
num dataset, responde um conjunto de perguntas estatisticas, gera graficos e
opcionalmente exporta pra SQLite, JSON ou um relatorio HTML.
"""
import argparse
import sys
from pathlib import Path

from pokedata.analysis import (
    average_stat_by_type,
    fastest_type,
    find_outliers,
    height_hp_correlation,
    most_common_type_by_generation,
    rarest_type_combination,
    top_n_by_stat,
    weight_defense_correlation,
)
from pokedata.charts import (
    charts_up_to_date,
    plot_average_speed_by_type,
    plot_correlation_heatmap,
    plot_top_n_by_stat,
    plot_type_distribution,
    plot_weight_vs_defense,
    write_charts_marker,
)
from pokedata.clean import clean_all
from pokedata.dataset import (
    build_dataframe,
    filter_by_generation,
    filter_by_type,
    load_csv,
    save_csv,
)
from pokedata.generations import add_generation_column
from pokedata.html_report import export_html_report
from pokedata.json_export import export_json
from pokedata.logging_setup import configure as configure_logging
from pokedata.sql_export import export_to_sqlite

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


def make_progress_reporter():
    """Barra de progresso com tqdm quando disponivel; um print com \\r como
    fallback, pra nao obrigar quem so' usa --source csv a instalar tqdm."""
    if tqdm is None:
        def progress(i, total):
            print(f"Baixando Pokemon {i}/{total}...", end="\r")
        return progress, lambda: None

    bar = tqdm(total=None, desc="Baixando Pokemon", unit="mon")

    def progress(i, total):
        if bar.total is None:
            bar.total = total
        bar.n = i
        bar.refresh()

    return progress, bar.close


def fetch_dataset(source, input_path, limit, save_csv_path):
    if source == "csv":
        return load_csv(input_path)

    # Import so' quando for buscar da API de verdade: quem usa --source csv
    # (o padrao) nao precisa nem ter o pacote requests instalado.
    from pokedata.fetch_api import fetch_all_pokemon

    progress, close_progress = make_progress_reporter()
    raw = fetch_all_pokemon(limit, on_progress=progress)
    close_progress()
    if tqdm is None:
        print()

    df = build_dataframe(clean_all(raw))
    save_csv(df, save_csv_path)
    print(f"Dataset salvo em {save_csv_path}")
    return df


def apply_filters(df, generation, type_name):
    if generation is not None:
        df = filter_by_generation(add_generation_column(df), generation)
    if type_name is not None:
        df = filter_by_type(df, type_name)
    return df


def print_report(df, compare_df=None, compare_label="Comparacao"):
    if df.empty:
        print("\nDataset vazio depois dos filtros -- nada pra reportar.")
        return

    print("\n=== Relatorio estatistico ===\n")

    combo, count = rarest_type_combination(df)
    print(f"Combinacao de tipos mais rara: {combo} ({count} Pokemon)")

    type_name, avg_speed = fastest_type(df)
    print(f"Tipo primario com maior velocidade media: {type_name} ({avg_speed:.1f})")

    print(f"Correlacao entre peso e defesa: {weight_defense_correlation(df):.3f}")
    print(f"Correlacao entre altura e HP: {height_hp_correlation(df):.3f}")

    generation_df = add_generation_column(df)
    common_by_gen = most_common_type_by_generation(generation_df)
    print("\nTipo mais comum por geracao:")
    print(common_by_gen.to_string())

    outliers = find_outliers(df, "hp")
    if not outliers.empty:
        print(f"\nOutliers de HP (fora da curva, {len(outliers)} encontrados):")
        print(outliers.to_string(index=False))

    print("\nTop 5 mais rapidos:")
    print(top_n_by_stat(df, "speed", 5).to_string(index=False))

    print("\nTop 5 maior ataque:")
    print(top_n_by_stat(df, "attack", 5).to_string(index=False))

    print("\nMedia de velocidade por tipo primario:")
    print(average_stat_by_type(df, "speed").round(1).to_string())

    if compare_df is not None and not compare_df.empty:
        print(f"\n=== Comparacao com {compare_label} ===\n")
        combo_b, count_b = rarest_type_combination(compare_df)
        print(f"[{compare_label}] Combinacao mais rara: {combo_b} ({count_b})")
        print(f"[{compare_label}] Correlacao peso/defesa: {weight_defense_correlation(compare_df):.3f}")


def generate_charts(df, output_dir, compare_df=None, compare_label="Comparacao"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # O marcador so' diz que o dataset nao mudou; se algum grafico foi apagado, gera de novo.
    graficos = ("distribuicao_tipos", "velocidade_media_por_tipo", "peso_vs_defesa", "top_ataque", "correlacao")
    faltando = any(not (output_dir / f"{nome}.{ext}").exists() for nome in graficos for ext in ("png", "svg"))
    if compare_df is None and not faltando and charts_up_to_date(df, output_dir):
        print(f"\nGraficos em {output_dir}/ ja estao atualizados (dataset nao mudou), pulando geracao.")
        return

    labels = ("Atual", compare_label)
    plot_type_distribution(df, output_dir / "distribuicao_tipos.png", compare_df=compare_df, labels=labels)
    plot_average_speed_by_type(df, output_dir / "velocidade_media_por_tipo.png")
    plot_weight_vs_defense(df, output_dir / "peso_vs_defesa.png", compare_df=compare_df, labels=labels)
    plot_top_n_by_stat(df, "attack", output_dir / "top_ataque.png")
    plot_correlation_heatmap(df, output_dir / "correlacao.png")

    if compare_df is None:
        write_charts_marker(df, output_dir)

    print(f"\nGraficos salvos em {output_dir}/ (.png e .svg)")


def run_interactive(args):
    """Prompts com questionary pra preencher as opcoes sem decorar as
    flags -- so' roda quando --interactive e' passado."""
    import questionary

    args.source = questionary.select(
        "De onde vem o dataset?", choices=["csv", "api"], default=args.source
    ).ask()
    if args.source == "csv":
        args.input = questionary.text("Caminho do CSV de entrada:", default=args.input).ask()
    else:
        args.limit = int(questionary.text("Quantos Pokemon buscar?", default=str(args.limit)).ask())

    if questionary.confirm("Filtrar por geracao?", default=False).ask():
        args.generation = int(questionary.text("Qual geracao (1-9)?").ask())
    if questionary.confirm("Filtrar por tipo?", default=False).ask():
        args.type = questionary.text("Qual tipo (ex: fire)?").ask()

    return args


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Analisador de dados Pokemon")
    parser.add_argument(
        "--source", choices=["api", "csv"], default="csv",
        help="De onde vem o dataset: 'api' busca ao vivo na PokeAPI, 'csv' le um arquivo ja salvo (padrao)",
    )
    parser.add_argument(
        "--input", default="data/sample_pokemon.csv",
        help="Caminho do CSV de entrada (quando --source csv)",
    )
    parser.add_argument(
        "--limit", type=int, default=151,
        help="Quantos Pokemon buscar na API (quando --source api). Padrao 151, a Pokedex de Kanto",
    )
    parser.add_argument(
        "--save-csv", default="data/pokemon_data.csv",
        help="Onde salvar o CSV baixado (quando --source api)",
    )
    parser.add_argument("--charts-dir", default="charts", help="Pasta onde salvar os graficos gerados")
    parser.add_argument("--no-charts", action="store_true", help="Pula a geracao de graficos")
    parser.add_argument("--sqlite-db", default=None, help="Caminho opcional pra exportar o dataset pra um banco SQLite")
    parser.add_argument("--html-report", default=None, help="Caminho opcional pra exportar um relatorio HTML autocontido")
    parser.add_argument("--export-json", default=None, help="Pasta opcional pra exportar pokemon.json e report.json")
    parser.add_argument("--generation", type=int, default=None, help="Filtra o dataset por geracao (1 a 9)")
    parser.add_argument("--type", default=None, help="Filtra o dataset por tipo (primario ou secundario)")
    parser.add_argument(
        "--compare-input", default=None,
        help="CSV de um segundo dataset (ex: outra regiao) pra comparar lado a lado nos graficos e no relatorio",
    )
    parser.add_argument("--compare-label", default="Comparacao", help="Rotulo do segundo dataset em --compare-input")
    parser.add_argument("--verbose", action="store_true", help="Liga logging (cache, rede) alem do relatorio")
    parser.add_argument("--interactive", action="store_true", help="Prompts interativos em vez de decorar as flags")
    return parser


def main():
    args = build_arg_parser().parse_args()
    configure_logging(verbose=args.verbose)

    if args.interactive:
        args = run_interactive(args)

    try:
        df = fetch_dataset(args.source, args.input, args.limit, args.save_csv)
    except ImportError:
        print("Rodar com --source api precisa do pacote requests instalado (esta no requirements.txt).")
        sys.exit(1)
    except ValueError as exc:  # schema invalido no CSV
        print(f"\nErro no dataset: {exc}")
        sys.exit(1)
    except Exception as exc:  # falha de rede/HTTP ao falar com a PokeAPI
        if args.source == "api":
            print(f"\nErro ao buscar dados na PokeAPI: {exc}")
            print("Confira sua conexao com a internet e tente de novo, ou rode com --source csv.")
            sys.exit(1)
        raise

    df = apply_filters(df, args.generation, args.type)

    compare_df = None
    if args.compare_input:
        compare_df = apply_filters(load_csv(args.compare_input), args.generation, args.type)

    print_report(df, compare_df, args.compare_label)

    if not args.no_charts and not df.empty:
        generate_charts(df, args.charts_dir, compare_df, args.compare_label)

    if args.sqlite_db and not df.empty:
        export_to_sqlite(df, args.sqlite_db)
        print(f"Dataset exportado pro banco SQLite em {args.sqlite_db}")

    if args.export_json and not df.empty:
        export_json(df, args.export_json)
        print(f"Dataset exportado pra JSON em {args.export_json}/")

    if args.html_report and not df.empty:
        export_html_report(df, args.html_report, charts_dir=None if args.no_charts else args.charts_dir)
        print(f"Relatorio HTML salvo em {args.html_report}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
