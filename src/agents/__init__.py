"""Compatibility shim for agent imports."""
from pkgutil import extend_path
from pathlib import Path

# Allow src.agents.* imports to resolve to src_new/agents modules.
__path__ = extend_path(__path__, __name__)
_src_new_agents = Path(__file__).resolve().parents[1] / "src_new" / "agents"
if _src_new_agents.exists():
    __path__.append(str(_src_new_agents))
