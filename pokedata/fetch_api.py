"""Busca dados de Pokemon na PokeAPI (https://pokeapi.co), a API publica e
gratuita mantida pela comunidade com dados de todos os jogos oficiais.

Duas chamadas por Pokemon: uma pra pegar a lista (nome + URL de cada um) e
outra pra pegar os detalhes (tipos, stats, altura, peso) de cada URL da
lista. Devolve os dicts exatamente como a API manda; quem limpa e organiza
isso e' o modulo clean.py, separado de proposito.
"""
import requests

DEFAULT_BASE_URL = "https://pokeapi.co/api/v2"
REQUEST_TIMEOUT = 15


def fetch_pokemon_list(limit, base_url=DEFAULT_BASE_URL):
    """Pega o nome e a URL dos primeiros `limit` Pokemon da Pokedex nacional."""
    response = requests.get(f"{base_url}/pokemon", params={"limit": limit}, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()["results"]


def fetch_pokemon_detail(name_or_url, base_url=DEFAULT_BASE_URL):
    """Pega os detalhes de 1 Pokemon, por nome (ex: "pikachu") ou pela URL
    completa que a lista ja devolve."""
    url = name_or_url if name_or_url.startswith("http") else f"{base_url}/pokemon/{name_or_url}"
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_all_pokemon(limit, base_url=DEFAULT_BASE_URL, on_progress=None):
    """Busca a lista e depois os detalhes de cada Pokemon nela. `on_progress`,
    se passado, e' chamado como on_progress(indice_atual, total) a cada
    Pokemon baixado, pra dar feedback num download que pode demorar."""
    entries = fetch_pokemon_list(limit, base_url)
    details = []
    for i, entry in enumerate(entries, start=1):
        details.append(fetch_pokemon_detail(entry["url"], base_url))
        if on_progress:
            on_progress(i, len(entries))
    return details
