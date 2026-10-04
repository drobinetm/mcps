"""Servidor MCP (stdio) para la Gaceta Oficial de Cuba."""

from __future__ import annotations

import asyncio
import io
from collections.abc import Iterator
from typing import Any

from mcp.server import MCPServer

from . import intent, topics
from .catalogs import Catalogs
from .client import BASE_URL, GacetaClient, GacetaError
from .parsers import (
    extract_norma_text,
    parse_ediciones,
    parse_gaceta_files,
    parse_gacetas_historicas,
    parse_norma_page,
    parse_normas,
)

INSTRUCTIONS = """\
Consulta la Gaceta Oficial de la República de Cuba (gacetaoficial.gob.cu).

PASO 1 (siempre, ANTES de cualquier búsqueda, sea por fecha o por contenido): pregunta al usuario
si desea buscar por un tema específico. Si ya indicó un tema en su mensaje, úsalo sin preguntar.
Si responde que no, usa los temas guardados (get_topics; por defecto: informática, contrato,
trabajo, mipymes). Si quiere cambiarlos de forma permanente, usa set_topics.

PASO 2: elige la herramienta según la intención:
- FECHA o periodo ("qué gacetas hay hoy", "de este mes", "octubre 2025") -> list_ediciones
  (página ediciones-del-mes), pasando los temas elegidos en 'topics_' para marcar las normas
  relevantes.
- CONTENIDO o tema ("qué gacetas hablan del contrato de trabajo en las mipymes", normas de
  un organismo, tipo de norma) -> search_normas (página busqueda-avanzada). Sin 'query' ni
  'topics_' busca los temas guardados.
- Un NÚMERO concreto de gaceta ("la Extraordinaria 92 de 2026") -> search_gacetas; gacetas
  anteriores a 2009 (con su índice) con search_gacetas_historicas.

- LEER una norma completa ("muéstrame el Acuerdo 651-X", "qué dice esa resolución") -> get_norma con
  la URL de la norma (la obtienes de cualquiera de los resultados anteriores).

PASO 3, al responder: sé completo y no abrevies. Para cada gaceta escribe su 'nombre_completo'
(p. ej. "Gaceta Oficial No. 92 Extraordinaria de 2026"), la fecha, el enlace y el PDF. Para cada
norma escribe su título COMPLETO (p. ej. "Acuerdo 651-X de 2026 de Consejo de Estado") con su
enlace, y su resumen si lo hay. Destaca primero las normas relevantes para los temas del usuario.
"""

mcp = MCPServer("gaceta-oficial", instructions=INSTRUCTIONS)

_client: GacetaClient | None = None
_catalogs: Catalogs | None = None


def _deps() -> tuple[GacetaClient, Catalogs]:
    global _client, _catalogs
    if _client is None or _catalogs is None:
        _client = GacetaClient()
        _catalogs = Catalogs(_client)
    return _client, _catalogs


MAX_MONTH_PAGES = 10
NO_GACETAS = "No hay gacetas publicadas que coincidan con la búsqueda."
STOPWORDS = {
    "de",
    "del",
    "la",
    "las",
    "el",
    "los",
    "en",
    "y",
    "e",
    "o",
    "u",
    "a",
    "al",
    "para",
    "por",
    "con",
    "sobre",
    "un",
    "una",
}


def subphrases(term: str, max_per_level: int = 6) -> Iterator[str]:
    """Sub-frases contiguas de ``term`` (de más largas a más cortas), sin extremos vacíos."""
    words = term.split()
    for size in range(len(words) - 1, 0, -1):
        level = []
        for i in range(len(words) - size + 1):
            chunk = words[i : i + size]
            if chunk[0].lower() in STOPWORDS or chunk[-1].lower() in STOPWORDS:
                continue
            level.append(" ".join(chunk))
        yield from level[:max_per_level]


async def collect_ediciones(client: GacetaClient, period: intent.Period) -> list[dict[str, Any]]:
    """Ediciones cuya fecha cae dentro del periodo, recorriendo las páginas de cada mes."""
    found: list[dict[str, Any]] = []
    for mes, anno in period.months:
        page = 0
        while page < MAX_MONTH_PAGES:
            html = await client.post_ajax(
                "getedicionesgaceta",
                {"mes": mes, "anno": anno, "from": 0 if page == 0 else 1, "page": page, "buscar": 1},
            )
            parsed = parse_ediciones(html)
            dated = [e for e in parsed["resultados"] if e["fecha"]]
            found += [e for e in dated if period.start.isoformat() <= e["fecha"] <= period.end.isoformat()]
            if not parsed["has_more"] or (dated and all(e["fecha"] < period.start.isoformat() for e in dated)):
                break
            page += 1
    return found


