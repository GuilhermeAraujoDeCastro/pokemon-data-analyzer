"""Exporta o dataset limpo pra um banco SQLite, pra servir de base a um
dashboard depois (Power BI, Metabase e ferramentas parecidas conseguem ler
direto de um arquivo .db do SQLite). E' o passo opcional que a proposta
original do projeto pede: o dataset em si ja funciona sem isso.
"""
import sqlite3


def export_to_sqlite(df, db_path, table_name="pokemon"):
    """Grava o DataFrame inteiro como uma tabela no banco SQLite em
    `db_path`. Se a tabela ja existir, substitui (util pra rodar de novo
    depois de atualizar o dataset)."""
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
