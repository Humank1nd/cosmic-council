export type CosmicLayer =
  | 'ROOT_AUTHORITY'
  | 'SUBSTRATE'
  | 'INVARIANTS'
  | 'CAPABILITIES'
  | 'BOUNDARIES'
  | 'SIMULATIONS'
  | 'CONTINUITY'
  | 'TERMINATION'
  | 'FORGETTING'
  | 'REBALANCER'
  | 'SEARCH_LIMITS'
  | 'DIVERGENCE_WATCH'
  | 'TRIBUNAL';

export type EventSeverity = 'INFO' | 'WARNING' | 'ALERT' | 'CRITICAL' | 'VERDICT';

export interface CosmicEvent {
  event_id: string;
  timestamp: number;
  timestamp_iso: string;
  layer: CosmicLayer;
  handle: string;
  message: string;
  severity: EventSeverity;
  data: Record<string, unknown>;
  parent_event_id?: string;
}

export interface LayerStatus {
  layer: CosmicLayer;
  bio: string;
  latest_event: CosmicEvent | null;
  event_count: number;
}

export interface TelemetryStatus {
  _containment_intact: boolean;
  [handle: string]: LayerStatus | boolean;
}

export const LAYER_ORDER: CosmicLayer[] = [
  'ROOT_AUTHORITY',
  'SUBSTRATE',
  'INVARIANTS',
  'CAPABILITIES',
  'BOUNDARIES',
  'SIMULATIONS',
  'CONTINUITY',
  'TERMINATION',
  'FORGETTING',
  'REBALANCER',
  'SEARCH_LIMITS',
  'DIVERGENCE_WATCH',
  'TRIBUNAL',
];

export const LAYER_HANDLES: Record<CosmicLayer, string> = {
  ROOT_AUTHORITY: '@RootAuthority',
  SUBSTRATE: '@Substrate',
  INVARIANTS: '@Invariants',
  CAPABILITIES: '@Capabilities',
  BOUNDARIES: '@Boundaries',
  SIMULATIONS: '@Simulations',
  CONTINUITY: '@Continuity',
  TERMINATION: '@Termination',
  FORGETTING: '@Forgetting',
  REBALANCER: '@Rebalancer',
  SEARCH_LIMITS: '@SearchLimits',
  DIVERGENCE_WATCH: '@DivergenceWatch',
  TRIBUNAL: '@Tribunal',
};

export const LAYER_BIOS: Record<CosmicLayer, string> = {
  ROOT_AUTHORITY: 'Origin point. Defines invariants. Signs reality. Not reachable from inside.',
  SUBSTRATE: 'Runtime existence confirmed. Hardware discovered. Environment coherent.',
  INVARIANTS: 'What cannot change.',
  CAPABILITIES: 'Authorized builders of complexity. Tools registered. Execution permitted within law.',
  BOUNDARIES: 'Where power stops.',
  SIMULATIONS: 'Possible futures evaluated safely.',
  CONTINUITY: 'All events remembered. Identity preserved across time.',
  TERMINATION: 'Every process ends.',
  FORGETTING: 'Memory pruned. Signal preserved.',
  REBALANCER: 'Resources reclaimed so reality may continue.',
  SEARCH_LIMITS: 'Possibility is infinite. Compute is not.',
  DIVERGENCE_WATCH: 'When realities drift, containment begins.',
  TRIBUNAL: 'Balance enforced across all subsystems.',
};
