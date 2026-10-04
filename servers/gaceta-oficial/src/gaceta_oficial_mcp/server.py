"""Servidor MCP (stdio) para la Gaceta Oficial de Cuba."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from mcp.server import MCPServer

from . import intent, topics
from .catalogs import Catalogs
from .client import GacetaClient
from .parsers import parse_ediciones, parse_gacetas_historicas, parse_normas

INSTRUCTIONS = """\
Consulta la Gaceta Oficial de la República de Cuba (gacetaoficial.gob.cu).

Elige la herramienta según la intención del usuario:
- FECHA o periodo ("qué gacetas hay hoy", "de este mes", "octubre 2025") -> list_ediciones
  (equivale a la página ediciones-del-mes). No hace falta preguntar por un tema.
- CONTENIDO o tema ("qué gacetas hablan del contrato de trabajo en las mipymes", normas de
  un organismo, tipo de norma) -> search_normas (equivale a busqueda-avanzada).
- Un NÚMERO concreto de gaceta ("la Extraordinaria 92 de 2026") -> search_gacetas; gacetas anteriores a 2009
  (con su índice) con search_gacetas_historicas.

ANTES de una búsqueda por contenido sin tema claro, pregunta al usuario si desea buscar por un
tema específico. Si responde que no, llama a search_normas sin 'query' y sin 'topics': usará los
temas guardados (get_topics; por defecto: informática, contrato, trabajo, mipymes). Si el
usuario quiere cambiarlos de forma permanente, usa set_topics.
Presenta siempre el título, el tipo/número/fecha y el enlace de cada resultado.
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


@mcp.tool()
async def list_ediciones(periodo: str = "hoy") -> dict[str, Any]:
    """Lista las gacetas publicadas en una fecha o periodo (página 'ediciones-del-mes').

    Úsala cuando el usuario pregunte por FECHAS: "qué gacetas hay hoy", "ayer", "esta semana",
    "este mes", "mes pasado", "octubre 2025", "2026-10-02" o "02/10/2026".
    Devuelve tipo, número, fecha, URL, PDF y las normas que contiene cada edición.
    """
    client, _ = _deps()
    period = intent.parse_period(periodo)
    ediciones = await collect_ediciones(client, period)
    result: dict[str, Any] = {
        "periodo": period.label,
        "desde": period.start.isoformat(),
        "hasta": period.end.isoformat(),
        "total": len(ediciones),
        "ediciones": ediciones,
    }
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
