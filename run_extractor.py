#!/usr/bin/env python3
"""Extrator e Analisador de Dados Pokemon.

Busca dados de Pokemon (na PokeAPI ao vivo, ou de um CSV ja salvo), organiza
num dataset, responde um conjunto de perguntas estatisticas, gera graficos e
opcionalmente exporta pra um banco SQLite.
"""
import argparse
import sys
from pathlib import Path

from pokedata.analysis import (
    average_stat_by_type,
    fastest_type,
    rarest_type_combination,
    top_n_by_stat,
    weight_defense_correlation,
)
from pokedata.charts import (
    plot_average_speed_by_type,
    plot_top_n_by_stat,
    plot_type_distribution,
    plot_weight_vs_defense,
)
from pokedata.clean import clean_all
from pokedata.dataset import build_dataframe, load_csv, save_csv
from pokedata.sql_export import export_to_sqlite


def build_dataset(args):
    if args.source == "csv":
        return load_csv(args.input)

    # Import so' quando for buscar da API de verdade: quem usa --source csv
    # (o padrao) nao precisa nem ter o pacote requests instalado.
    from pokedata.fetch_api import fetch_all_pokemon

    def progress(i, total):
        print(f"Baixando Pokemon {i}/{total}...", end="\r")

    raw = fetch_all_pokemon(args.limit, on_progress=progress)
    print()
    df = build_dataframe(clean_all(raw))
    save_csv(df, args.save_csv)
    print(f"Dataset salvo em {args.save_csv}")
    return df


def print_report(df):
    print("\n=== Relatorio estatistico ===\n")

    combo, count = rarest_type_combination(df)
    print(f"Combinacao de tipos mais rara: {combo} ({count} Pokemon)")

    type_name, avg_speed = fastest_type(df)
    print(f"Tipo primario com maior velocidade media: {type_name} ({avg_speed:.1f})")

    correlation = weight_defense_correlation(df)
    print(f"Correlacao entre peso e defesa: {correlation:.3f}")

    print("\nTop 5 mais rapidos:")
    print(top_n_by_stat(df, "speed", 5).to_string(index=False))

    print("\nTop 5 maior ataque:")
    print(top_n_by_stat(df, "attack", 5).to_string(index=False))

    print("\nMedia de velocidade por tipo primario:")
    print(average_stat_by_type(df, "speed").round(1).to_string())


def generate_charts(df, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_type_distribution(df, output_dir / "distribuicao_tipos.png")
    plot_average_speed_by_type(df, output_dir / "velocidade_media_por_tipo.png")
    plot_weight_vs_defense(df, output_dir / "peso_vs_defesa.png")
    plot_top_n_by_stat(df, "attack", output_dir / "top_ataque.png")

    print(f"\nGraficos salvos em {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Extrator e analisador de dados Pokemon")
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
    parser.add_argument(
        "--charts-dir", default="charts",
        help="Pasta onde salvar os graficos gerados",
    )
    parser.add_argument(
        "--sqlite-db", default=None,
        help="Caminho opcional pra exportar o dataset pra um banco SQLite",
    )
    parser.add_argument("--no-charts", action="store_true", help="Pula a geracao de graficos")
    args = parser.parse_args()

    try:
        df = build_dataset(args)
    except ImportError:
        print("Rodar com --source api precisa do pacote requests instalado (esta no requirements.txt).")
        sys.exit(1)
    except Exception as exc:  # falha de rede/HTTP ao falar com a PokeAPI
        if args.source == "api":
            print(f"\nErro ao buscar dados na PokeAPI: {exc}")
            print("Confira sua conexao com a internet e tente de novo, ou rode com --source csv.")
            sys.exit(1)
        raise

    print_report(df)

    if not args.no_charts:
        generate_charts(df, args.charts_dir)

    if args.sqlite_db:
        export_to_sqlite(df, args.sqlite_db)
        print(f"Dataset exportado pro banco SQLite em {args.sqlite_db}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
