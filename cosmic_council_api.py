"""
Legacy top-level API import compatibility shim.

Some legacy tests patch `cosmic_council_api.*`. This shim mirrors those writes
to the current `src.cosmic_council.core.api` globals used by route handlers.
"""

from __future__ import annotations

import sys
import types

from src.cosmic_council.core import api as _core_api

app = _core_api.app
perpetual_ai_engine = _core_api.perpetual_ai_engine
perpetual_db_service = _core_api.perpetual_db_service
PERPETUAL_SYSTEM_AVAILABLE = _core_api.PERPETUAL_SYSTEM_AVAILABLE


class _MirrorModule(types.ModuleType):
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in {"perpetual_ai_engine", "perpetual_db_service", "PERPETUAL_SYSTEM_AVAILABLE"}:
            setattr(_core_api, name, value)


sys.modules[__name__].__class__ = _MirrorModule

__all__ = ["app", "perpetual_ai_engine", "perpetual_db_service", "PERPETUAL_SYSTEM_AVAILABLE"]
