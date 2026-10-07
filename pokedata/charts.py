"""Gera os graficos a partir do DataFrame, sempre em .png e .svg. O backend
Agg (abaixo) gera o arquivo direto, sem tela -- essencial pra rodar num
servidor ou nos testes."""
import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pokedata.analysis import average_stat_by_type, correlation_matrix, top_n_by_stat

MARKER_FILENAME = ".source_hash"


def _save_png_and_svg(fig, output_path):
    output_path = Path(output_path)
    fig.savefig(output_path)
    fig.savefig(output_path.with_suffix(".svg"))


def dataframe_hash(df):
    """Hash estavel do conteudo do DataFrame, usado pra saber se os dados
    mudaram desde a ultima vez que os graficos foram gerados."""
    return hashlib.sha256(df.to_csv(index=False).encode("utf-8")).hexdigest()


def charts_up_to_date(df, output_dir):
    """True se ja existe um marcador de hash em `output_dir` e ele bate com
    o dataset atual -- nesse caso nao precisa regerar os graficos."""
    marker = Path(output_dir) / MARKER_FILENAME
    return marker.exists() and marker.read_text(encoding="utf-8") == dataframe_hash(df)


def write_charts_marker(df, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / MARKER_FILENAME).write_text(dataframe_hash(df), encoding="utf-8")


def plot_type_distribution(df, output_path, top_n=10, compare_df=None, labels=("Atual", "Comparacao")):
    """Barras com os `top_n` tipos primarios mais comuns. Se `compare_df` for
    passado, desenha barras agrupadas lado a lado pra comparar duas buscas
    (ex: Kanto x Johto)."""
    todos = df["type_1"].value_counts()
    counts = todos.head(top_n)
    fig, ax = plt.subplots(figsize=(9, 5))

    if compare_df is None:
        counts.plot(kind="bar", ax=ax, color="#4a90d9")
    else:
        compare_counts = compare_df["type_1"].value_counts()
        # Top N somando as duas buscas: o join completo trazia ate 18 tipos num grafico de "Top 10".
        tipos = todos.add(compare_counts, fill_value=0).sort_values(ascending=False).head(top_n).index
        combined = todos.reindex(tipos, fill_value=0).to_frame(labels[0]).join(
            compare_counts.reindex(tipos, fill_value=0).rename(labels[1]))
        combined.plot(kind="bar", ax=ax, color=["#4a90d9", "#e8a33d"])
        ax.legend()

    ax.set_title(f"Top {top_n} tipos primarios mais comuns")
    ax.set_xlabel("Tipo")
    ax.set_ylabel("Quantidade de Pokemon")
    fig.tight_layout()
    _save_png_and_svg(fig, output_path)
    plt.close(fig)


def plot_average_speed_by_type(df, output_path, top_n=10):
    """Barras com os `top_n` tipos primarios de maior velocidade media."""
    averages = average_stat_by_type(df, "speed").head(top_n)
    fig, ax = plt.subplots(figsize=(9, 5))
    averages.plot(kind="bar", ax=ax, color="#e8a33d")
    ax.set_title(f"Top {top_n} tipos com maior velocidade media")
    ax.set_xlabel("Tipo")
    ax.set_ylabel("Velocidade media")
    fig.tight_layout()
    _save_png_and_svg(fig, output_path)
    plt.close(fig)


def plot_weight_vs_defense(df, output_path, compare_df=None, labels=("Atual", "Comparacao")):
    """Dispersao (scatter) de peso x defesa, pra visualizar se existe
    correlacao entre as duas. Com `compare_df`, sobrepoe as duas buscas em
    cores diferentes com legenda."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(df["weight_kg"], df["defense"], alpha=0.6, color="#5cb85c", label=labels[0] if compare_df is not None else None)
    if compare_df is not None:
        ax.scatter(compare_df["weight_kg"], compare_df["defense"], alpha=0.6, color="#d9534f", label=labels[1])
        ax.legend()
    ax.set_title("Peso x Defesa")
    ax.set_xlabel("Peso (kg)")
    ax.set_ylabel("Defesa (base)")
    fig.tight_layout()
    _save_png_and_svg(fig, output_path)
    plt.close(fig)


def plot_top_n_by_stat(df, stat, output_path, n=10):
    """Barras horizontais com os N Pokemon de maior valor numa estatistica."""
    top = top_n_by_stat(df, stat, n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["name"], top[stat], color="#d9534f")
    ax.set_title(f"Top {n} Pokemon por {stat}")
    ax.set_xlabel(stat)
    fig.tight_layout()
    _save_png_and_svg(fig, output_path)
    plt.close(fig)


def plot_correlation_heatmap(df, output_path):
    """Heatmap da matriz de correlacao entre todas as stats, altura e peso."""
    matrix = correlation_matrix(df)
    labels_list = list(matrix.columns)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(labels_list)))
    ax.set_xticklabels(labels_list, rotation=45, ha="right")
    ax.set_yticks(range(len(labels_list)))
    ax.set_yticklabels(labels_list)
    for i in range(len(labels_list)):
        for j in range(len(labels_list)):
            ax.text(j, i, f"{matrix.values[i, j]:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax, label="Correlacao de Pearson")
    ax.set_title("Correlacao entre stats, altura e peso")
    fig.tight_layout()
    _save_png_and_svg(fig, output_path)
    plt.close(fig)
