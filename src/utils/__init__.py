"""Compatibility shim for utils imports."""
from pkgutil import extend_path
from pathlib import Path

# Allow src.utils.* imports to resolve to src_new/utils modules.
__path__ = extend_path(__path__, __name__)
_src_new_utils = Path(__file__).resolve().parents[1] / "src_new" / "utils"
if _src_new_utils.exists():
    __path__.append(str(_src_new_utils))