MAX_TOPIC_PAGES = 5


async def mark_topics(
    client: GacetaClient, catalogs: Catalogs, period: intent.Period, ediciones: list[dict[str, Any]], topics_: list[str]
) -> dict[str, Any]:
    """Marca las normas de las ediciones que la búsqueda avanzada devuelve para cada tema."""
    by_url = {n["url"]: n for e in ediciones for n in e["normas"] if n["url"]}
    relevant: dict[str, dict[str, Any]] = {}
    if by_url:
        for topic in topics_:
            for page in range(MAX_TOPIC_PAGES):
                res = await _search_normas_once(
                    client, catalogs, texto=topic, tipo_norma=None, estado=None, organismo=None,
                    anno=period.end.year, numero=None, identificador=None, page=page,
                )  # fmt: skip
                for item in res["resultados"]:
                    norma = by_url.get(item["url"])
                    if norma is None:
                        continue
                    if topic not in norma.setdefault("temas", []):
                        norma["temas"].append(topic)
                    norma["resumen"] = item["resumen"]
                    relevant.setdefault(item["url"], norma)
                if not res["has_more"] or set(by_url) <= set(relevant):
                    break
    out: dict[str, Any] = {"temas_consultados": topics_}
    out["normas_relevantes"] = [
        {**n, "gaceta": next(e["nombre_completo"] for e in ediciones if n in e["normas"])} for n in relevant.values()
    ]
    if not relevant:
        out["mensaje_temas"] = "Ninguna norma de este periodo coincide con los temas consultados."
    return out


@mcp.tool()
async def list_ediciones(periodo: str = "hoy", topics_: list[str] | None = None) -> dict[str, Any]:
    """Lista las gacetas publicadas en una fecha o periodo (página 'ediciones-del-mes').

    Úsala cuando el usuario pregunte por FECHAS: "qué gacetas hay hoy", "ayer", "esta semana",
    "este mes", "mes pasado", "octubre 2025", "2026-10-02" o "02/10/2026".
    Antes de llamarla pregunta al usuario si quiere un tema específico; pasa los temas elegidos
    (o los guardados, ver get_topics) en 'topics_' para marcar las normas relevantes.
    Devuelve por gaceta: nombre_completo, tipo, número, fecha, URL, PDF y todas sus normas con
    título completo y URL. Con 'topics_', cada norma coincidente lleva 'temas' y 'resumen', y se
    listan aparte en 'normas_relevantes'.
    """
    client, catalogs = _deps()
    period = intent.parse_period(periodo)
    ediciones = await collect_ediciones(client, period)
    result: dict[str, Any] = {
        "periodo": period.label,
        "desde": period.start.isoformat(),
        "hasta": period.end.isoformat(),
        "total": len(ediciones),
        "ediciones": ediciones,
    }
    if topics_ and ediciones:
        result.update(await mark_topics(client, catalogs, period, ediciones, topics_))
    if not ediciones:
        latest = None
        for mes, anno in intent.Period(period.start, period.end, "").months[:1] + [
            (period.start.month - 1, period.start.year)
        ]:
            html = await client.post_ajax(
                "getedicionesgaceta", {"mes": mes, "anno": anno, "from": 0, "page": 0, "buscar": 1}
            )
            items = parse_ediciones(html)["resultados"]
            if items:
                latest = items[0]
                break
        result["mensaje"] = "No hay gacetas publicadas en ese periodo."
        result["ultima_edicion_disponible"] = latest
    return result


async def _search_normas_once(client: GacetaClient, catalogs: Catalogs, **p: Any) -> dict[str, Any]:
    html = await client.post_ajax(
        "getdata",
        {
            "numero": p["numero"] or "",
            "anno": p["anno"] or 0,
            "page": p["page"],
            "t_norma": await catalogs.resolve("tipos_norma", p["tipo_norma"]),
            "estado": await catalogs.resolve("estados", p["estado"]),
            "organismo": await catalogs.resolve("organismos", p["organismo"]),
            "texto_norma": p["texto"] or "",
            "identificador": p["identificador"] or "",
            "buscar": 2,
        },
    )
    return parse_normas(html)


