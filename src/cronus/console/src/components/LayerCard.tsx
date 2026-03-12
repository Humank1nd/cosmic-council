import { Shield, AlertTriangle, Zap, Activity, Clock } from 'lucide-react';
import { CosmicEvent, CosmicLayer } from '../types';

interface LayerCardProps {
  layer: CosmicLayer;
  handle: string;
  bio: string;
  latestEvent: CosmicEvent | null;
  eventCount: number;
}

const LAYER_ICONS: Record<CosmicLayer, React.ReactNode> = {
  ROOT_AUTHORITY: <Shield size={16} />,
  SUBSTRATE: <Activity size={16} />,
  INVARIANTS: <Shield size={16} />,
  CAPABILITIES: <Zap size={16} />,
  BOUNDARIES: <Shield size={16} />,
  SIMULATIONS: <Activity size={16} />,
  CONTINUITY: <Clock size={16} />,
  TERMINATION: <AlertTriangle size={16} />,
  FORGETTING: <Activity size={16} />,
  REBALANCER: <Activity size={16} />,
  SEARCH_LIMITS: <Activity size={16} />,
  DIVERGENCE_WATCH: <AlertTriangle size={16} />,
  TRIBUNAL: <Shield size={16} />,
};

export function LayerCard({ layer, handle, bio, latestEvent, eventCount }: LayerCardProps) {
  const isCritical = latestEvent?.severity === 'CRITICAL' || latestEvent?.severity === 'ALERT';
  const isWarning = latestEvent?.severity === 'WARNING';
  const isRoot = layer === 'ROOT_AUTHORITY';

  const cardClass = [
    'layer-card',
    isCritical ? 'critical' : '',
    isWarning ? 'warning' : '',
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClass} style={isRoot ? { opacity: 0.5 } : undefined}>
      <div className="layer-header">
        <div className="layer-handle" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {LAYER_ICONS[layer]}
          {handle}
        </div>
        <div style={{
          fontSize: '0.625rem',
          color: '#8a8a9a',
          background: '#1a1a24',
          padding: '0.125rem 0.375rem',
          borderRadius: '0.125rem',
        }}>
          {eventCount} events
        </div>
      </div>

      <div className="layer-bio">{bio}</div>

      {latestEvent ? (
        <div className="layer-event">
          <div className={`message severity-${latestEvent.severity.toLowerCase()}`}>
            {latestEvent.message}
          </div>
          <div className="timestamp">
            {new Date(latestEvent.timestamp * 1000).toLocaleTimeString()}
          </div>
        </div>
      ) : (
        <div className="layer-event" style={{ color: '#6a6a7a', fontStyle: 'italic' }}>
          {isRoot ? 'Silent (as it should be)' : 'No events yet'}
        </div>
      )}
    </div>
  );
}
