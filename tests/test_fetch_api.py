from unittest.mock import Mock

import pytest

from pokedata.fetch_api import fetch_all_pokemon, fetch_pokemon_detail, fetch_pokemon_list


def fake_response(json_data, ok=True):
    response = Mock()
    response.json.return_value = json_data

    def raise_for_status():
        if not ok:
            raise RuntimeError("HTTP error")

    response.raise_for_status = raise_for_status
    return response


def test_fetch_pokemon_list_requests_correct_endpoint_and_params(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return fake_response({"results": [{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}]})

    monkeypatch.setattr("pokedata.fetch_api.requests.get", fake_get)

    results = fetch_pokemon_list(limit=1)

    assert captured["url"] == "https://pokeapi.co/api/v2/pokemon"
    assert captured["params"] == {"limit": 1}
    assert results == [{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}]


def test_fetch_pokemon_detail_by_name(monkeypatch):
    captured = {}

    def fake_get(url, timeout=None):
        captured["url"] = url
        return fake_response({"id": 25, "name": "pikachu"})

    monkeypatch.setattr("pokedata.fetch_api.requests.get", fake_get)

    detail = fetch_pokemon_detail("pikachu")

    assert captured["url"] == "https://pokeapi.co/api/v2/pokemon/pikachu"
    assert detail == {"id": 25, "name": "pikachu"}


def test_fetch_pokemon_detail_by_full_url(monkeypatch):
    captured = {}

    def fake_get(url, timeout=None):
        captured["url"] = url
        return fake_response({"id": 1, "name": "bulbasaur"})

    monkeypatch.setattr("pokedata.fetch_api.requests.get", fake_get)

    detail = fetch_pokemon_detail("https://pokeapi.co/api/v2/pokemon/1/")

    assert captured["url"] == "https://pokeapi.co/api/v2/pokemon/1/"
    assert detail == {"id": 1, "name": "bulbasaur"}


def test_fetch_pokemon_detail_raises_on_http_error(monkeypatch):
    def fake_get(url, timeout=None):
        return fake_response({}, ok=False)

    monkeypatch.setattr("pokedata.fetch_api.requests.get", fake_get)

    with pytest.raises(RuntimeError):
        fetch_pokemon_detail("pikachu")


def test_fetch_all_pokemon_returns_details_for_each_entry(monkeypatch):
    list_json = {
        "results": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
            {"name": "charmander", "url": "https://pokeapi.co/api/v2/pokemon/4/"},
        ]
    }
    detail_by_url = {
        "https://pokeapi.co/api/v2/pokemon/1/": {"id": 1, "name": "bulbasaur"},
        "https://pokeapi.co/api/v2/pokemon/4/": {"id": 4, "name": "charmander"},
    }

    def fake_get(url, params=None, timeout=None):
        if params is not None:
            return fake_response(list_json)
        return fake_response(detail_by_url[url])

    monkeypatch.setattr("pokedata.fetch_api.requests.get", fake_get)

    result = fetch_all_pokemon(limit=2)

    assert result == [{"id": 1, "name": "bulbasaur"}, {"id": 4, "name": "charmander"}]


def test_fetch_all_pokemon_calls_progress_callback(monkeypatch):
    list_json = {"results": [{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}]}

    def fake_get(url, params=None, timeout=None):
        if params is not None:
            return fake_response(list_json)
        return fake_response({"id": 1, "name": "bulbasaur"})

    monkeypatch.setattr("pokedata.fetch_api.requests.get", fake_get)

    progress_calls = []
    fetch_all_pokemon(limit=1, on_progress=lambda i, total: progress_calls.append((i, total)))

    assert progress_calls == [(1, 1)]
