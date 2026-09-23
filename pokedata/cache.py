"""Cache em disco pras respostas da PokeAPI, no mesmo padrao do pokeapi.py do
Simulador de Batalha: cada URL vira um arquivo .json em .pokecache/ (nomeado
pelo hash da URL), pra rodar `--source api` de novo sem repetir chamada de
rede pra Pokemon ja baixado antes.
"""
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / ".pokecache"


def _cache_path(key):
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def get(key):
    """Devolve o JSON cacheado pra essa chave (normalmente uma URL), ou None
    se ainda nao foi buscado."""
    path = _cache_path(key)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def set(key, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(key).write_text(json.dumps(data), encoding="utf-8")
