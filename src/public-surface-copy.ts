// Runtime consumes canon. Runtime must not recreate canon.

import type { ComedySeatColor } from "./comedy-spine";
import type { UniverseThemePackId } from "./theme-pack-types";
import {
  getThemedTotemOverlay,
  getThemedTotemOverlays,
  KJU_THEME_LAYER_NAMES,
  resolveThemePackId,
} from "./theme-pack-loader";

const PUBLIC_PACK: UniverseThemePackId = "know-joke";

export function getPublicCouncilBrandName(): string {
  return KJU_THEME_LAYER_NAMES.comedicCouncil;
}

export function formatThemedTotemAgentLabel(
  color: ComedySeatColor,
  packId: UniverseThemePackId = PUBLIC_PACK,
): string {
  const totem = getThemedTotemOverlay(color, packId);
  const alias = totem.optionalAlias?.trim();
  if (alias) {
    return `${totem.displayVariant} (${alias})`;
  }
  return totem.displayVariant;
}

export function buildBitLabCycleStartedFeedback(cycleId: string): string {
  const council = getPublicCouncilBrandName();
  const debaters = (["red", "orange", "yellow"] as const)
    .map((color) => formatThemedTotemAgentLabel(color))
    .join(", ");

  return `*Cycle Started: ${cycleId}*\n\nYour bit has been sent to the ${council}. ${debaters} are debating it now. Please check back for the final verdict.`;
}

export function buildBitLabMockDebateFeedback(): string {
  return `*(MOCK DEBATE - GATEWAY UNAVAILABLE)*\n\n${buildFullClownsDebateFeedback({
    setup: "",
    punchlines: [],
  })}`;
}

export type BitLabDebateInput = {
  setup: string;
  punchlines: string[];
  lineageLayer?: number;
  lessonTitle?: string;
  trackId?: string;
};

export function buildFullClownsDebateFeedback(input: BitLabDebateInput): string {
  const packId = resolveThemePackId(undefined, { publicSurface: true });
  const council = getPublicCouncilBrandName();
  const cleaned = input.punchlines.filter((p) => p.trim());
  const layer = input.lineageLayer ?? 10;
  const lessonTitle = input.lessonTitle ?? "ambient culture";
  const trackId = input.trackId ?? "foundations-of-comedy";

  const defaults: Record<ComedySeatColor, string> = {
    red: `[Lineage Layer ${layer}] The premise establishes a reality based on ${lessonTitle}. Truth-density confirmed at 88%.`,
    orange: "The logic path follows the C.L.O.W.N.S. sequence. Transition efficiency: High.",
    yellow: `"${cleaned[0] ?? "(draft pending)"}" is a fertile origin. Its creative delta matches the ${trackId} requirements.`,
    green: `Resource Audit: 1 setup, ${cleaned.length} punchline(s). The ratio is sustainable.`,
    blue: "Market Projection: This will resonate with the User layer. Empathy bridge secured.",
    purple: "Recursive Synthesis: Loop finalized. This bit is ready to be committed to the Sovereign Ledger.",
  };

  const lines = (["red", "orange", "yellow", "green", "blue", "purple"] as const).map(
    (color) => `**${formatThemedTotemAgentLabel(color, packId)}**: ${defaults[color]}`,
  );
  lines.push(`Canonical Recommendation: C.L.O.W.N.S. loop closed. ${council} verified.`);
  return lines.join("\n\n");
}

export async function pollGatewayPublicFeedback(
  gatewayUrl: string,
  cycleId: string,
  options?: { timeoutMs?: number; intervalMs?: number },
): Promise<string | null> {
  const timeoutMs = options?.timeoutMs ?? 8000;
  const intervalMs = options?.intervalMs ?? 500;
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    try {
      const statusRes = await fetch(`${gatewayUrl}/v1/cycles/${cycleId}`);
      if (statusRes.ok) {
        const data = (await statusRes.json()) as { public_feedback?: string; status?: string };
        if (typeof data.public_feedback === "string" && data.public_feedback.trim()) {
          return data.public_feedback;
        }
        if (data.status === "completed" || data.status === "COMPLETED") {
          return null;
        }
      }
    } catch {
      // Gateway poll is best-effort
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  return null;
}

/** C.L.O.W.N.S. totem display labels for hardcoded course/module fallbacks. */
export function getThemedCourseModuleAgents(): Record<ComedySeatColor, string> {
  const packId = resolveThemePackId(undefined, { publicSurface: true });
  return Object.fromEntries(
    getThemedTotemOverlays(packId).map((totem) => [
      totem.color,
      formatThemedTotemAgentLabel(totem.color, packId),
    ]),
  ) as Record<ComedySeatColor, string>;
}

export function getClownsAgentNamesForCurriculumPrompt(): string {
  const agents = getThemedCourseModuleAgents();
  return [
    agents.red,
    agents.orange,
    agents.yellow,
    agents.blue,
  ]
    .map((name) => `"${name}"`)
    .join(" | ");
}

export function applyThemedAgentToLessonBody(body: string): string {
  const agents = getThemedCourseModuleAgents();
  return body.replace(/\bRed Owl tradition\b/g, `${agents.red} tradition`);
}
