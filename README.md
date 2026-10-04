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
