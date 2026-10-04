# mcps

[![CI](https://github.com/drobinetm/mcps/actions/workflows/ci.yml/badge.svg)](https://github.com/drobinetm/mcps/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-8A2BE2.svg)](https://modelcontextprotocol.io)
[![uv](https://img.shields.io/badge/installs%20with-uvx-DE5FE9.svg)](https://docs.astral.sh/uv/)

A collection of [Model Context Protocol](https://modelcontextprotocol.io) (MCP) servers that you can install in any agent (Claude Code, Codex, Gemini CLI, Cursor, OpenCode, VS Code, ...) straight from this repository, without cloning it.

Each server lives in `servers/<name>/` as an independent Python project.

## Servers

| Server | Folder | Description |
|---|---|---|
| [gaceta-oficial](servers/gaceta-oficial) | `servers/gaceta-oficial` | Search the Gaceta Oficial of Cuba by date or by topic |

## Installation

**Requirement:** [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (it provides `uvx`).

Every server is installed with the same pattern:

```bash
uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/<name>" <command>
```

For example, to add `gaceta-oficial` to Claude Code:

```bash
claude mcp add gaceta-oficial -s user -- \
  uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/gaceta-oficial" gaceta-oficial-mcp
```

Per-agent instructions (Claude Code, Codex, Gemini CLI, Cursor, Claude Desktop, VS Code, OpenCode) are in each server's README.

## Adding a new server

1. Create `servers/<name>/` with its own `pyproject.toml` (with a console script) and tests.
2. Add a row to the table above and an entry to the matrix in `.github/workflows/ci.yml`.
3. Document the change with [OpenSpec](https://github.com/Fission-AI/OpenSpec) in `openspec/changes/` (`/opsx:propose`).

## License

[MIT](LICENSE)
