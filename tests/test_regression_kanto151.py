"""Teste de regressao com a Pokedex de Kanto inteira (151 Pokemon), buscada
de verdade na PokeAPI uma vez e congelada em tests/fixtures/kanto_151.csv --
mais confiavel que digitar stats de memoria (mesmo aviso que o README faz
sobre data/sample_pokemon.csv). Sem rede: so' le o CSV congelado. Serve pra
travar os numeros centrais do relatorio e confirmar que a correlacao
peso/defesa se mantem com o dataset completo (item do README "Proximos
passos possiveis").
"""
from pathlib import Path

from pokedata.analysis import (
    fastest_type,
    find_outliers,
    height_hp_correlation,
    rarest_type_combination,
    weight_defense_correlation,
)
from pokedata.dataset import load_csv

FIXTURE = Path(__file__).parent / "fixtures" / "kanto_151.csv"


def load_kanto():
    return load_csv(FIXTURE)


def test_kanto_151_has_all_pokemon():
    assert len(load_kanto()) == 151


def test_kanto_151_rarest_type_combination():
    assert rarest_type_combination(load_kanto()) == ("Dragon / Flying", 1)


def test_kanto_151_fastest_type():
    type_name, avg_speed = fastest_type(load_kanto())
    assert type_name == "electric"
    assert avg_speed == 100.0


def test_kanto_151_weight_defense_correlation_stays_moderate_positive():
    # A mesma pergunta do CSV de exemplo (20 Pokemon, correlacao 0.465):
    # com o dataset completo de Kanto a correlacao continua positiva e
    # moderada, na mesma faixa -- ela nao desaparece nem vira negativa.
    correlation = weight_defense_correlation(load_kanto())
    assert round(correlation, 3) == 0.413
    assert 0.2 < correlation < 0.6


def test_kanto_151_height_hp_correlation():
    assert round(height_hp_correlation(load_kanto()), 3) == 0.243


def test_kanto_151_hp_outliers():
    outliers = find_outliers(load_kanto(), "hp")
    assert list(outliers["name"]) == ["chansey", "snorlax", "wigglytuff"]
