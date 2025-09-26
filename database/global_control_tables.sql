-- 🔁 Global Control Tables
-- Central control and audit system for the Cosmic Council

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Global cycles table
CREATE TABLE IF NOT EXISTS cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    objective_ref VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'active',
            'completed',
            'failed',
            'paused'
        )
    ),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    parent_cycle_id UUID REFERENCES cycles (id), -- For fractal recursion
    cycle_depth INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage executions tracking
CREATE TABLE IF NOT EXISTS stage_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    cycle_id UUID NOT NULL REFERENCES cycles (id),
    stage_code VARCHAR(50) NOT NULL CHECK (
        stage_code IN (
            'red_research',
            'orange_logistics',
            'yellow_development',
            'green_budget',
            'blue_market',
            'purple_support'
        )
    ),
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'active',
            'completed',
            'failed',
            'skipped'
        )
    ),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    execution_order INTEGER NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comprehensive audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL CHECK (
        action IN (
            'create',
            'read',
            'update',
            'delete',
            'execute',
            'fail'
        )
    ),
    actor VARCHAR(200) NOT NULL, -- human, agent, or system
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    details_json JSONB,
    cycle_id UUID REFERENCES cycles (id),
    stage_execution_id UUID REFERENCES stage_executions (id)
);

-- Performance metrics tracking
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    cycle_id UUID NOT NULL REFERENCES cycles (id),
    metric_name VARCHAR(200) NOT NULL,
    metric_value DECIMAL(15, 4),
    metric_unit VARCHAR(50),
    measurement_timestamp TIMESTAMPTZ DEFAULT NOW(),
    context JSONB
);

-- System configuration
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    config_key VARCHAR(200) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) DEFAULT 'string' CHECK (
        config_type IN (
            'string',
            'number',
            'boolean',
            'json'
        )
    ),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cycles_status ON cycles (status);

CREATE INDEX IF NOT EXISTS idx_cycles_parent ON cycles (parent_cycle_id);

CREATE INDEX IF NOT EXISTS idx_cycles_started_at ON cycles (started_at);

CREATE INDEX IF NOT EXISTS idx_stage_executions_cycle ON stage_executions (cycle_id);

CREATE INDEX IF NOT EXISTS idx_stage_executions_stage ON stage_executions (stage_code);

CREATE INDEX IF NOT EXISTS idx_stage_executions_status ON stage_executions (status);

CREATE INDEX IF NOT EXISTS idx_stage_executions_order ON stage_executions (execution_order);

CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log (entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_log_actor ON audit_log (actor);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log (timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_log_cycle ON audit_log (cycle_id);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_cycle ON performance_metrics (cycle_id);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics (metric_name);

CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config (config_key);

CREATE INDEX IF NOT EXISTS idx_system_config_active ON system_config (is_active);

-- Audit trigger for cycles
CREATE TRIGGER update_cycles_updated_at BEFORE UPDATE ON cycles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Audit trigger for system config
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_entity_type VARCHAR(100),
    p_entity_id UUID,
    p_action VARCHAR(50),
    p_actor VARCHAR(200),
    p_details JSONB DEFAULT NULL,
    p_cycle_id UUID DEFAULT NULL,
    p_stage_execution_id UUID DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    audit_id UUID;
BEGIN
    INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json, cycle_id, stage_execution_id)
    VALUES (p_entity_type, p_entity_id, p_action, p_actor, p_details, p_cycle_id, p_stage_execution_id)
    RETURNING id INTO audit_id;
    
    RETURN audit_id;
END;
$$ LANGUAGE plpgsql;

-- Function to start a new cycle
CREATE OR REPLACE FUNCTION start_cycle(
    p_objective_ref VARCHAR(500),
    p_parent_cycle_id UUID DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    cycle_id UUID;
    parent_depth INTEGER := 0;
BEGIN
    -- Get parent depth if applicable
    IF p_parent_cycle_id IS NOT NULL THEN
        SELECT cycle_depth + 1 INTO parent_depth FROM cycles WHERE id = p_parent_cycle_id;
    END IF;
    
    -- Create new cycle
    INSERT INTO cycles (objective_ref, status, started_at, parent_cycle_id, cycle_depth)
    VALUES (p_objective_ref, 'active', NOW(), p_parent_cycle_id, parent_depth)
    RETURNING id INTO cycle_id;
    
    -- Log audit event
    PERFORM log_audit_event('cycle', cycle_id, 'create', 'system', 
                           jsonb_build_object('objective_ref', p_objective_ref, 'parent_cycle_id', p_parent_cycle_id),
                           cycle_id);
    
    RETURN cycle_id;
END;
$$ LANGUAGE plpgsql;

-- Function to complete a cycle
CREATE OR REPLACE FUNCTION complete_cycle(
    p_cycle_id UUID,
    p_status VARCHAR(50) DEFAULT 'completed'
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE cycles 
    SET status = p_status, completed_at = NOW(), updated_at = NOW()
    WHERE id = p_cycle_id;
    
    -- Log audit event
    PERFORM log_audit_event('cycle', p_cycle_id, 'update', 'system', 
                           jsonb_build_object('status', p_status, 'completed_at', NOW()),
                           p_cycle_id);
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;