-- Analytics Views for 108-Cycle Fractal System
-- Provides comprehensive analytics and monitoring capabilities for the Cosmic Council

-- ============================================================================
-- CYCLE PROGRESS AND PERFORMANCE ANALYTICS
-- ============================================================================

-- Real-time cycle progress dashboard
CREATE OR REPLACE VIEW v_cycle_dashboard AS
SELECT 
    cr.run_id,
    cr.objective_ref,
    c.title as cycle_title,
    cr.status,
    cr.priority,
    cr.created_at,
    cr.started_at,
    cr.completed_at,
    EXTRACT(EPOCH FROM (cr.completed_at - cr.started_at)) as duration_seconds,
    COUNT(csr.stage_run_id) as total_stages,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'completed') as completed_stages,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'failed') as failed_stages,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'running') as running_stages,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'pending') as pending_stages,
    ROUND(
        COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'completed')::NUMERIC / 
        NULLIF(COUNT(csr.stage_run_id), 0) * 100, 2
    ) as completion_percentage,
    crm.p95_latency_ms,
    crm.false_block_rate,
    crm.incident_rate,
    crm.cost_estimate
FROM cycle_runs cr
JOIN cycles c ON cr.cycle_id = c.cycle_id
LEFT JOIN cycle_stage_runs csr ON cr.run_id = csr.run_id
LEFT JOIN cycle_run_metrics crm ON cr.run_id = crm.run_id
GROUP BY cr.run_id, cr.objective_ref, c.title, cr.status, cr.priority, 
         cr.created_at, cr.started_at, cr.completed_at, crm.p95_latency_ms, 
         crm.false_block_rate, crm.incident_rate, crm.cost_estimate;

-- Stage performance analytics by enterprise and squad
CREATE OR REPLACE VIEW v_stage_performance_analytics AS
SELECT 
    cs.stage_id,
    cs.code,
    cs.name,
    e.name as enterprise_name,
    e.code as enterprise_code,
    sq.name as squad_name,
    sq.code as squad_code,
    rp.description as pass_description,
    rp.code as pass_code,
    COUNT(sr.stage_run_id) as total_executions,
    COUNT(sr.stage_run_id) FILTER (WHERE sr.status = 'completed') as successful_executions,
    COUNT(sr.stage_run_id) FILTER (WHERE sr.status = 'failed') as failed_executions,
    COUNT(sr.stage_run_id) FILTER (WHERE sr.status = 'timeout') as timeout_executions,
    ROUND(
        COUNT(sr.stage_run_id) FILTER (WHERE sr.status = 'completed')::NUMERIC / 
        NULLIF(COUNT(sr.stage_run_id), 0) * 100, 2
    ) as success_rate,
    AVG(EXTRACT(EPOCH FROM (sr.completed_at - sr.attempted_at)) * 1000) as avg_duration_ms,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (sr.completed_at - sr.attempted_at)) * 1000) as p50_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (sr.completed_at - sr.attempted_at)) * 1000) as p95_duration_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (sr.completed_at - sr.attempted_at)) * 1000) as p99_duration_ms,
    MAX(sr.completed_at) as last_execution,
    MIN(sr.attempted_at) as first_execution
FROM cycle_stages cs
JOIN enterprises e ON cs.enterprise_id = e.enterprise_id
JOIN squads sq ON cs.squad_id = sq.squad_id
JOIN redundancy_pass rp ON cs.pass_id = rp.pass_id
LEFT JOIN cycle_stage_runs sr ON cs.stage_id = sr.stage_id
GROUP BY cs.stage_id, cs.code, cs.name, e.name, e.code, sq.name, sq.code, 
         rp.description, rp.code;

-- Enterprise performance summary
CREATE OR REPLACE VIEW v_enterprise_performance AS
SELECT 
    e.enterprise_id,
    e.name as enterprise_name,
    e.code as enterprise_code,
    COUNT(DISTINCT cr.run_id) as total_cycles,
    COUNT(DISTINCT cr.run_id) FILTER (WHERE cr.status = 'completed') as completed_cycles,
    COUNT(DISTINCT cr.run_id) FILTER (WHERE cr.status = 'failed') as failed_cycles,
    COUNT(csr.stage_run_id) as total_stage_executions,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'completed') as successful_stages,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'failed') as failed_stages,
    ROUND(
        COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'completed')::NUMERIC / 
        NULLIF(COUNT(csr.stage_run_id), 0) * 100, 2
    ) as stage_success_rate,
    AVG(EXTRACT(EPOCH FROM (cr.completed_at - cr.started_at))) as avg_cycle_duration_seconds,
    AVG(crm.p95_latency_ms) as avg_p95_latency_ms,
    AVG(crm.false_block_rate) as avg_false_block_rate,
    AVG(crm.incident_rate) as avg_incident_rate,
    SUM(crm.cost_estimate) as total_cost_estimate
