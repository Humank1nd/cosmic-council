"""
Legacy API module path compatibility shim.

Historically tests imported `src.api.main:app`; current implementation lives in
`src.cosmic_council.core.api`.
"""

from cosmic_council_api import app
from src.cosmic_council.core import api as _core_api

# Test fixtures often construct TestClient without entering lifespan context.
# Ensure perpetual handles are available for those legacy tests.
if _core_api.PERPETUAL_SYSTEM_AVAILABLE and _core_api.perpetual_ai_engine is None:
    from perpetual_ai_integration import PerpetualAIThinkingEngine

    _core_api.perpetual_ai_engine = PerpetualAIThinkingEngine()

if _core_api.PERPETUAL_SYSTEM_AVAILABLE and _core_api.perpetual_db_service is None:
    from perpetual_database_service import PerpetualDatabaseService

    _core_api.perpetual_db_service = PerpetualDatabaseService("sqlite:///:memory:")


class _CompatOrchestrationSystem:
    def __init__(self):
        self.orchestration_sessions = {}
        self.session_history = []

    def get_orchestration_session_status(self, _session_id: str):
        return None

    async def pause_orchestration_session(self, _session_id: str):
        return None

    async def resume_orchestration_session(self, _session_id: str):
        return None

    async def stop_orchestration_session(self, _session_id: str):
        return None


class _CompatPerpetualEngine:
    class _Session:
        breakthrough_moments = []

    def get_session_status(self, _session_id: str):
        return self._Session()


if _core_api.PERPETUAL_SYSTEM_AVAILABLE and _core_api.orchestration_system is None:
    _core_api.orchestration_system = _CompatOrchestrationSystem()

if _core_api.PERPETUAL_SYSTEM_AVAILABLE and _core_api.perpetual_engine is None:
    _core_api.perpetual_engine = _CompatPerpetualEngine()

if _core_api.workflow_engine is None:
    _core_api.workflow_engine = object()

if _core_api.ai_integration is None:
    _core_api.ai_integration = object()


def _has_get_route(path: str) -> bool:
    for route in app.router.routes:
        if getattr(route, "path", None) == path and "GET" in getattr(route, "methods", set()):
            return True
    return False


if not _has_get_route("/api/web/perpetual/sessions"):
    @app.get("/api/web/perpetual/sessions", response_model=_core_api.ResponseModel)
    async def web_list_perpetual_sessions():
        sessions = []
        if _core_api.perpetual_db_service and hasattr(_core_api.perpetual_db_service, "get_all_sessions"):
            sessions = await _core_api._maybe_await(_core_api.perpetual_db_service.get_all_sessions())
        return _core_api.ResponseModel(
            success=True,
            message="Web perpetual sessions retrieved successfully",
            data={"sessions": sessions or []},
        )


if not _has_get_route("/api/web/perpetual/status"):
    @app.get("/api/web/perpetual/status", response_model=_core_api.ResponseModel)
    async def web_get_perpetual_status():
        active_ai_sessions = _core_api._safe_len(
            getattr(_core_api.perpetual_ai_engine, "ai_sessions", {})
        ) if _core_api.perpetual_ai_engine else 0
        return _core_api.ResponseModel(
            success=True,
            message="Web perpetual status retrieved successfully",
            data={
                "active_ai_sessions": active_ai_sessions,
                "perpetual_ai_engine_available": _core_api.perpetual_ai_engine is not None,
            },
        )


if not _has_get_route("/api/web/perpetual/ai/sessions"):
    @app.get("/api/web/perpetual/ai/sessions", response_model=_core_api.ResponseModel)
    async def web_list_ai_sessions():
        sessions = []
        if _core_api.perpetual_ai_engine:
            for session in getattr(_core_api.perpetual_ai_engine, "ai_sessions", {}).values():
                level = _core_api._get_session_value(session, "ai_enhancement_level")
                sessions.append(
                    {
                        "session_id": _core_api._get_session_value(session, "session_id"),
                        "session_name": _core_api._get_session_value(session, "session_name"),
                        "status": _core_api._get_session_value(session, "status"),
                        "ai_enhancement_level": level.value if hasattr(level, "value") else level,
                    }
                )
        return _core_api.ResponseModel(
            success=True,
            message="Web AI sessions retrieved successfully",
            data={"sessions": sessions},
        )

__all__ = ["app"]
