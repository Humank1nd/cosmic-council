-- 108 Cycles Fractal System Migration
-- Implements the complete 6×6×3 fractal cycle model with PostgreSQL + N8N orchestration
-- Based on Cosmic Council's symbolic and structural foundations

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

-- Ensure pgcrypto is available for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================================
-- DIMENSION TABLES (6×6×3 = 108 stages)
-- ============================================================================

-- Enterprises dimension (6 enterprises)
CREATE TABLE IF NOT EXISTS enterprises (
    enterprise_id SMALLINT PRIMARY KEY CHECK (enterprise_id BETWEEN 1 AND 6),
    code TEXT UNIQUE NOT NULL CHECK (
        code IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Squads dimension (6 squads per enterprise, fractal structure)
CREATE TABLE IF NOT EXISTS squads (
    squad_id SMALLINT PRIMARY KEY CHECK (squad_id BETWEEN 1 AND 6),
    code TEXT UNIQUE NOT NULL CHECK (
        code IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Redundancy pass dimension (3 passes: decide, validate, reflect)
CREATE TABLE IF NOT EXISTS redundancy_pass (
    pass_id SMALLINT PRIMARY KEY CHECK (pass_id BETWEEN 1 AND 3),
    code TEXT UNIQUE NOT NULL CHECK (
        code IN (
            'decide',
            'validate',
            'reflect'
        )
    ),
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- CANONICAL 108 STAGE DEFINITIONS
-- ============================================================================

-- The core 108 stages (6 enterprises × 6 squads × 3 redundancy passes)
CREATE TABLE IF NOT EXISTS cycle_stages (
    stage_id SMALLINT PRIMARY KEY CHECK (stage_id BETWEEN 1 AND 108),
    enterprise_id SMALLINT NOT NULL REFERENCES enterprises (enterprise_id),
    squad_id SMALLINT NOT NULL REFERENCES squads (squad_id),
    pass_id SMALLINT NOT NULL REFERENCES redundancy_pass (pass_id),
    ordinal SMALLINT NOT NULL CHECK (ordinal BETWEEN 1 AND 108),
    code TEXT UNIQUE NOT NULL, -- e.g., red:red:decide:001
    name TEXT NOT NULL, -- human-friendly stage name
    description TEXT, -- detailed stage description
    policy_pin TEXT, -- optional policy bundle version pin
    expected_duration_ms INTEGER DEFAULT 5000, -- expected stage duration
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (
        enterprise_id,
        squad_id,
        pass_id,
        ordinal
    )
);

-- ============================================================================
-- CYCLE TEMPLATES AND RUNS
-- ============================================================================

-- Cycle templates (reusable cycle definitions)
CREATE TABLE IF NOT EXISTS cycles (
    cycle_id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    title TEXT NOT NULL,
    description TEXT,
    version TEXT DEFAULT '1.0.0',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Cycle stage transitions (directed graph among stages)
CREATE TABLE IF NOT EXISTS cycle_stage_transitions (
  transition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_stage_id SMALLINT NOT NULL REFERENCES cycle_stages(stage_id),
  to_stage_id SMALLINT NOT NULL REFERENCES cycle_stage_transitions(stage_id),
  kind TEXT NOT NULL CHECK (kind IN ('clockwise','redundancy','fallback','skip','error')),
  condition JSONB DEFAULT '{}'::jsonb,    -- optional evaluation conditions
  priority INTEGER DEFAULT 1,             -- transition priority
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(from_stage_id, to_stage_id, kind)
);

-- Runtime cycle execution instances
CREATE TABLE IF NOT EXISTS cycle_runs (
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cycle_id UUID NOT NULL REFERENCES cycles(cycle_id),
  objective_ref TEXT NOT NULL,            -- reference to objective/request
  status TEXT NOT NULL CHECK (status IN ('pending','running','paused','completed','failed','aborted')) DEFAULT 'pending',
  priority INTEGER DEFAULT 5,             -- 1=highest, 10=lowest
  created_at TIMESTAMPTZ DEFAULT now(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  policy_bundle TEXT,                     -- policy bundle snapshot used
  context JSONB DEFAULT '{}'::jsonb,      -- run-level context
  metadata JSONB DEFAULT '{}'::jsonb,     -- additional run metadata
  created_by TEXT DEFAULT 'system'        -- who/what initiated the run
);

-- Individual stage executions within a cycle run
CREATE TABLE IF NOT EXISTS cycle_stage_runs (
  stage_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES cycle_runs(run_id) ON DELETE CASCADE,
  stage_id SMALLINT NOT NULL REFERENCES cycle_stages(stage_id),
  status TEXT NOT NULL CHECK (status IN ('pending','running','blocked','completed','skipped','failed','timeout')) DEFAULT 'pending',
  attempted_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  guard_decision_id UUID,                 -- FK to decisions table
  context JSONB DEFAULT '{}'::jsonb,      -- stage input context
  output JSONB DEFAULT '{}'::jsonb,       -- stage output results
  metrics JSONB DEFAULT '{}'::jsonb,      -- stage performance metrics
  error_message TEXT,                     -- error details if failed
  retry_count INTEGER DEFAULT 0,          -- number of retry attempts
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(run_id, stage_id)
);

-- ============================================================================
-- POLICY EVOLUTION AND REFLECTION
-- ============================================================================

-- Policy evolution proposals (Purple Elephant's continuous improvement)
CREATE TABLE IF NOT EXISTS policy_evolution (
  proposal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT now(),
  created_by TEXT DEFAULT 'purple_policy_agent',
  target_scope TEXT NOT NULL,            -- e.g., guard/access
  current_version TEXT NOT NULL,         -- e.g., 1.2.0
  proposed_version TEXT NOT NULL,        -- e.g., 1.3.0-monitor
  rationale TEXT,                        -- why this change is proposed
  sim_summary JSONB DEFAULT '{}'::jsonb, -- simulation results summary
  impact_analysis JSONB DEFAULT '{}'::jsonb, -- predicted impact metrics
  status TEXT NOT NULL CHECK (status IN ('proposed','testing','canary','rejected','promoted','archived')) DEFAULT 'proposed',
  approved_by TEXT,                      -- who approved the change
  approved_at TIMESTAMPTZ,
  deployed_at TIMESTAMPTZ,
  rollback_reason TEXT,                  -- reason for rollback if applicable
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Cycle run metrics and analytics
CREATE TABLE IF NOT EXISTS cycle_run_metrics (
    run_id UUID PRIMARY KEY REFERENCES cycle_runs (run_id) ON DELETE CASCADE,
    stages_total SMALLINT NOT NULL DEFAULT 108,
    stages_completed SMALLINT NOT NULL DEFAULT 0,
    stages_failed SMALLINT NOT NULL DEFAULT 0,
    stages_skipped SMALLINT NOT NULL DEFAULT 0,
    total_duration_ms INTEGER, -- total cycle duration
    p95_latency_ms INTEGER, -- 95th percentile stage latency
    p99_latency_ms INTEGER, -- 99th percentile stage latency
    false_block_rate NUMERIC(5, 2), -- percentage of false blocks
    incident_rate NUMERIC(5, 2), -- incident rate percentage
    cost_estimate NUMERIC(18, 4), -- estimated total cost
    carbon_estimate NUMERIC(18, 6), -- estimated carbon footprint
    policy_violations INTEGER DEFAULT 0, -- number of policy violations
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- N8N WORKFLOW INTEGRATION
-- ============================================================================

-- N8N workflow execution tracking
CREATE TABLE IF NOT EXISTS n8n_workflow_executions (
  execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id TEXT NOT NULL,             -- N8N workflow identifier
  run_id UUID REFERENCES cycle_runs(run_id),
  status TEXT NOT NULL CHECK (status IN ('running','completed','failed','cancelled')) DEFAULT 'running',
  started_at TIMESTAMPTZ DEFAULT now(),
  completed_at TIMESTAMPTZ,
  input_data JSONB DEFAULT '{}'::jsonb,
  output_data JSONB DEFAULT '{}'::jsonb,
  error_message TEXT,
  execution_url TEXT,                    -- link to N8N execution
  metadata JSONB DEFAULT '{}'::jsonb
);

-- N8N workflow templates registry
CREATE TABLE IF NOT EXISTS n8n_workflow_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    name TEXT NOT NULL,
    description TEXT,
    workflow_json JSONB NOT NULL, -- N8N workflow definition
    version TEXT DEFAULT '1.0.0',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Cycle stages indexes
CREATE INDEX IF NOT EXISTS idx_cycle_stages_enterprise ON cycle_stages (enterprise_id);

CREATE INDEX IF NOT EXISTS idx_cycle_stages_squad ON cycle_stages (squad_id);

CREATE INDEX IF NOT EXISTS idx_cycle_stages_pass ON cycle_stages (pass_id);

CREATE INDEX IF NOT EXISTS idx_cycle_stages_ordinal ON cycle_stages (ordinal);

CREATE INDEX IF NOT EXISTS idx_cycle_stages_code ON cycle_stages (code);

-- Cycle runs indexes
CREATE INDEX IF NOT EXISTS idx_cycle_runs_status ON cycle_runs (status);

CREATE INDEX IF NOT EXISTS idx_cycle_runs_created_at ON cycle_runs (created_at);

CREATE INDEX IF NOT EXISTS idx_cycle_runs_objective ON cycle_runs (objective_ref);

CREATE INDEX IF NOT EXISTS idx_cycle_runs_priority ON cycle_runs (priority);

-- Stage runs indexes
CREATE INDEX IF NOT EXISTS idx_stage_runs_run ON cycle_stage_runs (run_id);

CREATE INDEX IF NOT EXISTS idx_stage_runs_stage ON cycle_stage_runs (stage_id);

CREATE INDEX IF NOT EXISTS idx_stage_runs_status ON cycle_stage_runs (status);

CREATE INDEX IF NOT EXISTS idx_stage_runs_decision ON cycle_stage_runs (guard_decision_id);

CREATE INDEX IF NOT EXISTS idx_stage_runs_attempted ON cycle_stage_runs (attempted_at);

-- Transitions indexes
CREATE INDEX IF NOT EXISTS idx_transitions_from ON cycle_stage_transitions (from_stage_id);

CREATE INDEX IF NOT EXISTS idx_transitions_to ON cycle_stage_transitions (to_stage_id);

CREATE INDEX IF NOT EXISTS idx_transitions_kind ON cycle_stage_transitions (kind);

-- Policy evolution indexes
CREATE INDEX IF NOT EXISTS idx_policy_evolution_status ON policy_evolution (status);

CREATE INDEX IF NOT EXISTS idx_policy_evolution_scope ON policy_evolution (target_scope);

CREATE INDEX IF NOT EXISTS idx_policy_evolution_created ON policy_evolution (created_at);

-- N8N workflow indexes
CREATE INDEX IF NOT EXISTS idx_n8n_executions_workflow ON n8n_workflow_executions (workflow_id);

CREATE INDEX IF NOT EXISTS idx_n8n_executions_run ON n8n_workflow_executions (run_id);

CREATE INDEX IF NOT EXISTS idx_n8n_executions_status ON n8n_workflow_executions (status);

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

-- High-level cycle progress view
CREATE OR REPLACE VIEW v_cycle_progress AS
SELECT 
    r.run_id, 
    r.objective_ref, 
    r.status,
    r.created_at,
    r.started_at,
    r.completed_at,
    COUNT(s.stage_run_id) FILTER (WHERE s.status='completed') AS stages_completed,
    COUNT(s.stage_run_id) FILTER (WHERE s.status='failed') AS stages_failed,
    COUNT(s.stage_run_id) FILTER (WHERE s.status='skipped') AS stages_skipped,
    COUNT(s.stage_run_id) AS stages_total,
    ROUND(
        COUNT(s.stage_run_id) FILTER (WHERE s.status='completed')::NUMERIC / 
        NULLIF(COUNT(s.stage_run_id), 0) * 100, 2
    ) AS completion_percentage
FROM cycle_runs r
LEFT JOIN cycle_stage_runs s USING(run_id)
GROUP BY r.run_id, r.objective_ref, r.status, r.created_at, r.started_at, r.completed_at;

-- Stage performance analytics
CREATE OR REPLACE VIEW v_stage_performance AS
SELECT
    cs.stage_id,
    cs.code,
    cs.name,
    e.name as enterprise_name,
    sq.name as squad_name,
    rp.description as pass_description,
    COUNT(sr.stage_run_id) as total_executions,
    COUNT(sr.stage_run_id) FILTER (
        WHERE
            sr.status = 'completed'
    ) as successful_executions,
    COUNT(sr.stage_run_id) FILTER (
        WHERE
            sr.status = 'failed'
    ) as failed_executions,
    AVG(
        EXTRACT(
            EPOCH
            FROM (
                    sr.completed_at - sr.attempted_at
                )
        ) * 1000
    ) as avg_duration_ms,
    PERCENTILE_CONT (0.95) WITHIN GROUP (
        ORDER BY EXTRACT(
                EPOCH
                FROM (
                        sr.completed_at - sr.attempted_at
                    )
            ) * 1000
    ) as p95_duration_ms
FROM
    cycle_stages cs
    JOIN enterprises e ON cs.enterprise_id = e.enterprise_id
    JOIN squads sq ON cs.squad_id = sq.squad_id
    JOIN redundancy_pass rp ON cs.pass_id = rp.pass_id
    LEFT JOIN cycle_stage_runs sr ON cs.stage_id = sr.stage_id
GROUP BY
    cs.stage_id,
    cs.code,
    cs.name,
    e.name,
    sq.name,
    rp.description;

-- Incident heatmap by enterprise/squad
CREATE OR REPLACE VIEW v_incident_heatmap AS
SELECT
    cs.enterprise_id,
    e.name as enterprise_name,
    cs.squad_id,
    sq.name as squad_name,
    date_trunc ('hour', d.time) AS hour,
    COUNT(*) AS incidents,
    COUNT(*) FILTER (
        WHERE
            i.severity = 'critical'
    ) as critical_incidents,
    COUNT(*) FILTER (
        WHERE
            i.severity = 'high'
    ) as high_incidents
FROM
    decisions d
    JOIN incidents i ON d.decision_id = i.decision_id
    JOIN cycle_stage_runs ss ON ss.guard_decision_id = d.decision_id
    JOIN cycle_stages cs ON cs.stage_id = ss.stage_id
    JOIN enterprises e ON cs.enterprise_id = e.enterprise_id
    JOIN squads sq ON cs.squad_id = sq.squad_id
WHERE
    d.allow = false
GROUP BY
    cs.enterprise_id,
    e.name,
    cs.squad_id,
    sq.name,
    date_trunc ('hour', d.time);

-- Policy evolution tracking
CREATE OR REPLACE VIEW v_policy_evolution_summary AS
SELECT
    target_scope,
    COUNT(*) as total_proposals,
    COUNT(*) FILTER (
        WHERE
            status = 'proposed'
    ) as pending_proposals,
    COUNT(*) FILTER (
        WHERE
            status = 'testing'
    ) as testing_proposals,
    COUNT(*) FILTER (
        WHERE
            status = 'canary'
    ) as canary_proposals,
    COUNT(*) FILTER (
        WHERE
            status = 'promoted'
    ) as promoted_proposals,
    COUNT(*) FILTER (
        WHERE
            status = 'rejected'
    ) as rejected_proposals,
    MAX(created_at) as last_proposal_date
FROM policy_evolution
GROUP BY
    target_scope;

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to get next stage in cycle
CREATE OR REPLACE FUNCTION get_next_stage(
    p_current_stage_id SMALLINT,
    p_run_id UUID DEFAULT NULL
) RETURNS SMALLINT AS $$
DECLARE
    next_stage_id SMALLINT;
BEGIN
    -- Get the next stage based on transitions
    SELECT to_stage_id INTO next_stage_id
    FROM cycle_stage_transitions
    WHERE from_stage_id = p_current_stage_id
    AND kind = 'clockwise'
    ORDER BY priority ASC
    LIMIT 1;
    
    RETURN next_stage_id;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate cycle run metrics
CREATE OR REPLACE FUNCTION calculate_cycle_metrics(p_run_id UUID) RETURNS VOID AS $$
DECLARE
    total_stages INTEGER;
    completed_stages INTEGER;
    failed_stages INTEGER;
    skipped_stages INTEGER;
    total_duration INTEGER;
    p95_latency INTEGER;
    p99_latency INTEGER;
BEGIN
    -- Count stages
    SELECT COUNT(*) INTO total_stages FROM cycle_stage_runs WHERE run_id = p_run_id;
    SELECT COUNT(*) INTO completed_stages FROM cycle_stage_runs WHERE run_id = p_run_id AND status = 'completed';
    SELECT COUNT(*) INTO failed_stages FROM cycle_stage_runs WHERE run_id = p_run_id AND status = 'failed';
    SELECT COUNT(*) INTO skipped_stages FROM cycle_stage_runs WHERE run_id = p_run_id AND status = 'skipped';
    
    -- Calculate duration
    SELECT EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000 INTO total_duration
    FROM cycle_runs WHERE run_id = p_run_id;
    
    -- Calculate latency percentiles
    SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - attempted_at)) * 1000) INTO p95_latency
    FROM cycle_stage_runs WHERE run_id = p_run_id AND status = 'completed';
    
    SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - attempted_at)) * 1000) INTO p99_latency
    FROM cycle_stage_runs WHERE run_id = p_run_id AND status = 'completed';
    
    -- Insert or update metrics
    INSERT INTO cycle_run_metrics (
        run_id, stages_total, stages_completed, stages_failed, stages_skipped,
        total_duration_ms, p95_latency_ms, p99_latency_ms
    ) VALUES (
        p_run_id, total_stages, completed_stages, failed_stages, skipped_stages,
        total_duration, p95_latency, p99_latency
    )
    ON CONFLICT (run_id) DO UPDATE SET
        stages_total = EXCLUDED.stages_total,
        stages_completed = EXCLUDED.stages_completed,
        stages_failed = EXCLUDED.stages_failed,
        stages_skipped = EXCLUDED.stages_skipped,
        total_duration_ms = EXCLUDED.total_duration_ms,
        p95_latency_ms = EXCLUDED.p95_latency_ms,
        p99_latency_ms = EXCLUDED.p99_latency_ms,
        updated_at = now();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to update cycle run metrics when stage runs change
CREATE OR REPLACE FUNCTION trigger_update_cycle_metrics() RETURNS TRIGGER AS $$
BEGIN
    -- Recalculate metrics for the affected run
    PERFORM calculate_cycle_metrics(NEW.run_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_cycle_metrics
    AFTER INSERT OR UPDATE OR DELETE ON cycle_stage_runs
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_cycle_metrics();

-- Trigger to update cycle run status when all stages complete
CREATE OR REPLACE FUNCTION trigger_update_cycle_status() RETURNS TRIGGER AS $$
DECLARE
    total_stages INTEGER;
    completed_stages INTEGER;
    failed_stages INTEGER;
    new_status TEXT;
BEGIN
    -- Count stages for this run
    SELECT COUNT(*) INTO total_stages FROM cycle_stage_runs WHERE run_id = NEW.run_id;
    SELECT COUNT(*) INTO completed_stages FROM cycle_stage_runs WHERE run_id = NEW.run_id AND status IN ('completed', 'skipped');
    SELECT COUNT(*) INTO failed_stages FROM cycle_stage_runs WHERE run_id = NEW.run_id AND status = 'failed';
    
    -- Determine new status
    IF completed_stages = total_stages THEN
        new_status := 'completed';
    ELSIF failed_stages > 0 AND (completed_stages + failed_stages) = total_stages THEN
        new_status := 'failed';
    ELSE
        new_status := 'running';
    END IF;
    
    -- Update cycle run status
    UPDATE cycle_runs 
    SET status = new_status, 
        completed_at = CASE WHEN new_status IN ('completed', 'failed') THEN now() ELSE completed_at END
    WHERE run_id = NEW.run_id AND status != new_status;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_cycle_status
    AFTER UPDATE ON cycle_stage_runs
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_cycle_status();