@mcp.tool()
async def search_normas(
    query: str | None = None,
    topics_: list[str] | None = None,
    tipo_norma: str | None = None,
    estado: str | None = None,
    organismo: str | None = None,
    anno: int | None = None,
    numero: str | None = None,
    identificador: str | None = None,
    page: int = 0,
) -> dict[str, Any]:
    """Búsqueda avanzada de normas jurídicas por CONTENIDO (página 'busqueda-avanzada').

    Úsala para "qué gacetas/normas hablan sobre X". 'query' es texto libre; 'topics_' una lista
    de temas (una búsqueda por tema, resultados fusionados). Si no das 'query' ni 'topics_' ni
    otro filtro, se usan los temas guardados del usuario (por defecto: informática, contrato,
    trabajo, mipymes). Antes de usarla pregunta al usuario si quiere un tema específico.
    'tipo_norma' (Ley, Decreto-Ley, Resolución...), 'estado' (Vigente, Derogada...) y
    'organismo' admiten nombre o ID (ver list_catalogs). 'page' es base cero (10 por página).
    Aviso: el sitio no devuelve nada con estado 'Vigente' (comportamiento del propio buscador); omítelo.
    El sitio busca la frase literal: usa términos cortos ("contrato de trabajo"); si la frase larga no
    da resultados, se prueban sub-frases automáticamente.
    """
    client, catalogs = _deps()
    base = {
        "tipo_norma": tipo_norma, "estado": estado, "organismo": organismo, "anno": anno,
        "numero": numero, "identificador": identificador, "page": page,
    }  # fmt: skip
    has_filter = any([tipo_norma, estado, organismo, anno, numero, identificador])
    terms = [query] if query else list(topics_ or [])
    if not terms and not has_filter:
        terms = list(topics.get_topics()["topics"])  # type: ignore[arg-type]
    if not terms:
        terms = [""]

    merged: dict[str, dict[str, Any]] = {}
    searches = []

    async def run(term: str) -> dict[str, Any]:
        res = await _search_normas_once(client, catalogs, texto=term, **base)
        searches.append({
            "tema": term or None, "total_pagina": len(res["resultados"]), "page": res["page"],
            "last_page": res["last_page"], "has_more": res["has_more"],
        })  # fmt: skip
        for item in res["resultados"]:
            entry = merged.setdefault(item["url"] or item["titulo"], {**item, "temas": []})
            if term and term not in entry["temas"]:
                entry["temas"].append(term)
        return res

    nota = None
    for term in terms:
        res = await run(term)
        if not res["resultados"] and len(term.split()) > 1:
            # El sitio busca la frase literal: si no hay resultados, prueba sub-frases cada vez más cortas.
            before = len(merged)
            for sub in subphrases(term):
                await run(sub)
                if len(merged) > before:
                    nota = f"Sin resultados para la frase exacta '{term}'; se muestran coincidencias de sub-frases."
                    break
    out: dict[str, Any] = {"busquedas": searches, "total": len(merged), "resultados": list(merged.values())}
    if nota:
        out["nota"] = nota
    return out


@mcp.tool()
async def search_gacetas(
    numero: str | None = None,
    anno: int | None = None,
    tipo_edicion: str | None = None,
    page: int = 0,
) -> dict[str, Any]:
    """Busca gacetas por NÚMERO, año y/o tipo de edición (Ordinaria, Extraordinaria, Especial...).

    Úsala cuando el usuario cite un número concreto ("Gaceta Extraordinaria 92 de 2026").
    """
    client, catalogs = _deps()
    html = await client.post_ajax(
        "getdatagaceta",
        {
            "numero": numero or "",
            "anno": anno or 0,
            "page": page,
            "t_edicion": await catalogs.resolve("tipos_edicion", tipo_edicion),
            "buscar": 1,
        },
    )
    parsed = parse_ediciones(html)
    result = {"total_pagina": len(parsed["resultados"]), **parsed}
    if not parsed["resultados"]:
        result["mensaje"] = NO_GACETAS
    return result


