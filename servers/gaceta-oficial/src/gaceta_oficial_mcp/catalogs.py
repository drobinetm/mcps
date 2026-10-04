"""Catálogos (tipos de edición/norma, estados, organismos) leídos de la búsqueda avanzada."""

from __future__ import annotations

import time
import unicodedata

from .client import GacetaClient
from .parsers import parse_select_options

SELECTS = {
    "tipos_edicion": "St_edicion",
    "tipos_norma": "St-norma",
    "estados": "Sestado",
    "organismos": "Sorganismo",
}
TTL_SECONDS = 24 * 3600


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower().replace("-", " ").replace("_", " "))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


class Catalogs:
    def __init__(self, client: GacetaClient) -> None:
        self._client = client
        self._data: dict[str, list[dict[str, str]]] | None = None
        self._loaded_at = 0.0

    async def all(self) -> dict[str, list[dict[str, str]]]:
        if self._data is None or time.time() - self._loaded_at > TTL_SECONDS:
            html = await self._client.get_page("/es/busqueda-avanzada")
            self._data = {k: parse_select_options(html, sid) for k, sid in SELECTS.items()}
            self._loaded_at = time.time()
        return self._data

    async def resolve(self, catalog: str, value: str | int | None) -> str:
        """Nombre o ID -> ID del sitio; ``Cualquiera`` si no se indica."""
        if value in (None, "", 0, "0"):
            return "Cualquiera"
        options = (await self.all())[catalog]
        v = str(value)
        if any(o["id"] == v for o in options):
            return v
        target = norm(v)
        exact = [o for o in options if norm(o["nombre"]) == target]
        partial = [o for o in options if target in norm(o["nombre"])]
        match = exact or partial
        if not match:
            raise ValueError(f"'{value}' no coincide con ningún valor de {catalog}; usa list_catalogs.")
        if len(match) > 1 and not exact:
            names = ", ".join(f"{o['nombre']} ({o['id']})" for o in match[:8])
            raise ValueError(f"'{value}' es ambiguo en {catalog}: {names}")
        return match[0]["id"]
