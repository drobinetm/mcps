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


def _field_items(tree: HTMLParser, name: str) -> list[str]:
    out = []
    for node in tree.css(f"div.field-name-{name} .field-item"):
        text = _text(node)
        if text and not text.lower().startswith("no existen referencias"):
            out.append(text)
    return out


def parse_norma_page(html: str) -> dict[str, Any] | None:
    """Metadatos de la página de una norma (``/es/<slug>``); None si no es una norma."""
    tree = HTMLParser(html or "")
    if tree.css_first("div.node-norma-juridica") is None:
        return None
    title = _text(tree.css_first("title")).removesuffix("| Gaceta Oficial").strip()
    gaceta = tree.css_first("div.field-name-field-gaceta-oficial-norma a")
    one = lambda name: (_field_items(tree, name) or [""])[0]
    return {
        "titulo": title,
        "identificador": one("field-identificador-de-norma"),
        "numero": one("field-numero-v"),
        "anno": one("field-anno-norma"),
        "resumen": one("body").removeprefix("Resumen:").strip(),
        "palabras_clave": [_text(a) for a in tree.css("div.field-name-field-palabras-claves-norma-ju a")],
        "deroga": _field_items(tree, "field-normas-deroga-norma"),
        "modificada_por": _field_items(tree, "field-normas-que-la-modifican"),
        "derogada_por": _field_items(tree, "field-norma-que-la-deroga"),
        "gaceta_nombre": _text(gaceta) if gaceta else None,
        "gaceta_url": abs_url(gaceta.attributes.get("href")) if gaceta else None,
    }


def parse_gaceta_files(html: str) -> dict[str, str | None]:
    """Enlaces de descarga de la página de una gaceta: primer PDF y primer adjunto de cualquier tipo."""
    tree = HTMLParser(html or "")
    files = [a.attributes["href"] for a in tree.css("a[href]") if "/sites/default/files/" in a.attributes["href"]]
    pdf = next((h for h in files if h.lower().endswith(".pdf")), None)
    return {"pdf": abs_url(pdf), "descarga": abs_url(pdf or (files[0] if files else None))}


_ID_LINE = re.compile(r"(?m)^[ \t]*(GOC-\d{4}-\d+-[A-Z]+\d+)[ \t]*$")
_NOISE = [
    re.compile(r"(?m)^[ \t]*Gaceta Oficial de la Rep[uú]blica[ \t]*$\n?"),
    re.compile(r"(?m)^[ \t]*\d{2}/\d{2}/\d{4}[ \t]*GOC-\d{4}-[A-Z]+\d+[ \t]*$\n?"),
    re.compile(r"(?m)^[ \t]*\d{3,5}[ \t]*$\n?"),
]


def extract_norma_text(full_text: str, identificador: str) -> str | None:
    """Texto de la norma: desde la línea con su identificador hasta el identificador siguiente."""
    marks = list(_ID_LINE.finditer(full_text))
    for i, m in enumerate(marks):
        if m.group(1) == identificador:
            end = marks[i + 1].start() if i + 1 < len(marks) else len(full_text)
            text = full_text[m.end() : end]
            for noise in _NOISE:
                text = noise.sub("", text)
            text = re.sub(r"(?<=[a-záéíóúñü]) ?-\n(?=[a-záéíóúñü])", "", text)
            return text.strip() or None
    return None
