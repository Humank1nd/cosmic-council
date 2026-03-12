import { CosmicEvent } from '../types';

interface EventFeedProps {
  events: CosmicEvent[];
}

export function EventFeed({ events }: EventFeedProps) {
  return (
    <div className="event-feed">
      <div className="feed-header">
        <div className="feed-title">Live Event Feed</div>
        <div style={{ fontSize: '0.75rem', color: '#8a8a9a' }}>
          {events.length} events
        </div>
      </div>

      <div className="feed-events">
        {events.length === 0 ? (
          <div className="no-events">
            Awaiting telemetry...
          </div>
        ) : (
          events.map(event => (
            <div key={event.event_id} className="feed-event">
              <div className="event-handle">{event.handle}</div>
              <div className="event-content">
                <div className={`event-message severity-${event.severity.toLowerCase()}`}>
                  {event.message}
                </div>
                <div className="event-time">
                  {new Date(event.timestamp * 1000).toLocaleTimeString()} - {event.severity}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
