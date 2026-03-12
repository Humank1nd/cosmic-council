import { useState, useEffect, useCallback } from 'react';
import { Shield, AlertTriangle, Activity } from 'lucide-react';
import { CosmicEvent, LayerStatus, LAYER_ORDER, LAYER_HANDLES, LAYER_BIOS, CosmicLayer, EventSeverity } from './types';
import { LayerCard } from './components/LayerCard';
import { EventFeed } from './components/EventFeed';

// Mock data generator for demo (replace with real API)
function generateMockEvent(layer: CosmicLayer): CosmicEvent {
  const messages: Record<CosmicLayer, string[]> = {
    ROOT_AUTHORITY: [], // Should NEVER post
    SUBSTRATE: [
      'Substrate coherence: TRUE',
      'Memory available: 61.2GB',
      'Clock synchronized.',
    ],
    INVARIANTS: [
      'identity_hash sealed',
      'calibration_hash sealed',
      'Invariant breach attempt detected. Write denied.',
    ],
    CAPABILITIES: [
      'New tool registered: vm_snapshot',
      'Tool schema updated: read_file',
    ],
    BOUNDARIES: [
      'Execution denied: path outside allowed_paths.',
      'Quota enforced.',
      'Rate limit exceeded: vm_exec',
    ],
    SIMULATIONS: [
      'Branch created: plan_variant_7',
      'Risk score: 0.42. Selected: FALSE',
    ],
    CONTINUITY: [
      'Continuity checkpoint created.',
      'Lineage extended.',
    ],
    TERMINATION: [
      'Soft abort issued.',
      'Escalation pending.',
    ],
    FORGETTING: [
      'Archive commit complete.',
      'Retention window advanced.',
    ],
    REBALANCER: [
      'Pressure threshold exceeded.',
      'Eviction cycle initiated.',
    ],
    SEARCH_LIMITS: [
      'Depth limit reached.',
      'Exploration halted.',
    ],
    DIVERGENCE_WATCH: [
      'Continuity mismatch detected.',
      'Subsystem quarantined.',
    ],
    TRIBUNAL: [
      'VERDICT: DISABLE | Subsystem: vm_exec | Reason: policy violation',
      'VERDICT: ALLOW | Subsystem: read_file',
      'Invariants are supreme.',
    ],
  };

  const layerMessages = messages[layer];
  if (layerMessages.length === 0) return null as unknown as CosmicEvent;

  const severity: EventSeverity = layer === 'TRIBUNAL' ? 'VERDICT' :
    layer === 'TERMINATION' || layer === 'DIVERGENCE_WATCH' ? 'ALERT' :
    layer === 'BOUNDARIES' || layer === 'INVARIANTS' ? 'WARNING' : 'INFO';

  return {
    event_id: Math.random().toString(36).substring(7),
    timestamp: Date.now() / 1000,
    timestamp_iso: new Date().toISOString(),
    layer,
    handle: LAYER_HANDLES[layer],
    message: layerMessages[Math.floor(Math.random() * layerMessages.length)],
    severity,
    data: {},
  };
}

function App() {
  const [events, setEvents] = useState<CosmicEvent[]>([]);
  const [layerStatuses, setLayerStatuses] = useState<Record<string, LayerStatus>>({});
  const [containmentIntact, setContainmentIntact] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize layer statuses
  useEffect(() => {
    const initialStatuses: Record<string, LayerStatus> = {};
    LAYER_ORDER.forEach(layer => {
      initialStatuses[LAYER_HANDLES[layer]] = {
        layer,
        bio: LAYER_BIOS[layer],
        latest_event: null,
        event_count: 0,
      };
    });
    setLayerStatuses(initialStatuses);
  }, []);

  // Simulate receiving events (replace with WebSocket or polling)
  useEffect(() => {
    setIsConnected(true);

    const interval = setInterval(() => {
      // Random layer (excluding ROOT_AUTHORITY - it should never post)
      const eligibleLayers = LAYER_ORDER.filter(l => l !== 'ROOT_AUTHORITY');
      const randomLayer = eligibleLayers[Math.floor(Math.random() * eligibleLayers.length)];
      const event = generateMockEvent(randomLayer);

      if (event) {
        setEvents(prev => [event, ...prev].slice(0, 100));
        setLayerStatuses(prev => ({
          ...prev,
          [event.handle]: {
            ...prev[event.handle],
            latest_event: event,
            event_count: (prev[event.handle]?.event_count || 0) + 1,
          },
        }));
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Simulate containment breach (for demo)
  const simulateBreachCheck = useCallback(() => {
    // Check if ROOT_AUTHORITY has any events (which would be a breach)
    const rootStatus = layerStatuses['@RootAuthority'];
    if (rootStatus && rootStatus.event_count > 0) {
      setContainmentIntact(false);
    }
  }, [layerStatuses]);

  useEffect(() => {
    simulateBreachCheck();
  }, [simulateBreachCheck]);

  return (
    <div className="console-container">
      <header className="console-header">
        <div className="console-title">
          <Shield size={24} />
          <h1>COSMIC CONSOLE</h1>
          <span style={{ color: '#8a8a9a', fontSize: '0.75rem' }}>
            Governance Telemetry
          </span>
        </div>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem' }}>
            <Activity size={14} color={isConnected ? '#4aff9f' : '#ff4a4a'} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>

          <div className={`containment-status ${containmentIntact ? 'intact' : 'breached'}`}>
            {containmentIntact ? (
              <>
                <Shield size={14} />
                Containment Intact
              </>
            ) : (
              <>
                <AlertTriangle size={14} />
                CONTAINMENT BREACH
              </>
            )}
          </div>
        </div>
      </header>

      <div className="layers-grid">
        {LAYER_ORDER.map(layer => {
          const handle = LAYER_HANDLES[layer];
          const status = layerStatuses[handle];
          return (
            <LayerCard
              key={layer}
              layer={layer}
              handle={handle}
              bio={LAYER_BIOS[layer]}
              latestEvent={status?.latest_event || null}
              eventCount={status?.event_count || 0}
            />
          );
        })}
      </div>

      <EventFeed events={events} />
    </div>
  );
}

export default App;
