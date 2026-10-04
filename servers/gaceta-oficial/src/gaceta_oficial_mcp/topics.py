"""Temas de interés del usuario, persistidos en su directorio de configuración."""

from __future__ import annotations

import json
import os
from pathlib import Path

from platformdirs import user_config_dir

DEFAULT_TOPICS = ["informática", "contrato", "trabajo", "mipymes"]


def topics_path() -> Path:
    override = os.environ.get("GACETA_MCP_CONFIG_DIR")
    base = Path(override) if override else Path(user_config_dir("gaceta-oficial-mcp"))
    return base / "topics.json"


def get_topics() -> dict[str, object]:
    path = topics_path()
    try:
        topics = json.loads(path.read_text(encoding="utf-8"))["topics"]
        if isinstance(topics, list) and topics:
            return {"topics": [str(t) for t in topics], "is_default": False}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return {"topics": list(DEFAULT_TOPICS), "is_default": True}


def set_topics(topics: list[str]) -> dict[str, object]:
    cleaned = [t.strip() for t in topics if t and t.strip()]
    path = topics_path()
    if not cleaned:  # lista vacía = restablecer valores por defecto
        path.unlink(missing_ok=True)
        return get_topics()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"topics": cleaned}, ensure_ascii=False, indent=2), encoding="utf-8")
    return get_topics()
