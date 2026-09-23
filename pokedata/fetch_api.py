"""Busca dados de Pokemon na PokeAPI (https://pokeapi.co), a API publica e
gratuita mantida pela comunidade com dados de todos os jogos oficiais.

Duas chamadas por Pokemon: uma pra pegar a lista (nome + URL de cada um) e
outra pra pegar os detalhes (tipos, stats, altura, peso) de cada URL da
lista. Devolve os dicts exatamente como a API manda; quem limpa e organiza
isso e' o modulo clean.py, separado de proposito. Respostas ficam em cache
em disco (veja cache.py) e os detalhes sao buscados em paralelo, porque
buscar centenas de Pokemon um por um e' lento.
"""
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

from pokedata import cache
from pokedata.logging_setup import get_logger

DEFAULT_BASE_URL = "https://pokeapi.co/api/v2"
REQUEST_TIMEOUT = 15
MAX_WORKERS = 8


def fetch_pokemon_list(limit, base_url=DEFAULT_BASE_URL):
    """Pega o nome e a URL dos primeiros `limit` Pokemon da Pokedex nacional."""
    cache_key = f"{base_url}/pokemon?limit={limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        get_logger().info("Lista de Pokemon (limit=%s) veio do cache", limit)
        return cached["results"]

    response = requests.get(f"{base_url}/pokemon", params={"limit": limit}, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    cache.set(cache_key, data)
    return data["results"]


def fetch_pokemon_detail(name_or_url, base_url=DEFAULT_BASE_URL):
    """Pega os detalhes de 1 Pokemon, por nome (ex: "pikachu") ou pela URL
    completa que a lista ja devolve."""
    url = name_or_url if name_or_url.startswith("http") else f"{base_url}/pokemon/{name_or_url}"

    cached = cache.get(url)
    if cached is not None:
        return cached

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    cache.set(url, data)
    return data


def fetch_all_pokemon(limit, base_url=DEFAULT_BASE_URL, on_progress=None):
    """Busca a lista e depois os detalhes de cada Pokemon nela, em paralelo
    (ThreadPoolExecutor, mesmo padrao do roster.py do Simulador de Batalha).
    `on_progress`, se passado, e' chamado como on_progress(indice_atual,
    total) a cada Pokemon baixado -- serializado com um lock, porque varias
    threads terminam ao mesmo tempo."""
    entries = fetch_pokemon_list(limit, base_url)
    total = len(entries)
    completed = 0
    lock = threading.Lock()

    def fetch_one(entry):
        nonlocal completed
        detail = fetch_pokemon_detail(entry["url"], base_url)
        if on_progress:
            with lock:
                completed += 1
                on_progress(completed, total)
        return detail

    if total == 0:
        return []

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, total)) as pool:
        # pool.map preserva a ordem de entrada, mesmo buscando em paralelo
        return list(pool.map(fetch_one, entries))
