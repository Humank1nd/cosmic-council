from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "data"
LOG_ROOT = REPO_ROOT / "logs"
RUNTIME_ROOT = REPO_ROOT / "docs" / "runtime"
RECOVERY_ROOT = REPO_ROOT / "recovery"

DREAM_CAESAR_DB = DATA_ROOT / "dream_caesar.db"
PERPETUAL_DB = DATA_ROOT / "perpetual_thinking.db"
STRATEGY_DB = DATA_ROOT / "strategy_store.db"
MEMORY_GRAPH_DB = DATA_ROOT / "memory_graph.db"
COSMIC_MEMORY_DB = DATA_ROOT / "cosmic_memory.db"
API_LOG_FILE = LOG_ROOT / "dream_caesar.log"


def ensure_local_storage_roots() -> None:
    for path in (DATA_ROOT, LOG_ROOT, RUNTIME_ROOT, RECOVERY_ROOT):
        path.mkdir(parents=True, exist_ok=True)
