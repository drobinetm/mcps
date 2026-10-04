from gaceta_oficial_mcp import intent
from gaceta_oficial_mcp.server import mark_topics

URL = "https://www.gacetaoficial.gob.cu/es/resolucion-1-de-2026-de-ministerio-de-trabajo"


class FakeClient:
    """Devuelve getdata con una norma para el tema 'trabajo' y vacío para el resto."""

    async def post_ajax(self, endpoint, data):
        assert endpoint == "getdata" and data["anno"] == 2026
        if data["texto_norma"] != "trabajo":
            return ""
        return (
            '<div class="norma-juridica"><article><header><h2><a href="resolucion-1-de-2026-de-ministerio-de-trabajo">'
            "Resolución 1 de 2026 de Ministerio de Trabajo</a></h2></header>"
            '<div class="field-items"><div class="field-item">Regula el contrato de trabajo</div></div></article></div>'
        )


class FakeCatalogs:
    async def resolve(self, catalog, value):
        return "Cualquiera"


def edicion():
    return {
        "nombre_completo": "Gaceta Oficial No. 5 Ordinaria de 2026",
        "normas": [
            {"titulo": "Resolución 1 de 2026 de Ministerio de Trabajo", "url": URL},
            {"titulo": "Resolución 2 de 2026 de Ministerio de Cultura", "url": URL + "-x"},
        ],
    }


async def test_mark_topics_marca_normas_relevantes():
    period = intent.parse_period("2026-10-02")
    out = await mark_topics(FakeClient(), FakeCatalogs(), period, [edicion()], ["informática", "trabajo"])
    assert [n["titulo"] for n in out["normas_relevantes"]] == ["Resolución 1 de 2026 de Ministerio de Trabajo"]
    rel = out["normas_relevantes"][0]
    assert rel["temas"] == ["trabajo"] and rel["resumen"] == "Regula el contrato de trabajo"
    assert rel["gaceta"] == "Gaceta Oficial No. 5 Ordinaria de 2026"
    assert "mensaje_temas" not in out


async def test_mark_topics_sin_coincidencias():
    period = intent.parse_period("2026-10-02")
    out = await mark_topics(FakeClient(), FakeCatalogs(), period, [edicion()], ["informática"])
    assert out["normas_relevantes"] == [] and "mensaje_temas" in out
