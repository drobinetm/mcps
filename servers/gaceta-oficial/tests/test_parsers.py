from datetime import date
from pathlib import Path

from gaceta_oficial_mcp.parsers import (
    parse_ediciones,
    parse_fecha,
    parse_gacetas_historicas,
    parse_indice,
    parse_normas,
    parse_select_options,
)

FX = Path(__file__).parent / "fixtures"


def fx(name: str) -> str:
    return (FX / name).read_text(encoding="utf-8")


def test_parse_normas():
    r = parse_normas(fx("getdata.html"))
    assert r["resultados"], "debe haber normas"
    first = r["resultados"][0]
    assert first["titulo"].startswith("Resolución 28 de 2026")
    assert first["url"].startswith("https://www.gacetaoficial.gob.cu/es/resolucion-28")
    assert "contrato de trabajo" in first["resumen"]
    assert r["has_more"] is False


def test_parse_normas_pagination():
    r = parse_normas(fx("getdata_paginated.html"))
    assert len(r["resultados"]) == 10
    assert (r["page"], r["has_more"]) == (0, True)
    assert r["last_page"] > 1


def test_parse_normas_empty():
    assert parse_normas("") == {"resultados": [], "page": 0, "last_page": 0, "has_more": False}


def test_parse_ediciones():
    r = parse_ediciones(fx("getedicionesgaceta.html"))
    first = r["resultados"][0]
    assert first["numero"] == "92" and first["tipo"] == "Extraordinaria"
    assert first["fecha"] == "2026-10-02"
    assert first["pdf"].endswith("goc-2026-ex92.pdf")
    assert first["url"].endswith("/es/gaceta-oficial-no-92-extraordinaria-de-2026")
    assert first["normas"][0]["titulo"].startswith("Acuerdo 651-X")


def test_parse_getdatagaceta():
    r = parse_ediciones(fx("getdatagaceta.html"))
    assert any(e["numero"] == "92" for e in r["resultados"])


def test_parse_fecha():
    assert parse_fecha("02 Octubre, 2026") == date(2026, 10, 2)
    assert parse_fecha("basura") is None


def test_catalog_options():
    html = fx("busqueda-avanzada.html")
    tipos = {o["nombre"]: o["id"] for o in parse_select_options(html, "St_edicion")}
    assert tipos["Extraordinaria"] == "3"
    assert any(o["nombre"] == "Consejo de Ministros" for o in parse_select_options(html, "Sorganismo"))


def test_parse_gacetas_historicas():
    r = parse_gacetas_historicas(fx("getdatagacetasa.html"))
    assert len(r["resultados"]) == 10 and r["has_more"] and r["last_page"] == 11
    first = r["resultados"][0]
    assert first["fecha"].startswith("2001") and first["url"].startswith(
        "https://www.gacetaoficial.gob.cu/es/gaceta-oficial-no"
    )
    assert first["descarga"] and first["indice"][0]["organismo"]
    assert any("TRABAJO" in sec["organismo"] for r_ in r["resultados"] for sec in r_["indice"])


def test_parse_gacetas_historicas_empty():
    assert parse_gacetas_historicas("")["resultados"] == []


def test_parse_indice():
    assert parse_indice("A\nRES 1\n;B\nRES 2\nRES 3") == [
        {"organismo": "A", "normas": ["RES 1"]},
        {"organismo": "B", "normas": ["RES 2", "RES 3"]},
    ]
