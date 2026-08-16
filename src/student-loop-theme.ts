// Runtime consumes canon. Runtime must not recreate canon.

import type { ComedySeatColor } from "./comedy-spine";
import { getLineageForTrackTier } from "./lineage-theme-loader";
import {
  getMascotPersona,
  getPublicThemedSpineLayers,
  getThemedTotemOverlays,
  KJU_THEME_LAYER_NAMES,
} from "./theme-pack-loader";
import type { MascotPersonaOverlay, ThemedTotemOverlay } from "./theme-pack-types";

export { getMascotPersona, KJU_THEME_LAYER_NAMES };

/** First student loop pilot — curriculum tier 100 / lineage layer 10 (Population). */
export const FIRST_STUDENT_LOOP_PILOT = {
  trackId: "foundations-of-comedy",
  trackTier: 1,
  curriculumTier: 100,
  lessonId: "pilot-l10-signal-recognition",
  title: "Spot the Signal",
  lineageLayer: 10,
  lineageName: "Everyone's a Comedian",
  learningObjective:
    "Recognize a joke signal in everyday feed culture — memes, ratios, screenshots — before climbing toward deeper craft.",
  pilotCopy:
    "Start where comedy lives today: the feed. Your first task is to notice one real signal, name the contradiction, and turn it into a bit.",
} as const;

export type StudentLoopTotemStep = {
  color: ComedySeatColor;
  clownsLabel: string;
  essence: string;
  optionalAlias: string;
};

export type ComedicCognitionStepKey =
  | "learn"
  | "contradiction"
  | "write"
  | "explain"
  | "revise"
  | "save";

/** Maps Comedic Cognition ritual steps → C.L.O.W.N.S. totems (theme pack order). */
export const COMEDIC_COGNITION_CLOWS_MAP: ReadonlyArray<{
  stepKey: ComedicCognitionStepKey;
  color: ComedySeatColor;
}> = [
  { stepKey: "learn", color: "red" },
  { stepKey: "contradiction", color: "orange" },
  { stepKey: "write", color: "yellow" },
  { stepKey: "explain", color: "purple" },
  { stepKey: "revise", color: "green" },
  { stepKey: "save", color: "blue" },
];

export function getFirstStudentLoopPilotLineage() {
  return getLineageForTrackTier(FIRST_STUDENT_LOOP_PILOT.trackTier);
}

export function getStudentLoopTotemSteps(): StudentLoopTotemStep[] {
  return getThemedTotemOverlays("know-joke").map((totem) => ({
    color: totem.color,
    clownsLabel: totem.displayVariant,
    essence: totem.displayEssence,
    optionalAlias: totem.optionalAlias ?? "",
  }));
}

export function getComedicCognitionClownsSteps(): Array<
  StudentLoopTotemStep & { stepKey: ComedicCognitionStepKey }
> {
  const byColor = new Map<ComedySeatColor, ThemedTotemOverlay>(
    getThemedTotemOverlays("know-joke").map((totem) => [totem.color, totem]),
  );

  return COMEDIC_COGNITION_CLOWS_MAP.map(({ stepKey, color }) => {
    const totem = byColor.get(color);
    if (!totem) {
      throw new Error(`Missing totem overlay for color "${color}".`);
    }
    return {
      stepKey,
      color,
      clownsLabel: totem.displayVariant,
      essence: totem.displayEssence,
      optionalAlias: totem.optionalAlias ?? "",
    };
  });
}

export function getStudentLoopReasoningStack(): {
  user: string;
  thalia: string;
  comedicCouncil: string;
  population: string;
  mascot: MascotPersonaOverlay | undefined;
} {
  const layers = getPublicThemedSpineLayers();
  const layer10 = layers.find((layer) => layer.layer === 10);
  const mascot = getMascotPersona("know-joke");

  return {
    user: KJU_THEME_LAYER_NAMES.user,
    thalia: KJU_THEME_LAYER_NAMES.thalia,
    comedicCouncil: KJU_THEME_LAYER_NAMES.comedicCouncil,
    population: layer10?.displayArchetype ?? "The Population",
    mascot,
  };
}
