# gaceta-oficial-mcp

[![CI](https://github.com/drobinetm/mcps/actions/workflows/ci.yml/badge.svg)](https://github.com/drobinetm/mcps/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-8A2BE2.svg)](https://modelcontextprotocol.io)
[![uv](https://img.shields.io/badge/installs%20with-uvx-DE5FE9.svg)](https://docs.astral.sh/uv/)

An [MCP](https://modelcontextprotocol.io) server (stdio) for searching the **Gaceta Oficial de la República de Cuba** ([gacetaoficial.gob.cu](https://www.gacetaoficial.gob.cu/)) from any AI agent.

The site has no public API, so this server replays the AJAX calls its own search forms make (`POST /es/getdata`, `getdatagaceta`, `getedicionesgaceta`, `getdatagacetasa`) and turns the returned HTML into structured JSON.

## Requirements

You need [`uv`](https://docs.astral.sh/uv/) on the machine where the agent runs; it provides the `uvx` command. You do **not** need to install Python (uv downloads 3.11+ if missing), clone this repo, or install the dependencies manually.

**Linux / macOS**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Other options: `brew install uv`, `winget install --id=astral-sh.uv -e` or `pipx install uv`.

Restart your terminal and check it works:

```bash
uvx --version
```

> **"command not found" in the agent?** GUI agents (Claude Desktop, Cursor, VS Code) may not see the `PATH` of your terminal. Use the full path to `uvx` in the config: run `which uvx` (Linux/macOS) or `where uvx` (Windows) and put that value in `"command"`, e.g. `"/home/you/.local/bin/uvx"` or `"C:\\Users\\you\\.local\\bin\\uvx.exe"`.

## Installation

There is nothing to clone: `uvx` downloads only the `servers/gaceta-oficial` folder of the [drobinetm/mcps](https://github.com/drobinetm/mcps) monorepo.

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

### Cline (and Roo Code / Kilo Code)

Open the MCP servers panel, choose **Configure MCP Servers**, and add the entry to `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "gaceta-oficial": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial", "gaceta-oficial-mcp"],
      "disabled": false
    }
  }
}
```

Roo Code and Kilo Code, which are Cline forks, use the same `mcpServers` format in their own MCP settings file.

### Zed

Add it to your Zed `settings.json` (`zed: open settings file`) under `context_servers`, or use **Settings → AI → MCP Servers → Add Server**:

```json
{
  "context_servers": {
    "gaceta-oficial": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial", "gaceta-oficial-mcp"]
    }
  }
}
```

### Continue

Create `.continue/mcpServers/gaceta-oficial.yaml` in your workspace (MCP servers only work in agent mode):

```yaml
name: gaceta-oficial
version: 0.0.1
schema: v1
mcpServers:
  - name: gaceta-oficial
    type: stdio
    command: uvx
    args:
      - --from
      - git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial
      - gaceta-oficial-mcp
```

### Goose

Run `goose configure`, choose **Add Extension → Command-line Extension**, name it `gaceta-oficial` and use this as the command:

```
uvx --from git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial gaceta-oficial-mcp
```

Or add it to `~/.config/goose/config.yaml`:

```yaml
extensions:
  gaceta-oficial:
    name: gaceta-oficial
    type: stdio
    enabled: true
    cmd: uvx
    args:
      - --from
      - git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial
      - gaceta-oficial-mcp
    envs: {}
```

### Any other MCP client

The server speaks MCP over **stdio** and needs no API keys or environment variables. In any client that asks for a command, use:

| Field | Value |
|---|---|
| Transport | `stdio` |
| Command | `uvx` |
| Arguments | `--from`, `git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial`, `gaceta-oficial-mcp` |

> Each agent's configuration format may change; check its documentation if the server does not load.

## Tools

| Tool | Use it for | Site page |
|---|---|---|
| `list_ediciones(periodo, topics_)` | **Dates**: "which gacetas are out today", `ayer`, `este mes`, `octubre 2025`, `2026-10-02` | `/es/ediciones-del-mes` |
| `search_normas(query, topics_, tipo_norma, estado, organismo, anno, numero, identificador, page)` | **Content / topic**: "gacetas about employment contracts in mipymes" | `/es/busqueda-avanzada` |
| `search_gacetas(numero, anno, tipo_edicion, page)` | A specific gaceta **number** | `/es/busqueda-avanzada` |
| `search_gacetas_historicas(numero, anno, tipo_edicion, texto, page)` | **Historical archive** (up to 2008): gacetas with their index of issuing bodies and norms; `texto` searches that index | `/es/gacetas-oficiales-1990-2008` |
| `get_norma(norma, max_chars, desde)` | **Read a full norm**: metadata plus the complete text of an Acuerdo, Decreto, Resolución... | norm page + the gaceta's PDF |
| `list_catalogs()` | Valid IDs for edition types, norm types, statuses and issuing bodies | `/es/busqueda-avanzada` |
| `get_topics()` / `set_topics(new_topics)` | Read / change your topics of interest | local file |

The server instructions tell the agent how to route a request: date-based questions go to `list_ediciones`, content-based questions go to `search_normas`, and a specific number goes to `search_gacetas`, and old gacetas (before 2009) go to `search_gacetas_historicas`.

### Topics of interest

Default topics: **informática, contrato, trabajo, mipymes** (the site is in Spanish, so topics are Spanish keywords).

Before **any** search (by date or by content) the agent is instructed to ask whether you want a specific topic. If you don't, the saved topics are used:
- `search_normas` with no arguments searches every saved topic, merges the results and tags each one with the topic that matched.
- `list_ediciones(periodo, topics_)` returns all the gacetas of the period and marks which of their norms match your topics (cross-checking the site's advanced search for that year), listing them in `normas_relevantes` with their summary.

Topics are stored in `~/.config/gaceta-oficial-mcp/topics.json` (override the directory with `GACETA_MCP_CONFIG_DIR`). `set_topics([])` restores the defaults.

### Full names in answers

Every gaceta comes with a `nombre_completo` (e.g. `Gaceta Oficial No. 92 Extraordinaria de 2026`) and every norm with its full title (e.g. `Acuerdo 651-X de 2026 de Consejo de Estado`) and link, and the server instructions tell the agent to present them unabbreviated so you can locate them.

### Reading a full norm

The site's page for each norm only shows metadata and a one-line summary; the full text exists only inside the PDF of the gaceta that published it. `get_norma` takes the norm URL (or slug) returned by the other tools, downloads that gaceta's PDF, and extracts the section that starts at the norm's identifier (e.g. `GOC-2026-594-EX92`) and ends at the next one. It returns the identifier, number, year, summary, keywords, norms it repeals/is modified by, the gaceta, and the text. Long texts are cut at `max_chars` (default 30000) with `truncado: true`; ask for the rest with `desde`.

Notes: the first call for a big gaceta can take ~15 s (a 300-page PDF is downloaded and parsed); PDFs are cached in memory afterwards. Old gacetas that only offer a `.rar` or a scanned PDF have no extractable text, so you get the download link and a `mensaje` instead.

### Known issues and site quirks

- The site's search matches the **literal phrase**. If a long phrase returns nothing, the server retries with shorter sub-phrases and says so in a `nota` field.
- Filtering by `estado="Vigente"` returns no results on the site itself; omit it. `Derogada` and `Modificada` work.
- Results come 10 per page and `page` is zero-based. In the site's monthly editions endpoint the month is zero-based too (October = 9); the server handles that for you.
- `search_gacetas_historicas` only covers old gacetas (the site's 1990-2008 archive); for current ones use `list_ediciones` or `search_gacetas`.
- When nothing matches, the gaceta tools return a `mensaje` saying that no gacetas were published instead of an empty list.

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
