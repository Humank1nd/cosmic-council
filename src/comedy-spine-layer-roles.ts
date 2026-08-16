// Runtime consumes canon. Runtime must not recreate canon.

import { KJU_COMEDY_SPINE } from "./comedy-spine";

export type ComedySpineLayerRole = {
  layer: number;
  agentName: string;
  responsibility: string;
};

const LAYER_ROLE_BY_LAYER = new Map<number, Omit<ComedySpineLayerRole, "layer">>([
  [
    10,
    {
      agentName: "Signal Scout",
      responsibility: "Detect raw joke signals: memes, ratios, avatars, screenshots.",
    },
  ],
  [
    9,
    {
      agentName: "Street Editor",
      responsibility: "Shape observational/confessional material from modern contradictions.",
    },
  ],
  [
    8,
    {
      agentName: "Consequence Critic",
      responsibility: "Test taboo, truth, critique, and ethical risk.",
    },
  ],
  [
    7,
    {
      agentName: "Format Writer",
      responsibility: "Build character, episode rhythm, family/social tension.",
    },
  ],
  [
    6,
    {
      agentName: "Stage Mechanic",
      responsibility: "Refine timing, persona, repetition, room-read, performance discipline.",
    },
  ],
  [
    5,
    {
      agentName: "Civic Satirist",
      responsibility: "Turn critique into symbolic, civic, and political comedy.",
    },
  ],
  [
    4,
    {
      agentName: "Archetype Keeper",
      responsibility: "Preserve ancient/oral humor patterns and primal joke functions.",
    },
  ],
  [
    3,
    {
      agentName: "Comedic Council",
      responsibility: "Apply six-seat reasoning to advanced joke-craft and system decisions.",
    },
  ],
  [
    2,
    {
      agentName: "Thalia",
      responsibility:
        "Highest frontier reasoning model — crystallize logic into dream, orchestrate sessions, delegate to the Council ring below.",
    },
  ],
  [
    1,
    {
      agentName: "Primary Observer",
      responsibility: "Observe, judge, and direct initial intent. The ultimate source of feedback.",
    },
  ],
]);

export const KJU_COMEDY_SPINE_LAYER_ROLES: ComedySpineLayerRole[] =
  KJU_COMEDY_SPINE.map((spineLayer) => {
    const role = LAYER_ROLE_BY_LAYER.get(spineLayer.layer);

    if (!role) {
      throw new Error(`KJU Comedy Spine layer ${spineLayer.layer} is missing a layer role.`);
    }

    return {
      layer: spineLayer.layer,
      ...role,
    };
  });

export function getComedySpineLayerRole(layer: number): ComedySpineLayerRole {
  const role = KJU_COMEDY_SPINE_LAYER_ROLES.find((entry) => entry.layer === layer);

  if (!role) {
    throw new Error(`Cannot resolve layer role for KJU Comedy Spine layer ${layer}.`);
  }

  return role;
}
