"""Cliente HTTP que replica las llamadas AJAX del sitio gacetaoficial.gob.cu."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlencode

import httpx

BASE_URL = "https://www.gacetaoficial.gob.cu"
LANG_PREFIX = "/es"
USER_AGENT = "Mozilla/5.0 (compatible; gaceta-oficial-mcp/0.1; +https://github.com/)"

# Página desde la que el sitio dispara cada endpoint (se usa como Referer).
REFERERS = {
    "getdata": "/es/busqueda-avanzada",
    "getdatagaceta": "/es/busqueda-avanzada",
    "getdatagacetasa": "/es/busqueda-avanzada",
    "getedicionesgaceta": "/es/ediciones-del-mes",
}


class GacetaError(RuntimeError):
    """Error al consultar el sitio de la Gaceta Oficial."""


def encode_data(data: dict[str, Any]) -> list[tuple[str, str]]:
    """Serializa como jQuery: ``data[campo]=v`` y ``data[campo][]=v`` para listas."""
    out: list[tuple[str, str]] = []
    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            out.extend((f"data[{key}][]", str(v)) for v in value)
        else:
            out.append((f"data[{key}]", "" if value is None else str(value)))
    return out


class GacetaClient:
    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 60.0,
        retries: int = 3,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._retries = retries
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _request(self, method: str, url: str, **kwargs: Any) -> str:
        last: Exception | None = None
        for attempt in range(self._retries):
            try:
                resp = await self._http.request(method, url, **kwargs)
                if resp.status_code >= 500:
                    raise GacetaError(f"El sitio respondió HTTP {resp.status_code}")
                resp.raise_for_status()
                return resp.text
            except (httpx.TransportError, GacetaError) as exc:
                last = exc
                await asyncio.sleep(1.5 * (attempt + 1))
            except httpx.HTTPStatusError as exc:
                raise GacetaError(f"HTTP {exc.response.status_code} en {url}") from exc
        raise GacetaError(f"No se pudo consultar {url}: {last}") from last

    async def post_ajax(self, endpoint: str, data: dict[str, Any]) -> str:
        """POST a ``/es/<endpoint>``; devuelve el fragmento HTML ('' si no hay resultados)."""
        referer = BASE_URL + REFERERS.get(endpoint, LANG_PREFIX)
        return await self._request(
            "POST",
            f"{LANG_PREFIX}/{endpoint}",
            content=urlencode(encode_data(data)).encode(),
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": referer,
            },
        )

    async def get_page(self, path: str) -> str:
        return await self._request("GET", path)
