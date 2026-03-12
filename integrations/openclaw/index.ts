/**
 * Dream-Caesar OpenClaw Plugin
 *
 * Atomic-level CRONUS integration for OpenClaw agents.
 * Provides direct access to individual totems, think tanks, and pipeline stages.
 */

import type { AnyAgentTool, OpenClawPluginApi } from "openclaw/plugin-sdk";

type AgentToolResult = {
  content: Array<{ type: "text"; text: string }>;
  details?: unknown;
};

type DreamCaesarPluginConfig = {
  baseUrl?: string;
  apiToken?: string;
  timeoutMs?: number;
};

type RequestOptions = {
  baseUrl: string;
  apiToken: string;
  timeoutMs: number;
};

function normalizeBaseUrl(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

function resolveOptions(api: OpenClawPluginApi): RequestOptions {
  const cfg = (api.pluginConfig ?? {}) as DreamCaesarPluginConfig;
  return {
    baseUrl: normalizeBaseUrl(cfg.baseUrl ?? process.env.DREAM_CAESAR_API_URL ?? "http://127.0.0.1:8020"),
    apiToken: cfg.apiToken ?? process.env.DREAM_CAESAR_API_TOKEN ?? "",
    timeoutMs: Number.isFinite(cfg.timeoutMs) && (cfg.timeoutMs ?? 0) > 0 ? (cfg.timeoutMs as number) : 60000,
  };
}

function jsonResult(payload: unknown): AgentToolResult {
  return {
    content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
    details: payload,
  };
}

function errorResult(message: string, details?: unknown): AgentToolResult {
  return jsonResult({ error: message, details });
}

function toErrorMessage(err: unknown): string {
  if (err instanceof Error) {
    return err.message;
  }
  return String(err);
}

async function requestJson(
  method: "GET" | "POST" | "PUT",
  path: string,
  options: RequestOptions,
  body?: unknown,
  signal?: AbortSignal,
): Promise<unknown> {
  const timeoutController = new AbortController();
  const timeout = setTimeout(() => timeoutController.abort(), options.timeoutMs);
  const combined = new AbortController();
  const onAbort = () => combined.abort();

  try {
    if (signal) {
      signal.addEventListener("abort", onAbort, { once: true });
    }
    timeoutController.signal.addEventListener("abort", onAbort, { once: true });

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (options.apiToken) {
      headers.Authorization = `Bearer ${options.apiToken}`;
    }

    const response = await fetch(`${options.baseUrl}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: combined.signal,
    });

    const raw = await response.text();
    let parsed: unknown = raw;
    if (raw) {
      try {
        parsed = JSON.parse(raw);
      } catch {
        parsed = { raw };
      }
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return parsed;
  } finally {
    clearTimeout(timeout);
    if (signal) {
      signal.removeEventListener("abort", onAbort);
    }
  }
}

const dreamCaesarPlugin = {
  id: "dream-caesar",
  name: "Dream Caesar Tools",
  description: "Dream Caesar Cosmic Council API with atomic-level CRONUS integration.",
  configSchema: {
    type: "object",
    additionalProperties: false,
    properties: {
      baseUrl: { type: "string" },
      apiToken: { type: "string" },
      timeoutMs: { type: "integer", minimum: 1000, maximum: 120000 },
    },
  },
  register(api: OpenClawPluginApi) {
    const options = resolveOptions(api);

    // ═══════════════════════════════════════════════════════════════════════
    // SYSTEM TOOLS
    // ═══════════════════════════════════════════════════════════════════════

    api.registerTool(
      {
        name: "cronus_health",
        description: "Check CRONUS API health, model availability, and system status.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: Record<string, unknown>, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/health", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // ═══════════════════════════════════════════════════════════════════════
    // ATOMIC TOTEM TOOLS (Direct Individual Totem Access)
    // ═══════════════════════════════════════════════════════════════════════

    api.registerTool(
      {
        name: "cronus_totem_execute",
        description: `Execute a single CRONUS totem atomically.
Totems: red (Curiosity/Research), orange (Routing/Planning), yellow (Origin/Building),
green (Numbers/Resources), blue (User/Delivery), purple (Support/Reflection).`,
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            totem: {
              type: "string",
              enum: ["red", "orange", "yellow", "green", "blue", "purple"],
              description: "The totem color to execute"
            },
            task: { type: "string", description: "The task for this totem to process" },
            context: { type: "string", description: "Optional context from prior totems" },
          },
          required: ["totem", "task"],
        },
        async execute(
          _id: string,
          params: { totem: string; task: string; context?: string },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "POST",
              "/execute",
              options,
              {
                task: params.task,
                totem: params.totem,
                context: params.context ?? "",
              },
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    api.registerTool(
      {
        name: "cronus_list_totems",
        description: "List all CRONUS Cosmic Council totems with their roles and attributes.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: Record<string, unknown>, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/agents/cosmic-totems", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // ═══════════════════════════════════════════════════════════════════════
    // COUNCIL PIPELINE TOOLS
    // ═══════════════════════════════════════════════════════════════════════

    api.registerTool(
      {
        name: "cronus_council_deliberate",
        description: `Run a full Cosmic Council deliberation cycle (C-R-O-N-U-S pipeline).
Returns when complete. Modes: simplified (6 calls), full_108 (108 calls), adaptive.`,
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            objective: { type: "string", description: "The problem to deliberate on" },
            context: { type: "object", description: "Optional context object" },
            mode: {
              type: "string",
              enum: ["simplified", "full_108", "adaptive"],
              description: "Deliberation mode"
            },
            max_cycles: { type: "integer", minimum: 1, maximum: 10, description: "Max feedback cycles" },
          },
          required: ["objective"],
        },
        async execute(
          _id: string,
          params: { objective: string; context?: Record<string, unknown>; mode?: string; max_cycles?: number },
          signal?: AbortSignal,
        ) {
          try {
            const payload: Record<string, unknown> = {
              objective: params.objective,
              mode: params.mode ?? "simplified",
            };
            if (params.context !== undefined) payload.context = params.context;
            if (params.max_cycles !== undefined) payload.max_cycles = params.max_cycles;
            const result = await requestJson("POST", "/council", options, payload, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    api.registerTool(
      {
        name: "cronus_pipeline_start",
        description: "Start an async pipeline deliberation. Returns cycle_id immediately.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            problem: { type: "string", description: "The problem statement" },
            max_cycles: { type: "integer", minimum: 1, maximum: 10 },
            enable_think_tanks: { type: "boolean", description: "Enable fractal Think Tank sub-councils" },
          },
          required: ["problem"],
        },
        async execute(
          _id: string,
          params: { problem: string; max_cycles?: number; enable_think_tanks?: boolean },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "POST",
              "/agents/pipeline/async",
              options,
              params,
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    api.registerTool(
      {
        name: "cronus_pipeline_status",
        description: "Check status and results of a pipeline by cycle_id.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            cycle_id: { type: "string" },
          },
          required: ["cycle_id"],
        },
        async execute(_id: string, params: { cycle_id: string }, signal?: AbortSignal) {
          try {
            const result = await requestJson(
              "GET",
              `/agents/pipeline/${encodeURIComponent(params.cycle_id)}`,
              options,
              undefined,
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // ═══════════════════════════════════════════════════════════════════════
    // THINK TANK TOOLS (Fractal Sub-Councils)
    // ═══════════════════════════════════════════════════════════════════════

    api.registerTool(
      {
        name: "cronus_think_tank_spawn",
        description: `Spawn a fractal Think Tank sub-council for a specific totem.
Think Tanks provide deeper deliberation with diverse perspectives.`,
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            parent_totem: {
              type: "string",
              enum: ["red", "orange", "yellow", "green", "blue", "purple"],
              description: "The parent totem spawning the Think Tank"
            },
            problem: { type: "string", description: "The sub-problem to deliberate" },
            parent_analysis: { type: "string", description: "The parent totem's initial analysis" },
          },
          required: ["parent_totem", "problem", "parent_analysis"],
        },
        async execute(
          _id: string,
          params: { parent_totem: string; problem: string; parent_analysis: string },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "POST",
              "/agents/think-tank",
              options,
              params,
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // ═══════════════════════════════════════════════════════════════════════
    // COUNCIL STATS & MONITORING
    // ═══════════════════════════════════════════════════════════════════════

    api.registerTool(
      {
        name: "cronus_council_stats",
        description: "Get current council statistics including active cycles and totem states.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: Record<string, unknown>, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/council/stats", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    api.registerTool(
      {
        name: "cronus_list_cycles",
        description: "List all deliberation cycles (active and completed).",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: Record<string, unknown>, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/agents/cycles", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // ═══════════════════════════════════════════════════════════════════════
    // VM EXECUTION TOOLS (CRONUS Sandbox)
    // ═══════════════════════════════════════════════════════════════════════

    api.registerTool(
      {
        name: "cronus_vm_list",
        description: "List available VirtualBox VMs for sandboxed execution.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: Record<string, unknown>, signal?: AbortSignal) {
          try {
            const result = await requestJson(
              "POST",
              "/tools/call",
              options,
              { name: "cronus_vm_control", params: { action: "list_vms" } },
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    api.registerTool(
      {
        name: "cronus_vm_exec",
        description: "Execute a command in a VM via SSH or guestcontrol. Supports auto-start/stop and snapshots.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            command: { type: "string", description: "Command to execute in the VM" },
            vm_name: { type: "string", description: "VM name (uses CRONUS_VM_NAME env if not specified)" },
            method: { type: "string", enum: ["ssh", "guestcontrol"], description: "Execution method" },
            auto_start: { type: "boolean", description: "Auto-start VM if not running" },
            auto_stop: { type: "boolean", description: "Auto-stop VM after command" },
            auto_restore: { type: "boolean", description: "Restore snapshot before/after execution" },
          },
          required: ["command"],
        },
        async execute(
          _id: string,
          params: {
            command: string;
            vm_name?: string;
            method?: string;
            auto_start?: boolean;
            auto_stop?: boolean;
            auto_restore?: boolean;
          },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "POST",
              "/tools/call",
              options,
              { name: "cronus_vm_exec", params },
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // ═══════════════════════════════════════════════════════════════════════
    // DIRECT TOTEM SHORTCUTS (Convenience Methods)
    // ═══════════════════════════════════════════════════════════════════════

    const totemShortcuts: Array<{ name: string; totem: string; desc: string }> = [
      { name: "cronus_research", totem: "red", desc: "Red Owl: Research and investigate the problem (WHY)" },
      { name: "cronus_plan", totem: "orange", desc: "Orange Orangutan: Plan the approach (HOW)" },
      { name: "cronus_build", totem: "yellow", desc: "Yellow Honeybee: Build the solution (WHAT)" },
      { name: "cronus_evaluate", totem: "green", desc: "Green Tortoise: Evaluate resources (BALANCE)" },
      { name: "cronus_deliver", totem: "blue", desc: "Blue Dolphin: Deliver the output (OUTPUT)" },
      { name: "cronus_reflect", totem: "purple", desc: "Purple Elephant: Reflect and evaluate (REFLECTION)" },
    ];

    for (const shortcut of totemShortcuts) {
      api.registerTool(
        {
          name: shortcut.name,
          description: shortcut.desc,
          parameters: {
            type: "object",
            additionalProperties: false,
            properties: {
              task: { type: "string", description: "The task to process" },
              context: { type: "string", description: "Optional prior context" },
            },
            required: ["task"],
          },
          async execute(
            _id: string,
            params: { task: string; context?: string },
            signal?: AbortSignal,
          ) {
            try {
              const result = await requestJson(
                "POST",
                "/execute",
                options,
                {
                  task: params.task,
                  totem: shortcut.totem,
                  context: params.context ?? "",
                },
                signal,
              );
              return jsonResult(result);
            } catch (err) {
              return errorResult(toErrorMessage(err));
            }
          },
        } as AnyAgentTool,
        { optional: true },
      );
    }

    // ═══════════════════════════════════════════════════════════════════════
    // COSMIC CANON ACCESS (Spiritual/Quantum Framework)
    // ═══════════════════════════════════════════════════════════════════════

    // Get complete canon
    api.registerTool(
      {
        name: "cronus_canon",
        description: "Get the complete Cosmic Council canon including totems, chakras, quantum concepts, mantras, and LOST numbers",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: object, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/canon", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Get single totem profile with full canon info
    api.registerTool(
      {
        name: "cronus_canon_totem",
        description: "Get full profile for a specific totem including chakra, quantum concept, mantra, spirit animal, gemstone, and archetype",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            totem: {
              type: "string",
              enum: ["red", "orange", "yellow", "green", "blue", "purple"],
              description: "Totem color (red/orange/yellow/green/blue/purple)",
            },
          },
          required: ["totem"],
        },
        async execute(
          _id: string,
          params: { totem: string },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "GET",
              `/canon/totems/${params.totem}`,
              options,
              undefined,
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Get chakra information
    api.registerTool(
      {
        name: "cronus_canon_chakras",
        description: "Get all chakra information with frequencies (432Hz-963Hz) and associated totems",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: object, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/canon/chakras", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Get quantum concepts
    api.registerTool(
      {
        name: "cronus_canon_quantum",
        description: "Get quantum concepts mapped to each totem (Entanglement, Tunneling, Superposition, Teleportation, Wave-Particle Duality, Field Theory)",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: object, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/canon/quantum", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Get mantras
    api.registerTool(
      {
        name: "cronus_canon_mantras",
        description: "Get the mantras for each totem (Universal Love, Eternity, Awakening phrases)",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: object, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/canon/mantras", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Get LOST numbers
    api.registerTool(
      {
        name: "cronus_canon_lost",
        description: "Get the LOST numbers (4, 8, 15, 16, 23, 42 = 108) and their cosmic significance",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: object, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/canon/lost-numbers", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Get fractal depths
    api.registerTool(
      {
        name: "cronus_canon_fractals",
        description: "Get the 10 fractal depth levels (Macro through Quecto, 10^0 to 10^-9)",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: object, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/canon/fractal-depths", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Generate canon-enriched prompt
    api.registerTool(
      {
        name: "cronus_canon_prompt",
        description: "Generate a canon-enriched system prompt for a specific totem with full spiritual/quantum context",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            totem: {
              type: "string",
              enum: ["red", "orange", "yellow", "green", "blue", "purple"],
              description: "Totem color (red/orange/yellow/green/blue/purple)",
            },
          },
          required: ["totem"],
        },
        async execute(
          _id: string,
          params: { totem: string },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "GET",
              `/canon/prompt/${params.totem}`,
              options,
              undefined,
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // ═══════════════════════════════════════════════════════════════════════
    // SAHASRARA (Crown Chakra) - Meta-Analysis & Perpetual Evolution
    // ═══════════════════════════════════════════════════════════════════════

    // Run perpetual evolution cycle
    api.registerTool(
      {
        name: "cronus_perpetual_cycle",
        description: "Run perpetual improvement cycles - the Ouroboros pattern. Each cycle feeds refinements back to the next for continuous evolution toward cosmic alignment.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            objective: {
              type: "string",
              description: "The objective to iterate on through perpetual cycles",
            },
            iterations: {
              type: "number",
              description: "Number of evolution cycles (1-10, default 3)",
            },
            context: {
              type: "string",
              description: "Optional prior context to seed the cycles",
            },
          },
          required: ["objective"],
        },
        async execute(
          _id: string,
          params: { objective: string; iterations?: number; context?: string },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "POST",
              "/council/perpetual",
              options,
              {
                objective: params.objective,
                iterations: params.iterations ?? 3,
                context: params.context ?? null,
              },
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Get evolution status
    api.registerTool(
      {
        name: "cronus_evolution_status",
        description: "Get the evolution status from Sahasrara meta-analysis. Returns evolution trend, harmonization history, and optimization insights from the Crown Chakra.",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {},
        },
        async execute(_id: string, _params: object, signal?: AbortSignal) {
          try {
            const result = await requestJson("GET", "/council/evolution", options, undefined, signal);
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );

    // Activate Sahasrara at specific level
    api.registerTool(
      {
        name: "cronus_sahasrara_activate",
        description: "Activate Sahasrara meta-analysis layer at specified level (dormant, observing, analyzing, evolving)",
        parameters: {
          type: "object",
          additionalProperties: false,
          properties: {
            level: {
              type: "string",
              enum: ["dormant", "observing", "analyzing", "evolving"],
              description: "Activation level: dormant (off), observing (light), analyzing (full LLM), evolving (perpetual)",
            },
          },
          required: ["level"],
        },
        async execute(
          _id: string,
          params: { level: string },
          signal?: AbortSignal,
        ) {
          try {
            const result = await requestJson(
              "POST",
              `/council/sahasrara/activate?level=${params.level}`,
              options,
              {},
              signal,
            );
            return jsonResult(result);
          } catch (err) {
            return errorResult(toErrorMessage(err));
          }
        },
      } as AnyAgentTool,
      { optional: true },
    );
  },
};

export default dreamCaesarPlugin;
