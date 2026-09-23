"""Perguntas estatisticas sobre o DataFrame de Pokemon. Cada funcao so'
calcula e devolve o resultado (sem print, sem I/O), pra reaproveitar tanto
no relatorio de texto quanto nos graficos."""
import numpy as np


def type_combination_counts(df):
    """Conta quantos Pokemon existem em cada combinacao de tipo 1 + tipo 2,
    do mais comum pro mais raro."""
    combo = df["type_1"].str.capitalize() + " / " + df["type_2"].str.capitalize()
    return combo.value_counts()


def rarest_type_combination(df):
    """Devolve (combinacao, quantidade) da combinacao de tipos com menos
    Pokemon. Em empate, pega a primeira em ordem alfabetica, pra sempre dar
    o mesmo resultado em vez de depender da ordem de chegada dos dados."""
    counts = type_combination_counts(df)
    minimum = int(counts.min())
    empatados = counts[counts == minimum].sort_index()
    return empatados.index[0], minimum


def average_stat_by_type(df, stat):
    """Media de uma estatistica (ex: "speed") por tipo primario, da maior
    media pra menor."""
    return df.groupby("type_1")[stat].mean().sort_values(ascending=False)


def fastest_type(df):
    """Devolve (tipo, velocidade media) do tipo primario com maior
    velocidade media."""
    averages = average_stat_by_type(df, "speed")
    return averages.index[0], float(averages.iloc[0])


def _safe_corr(a, b):
    """Series.corr() entre duas colunas, sem o RuntimeWarning do numpy
    quando uma delas nao varia (desvio padrao 0 -> divisao por zero -> NaN,
    o que e' matematicamente correto, so' o aviso que e' ruido)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        return float(a.corr(b))


def weight_defense_correlation(df):
    """Coeficiente de correlacao de Pearson entre peso e defesa, de -1 a 1.
    Perto de 0 = sem relacao linear; perto de 1 = quanto mais pesado, mais
    defesa; perto de -1 seria o oposto."""
    return _safe_corr(df["weight_kg"], df["defense"])


def top_n_by_stat(df, stat, n=10):
    """Os N Pokemon com maior valor numa estatistica, do maior pro menor."""
    return df.nlargest(n, stat)[["name", stat]].reset_index(drop=True)


def height_hp_correlation(df):
    """Correlacao de Pearson entre altura e HP, no mesmo espirito de
    weight_defense_correlation."""
    return _safe_corr(df["height_m"], df["hp"])


def most_common_type_by_generation(df):
    """Requer a coluna "generation" (veja generations.add_generation_column).
    Devolve uma Series: geracao -> tipo primario mais comum nela."""
    return df.groupby("generation")["type_1"].agg(lambda types: types.value_counts().idxmax())


STAT_COLUMNS = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]


def stat_total_distribution_by_generation(df):
    """Requer a coluna "generation". Soma as 6 stats base por Pokemon e
    devolve o describe() (media, desvio, min/max etc.) dessa soma agrupado
    por geracao -- da pra ver se alguma geracao tem Pokemon "mais fortes" em
    media."""
    totals = df[STAT_COLUMNS].sum(axis=1)
    return totals.groupby(df["generation"]).describe()


def correlation_matrix(df):
    """Matriz de correlacao de Pearson entre todas as stats + altura/peso,
    pra visualizar como heatmap (veja charts.plot_correlation_heatmap). Uma
    coluna sem nenhuma variacao (ex: dataset filtrado com 1 Pokemon so') da'
    correlacao NaN pra ela -- matematicamente correto (divisao por desvio
    padrao 0), so' suprime o RuntimeWarning que o numpy solta por causa
    disso."""
    columns = STAT_COLUMNS + ["height_m", "weight_kg"]
    with np.errstate(invalid="ignore", divide="ignore"):
        return df[columns].corr()


def find_outliers(df, stat, k=1.5):
    """Pokemon fora da curva numa stat, pelo metodo do intervalo
    interquartil (IQR): abaixo de Q1 - k*IQR ou acima de Q3 + k*IQR. Serve
    pra tirar lendarios/Pokemon extremos da media geral e reportar eles
    separado (ex: Blissey puxando a media de HP pra cima)."""
    q1 = df[stat].quantile(0.25)
    q3 = df[stat].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    mask = (df[stat] < lower) | (df[stat] > upper)
    return df.loc[mask, ["name", stat]].sort_values(stat, ascending=False).reset_index(drop=True)
