// Runtime consumes canon. Runtime must not recreate canon.

import knowJokeLineagePack from "../theme-packs/know-joke.lineage.json";
import {
  LINEAGE_LAYER_NUMBERS,
  type LineageLayerEntry,
  type LineageThemePack,
} from "./lineage-theme-types";
import { ThemePackValidationError } from "./theme-pack-validation";

const RAW_LINEAGE_PACKS: Record<string, LineageThemePack> = {
  "know-joke-lineage": knowJokeLineagePack as LineageThemePack,
};

const VALIDATED_LINEAGE_PACKS = new Map<string, LineageThemePack>();

function validateLineagePack(pack: LineageThemePack): LineageThemePack {
  if (!pack.meta?.id) {
    throw new ThemePackValidationError("Lineage pack meta.id is required.");
  }

  const seen = new Set<number>();
  for (const layer of pack.layers) {
    if (!LINEAGE_LAYER_NUMBERS.includes(layer.lineageLayer as (typeof LINEAGE_LAYER_NUMBERS)[number])) {
      throw new ThemePackValidationError(
        `Lineage layer ${layer.lineageLayer} is outside range 1–10.`,
      );
    }
    if (seen.has(layer.lineageLayer)) {
      throw new ThemePackValidationError(
        `Duplicate lineage layer ${layer.lineageLayer}.`,
      );
    }
    seen.add(layer.lineageLayer);
  }

  for (const layer of LINEAGE_LAYER_NUMBERS) {
    if (!seen.has(layer)) {
      throw new ThemePackValidationError(`Lineage pack missing layer ${layer}.`);
    }
  }

  return pack;
}

for (const pack of Object.values(RAW_LINEAGE_PACKS)) {
  const validated = validateLineagePack(pack);
  VALIDATED_LINEAGE_PACKS.set(validated.meta.id, validated);
}

export function getLineageThemePack(id = "know-joke-lineage"): LineageThemePack {
  const pack = VALIDATED_LINEAGE_PACKS.get(id);
  if (!pack) {
    throw new ThemePackValidationError(`Unknown lineage pack "${id}".`);
  }
  return pack;
}

export function getLineageLayers(id = "know-joke-lineage"): LineageLayerEntry[] {
  return [...getLineageThemePack(id).layers].sort(
    (a, b) => a.lineageLayer - b.lineageLayer,
  );
}

export function getLineageLayerEntry(
  lineageLayer: number,
  id = "know-joke-lineage",
): LineageLayerEntry {
  const entry = getLineageLayers(id).find((layer) => layer.lineageLayer === lineageLayer);
  if (!entry) {
    throw new ThemePackValidationError(
      `Lineage pack "${id}" has no entry for lineage layer ${lineageLayer}.`,
    );
  }
  return entry;
}

export function getLineageLayerName(
  lineageLayer: number,
  id = "know-joke-lineage",
): string {
  return getLineageLayerEntry(lineageLayer, id).lineageName;
}

export function getLineageLayersForPyramid(id = "know-joke-lineage") {
  return getLineageLayers(id).map((entry) => ({
    layer: entry.lineageLayer,
    name: entry.lineageName,
    subtitle: entry.subtitle,
    tier: entry.primaryTrackTier,
    distributed: entry.distributed,
    curriculumTier: entry.curriculumTier,
    distributedAcrossTiers: entry.distributedAcrossTiers,
  }));
}

/** Academy track tier (1–8) → curriculum tier (100–800). */
export function curriculumTierFromTrackTier(trackTier: number): number {
  return trackTier * 100;
}

export function getDistributedLineageLayersForCurriculumTier(
  curriculumTier: number,
  id = "know-joke-lineage",
): LineageLayerEntry[] {
  return getLineageLayers(id).filter(
    (entry) =>
      entry.distributed &&
      (entry.distributedAcrossTiers ?? []).includes(curriculumTier),
  );
}

export function getLineageForTrackTier(
  trackTier: number,
  id = "know-joke-lineage",
): {
  lineageLayer: number;
  lineageName: string;
  distributedLineageLayers: number[];
  distributedLineageNames: string[];
} {
  const curriculumTier = curriculumTierFromTrackTier(trackTier);
  const layers = getLineageLayers(id);
  const primary =
    layers.find((entry) => entry.curriculumTier === curriculumTier) ??
    layers.find((entry) => entry.primaryTrackTier === trackTier && !entry.distributed);

  const distributed = getDistributedLineageLayersForCurriculumTier(curriculumTier, id);

  if (!primary) {
    return {
      lineageLayer: distributed[0]?.lineageLayer ?? 10,
      lineageName: distributed[0]?.lineageName ?? "Comedy Lineage",
      distributedLineageLayers: distributed.map((entry) => entry.lineageLayer),
      distributedLineageNames: distributed.map((entry) => entry.lineageName),
    };
  }

  return {
    lineageLayer: primary.lineageLayer,
    lineageName: primary.lineageName,
    distributedLineageLayers: distributed.map((entry) => entry.lineageLayer),
    distributedLineageNames: distributed.map((entry) => entry.lineageName),
  };
}
