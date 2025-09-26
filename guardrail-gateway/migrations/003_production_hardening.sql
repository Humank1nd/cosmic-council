-- Production Hardening Migration
-- Adds pgcrypto extension, performance indexes, budget caps, and provenance tracking

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Service-based decision lookup (for policy analysis)
CREATE INDEX IF NOT EXISTS idx_decisions_service ON decisions (
    (
        request -> 'resource' ->> 'service'
    )
);

-- Time-based partitioning support
CREATE INDEX IF NOT EXISTS idx_decisions_time ON decisions (time);

-- Agent-based decision lookup
CREATE INDEX IF NOT EXISTS idx_decisions_agent_id ON decisions (agent_id);

-- Enterprise-based decision lookup
CREATE INDEX IF NOT EXISTS idx_decisions_enterprise ON decisions (
    (
        request -> 'agent' ->> 'enterprise'
    )
);

-- Decision outcome lookup
CREATE INDEX IF NOT EXISTS idx_decisions_allow ON decisions (allow);

-- ============================================================================
-- BUDGET CAPS AND FINANCE MANAGEMENT
-- ============================================================================

-- Budget caps table for data-driven policy enforcement
CREATE TABLE IF NOT EXISTS finance_budget_caps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    resource_type TEXT NOT NULL, -- compute, storage, api_calls, etc.
    budget_cap DECIMAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    period TEXT NOT NULL, -- daily, weekly, monthly, quarterly
    effective_from TIMESTAMPTZ DEFAULT now(),
    effective_until TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Budget caps indexes
CREATE INDEX IF NOT EXISTS idx_budget_caps_enterprise ON finance_budget_caps (enterprise);

CREATE INDEX IF NOT EXISTS idx_budget_caps_resource_type ON finance_budget_caps (resource_type);

CREATE INDEX IF NOT EXISTS idx_budget_caps_effective ON finance_budget_caps (
    effective_from,
    effective_until
);

-- ============================================================================
-- KNOWLEDGE PROVENANCE TRACKING
-- ============================================================================

-- Knowledge provenance table for Red Owl's citation tracking
CREATE TABLE IF NOT EXISTS knowledge_provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    decision_id UUID REFERENCES decisions (decision_id) ON DELETE CASCADE,
    source_type TEXT NOT NULL, -- internal_db, external_api, vector_search, etc.
    source_url TEXT,
    source_hash TEXT, -- Content hash for integrity
    content_snippet TEXT,
    confidence_score FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Provenance indexes
CREATE INDEX IF NOT EXISTS idx_provenance_decision_id ON knowledge_provenance (decision_id);

CREATE INDEX IF NOT EXISTS idx_provenance_source_type ON knowledge_provenance (source_type);

CREATE INDEX IF NOT EXISTS idx_provenance_created_at ON knowledge_provenance (created_at);

-- ============================================================================
-- DECISIONS ARCHIVE FOR OLAP
-- ============================================================================

-- Create partitioned decisions table for long-term storage
CREATE TABLE IF NOT EXISTS decisions_archive (LIKE decisions INCLUDING ALL)
PARTITION BY
    RANGE (time);

-- Create monthly partitions (example for current month)
CREATE TABLE IF NOT EXISTS decisions_archive_2025_01 PARTITION OF decisions_archive FOR
VALUES
FROM ('2025-01-01') TO ('2025-02-01');

-- Create view for OLAP queries
CREATE OR REPLACE VIEW decisions_olap AS
SELECT 
    d.decision_id,
    d.time,
    d.agent_id,
    d.request->'agent'->>'enterprise' as enterprise,
    d.request->'agent'->>'squad' as squad,
    d.request->'resource'->>'service' as service,
    d.request->'resource'->>'action' as action,
    d.allow,
    d.policy_refs,
    d.latency_ms,
    d.explanation,
    -- Extract context metrics
    (d.request->'context'->>'risk')::FLOAT as risk_level,
    (d.request->'context'->>'estimated_cost')::DECIMAL as estimated_cost,
    (d.request->'context'->>'budget_cap')::DECIMAL as budget_cap,
    -- Provenance info
    kp.source_type,
    kp.confidence_score
