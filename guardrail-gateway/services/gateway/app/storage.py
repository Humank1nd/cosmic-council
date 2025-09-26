from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .settings import settings

_engine: Engine | None = None

def engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(settings.POSTGRES_DSN, pool_pre_ping=True)
    return _engine

def log_decision(payload: dict):
    e = engine()
    with e.begin() as cx:
        cx.execute(text(
            """
            INSERT INTO decisions(decision_id, agent_id, request, allow, policy_refs, explanation, latency_ms)
            VALUES (gen_random_uuid(), :agent_id, :request::jsonb, :allow, :policy_refs, :explanation::jsonb, :latency_ms)
            """
        ), {
            "agent_id": payload.get("agent", {}).get("id"),
            "request": payload.get("request_json", {}),
            "allow": payload.get("allow", False),
            "policy_refs": payload.get("policy_refs", []),
            "explanation": payload.get("explanation", {}),
            "latency_ms": payload.get("latency_ms", 0),
        })