FROM enterprises e
JOIN cycle_stages cs ON e.enterprise_id = cs.enterprise_id
LEFT JOIN cycle_stage_runs csr ON cs.stage_id = csr.stage_id
LEFT JOIN cycle_runs cr ON csr.run_id = cr.run_id
LEFT JOIN cycle_run_metrics crm ON cr.run_id = crm.run_id
GROUP BY e.enterprise_id, e.name, e.code;

-- ============================================================================
-- INCIDENT AND DECISION ANALYTICS
-- ============================================================================

-- Incident heatmap by enterprise, squad, and time
CREATE OR REPLACE VIEW v_incident_heatmap AS
SELECT
    cs.enterprise_id,
    e.name as enterprise_name,
    e.code as enterprise_code,
    cs.squad_id,
    sq.name as squad_name,
    sq.code as squad_code,
    date_trunc ('hour', d.time) AS hour,
    date_trunc ('day', d.time) AS day,
    COUNT(*) AS total_incidents,
    COUNT(*) FILTER (
        WHERE
            i.severity = 'critical'
    ) as critical_incidents,
    COUNT(*) FILTER (
        WHERE
            i.severity = 'high'
    ) as high_incidents,
    COUNT(*) FILTER (
        WHERE
            i.severity = 'medium'
    ) as medium_incidents,
    COUNT(*) FILTER (
        WHERE
            i.severity = 'low'
    ) as low_incidents,
    AVG(d.latency_ms) as avg_decision_latency_ms
FROM
    decisions d
    JOIN incidents i ON d.decision_id = i.decision_id
    JOIN cycle_stage_runs csr ON csr.guard_decision_id = d.decision_id
    JOIN cycle_stages cs ON csr.stage_id = cs.stage_id
    JOIN enterprises e ON cs.enterprise_id = e.enterprise_id
    JOIN squads sq ON cs.squad_id = sq.squad_id
WHERE
    d.allow = false
GROUP BY
    cs.enterprise_id,
    e.name,
    e.code,
    cs.squad_id,
    sq.name,
    sq.code,
    date_trunc ('hour', d.time),
    date_trunc ('day', d.time);

-- Decision analytics with policy performance
CREATE OR REPLACE VIEW v_decision_analytics AS
SELECT 
    date_trunc('hour', d.time) AS hour,
    date_trunc('day', d.time) AS day,
    COUNT(*) as total_decisions,
    COUNT(*) FILTER (WHERE d.allow = true) as allowed_decisions,
    COUNT(*) FILTER (WHERE d.allow = false) as blocked_decisions,
    ROUND(
        COUNT(*) FILTER (WHERE d.allow = false)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as block_rate,
    AVG(d.latency_ms) as avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY d.latency_ms) as p95_latency_ms,
    COUNT(DISTINCT d.agent_id) as unique_agents,
    COUNT(DISTINCT csr.run_id) as unique_cycle_runs,
    -- Policy performance
    COUNT(*) FILTER (WHERE d.policy_refs @> ARRAY['guard/access']) as access_policy_decisions,
    COUNT(*) FILTER (WHERE d.policy_refs @> ARRAY['guard/brand']) as brand_policy_decisions,
    COUNT(*) FILTER (WHERE d.policy_refs @> ARRAY['guard/budget']) as budget_policy_decisions
FROM decisions d
LEFT JOIN cycle_stage_runs csr ON csr.guard_decision_id = d.decision_id
GROUP BY date_trunc('hour', d.time), date_trunc('day', d.time);

-- ============================================================================
-- POLICY EVOLUTION TRACKING
-- ============================================================================

-- Policy evolution summary and tracking
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
    COUNT(*) FILTER (
        WHERE
            status = 'archived'
    ) as archived_proposals,
    MAX(created_at) as last_proposal_date,
    MIN(created_at) as first_proposal_date,
    AVG(
        EXTRACT(
            EPOCH
            FROM (deployed_at - created_at)
        ) / 3600
    ) as avg_time_to_deployment_hours
FROM policy_evolution
GROUP BY
    target_scope;

-- Policy evolution timeline
CREATE OR REPLACE VIEW v_policy_evolution_timeline AS
SELECT
    proposal_id,
    target_scope,
    current_version,
    proposed_version,
    rationale,
    status,
    created_at,
    approved_at,
    deployed_at,
    EXTRACT(
        EPOCH
        FROM (approved_at - created_at)
    ) / 3600 as time_to_approval_hours,
    EXTRACT(
        EPOCH
        FROM (deployed_at - created_at)
    ) / 3600 as time_to_deployment_hours,
    sim_summary,
    impact_analysis
