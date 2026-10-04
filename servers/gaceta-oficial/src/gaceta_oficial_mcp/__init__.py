"""Servidor MCP para consultar la Gaceta Oficial de Cuba."""

__version__ = "0.1.0"


def main() -> None:
    from .server import main as _main

    _main()
