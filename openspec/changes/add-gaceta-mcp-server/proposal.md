## Why

La Gaceta Oficial de Cuba (https://www.gacetaoficial.gob.cu/) no ofrece API pública; su buscador carga resultados mediante AJAX. Los asistentes de IA no pueden consultarla de forma fiable. Se necesita un servidor MCP instalable en cualquier agente que consulte esos endpoints AJAX, interprete la intención del usuario (fecha vs. contenido) y priorice los temas de interés del usuario.

## What Changes

- Nuevo servidor MCP (stdio, Python, instalable con `uvx` desde GitHub) llamado `gaceta-oficial-mcp`.
- Cliente HTTP que replica los POST AJAX del sitio (`/es/getdata`, `/es/getdatagaceta`, `/es/getedicionesgaceta`, `/es/getdatagacetasa`) y parsea los fragmentos HTML devueltos.
- Herramientas: búsqueda de normas (busqueda-avanzada), búsqueda de gacetas, listado de ediciones por fecha/mes (ediciones-del-mes), índice de una gaceta, catálogos y gestión de temas de interés.
- Temas de interés persistentes con valor por defecto: informática, contrato, trabajo, mipymes; el servidor instruye al agente a preguntar al usuario por un tema antes de buscar por contenido.
- Enrutamiento de intención documentado: consultas por fecha → ediciones-del-mes; consultas por contenido → busqueda-avanzada.

## Capabilities

### New Capabilities
- `cliente-http-ajax`: sesión HTTP y reproducción de los POST AJAX del sitio, con parsing de HTML.
- `busqueda-normas`: búsqueda avanzada de normas jurídicas (`getdata`).
- `busqueda-gacetas`: búsqueda de gacetas por número/año/tipo e índice de una gaceta.
- `ediciones-por-fecha`: listado de ediciones por mes/año/día (`getedicionesgaceta`).
- `temas-de-interes`: temas por defecto, persistencia y flujo de confirmación previa a la búsqueda.
- `catalogos`: tipos de edición, tipos de norma, estados y organismos.

### Modified Capabilities
(ninguna)

## Impact

Repositorio nuevo; sin código previo afectado. Dependencias: `mcp`, `httpx`, `selectolax`, `platformdirs`. Depende de la estructura HTML/AJAX actual del sitio (Drupal 7), que puede cambiar.
