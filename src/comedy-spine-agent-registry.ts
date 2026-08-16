// Runtime consumes canon. Runtime must not recreate canon.

import {
  KJU_COMEDY_SPINE,
  type ComedySeatColor,
  type ComedySpineLayer,
} from "./comedy-spine";

export type ComedySpineAgentResponsibility = {
  layer: number;
  color: ComedySeatColor;
  agentName: string;
  responsibility: string;
};

export type ComedySpineAgentRegistryEntry = {
  layer: ComedySpineLayer;
  agents: ComedySpineAgentResponsibility[];
};

export const KJU_COMEDY_SPINE_AGENT_REGISTRY: ComedySpineAgentRegistryEntry[] =
  KJU_COMEDY_SPINE.map((layer) => ({
    layer,
    agents: layer.seats.map((seat) => ({
      layer: layer.layer,
      color: seat.color,
      agentName: seat.anchor,
      responsibility: seat.function,
    })),
  }));

export function getComedySpineAgentsForLayer(
  layerNumber: number,
): ComedySpineAgentRegistryEntry | undefined {
  return KJU_COMEDY_SPINE_AGENT_REGISTRY.find(
    (entry) => entry.layer.layer === layerNumber,
  );
}

export function getComedySpineAgent(
  layerNumber: number,
  color: ComedySeatColor,
): ComedySpineAgentResponsibility | undefined {
  return getComedySpineAgentsForLayer(layerNumber)?.agents.find(
    (agent) => agent.color === color,
  );
}
