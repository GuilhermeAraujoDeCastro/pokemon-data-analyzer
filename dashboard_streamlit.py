"""Dashboard local opcional: mesma analise de pokedata/analysis.py, em
versao interativa (Streamlit) como alternativa aos PNGs estaticos que
run_extractor.py gera. Nao faz parte do site publicado na Vercel -- roda
so' na maquina de quem instalar requirements-dashboard.txt.

Como rodar:
    pip install -r requirements-dashboard.txt
    streamlit run dashboard_streamlit.py
"""
import streamlit as st

from pokedata.analysis import (
    average_stat_by_type,
    correlation_matrix,
    fastest_type,
    find_outliers,
    rarest_type_combination,
    top_n_by_stat,
    weight_defense_correlation,
)
from pokedata.dataset import filter_by_type, load_csv
from pokedata.generations import add_generation_column

STATS = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]

st.set_page_config(page_title="Analisador de Dados Pokémon", layout="wide")
st.title("Analisador de Dados Pokémon")

source_path = st.sidebar.text_input("CSV de entrada", "data/sample_pokemon.csv")
try:
    df = add_generation_column(load_csv(source_path))
except (FileNotFoundError, ValueError) as exc:
    st.error(f"Nao consegui carregar {source_path}: {exc}")
    st.stop()

generations = sorted(g for g in df["generation"].dropna().unique().tolist())
generation = st.sidebar.selectbox("Geracao", ["Todas"] + generations)
if generation != "Todas":
    df = df[df["generation"] == generation]

type_filter = st.sidebar.text_input("Filtrar por tipo (opcional)")
if type_filter:
    df = filter_by_type(df, type_filter)

if df.empty:
    st.warning("Nenhum Pokemon depois dos filtros.")
    st.stop()

col1, col2, col3 = st.columns(3)
combo, count = rarest_type_combination(df)
col1.metric("Combinacao mais rara", combo, f"{count} Pokemon")
type_name, avg_speed = fastest_type(df)
col2.metric("Tipo mais rapido", type_name, f"{avg_speed:.1f} vel. media")
col3.metric("Correlacao peso/defesa", f"{weight_defense_correlation(df):.3f}")

st.subheader("Velocidade media por tipo")
st.bar_chart(average_stat_by_type(df, "speed"))

st.subheader("Peso x Defesa")
st.scatter_chart(df, x="weight_kg", y="defense")

st.subheader("Top 10 por stat")
stat = st.selectbox("Stat", STATS)
st.dataframe(top_n_by_stat(df, stat, 10), use_container_width=True)

st.subheader("Correlacao entre stats, altura e peso")
st.dataframe(correlation_matrix(df).round(2), use_container_width=True)

outliers = find_outliers(df, "hp")
if not outliers.empty:
    st.subheader("Outliers de HP (fora da curva)")
    st.dataframe(outliers, use_container_width=True)

st.subheader("Dataset")
st.dataframe(df, use_container_width=True)