@mcp.tool()
async def search_gacetas_historicas(
    numero: str | None = None,
    anno: int | None = None,
    tipo_edicion: str | None = None,
    texto: str | None = None,
    page: int = 0,
) -> dict[str, Any]:
    """Busca en el archivo histórico de gacetas (aprox. 1990-2008; página 'gacetas-oficiales-1990-2008').

    Cada gaceta incluye su ÍNDICE (organismos y normas que contiene) y 'texto' busca dentro de ese
    índice. Úsala solo para gacetas antiguas; para las actuales usa list_ediciones/search_gacetas.
    Si no hay gacetas que coincidan, devuelve 'mensaje' indicándolo.
    """
    client, catalogs = _deps()
    html = await client.post_ajax(
        "getdatagacetasa",
        {
            "numero": numero or "",
            "anno": anno or 0,
            "t_edicion": await catalogs.resolve("tipos_edicion", tipo_edicion),
            "indice": texto or "",
            "page": page,
            "buscar": 1,
        },
    )
    parsed = parse_gacetas_historicas(html)
    result = {"total_pagina": len(parsed["resultados"]), **parsed}
    if not parsed["resultados"]:
        result["mensaje"] = NO_GACETAS + " El archivo histórico cubre solo gacetas anteriores a 2009."
    return result


_PDF_TEXT_CACHE: dict[str, str] = {}


def _pdf_text(data: bytes) -> str:
    from pypdf import PdfReader

    return "\n".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(data)).pages)


async def _gaceta_text(client: GacetaClient, pdf_url: str) -> str:
    if pdf_url not in _PDF_TEXT_CACHE:
        data = await client.get_bytes(pdf_url)
        _PDF_TEXT_CACHE[pdf_url] = await asyncio.to_thread(_pdf_text, data)
        while len(_PDF_TEXT_CACHE) > 2:
            _PDF_TEXT_CACHE.pop(next(iter(_PDF_TEXT_CACHE)))
    return _PDF_TEXT_CACHE[pdf_url]


@mcp.tool()
async def get_norma(norma: str, max_chars: int = 30000, desde: int = 0) -> dict[str, Any]:
    """Trae una norma COMPLETA: metadatos y texto íntegro (p. ej. un Acuerdo, Decreto o Resolución).

    'norma' es la URL o el slug que devuelven las demás herramientas (p. ej.
    "acuerdo-651-x-de-2026-de-consejo-de-estado"). El texto se extrae del PDF de la gaceta que la
    publica (la primera consulta de una gaceta grande puede tardar ~15 s). 'max_chars' limita el
    texto devuelto; si sale 'truncado', pide el resto con 'desde'. En gacetas antiguas sin PDF con
    texto devuelve los metadatos, el enlace de descarga y un 'mensaje'.
    """
    client, _ = _deps()
    slug = norma.strip().rstrip("/").rsplit("/", 1)[-1]
    try:
        meta = parse_norma_page(await client.get_page(f"/es/{slug}"))
    except GacetaError as exc:
        return {"error": f"No se pudo abrir la norma '{slug}': {exc}"}
    if meta is None:
        return {"error": f"'{slug}' no es una norma de la Gaceta Oficial. Usa la URL que devuelven las búsquedas."}
    result: dict[str, Any] = {**meta, "url": f"{BASE_URL}/es/{slug}"}
    files = (
        parse_gaceta_files(await client.get_page(meta["gaceta_url"].replace(BASE_URL, "")))
        if meta["gaceta_url"]
        else {}
    )
    result["pdf"] = files.get("pdf")
    result["descarga"] = files.get("descarga")
    if not files.get("pdf") or not meta["identificador"]:
        result["mensaje"] = "El texto íntegro no está disponible en PDF; usa el enlace de descarga de la gaceta."
        return result
    try:
        text = extract_norma_text(await _gaceta_text(client, files["pdf"]), meta["identificador"])
    except GacetaError as exc:
        result["mensaje"] = f"No se pudo descargar el PDF de la gaceta: {exc}"
        return result
    if not text:
        result["mensaje"] = (
            "No se encontró el texto de esta norma en el PDF (puede estar escaneado); usa el enlace del PDF."
        )
        return result
    chunk = text[desde : desde + max_chars]
    result.update(
        {
            "texto": chunk,
            "texto_total_caracteres": len(text),
            "desde": desde,
            "truncado": desde + max_chars < len(text),
        }
    )
    return result


@mcp.tool()
async def list_catalogs() -> dict[str, Any]:
    """Valores válidos (id y nombre) de tipos de edición, tipos de norma, estados y organismos."""
    _, catalogs = _deps()
    return await catalogs.all()


@mcp.tool()
def get_topics() -> dict[str, Any]:
    """Temas de interés guardados del usuario (por defecto: informática, contrato, trabajo, mipymes)."""
    return topics.get_topics()


@mcp.tool()
def set_topics(new_topics: list[str]) -> dict[str, Any]:
    """Guarda los temas de interés del usuario. Una lista vacía restablece los valores por defecto."""
    return topics.set_topics(new_topics)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