FROM decisions d
LEFT JOIN knowledge_provenance kp ON d.decision_id = kp.decision_id;

-- ============================================================================
-- BUDGET CAPS CACHE VIEW
-- ============================================================================

-- View for fast budget cap lookups (cached by application)
CREATE OR REPLACE VIEW budget_caps_cache AS
SELECT
    enterprise,
    resource_type,
    budget_cap,
    currency,
    period,
    effective_from,
    effective_until,
    metadata
FROM finance_budget_caps
WHERE
    effective_from <= now()
    AND (
        effective_until IS NULL
        OR effective_until > now()
    )
ORDER BY
    enterprise,
    resource_type,
    effective_from DESC;

-- ============================================================================
-- SAMPLE BUDGET CAPS DATA
-- ============================================================================

-- Insert default budget caps for each enterprise
INSERT INTO
    finance_budget_caps (
        enterprise,
        resource_type,
        budget_cap,
        period
    )
VALUES (
        'red',
        'compute',
        1000.00,
        'monthly'
    ),
    (
        'red',
        'api_calls',
        10000,
        'daily'
    ),
    (
        'orange',
        'compute',
        800.00,
        'monthly'
    ),
    (
        'orange',
        'storage',
        500.00,
        'monthly'
    ),
    (
        'yellow',
        'compute',
        2000.00,
        'monthly'
    ),
    (
        'yellow',
        'api_calls',
        20000,
        'daily'
    ),
    (
        'green',
        'compute',
        500.00,
        'monthly'
    ),
    (
        'green',
        'storage',
        1000.00,
        'monthly'
    ),
    (
        'blue',
        'compute',
        600.00,
        'monthly'
    ),
    (
        'blue',
        'api_calls',
        15000,
        'daily'
    ),
    (
        'purple',
        'compute',
        400.00,
        'monthly'
    ),
    (
        'purple',
        'api_calls',
        5000,
        'daily'
    ) ON CONFLICT DO NOTHING;

-- ============================================================================
-- PROVENANCE OBLIGATION HANDLER FUNCTION
-- ============================================================================

-- Function to handle provenance obligations
CREATE OR REPLACE FUNCTION handle_provenance_obligation(
    p_decision_id UUID,
    p_provenance_data JSONB
) RETURNS VOID AS $$
BEGIN
    -- Insert provenance records for each source
    IF p_provenance_data ? 'sources' THEN
        FOR source_record IN SELECT * FROM jsonb_array_elements(p_provenance_data->'sources')
        LOOP
            INSERT INTO knowledge_provenance (
                decision_id,
                source_type,
                source_url,
                source_hash,
                content_snippet,
                confidence_score,
                metadata
            ) VALUES (
                p_decision_id,
                source_record->>'type',
                source_record->>'url',
                source_record->>'hash',
                source_record->>'snippet',
                COALESCE((source_record->>'confidence')::FLOAT, 0.0),
                source_record->'metadata'
            );
        END LOOP;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BUDGET TELEMETRY EMISSION FUNCTION
-- ============================================================================

-- Function to emit budget telemetry when obligations include emit_budget_usage
CREATE OR REPLACE FUNCTION emit_budget_telemetry(
    p_decision_id UUID,
    p_agent_id UUID,
    p_enterprise TEXT,
    p_resource_type TEXT,
    p_estimated_cost DECIMAL,
    p_budget_cap DECIMAL
) RETURNS JSONB AS $$
DECLARE
    telemetry_record JSONB;
BEGIN
    -- Create telemetry record
    telemetry_record := jsonb_build_object(
        'job_id', p_decision_id,
        'estimated_cost', p_estimated_cost,
        'cap', p_budget_cap,
        'cost_center', p_enterprise || '-' || p_resource_type,
        'agent_id', p_agent_id,
        'timestamp', now(),
        'enterprise', p_enterprise
    );
    
    -- In production, this would emit to Kafka topic 'budget.guard.v1'
    -- For now, we'll log it (replace with actual Kafka emission)
    RAISE NOTICE 'BUDGET_TELEMETRY: %', telemetry_record;
    
    RETURN telemetry_record;
END;
$$ LANGUAGE plpgsql;