FROM policy_evolution
ORDER BY created_at DESC;

-- ============================================================================
-- N8N WORKFLOW EXECUTION ANALYTICS
-- ============================================================================

-- N8N workflow performance tracking
CREATE OR REPLACE VIEW v_n8n_workflow_analytics AS
SELECT 
    nwe.workflow_id,
    nwt.name as workflow_name,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE nwe.status = 'completed') as successful_executions,
    COUNT(*) FILTER (WHERE nwe.status = 'failed') as failed_executions,
    COUNT(*) FILTER (WHERE nwe.status = 'cancelled') as cancelled_executions,
    ROUND(
        COUNT(*) FILTER (WHERE nwe.status = 'completed')::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as success_rate,
    AVG(EXTRACT(EPOCH FROM (nwe.completed_at - nwe.started_at))) as avg_execution_duration_seconds,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (nwe.completed_at - nwe.started_at))) as p95_execution_duration_seconds,
    COUNT(DISTINCT nwe.run_id) as unique_cycle_runs,
    MAX(nwe.started_at) as last_execution,
    MIN(nwe.started_at) as first_execution
FROM n8n_workflow_executions nwe
LEFT JOIN n8n_workflow_templates nwt ON nwe.workflow_id = nwt.template_id::text
GROUP BY nwe.workflow_id, nwt.name;

-- ============================================================================
-- SYSTEM HEALTH AND MONITORING
-- ============================================================================

-- System health overview
CREATE OR REPLACE VIEW v_system_health AS
SELECT
    'cycle_runs' as metric_category,
    COUNT(*) as total_count,
    COUNT(*) FILTER (
        WHERE
            status = 'running'
    ) as active_count,
    COUNT(*) FILTER (
        WHERE
            status = 'completed'
    ) as completed_count,
    COUNT(*) FILTER (
        WHERE
            status = 'failed'
    ) as failed_count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (completed_at - started_at)
        )
    ) as avg_duration_seconds
FROM cycle_runs
WHERE
    created_at >= now() - interval '24 hours'
UNION ALL
SELECT
    'stage_runs' as metric_category,
    COUNT(*) as total_count,
    COUNT(*) FILTER (
        WHERE
            status = 'running'
    ) as active_count,
    COUNT(*) FILTER (
        WHERE
            status = 'completed'
    ) as completed_count,
    COUNT(*) FILTER (
        WHERE
            status = 'failed'
    ) as failed_count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (completed_at - attempted_at)
        )
    ) as avg_duration_seconds
FROM cycle_stage_runs
WHERE
    created_at >= now() - interval '24 hours'
UNION ALL
SELECT
    'decisions' as metric_category,
    COUNT(*) as total_count,
    COUNT(*) FILTER (
        WHERE
            allow = true
    ) as active_count,
    COUNT(*) FILTER (
        WHERE
            allow = false
    ) as completed_count,
    0 as failed_count,
    AVG(latency_ms) as avg_duration_seconds
FROM decisions
WHERE
    time >= now() - interval '24 hours'
UNION ALL
SELECT
    'incidents' as metric_category,
    COUNT(*) as total_count,
    COUNT(*) FILTER (
        WHERE
            status = 'open'
    ) as active_count,
    COUNT(*) FILTER (
        WHERE
            status = 'closed'
    ) as completed_count,
    COUNT(*) FILTER (
        WHERE
            status = 'mitigated'
    ) as failed_count,
    0 as avg_duration_seconds
FROM incidents
WHERE
    created_at >= now() - interval '24 hours';

-- Resource utilization by enterprise
CREATE OR REPLACE VIEW v_resource_utilization AS
SELECT
    e.name as enterprise_name,
    e.code as enterprise_code,
    ra.resource_type,
    SUM(ra.amount) as total_allocated,
    SUM(ra.amount) FILTER (
        WHERE
            ra.status = 'used'
    ) as total_used,
    SUM(ra.total_cost) as total_cost,
    AVG(ra.cost_per_unit) as avg_cost_per_unit,
    COUNT(*) as allocation_count,
    MAX(ra.created_at) as last_allocation
FROM
    resource_allocations ra
    JOIN enterprises e ON ra.enterprise = e.code
WHERE
    ra.created_at >= now() - interval '30 days'
GROUP BY
    e.name,
    e.code,
    ra.resource_type;

