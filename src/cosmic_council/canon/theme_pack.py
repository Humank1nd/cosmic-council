"""
Load universe theme packs for Cosmic Council runtime display (Dream Caesar).

Theme JSON lives in @know-joke-u/council-core — resolved from node_modules or know-joke-u path.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_THEME_PACK_ID = "marvel-omniverse"
PUBLIC_THEME_PACK_ID = "know-joke"
DEFAULT_LINEAGE_PACK_ID = "know-joke-lineage"


def _resolve_theme_pack_dir() -> Path:
    env_dir = os.environ.get("COUNCIL_CORE_THEME_PACK_DIR")
    if env_dir:
        return Path(env_dir)

    repo_root = Path(__file__).resolve().parents[3]
    candidates = [
        repo_root / "frontend" / "node_modules" / "@know-joke-u" / "council-core" / "theme-packs",
        repo_root / "vendor" / "know-joke-u" / "packages" / "council-core" / "theme-packs",
    ]
    for candidate in candidates:
        if (candidate / "marvel-omniverse.theme.json").is_file():
            return candidate
    return candidates[0]


THEME_PACK_DIR = _resolve_theme_pack_dir()


@dataclass(frozen=True)
class TotemThemeOverlay:
    color: str
    theme_variant: str
    variant_essence: str
    optional_alias: str = ""


def _resolve_display_variant(overlay: TotemThemeOverlay) -> str:
    variant = (overlay.theme_variant or "").strip()
    if not variant or variant == "TBD":
        return overlay.optional_alias
    return variant


def _resolve_display_essence(overlay: TotemThemeOverlay) -> str:
    essence = (overlay.variant_essence or "").strip()
    if essence == "TBD":
        return ""
    return essence


@lru_cache(maxsize=8)
def load_theme_pack(pack_id: str = DEFAULT_THEME_PACK_ID) -> Dict[str, Any]:
    path = THEME_PACK_DIR / f"{pack_id}.theme.json"
    if not path.is_file():
        raise FileNotFoundError(f"Theme pack not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_totem_theme_overlay(
    color: str,
    pack_id: str = DEFAULT_THEME_PACK_ID,
) -> TotemThemeOverlay:
    pack = load_theme_pack(pack_id)
    for entry in pack.get("totems", []):
        if entry.get("color") == color:
            return TotemThemeOverlay(
                color=color,
                theme_variant=entry.get("themeVariant", ""),
                variant_essence=entry.get("variantEssence", ""),
                optional_alias=entry.get("optionalAlias", ""),
            )
    raise KeyError(f"Theme pack '{pack_id}' has no totem overlay for color '{color}'")


def get_themed_totem_display(
    color: str,
    pack_id: str = DEFAULT_THEME_PACK_ID,
) -> Dict[str, str]:
    overlay = get_totem_theme_overlay(color, pack_id)
    return {
        "theme_variant": _resolve_display_variant(overlay),
        "variant_essence": _resolve_display_essence(overlay),
        "theme_pack_id": pack_id,
    }


def get_layer_archetype_label(
    layer: int,
    pack_id: str = DEFAULT_THEME_PACK_ID,
    *,
    structural_archetype: Optional[str] = None,
    structural_era: Optional[str] = None,
) -> str:
    pack = load_theme_pack(pack_id)
    overlay = next((entry for entry in pack.get("layers", []) if entry.get("layer") == layer), None)
    if overlay is None:
        raise KeyError(f"Theme pack '{pack_id}' has no layer overlay for layer {layer}")

    label = (overlay.get("archetypeLabel") or "").strip()
    if not label or label == "TBD":
        subtitle = (overlay.get("archetypeSubtitle") or "").strip()
        if subtitle:
            return subtitle
        if structural_era:
            return structural_era
        if structural_archetype:
            return structural_archetype
        return f"Layer {layer}"
    return label


def resolve_theme_pack_id(explicit: Optional[str] = None, *, public_surface: bool = False) -> str:
    if public_surface:
        return PUBLIC_THEME_PACK_ID
    if explicit:
        return explicit
    env_pack = os.environ.get("THEME_PACK") or os.environ.get("NEXT_PUBLIC_THEME_PACK")
    if env_pack:
        return env_pack
    return DEFAULT_THEME_PACK_ID


def get_council_brand_name(pack_id: Optional[str] = None) -> str:
    resolved = pack_id or resolve_theme_pack_id()
    return get_layer_archetype_label(3, resolved, structural_archetype="Cosmic Council")


def get_themed_totem_prompt_line(color: str, pack_id: Optional[str] = None) -> str:
    resolved = pack_id or resolve_theme_pack_id()
    display = get_themed_totem_display(color, resolved)
    variant = display.get("theme_variant", "").strip()
    essence = display.get("variant_essence", "").strip()
    if variant and essence:
        return f"Theme persona: {variant} — {essence}"
    if variant:
        return f"Theme persona: {variant}"
    return ""
