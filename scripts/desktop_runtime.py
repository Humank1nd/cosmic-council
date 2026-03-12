from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = Path(
    os.environ.get(
        "DREAM_CAESAR_RUNTIME_ROOT",
        REPO_ROOT / "docs" / "runtime" / "desktop-council",
    )
).resolve()
ARTIFACT_ROOT = Path(
    os.environ.get(
        "DREAM_CAESAR_ARTIFACT_ROOT",
        RUNTIME_ROOT / "artifacts",
    )
).resolve()
HANDOFF_DIR = Path(
    os.environ.get(
        "DREAM_CAESAR_HANDOFF_DIR",
        RUNTIME_ROOT / "handoffs",
    )
).resolve()
MAIL_ROOT = Path(
    os.environ.get(
        "DREAM_CAESAR_MAIL_ROOT",
        RUNTIME_ROOT / "mail",
    )
).resolve()
ACTIVE_CANON_PATH = Path(
    os.environ.get(
        "DREAM_CAESAR_ACTIVE_CANON_PATH",
        RUNTIME_ROOT / "active-canon.json",
    )
).resolve()
AJNA_DIR = ARTIFACT_ROOT / "ajna"
SEAT_MAP_PATH = ARTIFACT_ROOT / "desktop-fractal-seat-map.json"


def ensure_runtime_dirs() -> None:
    for path in (RUNTIME_ROOT, ARTIFACT_ROOT, HANDOFF_DIR, MAIL_ROOT, AJNA_DIR):
        path.mkdir(parents=True, exist_ok=True)
