"""Parsers de los fragmentos HTML devueltos por los endpoints AJAX."""

from __future__ import annotations

import re
from datetime import date
from typing import Any
from urllib.parse import urljoin

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from .client import BASE_URL, LANG_PREFIX

_PAGE_BASE = f"{BASE_URL}{LANG_PREFIX}/"

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}  # fmt: skip


def abs_url(href: str | None) -> str | None:
    return urljoin(_PAGE_BASE, href) if href else None


def _text(node: Node | None) -> str:
    return re.sub(r"\s+", " ", node.text(strip=True)).strip() if node else ""


def parse_fecha(text: str) -> date | None:
    """'02 Octubre, 2026' -> date(2026, 10, 2)."""
    m = re.search(r"(\d{1,2})\s+([A-Za-zñÑáéíóú]+),?\s+(\d{4})", text)
    if not m or m.group(2).lower() not in MESES:
        return None
    return date(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1)))


def nombre_completo(numero: str, tipo: str, fecha: date | None, url: str | None) -> str:
    """'Gaceta Oficial No. 92 Extraordinaria de 2026' (el año sale de la fecha o del slug)."""
    year = fecha.year if fecha else None
    if year is None and url and (m := re.search(r"-de-(\d{4})$", url)):
        year = int(m[1])
    return " ".join(p for p in [f"Gaceta Oficial No. {numero}".strip(), tipo, f"de {year}" if year else ""] if p)


def parse_pager(tree: HTMLParser) -> dict[str, Any]:
    """Paginación base cero: página actual y última página."""
    pager = tree.css_first("ul#pagination")
    if pager is None:
        return {"page": 0, "last_page": 0, "has_more": False}
    current = pager.css_first("li.pager-current")
    page = int(_text(current)) - 1 if current and _text(current).isdigit() else 0
    pages = [
        int(n.attributes["data-page"]) for n in pager.css("a.page-item") if n.attributes.get("data-page", "").isdigit()
    ]
    last_node = pager.css_first("li.pager-last a.page-item")
    last = int(last_node.attributes["data-page"]) if last_node else max([page, *pages])
    return {"page": page, "last_page": last, "has_more": page < last}


def parse_normas(html: str) -> dict[str, Any]:
    """Resultados de ``getdata``: bloques ``.norma-juridica``."""
    tree = HTMLParser(html or "")
    items = []
    for block in tree.css("div.norma-juridica"):
        link = block.css_first("h2 a")
        items.append(
            {
                "titulo": _text(link),
                "url": abs_url(link.attributes.get("href") if link else None),
                "resumen": _text(block.css_first(".field-item")),
            }
        )
    return {"resultados": items, **parse_pager(tree)}


def parse_ediciones(html: str) -> dict[str, Any]:
    """Resultados de ``getedicionesgaceta`` / ``getdatagaceta``: bloques ``.result-gaceta``."""
    tree = HTMLParser(html or "")
    items = []
    for block in tree.css("div.result-gaceta"):
        ver = block.css_first(".views-field-view-node a")
        pdf = block.css_first(".views-field-field-fichero-gaceta a")
        fecha_txt = _text(block.css_first(".date-display-single"))
        fecha = parse_fecha(fecha_txt)
        numero = _text(block.css_first(".views-field-field-numero-de-gaceta .field-content"))
        tipo = _text(block.css_first(".views-field-field-tipo-edicion-gaceta .field-content"))
        url = abs_url(ver.attributes.get("href") if ver else None)
        items.append(
            {
                "nombre_completo": nombre_completo(numero, tipo, fecha, url),
                "numero": numero,
                "tipo": tipo,
                "fecha": fecha.isoformat() if fecha else None,
                "fecha_texto": fecha_txt,
                "url": url,
                "pdf": abs_url(pdf.attributes.get("href") if pdf else None),
                "normas": [
                    {"titulo": _text(a), "url": abs_url(a.attributes.get("href"))} for a in block.css(".norma-gaceta a")
                ],
            }
        )
    return {"resultados": items, **parse_pager(tree)}


def parse_select_options(html: str, select_id: str) -> list[dict[str, str]]:
    """Opciones ``{id, nombre}`` de un ``<select>`` de la búsqueda avanzada."""
    tree = HTMLParser(html)
    sel = tree.css_first(f"select#{select_id}")
    if sel is None:
        return []
    out = []
    for opt in sel.css("option"):
        value = opt.attributes.get("value") or ""
        if value in ("", "0", "-1", "Cualquiera"):
            continue
        out.append({"id": value, "nombre": _text(opt)})
    return out


def parse_indice(text: str) -> list[dict[str, Any]]:
    """Índice de una gaceta histórica: secciones separadas por ';', primera línea = organismo."""
    sections = []
    for chunk in text.split(";"):
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if lines:
            sections.append({"organismo": lines[0], "normas": lines[1:]})
    return sections


def parse_gacetas_historicas(html: str) -> dict[str, Any]:
    """Resultados de ``getdatagacetasa`` (gacetas 1990-2008): ``.result-gacetagsa`` con su índice."""
    tree = HTMLParser(html or "")
    items = []
    for block in tree.css("div.result-gacetagsa"):
        ver = block.css_first(".views-field-view-node a")
        pdf = block.css_first(".views-field-field-fichero-gaceta a")
        fecha_txt = _text(block.css_first(".date-display-single"))
        fecha = parse_fecha(fecha_txt)
        indices = block.css_first(".indices")
        numero = _text(block.css_first(".views-field-field-numero-de-gaceta .field-content"))
        tipo = _text(block.css_first(".views-field-field-tipo-edicion-gaceta .field-content"))
        url = abs_url(ver.attributes.get("href") if ver else None)
        items.append(
            {
                "nombre_completo": nombre_completo(numero, tipo, fecha, url),
                "numero": numero,
                "tipo": tipo,
                "fecha": fecha.isoformat() if fecha else None,
                "fecha_texto": fecha_txt,
                "url": url,
                "descarga": abs_url(pdf.attributes.get("href") if pdf else None),
                "indice": parse_indice(indices.text() if indices else ""),
            }
        )
    return {"resultados": items, **parse_pager(tree)}
