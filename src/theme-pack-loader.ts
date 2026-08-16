// Runtime consumes canon. Runtime must not recreate canon.

import knowJokeThemePack from "../theme-packs/know-joke.theme.json";
import marvelOmniverseThemePack from "../theme-packs/marvel-omniverse.theme.json";

import { KJU_COMEDY_SPINE, type ComedySeatColor, type ComedySpineLayer } from "./comedy-spine";
import {
  DEFAULT_THEME_PACK_ID,
  PUBLIC_THEME_PACK_ID,
  THEME_PACK_TOTEM_COLORS,
  type LayerThemeOverlay,
  type MascotPersonaOverlay,
  type OpenClownProductOverlay,
  type ThemedSpineLayer,
  type ThemedTotemOverlay,
  type TotemThemeOverlay,
  type UniverseThemePack,
  type UniverseThemePackId,
  type UserPersonaOverlay,
  type DimensionBoundaryOverlay,
  type StructuralSpeciesMap,
} from "./theme-pack-types";
import { ThemePackValidationError, validateThemePack } from "./theme-pack-validation";

const RAW_THEME_PACKS: Record<string, UniverseThemePack> = {
  "know-joke": knowJokeThemePack as UniverseThemePack,
  "marvel-omniverse": marvelOmniverseThemePack as UniverseThemePack,
};

const VALIDATED_THEME_PACKS = new Map<UniverseThemePackId, UniverseThemePack>();

function registerThemePack(pack: UniverseThemePack): UniverseThemePack {
  const validated = validateThemePack(pack);
  VALIDATED_THEME_PACKS.set(validated.meta.id, validated);
  return validated;
}

for (const pack of Object.values(RAW_THEME_PACKS)) {
  registerThemePack(pack);
}

export function listThemePackIds(): UniverseThemePackId[] {
  return [...VALIDATED_THEME_PACKS.keys()];
}

export function getThemePack(id: UniverseThemePackId = DEFAULT_THEME_PACK_ID): UniverseThemePack {
  const pack = VALIDATED_THEME_PACKS.get(id);

  if (!pack) {
    throw new ThemePackValidationError(
      `Unknown theme pack "${id}". Available packs: ${listThemePackIds().join(", ")}`,
    );
  }

  return pack;
}

export function resolveThemePackId(
  explicit?: UniverseThemePackId,
  options?: { publicSurface?: boolean },
): UniverseThemePackId {
  if (options?.publicSurface) {
    return PUBLIC_THEME_PACK_ID;
  }

  if (explicit) {
    return explicit;
  }

  const envPack =
    typeof process !== "undefined"
      ? (process.env.THEME_PACK ??
        process.env.NEXT_PUBLIC_THEME_PACK ??
        process.env.VITE_THEME_PACK)
      : undefined;

  if (envPack && VALIDATED_THEME_PACKS.has(envPack)) {
    return envPack;
  }

  return DEFAULT_THEME_PACK_ID;
}

function getLayerOverlay(
  pack: UniverseThemePack,
  layer: number,
): LayerThemeOverlay | undefined {
  return pack.layers.find((entry) => entry.layer === layer);
}

function resolveArchetypeLabel(
  structural: ComedySpineLayer,
  overlay: LayerThemeOverlay | undefined,
): string {
  const label = overlay?.archetypeLabel?.trim();

  if (!label || label === "TBD") {
    return overlay?.archetypeSubtitle ?? structural.era ?? structural.archetype;
  }

  return label;
}

export function getThemedSpineLayer(
  layer: number,
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): ThemedSpineLayer {
  const pack = getThemePack(packId);
  const structural = KJU_COMEDY_SPINE.find((entry) => entry.layer === layer);

  if (!structural) {
    throw new ThemePackValidationError(
      `Structural comedy spine has no layer ${layer}. Theme packs cannot invent layers.`,
    );
  }

  const overlay = getLayerOverlay(pack, layer);

  return {
    ...structural,
    displayArchetype: resolveArchetypeLabel(structural, overlay),
    displaySubtitle: overlay?.archetypeSubtitle,
    displayMythFrame: overlay?.mythFrame ?? structural.era,
    iconKey: overlay?.icon,
    accentColor: overlay?.accentColor,
    themePackId: pack.meta.id,
  };
}

export function getThemedSpineLayers(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): ThemedSpineLayer[] {
  return KJU_COMEDY_SPINE.map((layer) => getThemedSpineLayer(layer.layer, packId));
}

function getTotemOverlay(
  pack: UniverseThemePack,
  color: ComedySeatColor,
): TotemThemeOverlay | undefined {
  return pack.totems.find((entry) => entry.color === color);
}

function resolveThemeVariant(overlay: TotemThemeOverlay | undefined): string {
  const variant = overlay?.themeVariant?.trim();

  if (!variant || variant === "TBD") {
    return overlay?.optionalAlias ?? "";
  }

  return variant;
}

function resolveVariantEssence(overlay: TotemThemeOverlay | undefined): string {
  const essence = overlay?.variantEssence?.trim();

  if (!essence || essence === "TBD") {
    return "";
  }

  return essence;
}

export function getThemedTotemOverlay(
  color: ComedySeatColor,
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): ThemedTotemOverlay {
  const pack = getThemePack(packId);
  const overlay = getTotemOverlay(pack, color);

  if (!overlay) {
    throw new ThemePackValidationError(
      `Theme pack "${packId}" is missing totem overlay for color ${color}.`,
    );
  }

  return {
    ...overlay,
    displayVariant: resolveThemeVariant(overlay),
    displayEssence: resolveVariantEssence(overlay),
    themePackId: pack.meta.id,
  };
}

export function assertPublicThemePack(packId: UniverseThemePackId): void {
  const pack = getThemePack(packId);

  if (!pack.meta.publicSafe) {
    throw new ThemePackValidationError(
      `Theme pack "${packId}" is not public-safe and cannot be used on student-facing surfaces.`,
    );
  }
}

export function getPublicThemedSpineLayers(): ThemedSpineLayer[] {
  assertPublicThemePack(PUBLIC_THEME_PACK_ID);
  return getThemedSpineLayers(PUBLIC_THEME_PACK_ID);
}

export function getThemedTotemOverlays(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): ThemedTotemOverlay[] {
  return THEME_PACK_TOTEM_COLORS.map((color) => getThemedTotemOverlay(color, packId));
}

export function getMascotPersona(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): MascotPersonaOverlay | undefined {
  return getThemePack(packId).mascotPersona;
}

export function getUserPersona(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): UserPersonaOverlay | undefined {
  return getThemePack(packId).userPersona;
}

export function getDimensionBoundary(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): DimensionBoundaryOverlay | undefined {
  return getThemePack(packId).dimensionBoundary;
}

export function getStructuralSpeciesMap(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): StructuralSpeciesMap | undefined {
  return getThemePack(packId).structuralSpecies;
}

export function getOpenClownProduct(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): OpenClownProductOverlay | undefined {
  return getThemePack(packId).openClownProduct;
}

/** Layer 2 themed label (Thalia on KJU, Uatu the Watcher on Marvel Omniverse). */
export function getMembraneBrandName(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): string {
  const layer = getThemedSpineLayers(packId).find((entry) => entry.layer === 2);
  return layer?.displayArchetype ?? "Dream Caesar";
}

export function getUniverseProductDisplayName(
  packId: UniverseThemePackId = DEFAULT_THEME_PACK_ID,
): string {
  return getThemePack(packId).meta.displayName;
}

export const KJU_THEME_LAYER_NAMES = {
  user: "The User",
  thalia: "Thalia",
  comedicCouncil: "Comedic Council",
} as const;
