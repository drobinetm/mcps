from pathlib import Path

import httpx
import pytest

from gaceta_oficial_mcp import server
from gaceta_oficial_mcp.client import GacetaClient, GacetaError
from gaceta_oficial_mcp.parsers import extract_norma_text, parse_gaceta_files, parse_norma_page

FX = Path(__file__).parent / "fixtures"


def fx(name: str) -> str:
    return (FX / name).read_text(encoding="utf-8")


def test_parse_norma_page():
    m = parse_norma_page(fx("norma_acuerdo.html"))
    assert m["titulo"] == "Acuerdo 651-X de 2026 de Consejo de Estado"
    assert m["identificador"] == "GOC-2026-594-EX92" and m["numero"] == "651-X" and m["anno"] == "2026"
    assert m["gaceta_nombre"] == "Gaceta Oficial No. 92 Extraordinaria de 2026"
    assert m["gaceta_url"].endswith("/es/gaceta-oficial-no-92-extraordinaria-de-2026")
    assert m["palabras_clave"] == ["embajador"] and m["deroga"] == [] and m["derogada_por"] == []


def test_parse_norma_page_deroga():
    m = parse_norma_page(fx("norma_resolucion.html"))
    assert m["deroga"] == ["Resolución 44 de 2014 de Ministerio de Cultura"]
    assert m["palabras_clave"] == ["reglamento", "contrato", "artista"]


def test_parse_norma_page_no_es_norma():
    assert parse_norma_page(fx("busqueda-avanzada.html")) is None


def test_parse_gaceta_files():
    f = parse_gaceta_files(fx("gaceta_page_78.html"))
    assert f["pdf"] == "https://www.gacetaoficial.gob.cu/sites/default/files/goc-2026-o78.pdf"
    assert parse_gaceta_files("<html></html>") == {"pdf": None, "descarga": None}


def test_extract_norma_text_acuerdo_completo():
    text = extract_norma_text(fx("gaceta_ex92.txt"), "GOC-2026-594-EX92")
    assert text.startswith("JUAN ESTEBAN LAZO")
    for expected in ("ACUERDO 651-X", "PRIMERO:", "SEGUNDO:", "COMUNÍQUESE", "Extraordinario y Plenipotenciario"):
        assert expected in text
    assert "ACUERDO 661-X" not in text and "GOC-2026-595-EX92" not in text
    assert "Extraor-" not in text  # palabra partida reunida


def test_extract_norma_text_ultima_y_inexistente():
    full = fx("gaceta_ex92.txt")
    assert "ACUERDO 664-X" in extract_norma_text(full, "GOC-2026-598-EX92")
    assert extract_norma_text(full, "GOC-2026-999-EX92") is None


def test_extract_limpia_encabezados_y_guiones():
    full = "x\nGOC-2026-1-O1\nArtículo 1. Dis-\nposición\n2617\nGaceta Oficial de la República\n18/09/2026 GOC-2026-O1\nsigue per -\ntenecientes\nGOC-2026-2-O1\notra"
    assert extract_norma_text(full, "GOC-2026-1-O1") == "Artículo 1. Disposición\nsigue pertenecientes"


async def test_get_bytes_cache_y_limite():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, content=b"%PDF-data")

    client = GacetaClient(transport=httpx.MockTransport(handler))
    assert await client.get_bytes("/a.pdf") == b"%PDF-data"
    assert await client.get_bytes("/a.pdf") == b"%PDF-data"
    assert calls == ["/a.pdf"]  # segunda vez desde caché
    with pytest.raises(GacetaError):
        await client.get_bytes("/b.pdf", max_bytes=3)
    await client.aclose()


async def test_get_norma_flujo_completo(monkeypatch):
    pages = {
        "/es/acuerdo-651-x-de-2026-de-consejo-de-estado": fx("norma_acuerdo.html"),
        "/es/gaceta-oficial-no-92-extraordinaria-de-2026": '<a href="/sites/default/files/goc-2026-ex92.pdf">PDF</a>',
    }

    class Fake:
        async def get_page(self, path):
            return pages[path]

    async def fake_text(client, pdf_url):
        return fx("gaceta_ex92.txt")

    monkeypatch.setattr(server, "_deps", lambda: (Fake(), None))
    monkeypatch.setattr(server, "_gaceta_text", fake_text)
    r = await server.get_norma(
        "https://www.gacetaoficial.gob.cu/es/acuerdo-651-x-de-2026-de-consejo-de-estado", max_chars=200
    )
    assert r["identificador"] == "GOC-2026-594-EX92" and r["truncado"] is True and len(r["texto"]) == 200
    rest = await server.get_norma("acuerdo-651-x-de-2026-de-consejo-de-estado", max_chars=5000, desde=200)
    assert rest["truncado"] is False and "COMUNÍQUESE" in rest["texto"]
