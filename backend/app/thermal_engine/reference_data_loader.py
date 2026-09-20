"""Chargement en memoire des bibliotheques de valeurs par defaut (JSON) du moteur thermique."""
import json
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "reference_data"


@lru_cache
def load_materials() -> dict:
    return json.loads((_DATA_DIR / "materials.json").read_text())


@lru_cache
def load_glazing() -> dict:
    return json.loads((_DATA_DIR / "glazing.json").read_text())


@lru_cache
def load_thermal_bridges() -> dict:
    return json.loads((_DATA_DIR / "thermal_bridges.json").read_text())


@lru_cache
def load_construction_types() -> dict:
    return json.loads((_DATA_DIR / "construction_types.json").read_text())


@lru_cache
def load_thermal_inertia() -> dict:
    return json.loads((_DATA_DIR / "thermal_inertia.json").read_text())
