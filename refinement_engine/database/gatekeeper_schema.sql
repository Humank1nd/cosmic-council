-- Purple Elephant Gatekeeper - Database Schema Extensions
-- This extends the main schema with tables for reflection reports and gatekeeper decisions

-- Reflection Reports Table
CREATE TABLE IF NOT EXISTS reflection_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    cycle_id UUID NOT NULL,
    summary TEXT NOT NULL,
    contradictions JSONB DEFAULT '[]',
    empathy_insights JSONB DEFAULT '{}',
    sector_analysis JSONB DEFAULT '{}',
    confidence_indicators JSONB DEFAULT '{}',
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cycle_id) REFERENCES layer_runs (id) ON DELETE CASCADE
);

-- Gatekeeper Decisions Table
CREATE TABLE IF NOT EXISTS gatekeeper_decisions (
    decision_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    report_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (
        status IN (
            'sufficient',
            'insufficient',
            'needs_refinement',
            'contradictory'
        )
    ),
    confidence_score DECIMAL(3, 2) NOT NULL CHECK (
        confidence_score >= 0
        AND confidence_score <= 1
    ),
    completeness_score DECIMAL(3, 2) NOT NULL CHECK (
        completeness_score >= 0
        AND completeness_score <= 1
    ),
    alignment_score DECIMAL(3, 2) NOT NULL CHECK (
        alignment_score >= 0
        AND alignment_score <= 1
    ),
    failing_sectors JSONB DEFAULT '[]',
    routing_decision VARCHAR(50) NOT NULL CHECK (
        routing_decision IN (
            'exit_upward',
            'descend_sector',
            'retry_cycle',
            'escalate_human'
        )
    ),
    routing_target TEXT,
    rationale TEXT NOT NULL,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES reflection_reports (report_id) ON DELETE CASCADE
);

-- Sector Refinements Table (for tracking sector-specific descents)
CREATE TABLE IF NOT EXISTS sector_refinements (
    refinement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL,
    sector VARCHAR(50) NOT NULL CHECK (
        sector IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ),
    from_layer VARCHAR(50) NOT NULL,
    to_layer VARCHAR(50) NOT NULL,
    rationale TEXT NOT NULL,
    decision_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE,
        FOREIGN KEY (from_layer) REFERENCES layers (name),
        FOREIGN KEY (to_layer) REFERENCES layers (name)
);

-- Cycle Tracking Table (for tracking cycles per layer)
CREATE TABLE IF NOT EXISTS cycle_tracking (
    cycle_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL,
    layer VARCHAR(50) NOT NULL,
    cycle_number INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (
        status IN (
            'active',
            'completed',
            'failed',
            'escalated'
        )
    ),
    started_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        finished_at TIMESTAMP
    WITH
        TIME ZONE,
        total_cost_usd DECIMAL(10, 4) DEFAULT 0.0,
        total_latency_ms INTEGER DEFAULT 0,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE,
        FOREIGN KEY (layer) REFERENCES layers (name),
        UNIQUE (
            problem_id,
            layer,
            cycle_number
        )
);

-- Solution Contracts Table (for storing success criteria)
CREATE TABLE IF NOT EXISTS solution_contracts (
    contract_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL,
    constraints JSONB DEFAULT '{}',
    quality_metrics JSONB DEFAULT '{}',
    human_factors JSONB DEFAULT '{}',
    acceptance_criteria JSONB DEFAULT '{}',
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE
);

