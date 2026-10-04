# gaceta-oficial-mcp

[![CI](https://github.com/drobinetm/mcps/actions/workflows/ci.yml/badge.svg)](https://github.com/drobinetm/mcps/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-8A2BE2.svg)](https://modelcontextprotocol.io)
[![uv](https://img.shields.io/badge/installs%20with-uvx-DE5FE9.svg)](https://docs.astral.sh/uv/)

An [MCP](https://modelcontextprotocol.io) server (stdio) for searching the **Gaceta Oficial de la República de Cuba** ([gacetaoficial.gob.cu](https://www.gacetaoficial.gob.cu/)) from any AI agent.

The site has no public API, so this server replays the AJAX calls its own search forms make (`POST /es/getdata`, `getdatagaceta`, `getedicionesgaceta`, `getdatagacetasa`) and turns the returned HTML into structured JSON.

## Installation

**Requirement:** [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (it provides `uvx`). There is nothing to clone: `uvx` downloads only the `servers/gaceta-oficial` folder of the [drobinetm/mcps](https://github.com/drobinetm/mcps) monorepo.

Quick check that it starts:

```bash
uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial" gaceta-oficial-mcp
```

### Claude Code

```bash
claude mcp add gaceta-oficial -s user -- \
  uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial" gaceta-oficial-mcp
```

`-s user` makes it available in all your projects.

### Codex

```bash
codex mcp add gaceta-oficial -- \
  uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial" gaceta-oficial-mcp
```

Or edit `~/.codex/config.toml`:

```toml
[mcp_servers.gaceta-oficial]
command = "uvx"
args = ["--from", "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial", "gaceta-oficial-mcp"]
```

### Gemini CLI, Cursor, Claude Desktop, Windsurf

Add this to `~/.gemini/settings.json`, `~/.cursor/mcp.json`, `claude_desktop_config.json`, etc.:

```json
{
  "mcpServers": {
    "gaceta-oficial": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial",
        "gaceta-oficial-mcp"
      ]
    }
  }
}
```

### VS Code / Copilot

Same JSON in `.vscode/mcp.json`, but with `"servers"` instead of `"mcpServers"` as the root key.

### OpenCode

```json
{
  "mcp": {
    "gaceta-oficial": {
      "type": "local",
      "command": [
        "uvx",
        "--from",
        "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial",
        "gaceta-oficial-mcp"
      ]
    }
  }
}
```

> Each agent's configuration format may change; check its documentation if the server does not load.

## Tools

| Tool | Use it for | Site page |
|---|---|---|
| `list_ediciones(periodo)` | **Dates**: "which gacetas are out today", `ayer`, `este mes`, `octubre 2025`, `2026-10-02` | `/es/ediciones-del-mes` |
| `search_normas(query, topics_, tipo_norma, estado, organismo, anno, numero, identificador, page)` | **Content / topic**: "gacetas about employment contracts in mipymes" | `/es/busqueda-avanzada` |
| `search_gacetas(numero, anno, tipo_edicion, page)` | A specific gaceta **number** | `/es/busqueda-avanzada` |
| `get_gaceta_indice(...)` | Table of contents of a gaceta (see known issues) | `getdatagacetasa` |
| `list_catalogs()` | Valid IDs for edition types, norm types, statuses and issuing bodies | `/es/busqueda-avanzada` |
| `get_topics()` / `set_topics(new_topics)` | Read / change your topics of interest | local file |

The server instructions tell the agent how to route a request: date-based questions go to `list_ediciones`, content-based questions go to `search_normas`, and a specific number goes to `search_gacetas`.

### Topics of interest

Default topics: **informática, contrato, trabajo, mipymes** (the site is in Spanish, so topics are Spanish keywords).

Before a content search, the agent is instructed to ask whether you want a specific topic. If you don't, `search_normas` with no arguments searches every saved topic and merges the results, tagging each one with the topic that matched. Topics are stored in `~/.config/gaceta-oficial-mcp/topics.json` (override the directory with `GACETA_MCP_CONFIG_DIR`). `set_topics([])` restores the defaults.

### Known issues and site quirks

- The site's search matches the **literal phrase**. If a long phrase returns nothing, the server retries with shorter sub-phrases and says so in a `nota` field.
- Filtering by `estado="Vigente"` returns no results on the site itself; omit it. `Derogada` and `Modificada` work.
- Results come 10 per page and `page` is zero-based. In the site's monthly editions endpoint the month is zero-based too (October = 9); the server handles that for you.
- `get_gaceta_indice` (`getdatagacetasa`) returned empty responses in every test, so its behavior is unverified.

## Development

```bash
cd servers/gaceta-oficial
uv sync
uv run pytest                                  # tests use real HTML fixtures
uv run ruff check . && uv run ruff format --check .
npx @modelcontextprotocol/inspector uv run gaceta-oficial-mcp
```

The project is spec-driven with [OpenSpec](https://github.com/Fission-AI/OpenSpec); specs and changes live in `openspec/` at the root of the monorepo.

## License

[MIT](../../LICENSE)
