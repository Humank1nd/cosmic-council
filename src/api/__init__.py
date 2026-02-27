"""
Legacy API package compatibility shim.
"""

from pathlib import Path
from pkgutil import extend_path

# Allow `src.api.*` imports to resolve to recovered `src_new/api` modules.
__path__ = extend_path(__path__, __name__)
_src_new_api = Path(__file__).resolve().parents[1] / "src_new" / "api"
if _src_new_api.exists():
    __path__.append(str(_src_new_api))

from .main import app

__all__ = ["app"]
