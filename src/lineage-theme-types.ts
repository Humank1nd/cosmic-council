// Runtime consumes canon. Runtime must not recreate canon.

export type LineageThemePackMeta = {
  id: string;
  displayName: string;
  version: string;
  publicSafe: boolean;
  sourceRef?: string;
  notes?: string;
};

export type LineageLayerEntry = {
  lineageLayer: number;
  lineageName: string;
  subtitle?: string;
  description?: string;
  curriculumTier: number | null;
  primaryTrackTier: number;
  distributed: boolean;
  distributedAcrossTiers?: number[];
};

export type LineageThemePack = {
  meta: LineageThemePackMeta;
  layers: LineageLayerEntry[];
};

export const LINEAGE_LAYER_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] as const;

export const DEFAULT_LINEAGE_PACK_ID = "know-joke-lineage";