-- ============================================================================
-- ALERTING AND THRESHOLD MONITORING
-- ============================================================================

-- Performance threshold violations

CREATE OR REPLACE VIEW v_performance_violations AS
SELECT 
    'high_latency' as violation_type,
    csr.stage_run_id,
    csr.run_id,
    cs.code as stage_code,
    e.name as enterprise_name,
    EXTRACT(EPOCH FROM (csr.completed_at - csr.attempted_at)) * 1000 as actual_duration_ms,
    cs.expected_duration_ms,
    EXTRACT(EPOCH FROM (csr.completed_at - csr.attempted_at)) * 1000 - cs.expected_duration_ms as duration_excess_ms,
    csr.completed_at as violation_time
FROM cycle_stage_runs csr
JOIN cycle_stages cs ON csr.stage_id = cs.stage_id
JOIN enterprises e ON cs.enterprise_id = e.enterprise_id
WHERE csr.status = 'completed' 
AND EXTRACT(EPOCH FROM (csr.completed_at - csr.attempted_at)) * 1000 > cs.expected_duration_ms * 2
AND csr.completed_at >= now() - interval '24 hours'

UNION ALL

SELECT 
    'high_failure_rate' as violation_type,
    NULL as stage_run_id,
    cr.run_id,
    NULL as stage_code,
    e.name as enterprise_name,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'failed')::float / COUNT(csr.stage_run_id) * 100 as actual_failure_rate,
    10.0 as expected_failure_rate,
    COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'failed')::float / COUNT(csr.stage_run_id) * 100 - 10.0 as failure_rate_excess,
    cr.completed_at as violation_time
FROM cycle_runs cr
JOIN cycle_stage_runs csr ON cr.run_id = csr.run_id
JOIN cycle_stages cs ON csr.stage_id = cs.stage_id
JOIN enterprises e ON cs.enterprise_id = e.enterprise_id
WHERE cr.status = 'completed'
AND cr.completed_at >= now() - interval '24 hours'
GROUP BY cr.run_id, e.name, cr.completed_at
HAVING COUNT(csr.stage_run_id) FILTER (WHERE csr.status = 'failed')::float / COUNT(csr.stage_run_id) * 100 > 10.0;

-- ============================================================================
-- INDEXES FOR ANALYTICS VIEWS
-- ============================================================================

-- Create indexes to optimize analytics queries
CREATE INDEX IF NOT EXISTS idx_cycle_runs_created_at ON cycle_runs (created_at);

CREATE INDEX IF NOT EXISTS idx_cycle_runs_status ON cycle_runs (status);

CREATE INDEX IF NOT EXISTS idx_cycle_stage_runs_completed_at ON cycle_stage_runs (completed_at);

CREATE INDEX IF NOT EXISTS idx_cycle_stage_runs_attempted_at ON cycle_stage_runs (attempted_at);

CREATE INDEX IF NOT EXISTS idx_decisions_time ON decisions (time);

CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents (created_at);

CREATE INDEX IF NOT EXISTS idx_policy_evolution_created_at ON policy_evolution (created_at);

CREATE INDEX IF NOT EXISTS idx_n8n_executions_started_at ON n8n_workflow_executions (started_at);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_cycle_stage_runs_status_completed ON cycle_stage_runs (status, completed_at);

CREATE INDEX IF NOT EXISTS idx_decisions_allow_time ON decisions (allow, time);

CREATE INDEX IF NOT EXISTS idx_incidents_severity_created ON incidents (severity, created_at);

-- ============================================================================
-- USAGE EXAMPLES AND DOCUMENTATION
-- ============================================================================

/*
-- Example queries for common analytics needs:

-- 1. Get current cycle progress
SELECT * FROM v_cycle_dashboard WHERE status = 'running' ORDER BY created_at DESC;

-- 2. Find slowest stages
SELECT * FROM v_stage_performance_analytics ORDER BY p95_duration_ms DESC LIMIT 10;

-- 3. Monitor enterprise performance
SELECT * FROM v_enterprise_performance ORDER BY stage_success_rate DESC;

-- 4. Track incidents by time
SELECT * FROM v_incident_heatmap WHERE day = CURRENT_DATE ORDER BY hour;

-- 5. Monitor policy evolution
SELECT * FROM v_policy_evolution_timeline WHERE status = 'canary';

-- 6. Check system health
SELECT * FROM v_system_health ORDER BY metric_category;

-- 7. Find performance violations
SELECT * FROM v_performance_violations ORDER BY violation_time DESC;

-- 8. Resource utilization trends
SELECT * FROM v_resource_utilization ORDER BY total_cost DESC;
*/