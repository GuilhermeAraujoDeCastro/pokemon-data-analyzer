"""Serializa o dataset e os resultados de analysis.py pra JSON -- e' o que
alimenta o site estatico em site/ (Fase 5), mas tambem serve como
exportacao alternativa em texto puro, sem precisar de pandas do outro lado.
"""
import json
from pathlib import Path

from pokedata.analysis import (
    average_stat_by_type,
    correlation_matrix,
    find_outliers,
    rarest_type_combination,
    top_n_by_stat,
    type_combination_counts,
    weight_defense_correlation,
)


def build_report_dict(df):
    """Junta dataset + perguntas respondidas num dict facil de virar JSON."""
    combo, combo_count = rarest_type_combination(df)
    return {
        "pokemon": df.to_dict(orient="records"),
        "summary": {
            "total": len(df),
            "rarest_type_combination": {"combo": combo, "count": combo_count},
            "average_speed_by_type": average_stat_by_type(df, "speed").round(1).to_dict(),
            "weight_defense_correlation": round(weight_defense_correlation(df), 3),
            "type_combination_counts": type_combination_counts(df).to_dict(),
            "top_attack": top_n_by_stat(df, "attack", 10).to_dict(orient="records"),
            "top_speed": top_n_by_stat(df, "speed", 10).to_dict(orient="records"),
            "correlation_matrix": correlation_matrix(df).round(3).to_dict(),
            "hp_outliers": find_outliers(df, "hp").to_dict(orient="records"),
        },
    }


def export_json(df, output_dir):
    """Grava pokemon.json (so' o dataset) e report.json (dataset + analise)
    em `output_dir`."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "pokemon.json").write_text(
        json.dumps(df.to_dict(orient="records"), ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "report.json").write_text(
        json.dumps(build_report_dict(df), ensure_ascii=False), encoding="utf-8"
    )
