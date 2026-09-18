"""Gera os graficos (PNG) a partir do DataFrame. matplotlib.use("Agg") faz
gerar o arquivo direto, sem precisar de tela, essencial pra rodar num
servidor ou dentro dos testes automatizados.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pokedata.analysis import average_stat_by_type, top_n_by_stat


def plot_type_distribution(df, output_path, top_n=10):
    """Barras com os `top_n` tipos primarios mais comuns."""
    counts = df["type_1"].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(9, 5))
    counts.plot(kind="bar", ax=ax, color="#4a90d9")
    ax.set_title(f"Top {top_n} tipos primarios mais comuns")
    ax.set_xlabel("Tipo")
    ax.set_ylabel("Quantidade de Pokemon")
    fig.tight_layout()
    fig.savefig(output_path)
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
    fig.savefig(output_path)
    plt.close(fig)


def plot_weight_vs_defense(df, output_path):
    """Dispersao (scatter) de peso x defesa, pra visualizar se existe
    correlacao entre as duas."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(df["weight_kg"], df["defense"], alpha=0.6, color="#5cb85c")
    ax.set_title("Peso x Defesa")
    ax.set_xlabel("Peso (kg)")
    ax.set_ylabel("Defesa (base)")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_top_n_by_stat(df, stat, output_path, n=10):
    """Barras horizontais com os N Pokemon de maior valor numa estatistica."""
    top = top_n_by_stat(df, stat, n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["name"], top[stat], color="#d9534f")
    ax.set_title(f"Top {n} Pokemon por {stat}")
    ax.set_xlabel(stat)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
