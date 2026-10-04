# gaceta-oficial-mcp

Servidor [MCP](https://modelcontextprotocol.io) (stdio) para consultar la **Gaceta Oficial de la República de Cuba** ([gacetaoficial.gob.cu](https://www.gacetaoficial.gob.cu/)) desde cualquier agente de IA.

El sitio no tiene API pública: este servidor reproduce las llamadas AJAX que usa su buscador (`POST /es/getdata`, `getdatagaceta`, `getedicionesgaceta`, `getdatagacetasa`) y convierte el HTML devuelto en JSON.

## Herramientas

| Herramienta | Cuándo usarla | Fuente en el sitio |
|---|---|---|
| `list_ediciones(periodo)` | Por **fecha**: "qué gacetas hay hoy", "ayer", "este mes", "octubre 2025", `2026-10-02` | `/es/ediciones-del-mes` |
| `search_normas(query, topics_, tipo_norma, estado, organismo, anno, numero, identificador, page)` | Por **contenido/tema**: "gacetas sobre el contrato de trabajo en las mipymes" | `/es/busqueda-avanzada` |
| `search_gacetas(numero, anno, tipo_edicion, page)` | Un **número** concreto de gaceta | `/es/busqueda-avanzada` |
| `get_gaceta_indice(...)` | Sumario de una gaceta | `getdatagacetasa` |
| `list_catalogs()` | IDs válidos de tipos de edición/norma, estados y organismos | `/es/busqueda-avanzada` |
| `get_topics()` / `set_topics(new_topics)` | Temas de interés del usuario | archivo local |

### Temas de interés
Por defecto: **informática, contrato, trabajo, mipymes**. Las instrucciones del servidor piden al agente que, antes de una búsqueda por contenido, pregunte si quieres un tema específico; si no, `search_normas` sin argumentos busca cada tema guardado y fusiona los resultados. Se guardan en `~/.config/gaceta-oficial-mcp/topics.json` (o la ruta de `GACETA_MCP_CONFIG_DIR`).

### Notas del sitio
- El buscador busca la **frase literal**; si una frase larga no da resultados, el servidor prueba sub-frases más cortas.
- El filtro `estado=Vigente` no devuelve resultados en el propio sitio; omítelo.
- Hasta 10 resultados por página (`page` empieza en 0). En `getedicionesgaceta` el mes es base cero (octubre = 9); el servidor lo encapsula.

## Instalación

Requisito: [`uv`](https://docs.astral.sh/uv/). No hace falta clonar: `uvx` descarga solo la carpeta `servers/gaceta-oficial` del monorepo [drobinetm/mcps](https://github.com/drobinetm/mcps).

```
uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial" gaceta-oficial-mcp
```

**Claude Code**
```bash
claude mcp add gaceta-oficial -s user -- uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial" gaceta-oficial-mcp
```

**Codex** (`~/.codex/config.toml`)
```toml
[mcp_servers.gaceta-oficial]
command = "uvx"
args = ["--from", "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial", "gaceta-oficial-mcp"]
```

**Gemini CLI** (`~/.gemini/settings.json`), **Cursor** (`~/.cursor/mcp.json`), **Claude Desktop**, **Windsurf**
```json
{
  "mcpServers": {
    "gaceta-oficial": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial", "gaceta-oficial-mcp"]
    }
  }
}
```

**VS Code / Copilot** (`.vscode/mcp.json`): igual, con `"servers"` en lugar de `"mcpServers"`.

**OpenCode** (`opencode.json`)
```json
{ "mcp": { "gaceta-oficial": { "type": "local",
  "command": ["uvx", "--from", "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial", "gaceta-oficial-mcp"] } } }
```

> Los formatos de configuración de cada agente pueden cambiar; consulta su documentación si algo no carga.

## Desarrollo

```bash
cd servers/gaceta-oficial
uv sync
uv run pytest          # tests con fixtures HTML reales
uv run ruff check . && uv run ruff format --check .
npx @modelcontextprotocol/inspector uv run gaceta-oficial-mcp
```

El proyecto usa [OpenSpec](https://github.com/Fission-AI/OpenSpec): specs y cambios en `openspec/` en la raíz del monorepo.

## Licencia
MIT
