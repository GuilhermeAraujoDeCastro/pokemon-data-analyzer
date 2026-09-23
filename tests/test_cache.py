import pytest

from pokedata import cache


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path / ".pokecache")


def test_get_returns_none_when_not_cached():
    assert cache.get("https://pokeapi.co/api/v2/pokemon/1") is None


def test_set_then_get_roundtrips():
    cache.set("https://pokeapi.co/api/v2/pokemon/1", {"id": 1, "name": "bulbasaur"})

    assert cache.get("https://pokeapi.co/api/v2/pokemon/1") == {"id": 1, "name": "bulbasaur"}


def test_different_keys_dont_collide():
    cache.set("url-a", {"value": "a"})
    cache.set("url-b", {"value": "b"})

    assert cache.get("url-a") == {"value": "a"}
    assert cache.get("url-b") == {"value": "b"}
