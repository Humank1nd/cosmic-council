"""
Legacy perpetual database service compatibility shim for tests.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any, Dict, List


_STATE: Dict[str, Dict[str, Any]] = defaultdict(
    lambda: {"sessions": {}, "cycles": defaultdict(list), "metrics": {}}
)


class PerpetualDatabaseService:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._bucket = _STATE[database_url]

    async def create_tables(self) -> None:
        return None

    async def save_session(self, session: Dict[str, Any]) -> None:
        session_id = str(session["session_id"])
        self._bucket["sessions"][session_id] = deepcopy(session)

    async def save_cycle(self, session_id: str, cycle: Dict[str, Any]) -> None:
        self._bucket["cycles"][session_id].append(deepcopy(cycle))

    async def save_metrics(self, session_id: str, metrics: Dict[str, Any]) -> None:
        self._bucket["metrics"][session_id] = deepcopy(metrics)

    async def get_session(self, session_id: str):
        value = self._bucket["sessions"].get(session_id)
        return deepcopy(value) if value is not None else None

    async def get_session_cycles(self, session_id: str):
        return deepcopy(self._bucket["cycles"].get(session_id, []))

    async def get_session_metrics(self, session_id: str):
        value = self._bucket["metrics"].get(session_id)
        return deepcopy(value) if value is not None else None

    async def get_all_sessions(self):
        return [deepcopy(v) for v in self._bucket["sessions"].values()]
