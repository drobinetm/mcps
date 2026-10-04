import json
from datetime import date

import httpx
import pytest

from gaceta_oficial_mcp import topics
from gaceta_oficial_mcp.catalogs import Catalogs
from gaceta_oficial_mcp.client import GacetaClient, encode_data
from gaceta_oficial_mcp.intent import parse_period

REF = date(2026, 10, 4)


def test_period_hoy_y_ayer():
    assert parse_period("hoy", REF).start == REF
    assert parse_period("ayer", REF).end == date(2026, 10, 3)


def test_period_mes_base_cero():
    p = parse_period("octubre 2025", REF)
    assert (p.start, p.end) == (date(2025, 10, 1), date(2025, 10, 31))
    assert p.months == [(9, 2025)]


def test_period_cruza_meses_y_anios():
    p = parse_period("esta semana", date(2026, 1, 1))  # jueves
    assert p.months == [(0, 2026), (11, 2025)]
    assert parse_period("mes pasado", date(2026, 1, 15)).months == [(11, 2025)]


def test_period_formatos():
    assert parse_period("02/10/2026", REF).start == date(2026, 10, 2)
    assert parse_period("2026-10-02", REF).end == date(2026, 10, 2)
    with pytest.raises(ValueError):
        parse_period("cuando sea", REF)


def test_encode_data_like_jquery():
    out = encode_data({"anno": 0, "palabras": [1, 2], "x": None})
    assert out == [("data[anno]", "0"), ("data[palabras][]", "1"), ("data[palabras][]", "2"), ("data[x]", "")]


def test_topics_default_and_persist(tmp_path, monkeypatch):
    monkeypatch.setenv("GACETA_MCP_CONFIG_DIR", str(tmp_path))
    assert topics.get_topics() == {"topics": ["informática", "contrato", "trabajo", "mipymes"], "is_default": True}
    assert topics.set_topics([" ley ", "salud"])["topics"] == ["ley", "salud"]
    assert json.loads((tmp_path / "topics.json").read_text())["topics"] == ["ley", "salud"]
    assert topics.set_topics([])["is_default"] is True


async def test_client_post_headers_and_catalog_resolve():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, text=open("tests/fixtures/busqueda-avanzada.html", encoding="utf-8").read())
        seen["ref"] = request.headers["referer"]
        seen["xhr"] = request.headers["x-requested-with"]
        seen["body"] = request.content.decode()
        return httpx.Response(200, text="")

    client = GacetaClient(transport=httpx.MockTransport(handler))
    assert await client.post_ajax("getedicionesgaceta", {"mes": 9, "anno": 2026}) == ""
    assert seen["ref"].endswith("/es/ediciones-del-mes") and seen["xhr"] == "XMLHttpRequest"
    assert "data%5Bmes%5D=9" in seen["body"]

    cat = Catalogs(client)
    assert await cat.resolve("tipos_edicion", "extraordinaria") == "3"
    assert await cat.resolve("tipos_norma", "Ley") == "11"
    assert await cat.resolve("estados", None) == "Cualquiera"
    with pytest.raises(ValueError):
        await cat.resolve("estados", "inexistente")
    await client.aclose()
