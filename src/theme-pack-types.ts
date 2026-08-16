// Runtime consumes canon. Runtime must not recreate canon.

import type { ComedySeatColor, ComedySpineLayer } from "./comedy-spine";

export type UniverseThemePackId = "know-joke" | "marvel-omniverse" | (string & {});

export type UniverseThemePackMeta = {
  id: UniverseThemePackId;
  displayName: string;
  version: string;
  publicSafe: boolean;
  structuralCanonRef: string;
  notes?: string;
};

export type LayerThemeOverlay = {
  layer: number;
  archetypeLabel: string;
  archetypeSubtitle?: string;
  mythFrame?: string;
  icon?: string;
  accentColor?: string;
};

export type TotemThemeOverlay = {
  color: ComedySeatColor;
  themeVariant: string;
  variantEssence: string;
  optionalAlias?: string;
};

export type MascotPersonaOverlay = {
  id: string;
  displayName: string;
  role: string;
  notASpineLayer?: boolean;
  notSynonymousWith?: string[];
};

/** Sovereign human user above the spine stack (Marvel: One Above All). */
export type UserPersonaOverlay = {
  id: string;
  displayName: string;
  role: string;
  aboveSpineLayers?: boolean;
  notSynonymousWith?: string[];
};

export type DimensionBoundaryOverlay = {
  id: string;
  isolatedFrom: UniverseThemePackId[];
  councilLoreDomain: string;
  notes: string;
};

export type StructuralSpeciesOverlay = {
  structuralKey: string;
  shapeshiftLabel: string;
  spineLayer: number;
  notes?: string;
};

export type StructuralSpeciesMap = {
  dreamCaesar: StructuralSpeciesOverlay;
  cosmicCouncil: StructuralSpeciesOverlay;
};

export type OpenClownProductOverlay = {
  id: string;
  displayName: string;
  role: string;
  structuralRuntimeKey?: string;
  studentFacingOnly?: boolean;
  notSynonymousWith?: string[];
};

export type UniverseThemePack = {
  meta: UniverseThemePackMeta;
  dimensionBoundary?: DimensionBoundaryOverlay;
  structuralSpecies?: StructuralSpeciesMap;
  userPersona?: UserPersonaOverlay;
  mascotPersona?: MascotPersonaOverlay;
  openClownProduct?: OpenClownProductOverlay;
  layers: LayerThemeOverlay[];
  totems: TotemThemeOverlay[];
};

export type ThemedSpineLayer = ComedySpineLayer & {
  displayArchetype: string;
  displaySubtitle?: string;
  displayMythFrame?: string;
  iconKey?: string;
  accentColor?: string;
  themePackId: UniverseThemePackId;
};

export type ThemedTotemOverlay = TotemThemeOverlay & {
  displayVariant: string;
  displayEssence: string;
  themePackId: UniverseThemePackId;
};

export const THEME_PACK_LAYER_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] as const;

export const THEME_PACK_TOTEM_COLORS: ComedySeatColor[] = [
  "red",
  "orange",
  "yellow",
  "green",
  "blue",
  "purple",
];

export const DEFAULT_THEME_PACK_ID: UniverseThemePackId = "know-joke";

export const PUBLIC_THEME_PACK_ID: UniverseThemePackId = "know-joke";