-- Human Escalations Table (for tracking human interventions)
CREATE TABLE IF NOT EXISTS human_escalations (
    escalation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL,
    cycle_id UUID,
    reason TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'in_progress',
            'resolved',
            'rejected'
        )
    ),
    human_feedback JSONB DEFAULT '{}',
    resolution TEXT,
    escalated_by VARCHAR(100),
    resolved_by VARCHAR(100),
    escalated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    WITH
        TIME ZONE,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE,
        FOREIGN KEY (cycle_id) REFERENCES cycle_tracking (cycle_id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_reflection_reports_cycle_id ON reflection_reports (cycle_id);

CREATE INDEX IF NOT EXISTS idx_reflection_reports_created_at ON reflection_reports (created_at);

CREATE INDEX IF NOT EXISTS idx_gatekeeper_decisions_report_id ON gatekeeper_decisions (report_id);

CREATE INDEX IF NOT EXISTS idx_gatekeeper_decisions_status ON gatekeeper_decisions (status);

CREATE INDEX IF NOT EXISTS idx_gatekeeper_decisions_routing_decision ON gatekeeper_decisions (routing_decision);

CREATE INDEX IF NOT EXISTS idx_sector_refinements_problem_id ON sector_refinements (problem_id);

CREATE INDEX IF NOT EXISTS idx_sector_refinements_sector ON sector_refinements (sector);

CREATE INDEX IF NOT EXISTS idx_cycle_tracking_problem_id ON cycle_tracking (problem_id);

CREATE INDEX IF NOT EXISTS idx_cycle_tracking_layer ON cycle_tracking (layer);

CREATE INDEX IF NOT EXISTS idx_cycle_tracking_status ON cycle_tracking (status);

CREATE INDEX IF NOT EXISTS idx_solution_contracts_problem_id ON solution_contracts (problem_id);

CREATE INDEX IF NOT EXISTS idx_human_escalations_problem_id ON human_escalations (problem_id);

CREATE INDEX IF NOT EXISTS idx_human_escalations_status ON human_escalations (status);

-- Create triggers for updated_at timestamps
CREATE TRIGGER update_reflection_reports_updated_at BEFORE UPDATE ON reflection_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gatekeeper_decisions_updated_at BEFORE UPDATE ON gatekeeper_decisions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sector_refinements_updated_at BEFORE UPDATE ON sector_refinements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cycle_tracking_updated_at BEFORE UPDATE ON cycle_tracking FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solution_contracts_updated_at BEFORE UPDATE ON solution_contracts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_human_escalations_updated_at BEFORE UPDATE ON human_escalations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW gatekeeper_analytics AS
SELECT
    DATE_TRUNC ('day', gd.created_at) as date,
    gd.status,
    gd.routing_decision,
    COUNT(*) as decision_count,
    AVG(gd.confidence_score) as avg_confidence,
    AVG(gd.completeness_score) as avg_completeness,
    AVG(gd.alignment_score) as avg_alignment,
    COUNT(*) FILTER (
        WHERE
            gd.routing_decision = 'exit_upward'
    ) as solutions_delivered,
    COUNT(*) FILTER (
        WHERE
            gd.routing_decision = 'descend_sector'
    ) as sector_descents,
    COUNT(*) FILTER (
        WHERE
            gd.routing_decision = 'retry_cycle'
    ) as cycle_retries,
    COUNT(*) FILTER (
        WHERE
            gd.routing_decision = 'escalate_human'
    ) as human_escalations
FROM gatekeeper_decisions gd
GROUP BY
    DATE_TRUNC ('day', gd.created_at),
    gd.status,
    gd.routing_decision
ORDER BY date DESC;

CREATE OR REPLACE VIEW sector_performance AS
SELECT
    sr.sector,
    sr.from_layer,
    sr.to_layer,
    COUNT(*) as refinement_count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (sr.updated_at - sr.created_at)
        )
    ) as avg_refinement_time_seconds,
    COUNT(*) FILTER (
        WHERE
            sr.from_layer = sr.to_layer
    ) as same_layer_refinements,
    COUNT(*) FILTER (
        WHERE
            sr.from_layer != sr.to_layer
    ) as cross_layer_refinements
FROM sector_refinements sr
GROUP BY
    sr.sector,
    sr.from_layer,
    sr.to_layer
ORDER BY refinement_count DESC;

