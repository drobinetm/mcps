# mcps

Colección de servidores [MCP](https://modelcontextprotocol.io) listos para instalar en cualquier agente (Claude Code, Codex, Gemini CLI, Cursor, OpenCode, VS Code…). Cada servidor vive en `servers/<nombre>/` como proyecto independiente y se instala directamente desde este repositorio con `uvx`, sin clonar:

```
uvx --from "git+https://github.com/drobinetm/mcps#subdirectory=servers/<nombre>" <comando>
```

| Servidor | Carpeta | Descripción |
|---|---|---|
| [gaceta-oficial](servers/gaceta-oficial) | `servers/gaceta-oficial` | Busca gacetas y normas de la Gaceta Oficial de Cuba por fecha o por tema |

Requisito: [`uv`](https://docs.astral.sh/uv/). Las instrucciones por agente están en el README de cada servidor.

## Añadir un servidor nuevo
1. Crear `servers/<nombre>/` con su `pyproject.toml` (script de consola propio) y sus tests.
2. Añadir una fila a la tabla de arriba y a la matriz de `.github/workflows/ci.yml`.
3. Documentar el cambio con OpenSpec en `openspec/changes/` (`/opsx:propose`).
