// Runtime consumes canon. Runtime must not recreate canon.

import {
  KJU_COMEDY_SPINE,
  type ComedySpineLayer,
} from "./comedy-spine";
import {
  getComedySpineLayerRole,
  type ComedySpineLayerRole,
} from "./comedy-spine-layer-roles";
import { getLineageForTrackTier } from "./lineage-theme-loader";

export type ComedySpineCurriculumLevel = {
  level: number;
  layerNumber: number;
  layer: ComedySpineLayer;
  layerRole: ComedySpineLayerRole;
  studentSkill: string;
  /** Lineage pyramid layer from know-joke.lineage.json (separate numbering from system spine) */
  lineageLayerNumber: number;
  lineageName: string;
  distributedLineageLayers: number[];
};

type ComedySpineCurriculumDefinition = {
  level: number;
  layer: number;
  studentSkill: string;
};

const CURRICULUM_BY_LEVEL: ComedySpineCurriculumDefinition[] = [
  {
    level: 1,
    layer: 10,
    studentSkill: "Recognize joke signals, memes, ratios, avatars, screenshots.",
  },
  {
    level: 2,
    layer: 9,
    studentSkill: "Build observational and confessional material.",
  },
  {
    level: 3,
    layer: 8,
    studentSkill: "Use taboo, truth, critique, and consequence responsibly.",
  },
  {
    level: 4,
    layer: 7,
    studentSkill: "Write character, episode rhythm, and family/social tension.",
  },
  {
    level: 5,
    layer: 6,
    studentSkill: "Develop timing, persona, repetition, and live performance discipline.",
  },
  {
    level: 6,
    layer: 5,
    studentSkill: "Use satire as civic critique and symbolic force.",
  },
  {
    level: 7,
    layer: 4,
    studentSkill: "Study ancient/oral humor and archetypal joke functions.",
  },
  {
    level: 8,
    layer: 3,
    studentSkill: "Apply the six-seat reasoning model to advanced joke-craft.",
  },
];

export const KJU_COMEDY_SPINE_CURRICULUM: ComedySpineCurriculumLevel[] =
  CURRICULUM_BY_LEVEL.map((definition) => {
    const lineage = getLineageForTrackTier(definition.level);
    return {
      level: definition.level,
      layerNumber: definition.layer,
      get layer() {
        return getRequiredComedySpineLayer(definition);
      },
      get layerRole() {
        return getComedySpineLayerRole(definition.layer);
      },
      studentSkill: definition.studentSkill,
      lineageLayerNumber: lineage.lineageLayer,
      lineageName: lineage.lineageName,
      distributedLineageLayers: lineage.distributedLineageLayers,
    };
  });

export function getComedySpineCurriculumLevel(level: number): ComedySpineCurriculumLevel {
  const curriculumLevel = KJU_COMEDY_SPINE_CURRICULUM.find((entry) => entry.level === level);

  if (!curriculumLevel) {
    throw new Error(`Cannot resolve KJU Comedy Spine curriculum level ${level}.`);
  }

  return curriculumLevel;
}

export function getResolvedComedySpineCurriculum(): ComedySpineCurriculumLevel[] {
  return KJU_COMEDY_SPINE_CURRICULUM.map((level) => {
    level.layer;
    level.layerRole;

    return level;
  });
}

function getRequiredComedySpineLayer(
  definition: ComedySpineCurriculumDefinition,
): ComedySpineLayer {
  const layer = KJU_COMEDY_SPINE.find((entry) => entry.layer === definition.layer);

  if (!layer) {
    throw new Error(
      `KJU Comedy Spine curriculum level ${definition.level} references missing canon layer ${definition.layer}.`,
    );
  }

  return layer;
}
