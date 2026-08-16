// Runtime consumes canon. Runtime must not recreate canon.

import { KJU_COMEDY_SPINE, type ComedySeatColor, type ComedySpineLayer } from "./comedy-spine";
import { getComedySpineAgentsForLayer } from "./comedy-spine-agent-registry";
import {
  getComedySpineCurriculumLevel,
  KJU_COMEDY_SPINE_CURRICULUM,
} from "./comedy-spine-curriculum";
import { getComedySpineLayerRole } from "./comedy-spine-layer-roles";
import {
  getComedySpineEscalationPath,
  getDeepestComedySpineLayer,
  routeComedySpineRequest,
} from "./comedy-spine-router";

export type ComedySpineVerificationCheck =
  | "canon-seat-check"
  | "layer-function-check"
  | "routing-check"
  | "curriculum-check"
  | "agent-responsibility-check"
  | "non-drift-check";

export type ComedySpineVerificationSeverity = "pass" | "warning" | "fail";

export type ComedySpineVerificationCheckResult = {
  check: ComedySpineVerificationCheck;
  passed: boolean;
  severity: ComedySpineVerificationSeverity;
  message: string;
};

export type ComedySpineVerificationResult = {
  passed: boolean;
  checks: ComedySpineVerificationCheckResult[];
};

export type ComedySpineLayerCanonStatus =
  | "awaiting-canon-finalization"
  | "locked-canon"
  | "runtime";

export function getComedySpineLayerCanonStatus(
  layer: ComedySpineLayer,
): ComedySpineLayerCanonStatus {
  if (getComedySpinePlaceholderSeatCount(layer) > 0) {
    return "awaiting-canon-finalization";
  }

  if (isLockedCanonLayer(layer)) {
    return "locked-canon";
  }

  return "runtime";
}

export function getComedySpinePlaceholderSeatCount(layer: ComedySpineLayer): number {
  return layer.seats.filter((seat) => isPlaceholderSeat(seat.anchor)).length;
}

export function verifyComedySpineRuntimeAlignment(): ComedySpineVerificationResult {
  const checks: ComedySpineVerificationCheckResult[] = [
    verifyCanonSeatCheck(),
    verifyLayerFunctionCheck(),
    verifyRoutingCheck(),
    verifyCurriculumCheck(),
    verifyAgentResponsibilityCheck(),
    verifyNonDriftCheck(),
  ];

  return {
    passed: checks.every((check) => check.passed),
    checks,
  };
}

function verifyCanonSeatCheck(): ComedySpineVerificationCheckResult {
  const failures: string[] = [];

  for (const layer of KJU_COMEDY_SPINE) {
    if (layer.seats.length !== 6) {
      failures.push(`Layer ${layer.layer} has ${layer.seats.length} seats instead of 6.`);
    }

    const duplicateColors = getDuplicateSeatColors(layer.seats.map((seat) => seat.color));

    if (duplicateColors.length > 0) {
      failures.push(`Layer ${layer.layer} has duplicate seat colors: ${duplicateColors.join(", ")}.`);
    }
  }

  if (failures.length > 0) {
    return failed("canon-seat-check", failures.join(" "));
  }

  return passed(
    "canon-seat-check",
    `All ${KJU_COMEDY_SPINE.length} canon layers have six seats and no duplicate seat colors.`,
  );
}

function verifyLayerFunctionCheck(): ComedySpineVerificationCheckResult {
  const failures: string[] = [];

  for (const layer of KJU_COMEDY_SPINE) {
    try {
      const role = getComedySpineLayerRole(layer.layer);

      if (!role.agentName || !role.responsibility) {
        failures.push(`Layer ${layer.layer} has an incomplete layer role.`);
      }
    } catch (error) {
      failures.push(getErrorMessage(error));
    }
  }

  if (failures.length > 0) {
    return failed("layer-function-check", failures.join(" "));
  }

  return passed("layer-function-check", "Every canon layer resolves to a layer role.");
}

