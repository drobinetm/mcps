## Context

Sitio Drupal 7 + jQuery. El script `busqueda_avanzada.min.js` hace `$.ajax POST` a URLs relativas (`getdata`, `getdatagaceta`, `getedicionesgaceta`, `getdatagacetasa`) enviando `{data: {...}}` y recibe HTML. No hay API JSON. Una prueba con `fetch` manual devolvió cuerpo vacío mientras que el click en la UI funcionó, por lo que hay que reproducir cabeceras/cookies exactas.

## Goals / Non-Goals

**Goals:** servidor MCP stdio instalable con `uvx`; usar los endpoints AJAX; interpretar fecha vs. contenido; temas de interés con defaults.
**Non-Goals:** descargar/OCR de PDFs; indexar el sitio; escritura sobre el sitio.

## Decisions

- **Python + FastMCP (`mcp`)**, `httpx` sync/async, `selectolax` para parsing, `platformdirs` para config. Elegido por el usuario (uvx).
- **Enrutamiento por herramienta, no por NLP en servidor**: el LLM del agente interpreta la intención; el servidor ofrece herramientas con descripciones inequívocas (`list_ediciones` para fechas, `search_normas` para contenido) y un módulo `intent.py` determinista solo para resolver fechas relativas ("hoy", "este mes").
- **Confirmación de tema** vía `instructions` + `get_topics`, porque no todos los clientes soportan elicitation.
- **`mes` base cero** en `getedicionesgaceta`; se encapsula en el cliente.
- Caché en memoria de catálogos (organismos, palabras) con TTL.

## Risks / Trade-offs

- Cambio de HTML/endpoints del sitio → parsers aislados con fixtures y tests; errores explícitos.
- Sitio lento (curl directo hizo timeout) → timeouts amplios, reintentos, uso moderado.
- Cuerpo vacío si faltan cookies/cabeceras → GET previo y cabeceras idénticas a la UI; verificar en tarea 2.

## Corrección posterior: `getdatagacetasa`
Inicialmente se supuso que devolvía el "sumario" de una gaceta. La investigación mostró que alimenta la página `gacetas-oficiales-1990-2008`: busca en el archivo histórico (hasta 2008) y cada resultado trae un índice por organismo. Sus bloques usan la clase `result-gacetagsa` (no `result-gaceta`), por lo que el parser original devolvía siempre vacío. La herramienta se renombró a `search_gacetas_historicas`. Las gacetas actuales y por mes siguen cubiertas por `list_ediciones` y `search_gacetas`.
