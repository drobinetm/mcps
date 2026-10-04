"""Cliente HTTP que replica las llamadas AJAX del sitio gacetaoficial.gob.cu."""

from __future__ import annotations

import asyncio
from collections import OrderedDict
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


MAX_PDF_BYTES = 50 * 1024 * 1024
PDF_CACHE_SIZE = 4


class GacetaError(RuntimeError):
    """Error al consultar el sitio de la Gaceta Oficial."""


class _Transient(GacetaError):
    """Error temporal (5xx) que merece reintento."""


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
        self._bytes_cache: OrderedDict[str, bytes] = OrderedDict()
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

    async def get_bytes(self, url: str, max_bytes: int = MAX_PDF_BYTES) -> bytes:
        """Descarga un binario (PDF) con reintentos, límite de tamaño y caché LRU en memoria."""
        if url in self._bytes_cache:
            self._bytes_cache.move_to_end(url)
            return self._bytes_cache[url]
        last: Exception | None = None
        for attempt in range(self._retries):
            try:
                async with self._http.stream("GET", url, timeout=180) as resp:
                    if resp.status_code >= 500:
                        raise _Transient(f"El sitio respondió HTTP {resp.status_code}")
                    if resp.status_code >= 400:
                        raise GacetaError(f"HTTP {resp.status_code} al descargar {url}")
                    size = int(resp.headers.get("content-length") or 0)
                    if size > max_bytes:
                        raise GacetaError(f"El archivo pesa {size // 1048576} MB (máximo {max_bytes // 1048576} MB)")
                    chunks, total = [], 0
                    async for chunk in resp.aiter_bytes():
                        total += len(chunk)
                        if total > max_bytes:
                            raise GacetaError(f"El archivo supera {max_bytes // 1048576} MB")
                        chunks.append(chunk)
                data = b"".join(chunks)
                self._bytes_cache[url] = data
                while len(self._bytes_cache) > PDF_CACHE_SIZE:
                    self._bytes_cache.popitem(last=False)
                return data
            except (httpx.TransportError, _Transient) as exc:
                last = exc
                await asyncio.sleep(1.5 * (attempt + 1))
        raise GacetaError(f"No se pudo descargar {url}: {last}") from last