function verifyRoutingCheck(): ComedySpineVerificationCheckResult {
  const failures: string[] = [];

  try {
    const deepestLayer = getDeepestComedySpineLayer();
    const defaultRoute = routeComedySpineRequest({ text: "verification" });

    if (deepestLayer.layer !== 10) {
      failures.push(`Deepest canon layer is ${deepestLayer.layer}; expected current Layer 10.`);
    }

    if (defaultRoute.startLayer.layer !== deepestLayer.layer) {
      failures.push(
        `Default route starts at Layer ${defaultRoute.startLayer.layer}; expected deepest Layer ${deepestLayer.layer}.`,
      );
    }

    for (const layer of KJU_COMEDY_SPINE) {
      const escalationPath = getComedySpineEscalationPath(layer.layer);

      if (escalationPath[0]?.layer !== layer.layer) {
        failures.push(`Escalation path for Layer ${layer.layer} does not start at that layer.`);
      }
    }
  } catch (error) {
    failures.push(getErrorMessage(error));
  }

  if (failures.length > 0) {
    return failed("routing-check", failures.join(" "));
  }

  return passed(
    "routing-check",
    "Default routing starts at deepest Layer 10 and every canon layer can produce an escalation path.",
  );
}

function verifyCurriculumCheck(): ComedySpineVerificationCheckResult {
  const failures: string[] = [];

  try {
    const curriculumRoute = routeComedySpineRequest({
      text: "verification curriculum request",
      requestType: "curriculum",
    });

    if (!curriculumRoute.requiresVerification) {
      failures.push("Curriculum route does not require verification.");
    }

    for (const curriculumLevel of KJU_COMEDY_SPINE_CURRICULUM) {
      try {
        curriculumLevel.layer;
        curriculumLevel.layerRole;
      } catch (error) {
        failures.push(getErrorMessage(error));
      }
    }

    const firstLevel = getComedySpineCurriculumLevel(1);
    const finalLevelDefinition = KJU_COMEDY_SPINE_CURRICULUM.find((entry) => entry.level === 8);

    if (firstLevel.layer.layer !== 10) {
      failures.push(`Curriculum level 1 resolves to Layer ${firstLevel.layer.layer}; expected Layer 10.`);
    }

    if (firstLevel.layerRole.agentName !== "Signal Scout") {
      failures.push(
        `Curriculum level 1 resolves to ${firstLevel.layerRole.agentName}; expected Signal Scout.`,
      );
    }

    if (finalLevelDefinition?.layerNumber !== 3) {
      failures.push("Curriculum level 8 does not map to Layer 3.");
    }
  } catch (error) {
    failures.push(getErrorMessage(error));
  }

  if (failures.length > 0) {
    return failed("curriculum-check", failures.join(" "));
  }

  return passed(
    "curriculum-check",
    "Curriculum requests require verification, every curriculum layer resolves, level 1 resolves to Layer 10, and level 8 maps to Layer 3.",
  );
}

function verifyAgentResponsibilityCheck(): ComedySpineVerificationCheckResult {
  const failures: string[] = [];

  for (const layer of KJU_COMEDY_SPINE) {
    try {
      const layerRole = getComedySpineLayerRole(layer.layer);
      const agentRegistry = getComedySpineAgentsForLayer(layer.layer);

      if (!layerRole.agentName || !layerRole.responsibility) {
        failures.push(`Layer ${layer.layer} has an incomplete layer role.`);
      }

      if (!agentRegistry) {
        failures.push(`Layer ${layer.layer} is missing a seat-level agent registry entry.`);
        continue;
      }

      if (agentRegistry.agents.length !== layer.seats.length) {
        failures.push(
          `Layer ${layer.layer} has ${agentRegistry.agents.length} registered agents for ${layer.seats.length} seats.`,
        );
      }
    } catch (error) {
      failures.push(getErrorMessage(error));
    }
  }

  if (failures.length > 0) {
    return failed("agent-responsibility-check", failures.join(" "));
  }

  return passed(
    "agent-responsibility-check",
    "Every canon layer has a layer role and matching seat-level agent responsibilities.",
  );
}

