"""
storage.py - tiny JSON persistence for research history / saved projects.

Set RESEARCHMATE_PERSIST=0 (env var or Streamlit secret) to keep everything in memory only.
Use that on a shared deployment (e.g. Streamlit Community Cloud) so users never see each other's data.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "history.json"


def persistence_enabled() -> bool:
    return os.getenv("RESEARCHMATE_PERSIST", "1").strip().lower() not in ("0", "false", "no", "off")


def load() -> list[dict]:
    if not persistence_enabled() or not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save(entries: list[dict]) -> None:
    if not persistence_enabled():
        return
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass  # read-only filesystem: keep working in memory