CREATE OR REPLACE VIEW cycle_efficiency AS
SELECT
    ct.layer,
    ct.cycle_number,
    COUNT(*) as total_cycles,
    AVG(ct.total_cost_usd) as avg_cost_usd,
    AVG(ct.total_latency_ms) as avg_latency_ms,
    COUNT(*) FILTER (
        WHERE
            ct.status = 'completed'
    ) as completed_cycles,
    COUNT(*) FILTER (
        WHERE
            ct.status = 'failed'
    ) as failed_cycles,
    COUNT(*) FILTER (
        WHERE
            ct.status = 'escalated'
    ) as escalated_cycles,
    AVG(
        EXTRACT(
            EPOCH
            FROM (
                    ct.finished_at - ct.started_at
                )
        )
    ) as avg_cycle_duration_seconds
FROM cycle_tracking ct
GROUP BY
    ct.layer,
    ct.cycle_number
ORDER BY ct.layer, ct.cycle_number;

-- Create functions for common operations
CREATE OR REPLACE FUNCTION get_problem_reflection_history(problem_uuid UUID)
RETURNS TABLE (
    report_id UUID,
    summary TEXT,
    confidence_score DECIMAL(3,2),
    completeness_score DECIMAL(3,2),
    alignment_score DECIMAL(3,2),
    status VARCHAR(50),
    routing_decision VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rr.report_id,
        rr.summary,
        gd.confidence_score,
        gd.completeness_score,
        gd.alignment_score,
        gd.status,
        gd.routing_decision,
        rr.created_at
    FROM reflection_reports rr
    JOIN gatekeeper_decisions gd ON rr.report_id = gd.report_id
    JOIN cycle_tracking ct ON rr.cycle_id = ct.cycle_id
    WHERE ct.problem_id = problem_uuid
    ORDER BY rr.created_at DESC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_sector_refinement_count(problem_uuid UUID, sector_name VARCHAR(50))
RETURNS INTEGER AS $$
DECLARE
    refinement_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO refinement_count
    FROM sector_refinements
    WHERE problem_id = problem_uuid AND sector = sector_name;
    
    RETURN refinement_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_layer_cycle_count(problem_uuid UUID, layer_name VARCHAR(50))
RETURNS INTEGER AS $$
DECLARE
    cycle_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO cycle_count
    FROM cycle_tracking
    WHERE problem_id = problem_uuid AND layer = layer_name;
    
    RETURN cycle_count;
END;
$$ LANGUAGE plpgsql;

-- Create a function to clean up old reflection data
CREATE OR REPLACE FUNCTION cleanup_old_reflections(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete old reflection reports and related data
    DELETE FROM gatekeeper_decisions 
    WHERE report_id IN (
        SELECT report_id FROM reflection_reports 
        WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep
    );
    
    DELETE FROM reflection_reports 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Delete old cycle tracking data
    DELETE FROM cycle_tracking 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    -- Delete old human escalations
    DELETE FROM human_escalations 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep
    AND status IN ('resolved', 'rejected');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Insert default solution contract templates
INSERT INTO
    solution_contracts (
        problem_id,
        constraints,
        quality_metrics,
        human_factors,
        acceptance_criteria
    )
VALUES (
        (
            SELECT id
            FROM problems
            LIMIT 1
        ), -- This would be replaced with actual problem_id
        '{"budget_limit": 50000, "time_limit_days": 30, "resource_constraints": ["human", "material"]}',
        '{"confidence_threshold": 0.8, "completeness_threshold": 0.75, "novelty_threshold": 0.3}',
        '{"stakeholder_satisfaction": 0.8, "ethical_compliance": true, "accessibility": true}',
        '{"deliverable_quality": "high", "documentation_completeness": "full", "testing_coverage": 0.9}'
    ) ON CONFLICT DO NOTHING;

-- Final message
DO $$
BEGIN
    RAISE NOTICE 'Purple Elephant Gatekeeper database schema initialized successfully!';
    RAISE NOTICE 'Added tables: reflection_reports, gatekeeper_decisions, sector_refinements, cycle_tracking, solution_contracts, human_escalations';
    RAISE NOTICE 'Added views: gatekeeper_analytics, sector_performance, cycle_efficiency';
    RAISE NOTICE 'Added functions: get_problem_reflection_history, get_sector_refinement_count, get_layer_cycle_count, cleanup_old_reflections';
END $$;