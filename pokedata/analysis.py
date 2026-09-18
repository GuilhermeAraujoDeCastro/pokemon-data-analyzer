"""Funcoes de analise estatistica sobre o DataFrame de Pokemon. Cada funcao
recebe o DataFrame e devolve um resultado simples (numero, string, ou outro
DataFrame pequeno), sem imprimir nada e sem ler/gravar arquivo -- fica facil
de testar e da pra reaproveitar tanto no relatorio de texto quanto nos
graficos.
"""


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


def weight_defense_correlation(df):
    """Coeficiente de correlacao de Pearson entre peso e defesa, de -1 a 1.
    Perto de 0 = sem relacao linear; perto de 1 = quanto mais pesado, mais
    defesa; perto de -1 seria o oposto."""
    return float(df["weight_kg"].corr(df["defense"]))


def top_n_by_stat(df, stat, n=10):
    """Os N Pokemon com maior valor numa estatistica, do maior pro menor."""
    return df.nlargest(n, stat)[["name", stat]].reset_index(drop=True)
