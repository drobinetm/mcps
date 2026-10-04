## 1. Preparación
- [x] 1.1 Configurar `pyproject.toml` (deps `mcp`, `httpx`, `selectolax`, `platformdirs`; dev `pytest`, `ruff`; script `gaceta-oficial-mcp`)
- [x] 1.2 `.gitignore`, LICENSE (MIT), CHANGELOG, `openspec/config.yaml` con contexto del proyecto

## 2. Cliente AJAX (cliente-http-ajax)
- [x] 2.1 Verificar en vivo el request exacto que acepta `/es/getdata` (cookies, Referer, X-Requested-With)
- [x] 2.2 Implementar `client.py` (sesión, serialización `data[...]`, reintentos, timeouts)
- [x] 2.3 Guardar fixtures HTML reales en `tests/fixtures/`

## 3. Parsers
- [x] 3.1 `parse_normas` (`.norma-juridica`) + paginación
- [x] 3.2 `parse_ediciones` (`.result-gaceta`, `.norma-gaceta`)
- [x] 3.3 Parser de `getdatagaceta` y `getdatagacetasa`
- [x] 3.4 Tests de parsers

## 4. Catálogos y temas
- [x] 4.1 `catalogs.py` (estáticos + organismos/palabras desde la página, caché)
- [x] 4.2 `topics.py` con defaults y persistencia; tests

## 5. Herramientas MCP
- [x] 5.1 `intent.py` (hoy, ayer, este mes, mes+año)
- [x] 5.2 Tools: `list_ediciones`, `search_normas`, `search_gacetas`, `get_gaceta_indice`, `list_catalogs`, `get_topics`, `set_topics`
- [x] 5.3 `instructions` del servidor con enrutamiento de intención y confirmación de tema

## 6. Distribución
- [x] 6.1 README con instalación para Claude Code, Cursor, Codex, Gemini CLI, Claude Desktop
- [x] 6.2 CI en GitHub Actions (uv, ruff, pytest)
- [x] 6.3 Probar `uvx --from . gaceta-oficial-mcp` (cliente MCP stdio; Inspector pendiente de prueba manual)
- [x] 6.4 Pruebas en vivo de los escenarios de los specs