function verifyNonDriftCheck(): ComedySpineVerificationCheckResult {
  const layerNumbers = KJU_COMEDY_SPINE.map((layer) => layer.layer);
  const duplicateLayerNumbers = getDuplicateNumbers(layerNumbers);
  const placeholderReport = analyzePlaceholders();
  const failures: string[] = [];

  if (duplicateLayerNumbers.length > 0) {
    failures.push(`Duplicate canon layer numbers found: ${duplicateLayerNumbers.join(", ")}.`);
  }

  failures.push(...placeholderReport.failures);

  if (failures.length > 0) {
    return failed("non-drift-check", failures.join(" "));
  }

  if (placeholderReport.warnings.length > 0) {
    return warning(
      "non-drift-check",
      [
        "No duplicate canon layer numbers exist.",
        ...placeholderReport.warnings,
      ].join(" "),
    );
  }

  return passed("non-drift-check", "No duplicate canon layer numbers exist and no placeholders remain.");
}

function getDuplicateSeatColors(colors: ComedySeatColor[]): ComedySeatColor[] {
  const seen = new Set<ComedySeatColor>();
  const duplicates = new Set<ComedySeatColor>();

  for (const color of colors) {
    if (seen.has(color)) {
      duplicates.add(color);
    }

    seen.add(color);
  }

  return [...duplicates];
}

function getDuplicateNumbers(numbers: number[]): number[] {
  const seen = new Set<number>();
  const duplicates = new Set<number>();

  for (const number of numbers) {
    if (seen.has(number)) {
      duplicates.add(number);
    }

    seen.add(number);
  }

  return [...duplicates];
}

function passed(
  check: ComedySpineVerificationCheck,
  message: string,
): ComedySpineVerificationCheckResult {
  return {
    check,
    passed: true,
    severity: "pass",
    message,
  };
}

function failed(
  check: ComedySpineVerificationCheck,
  message: string,
): ComedySpineVerificationCheckResult {
  return {
    check,
    passed: false,
    severity: "fail",
    message,
  };
}

function warning(
  check: ComedySpineVerificationCheck,
  message: string,
): ComedySpineVerificationCheckResult {
  return {
    check,
    passed: true,
    severity: "warning",
    message,
  };
}

function analyzePlaceholders(): { warnings: string[]; failures: string[] } {
  const warnings: string[] = [];
  const failures: string[] = [];
  const placeholderLayers = new Map<number, number>();

  for (const layer of KJU_COMEDY_SPINE) {
    for (const seat of layer.seats) {
      if (!isPlaceholderSeat(seat.anchor)) {
        continue;
      }

      placeholderLayers.set(layer.layer, (placeholderLayers.get(layer.layer) ?? 0) + 1);

      if (isLockedCanonLayer(layer)) {
        failures.push(`Locked Layer ${layer.layer} contains placeholder anchor ${seat.anchor}.`);
      }

      if (!seat.function.includes("Awaiting canon finalization")) {
        failures.push(
          `Layer ${layer.layer} ${seat.color} placeholder is missing the Awaiting canon finalization marker.`,
        );
      }
    }
  }

  for (const [layer, count] of [...placeholderLayers].sort(([left], [right]) => left - right)) {
    if (!isPlaceholderAllowedLayer(layer)) {
      failures.push(`Layer ${layer} contains ${count} placeholder seats but is not placeholder-approved.`);
      continue;
    }

    warnings.push(`Layer ${layer} contains ${count} placeholder seats awaiting canon finalization.`);
  }

  return {
    warnings,
    failures,
  };
}

function isPlaceholderSeat(anchor: string): boolean {
  return anchor === "TBD";
}

function isPlaceholderAllowedLayer(layer: number): boolean {
  return layer === 3 || layer === 4;
}

function isLockedCanonLayer(layer: ComedySpineLayer): boolean {
  return layer.layer >= 5 && layer.layer <= 10;
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
