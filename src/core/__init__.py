"""Compatibility shims for legacy `src.core.*` imports."""
from pkgutil import extend_path
from pathlib import Path

# Allow src.core.* imports to resolve to src_new/core modules
__path__ = extend_path(__path__, __name__)
_src_new_core = Path(__file__).resolve().parents[1] / "src_new" / "core"
if _src_new_core.exists():
    __path__.append(str(_src_new_core))

from .types import *  # re-export common types

__all__ = [name for name in globals() if not name.startswith("_")]

