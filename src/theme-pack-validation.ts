// Runtime consumes canon. Runtime must not recreate canon.

import {
  THEME_PACK_LAYER_NUMBERS,
  THEME_PACK_TOTEM_COLORS,
  type LayerThemeOverlay,
  type TotemThemeOverlay,
  type UniverseThemePack,
} from "./theme-pack-types";

const LAYER_SET = new Set<number>(THEME_PACK_LAYER_NUMBERS);

export class ThemePackValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ThemePackValidationError";
  }
}

function assertLayerCoverage(layers: LayerThemeOverlay[]): void {
  const seen = new Set<number>();

  for (const overlay of layers) {
    if (!LAYER_SET.has(overlay.layer)) {
      throw new ThemePackValidationError(
        `Theme pack layer ${overlay.layer} is outside the structural range 1–10.`,
      );
    }

    if (seen.has(overlay.layer)) {
      throw new ThemePackValidationError(
        `Theme pack defines duplicate layer overlay for layer ${overlay.layer}.`,
      );
    }

    seen.add(overlay.layer);
  }

  for (const layer of THEME_PACK_LAYER_NUMBERS) {
    if (!seen.has(layer)) {
      throw new ThemePackValidationError(
        `Theme pack is missing required layer overlay for layer ${layer}.`,
      );
    }
  }
}

function assertTotemCoverage(totems: TotemThemeOverlay[]): void {
  const seen = new Set<string>();

  for (const overlay of totems) {
    if (seen.has(overlay.color)) {
      throw new ThemePackValidationError(
        `Theme pack defines duplicate totem overlay for color ${overlay.color}.`,
      );
    }

    seen.add(overlay.color);
  }

  for (const color of THEME_PACK_TOTEM_COLORS) {
    if (!seen.has(color)) {
      throw new ThemePackValidationError(
        `Theme pack is missing required totem overlay for color ${color}.`,
      );
    }
  }
}

export function validateThemePack(pack: UniverseThemePack): UniverseThemePack {
  if (!pack.meta?.id) {
    throw new ThemePackValidationError("Theme pack meta.id is required.");
  }

  if (!pack.meta.displayName) {
    throw new ThemePackValidationError("Theme pack meta.displayName is required.");
  }

  if (!/^\d+\.\d+\.\d+$/.test(pack.meta.version)) {
    throw new ThemePackValidationError(
      `Theme pack meta.version must be semver. Received "${pack.meta.version}".`,
    );
  }

  assertLayerCoverage(pack.layers);
  assertTotemCoverage(pack.totems);

  return pack;
}
