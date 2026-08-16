// Runtime consumes canon. Runtime must not recreate canon.

import { KJU_COMEDY_SPINE, type ComedySpineLayer } from "./comedy-spine";

export type ComedySpineRequestType =
  | "joke"
  | "lesson"
  | "agent"
  | "curriculum"
  | "canon"
  | "runtime"
  | "unknown";

export type ComedySpineRouteReason =
  | "default-bottom-up"
  | "explicit-layer-request"
  | "explicit-layer-without-justification"
  | "curriculum-request"
  | "agent-request"
  | "canon-or-runtime-request";

export type RouteComedySpineRequestInput = {
  text: string;
  explicitLayer?: number;
  explicitJustification?: string;
  requestType?: ComedySpineRequestType;
};

export type ComedySpineRoute = {
  startLayer: ComedySpineLayer;
  escalationPath: ComedySpineLayer[];
  reason: ComedySpineRouteReason;
  requiresVerification: boolean;
  notes: string[];
};

export function getComedySpineLayer(layer: number): ComedySpineLayer | undefined {
  return KJU_COMEDY_SPINE.find((item) => item.layer === layer);
}

export function getDeepestComedySpineLayer(): ComedySpineLayer {
  const deepest = [...KJU_COMEDY_SPINE].sort((a, b) => b.layer - a.layer)[0];

  if (!deepest) {
    throw new Error("KJU_COMEDY_SPINE is empty. Runtime cannot route without canon.");
  }

  return deepest;
}

export function routeComedySpineRequest(
  input: RouteComedySpineRequestInput,
): ComedySpineRoute {
  const deepestLayer = getDeepestComedySpineLayer();

  if (input.explicitLayer !== undefined) {
    const requestedLayer = getComedySpineLayer(input.explicitLayer);

    if (!requestedLayer) {
      throw new Error(`Requested layer ${input.explicitLayer} does not exist in KJU_COMEDY_SPINE.`);
    }

    if (requestedLayer.layer !== deepestLayer.layer && !input.explicitJustification) {
      return {
        startLayer: deepestLayer,
        escalationPath: getComedySpineEscalationPath(deepestLayer.layer),
        reason: "explicit-layer-without-justification",
        requiresVerification: true,
        notes: [
          "Routing starts at the deepest canonical layer unless explicit justification is provided for higher-layer escalation.",
        ],
      };
    }

    return {
      startLayer: requestedLayer,
      escalationPath: getComedySpineEscalationPath(requestedLayer.layer),
      reason: "explicit-layer-request",
      requiresVerification: true,
      notes: ["Explicit layer requested. Verify request is justified before execution."],
    };
  }

  if (input.requestType === "canon" || input.requestType === "runtime") {
    return {
      startLayer: deepestLayer,
      escalationPath: getComedySpineEscalationPath(deepestLayer.layer),
      reason: "canon-or-runtime-request",
      requiresVerification: true,
      notes: ["Canon/runtime requests must pass verification before structural changes."],
    };
  }

  if (input.requestType === "curriculum" || input.requestType === "lesson") {
    return {
      startLayer: deepestLayer,
      escalationPath: getComedySpineEscalationPath(deepestLayer.layer),
      reason: "curriculum-request",
      requiresVerification: true,
      notes: ["Curriculum requests start bottom-up unless explicitly justified otherwise."],
    };
  }

  if (input.requestType === "agent") {
    return {
      startLayer: deepestLayer,
      escalationPath: getComedySpineEscalationPath(deepestLayer.layer),
      reason: "agent-request",
      requiresVerification: true,
      notes: ["Agent requests require responsibility verification before execution."],
    };
  }

  return {
    startLayer: deepestLayer,
    escalationPath: getComedySpineEscalationPath(deepestLayer.layer),
    reason: "default-bottom-up",
    requiresVerification: true,
    notes: ["Default route begins at the deepest canonical layer."],
  };
}

export function getComedySpineEscalationPath(startLayer: number): ComedySpineLayer[] {
  if (!getComedySpineLayer(startLayer)) {
    throw new Error(`Cannot build escalation path from missing KJU_COMEDY_SPINE layer ${startLayer}.`);
  }

  return KJU_COMEDY_SPINE
    .filter((layer) => layer.layer <= startLayer)
    .sort((a, b) => b.layer - a.layer);
}
