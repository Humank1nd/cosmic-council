-- Cosmic Council Refinement Engine Database Schema
-- Extends the existing schema to support Deci → Quecto refinement layers
-- Implements the problem-refinement ladder with ROYGBV cycles per layer

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- REFINEMENT LAYERS DEFINITION
-- ============================================================================

-- Define the 12 refinement layers (Deci → Quecto)
CREATE TABLE layers (
    layer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name VARCHAR(20) UNIQUE NOT NULL CHECK (
        name IN (
            'deci',
            'centi',
            'milli',
            'micro',
            'nano',
            'pico',
            'femto',
            'atto',
            'zepto',
            'yocto',
            'ronto',
            'quecto'
        )
    ),
    order_idx INTEGER UNIQUE NOT NULL CHECK (
        order_idx >= 1
        AND order_idx <= 12
    ),
    scale_exponent INTEGER NOT NULL, -- 10^-1, 10^-2, etc.
    description TEXT,
    purpose TEXT,
    example_reframing TEXT,
    toolchain_type VARCHAR(50), -- e.g., 'llm', 'optimization', 'simulation'
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Insert the 12 refinement layers
INSERT INTO
    layers (
        name,
        order_idx,
        scale_exponent,
        description,
        purpose,
        example_reframing,
        toolchain_type
    )
VALUES (
        'deci',
        1,
        -1,
        'Surface Reasoning',
        'Big-picture framing of the problem',
        'How do we reduce carbon emissions globally?',
        'llm'
    ),
    (
        'centi',
        2,
        -2,
        'Problem Decomposition',
        'Break problem into parts, identify dependencies',
        'Which industries account for the largest share?',
        'graph_analysis'
    ),
    (
        'milli',
        3,
        -3,
        'Focused Research',
        'Deep research on each subproblem',
        'How can steel production be made cleaner?',
        'rag'
    ),
    (
        'micro',
        4,
        -6,
        'Detailed Analysis',
        'Precision modeling and validation',
        'What innovations in smelting could cut energy?',
        'statistical'
    ),
    (
        'nano',
        5,
        -9,
        'Symbolic & Formal Methods',
        'Structured reasoning with rules and logic',
        'What catalysts can reduce CO₂ in steel reactions?',
        'symbolic'
    ),
    (
        'pico',
        6,
        -12,
        'Algorithmic Optimization',
        'Find optimal solutions to well-structured problems',
        'What quantum properties affect catalyst efficiency?',
        'optimization'
    ),
    (
        'femto',
        7,
        -15,
        'Micro-Mechanistic Modeling',
        'Simulate inner mechanics of the system',
        'What resonance effects matter in the reaction?',
        'simulation'
    ),
    (
        'atto',
        8,
        -18,
        'Edge Case Exploration',
        'Stress-test against rare scenarios and anomalies',
        'How could quantum algorithms optimize this?',
        'adversarial'
    ),
    (
        'zepto',
        9,
        -21,
        'Creative Divergence',
        'Wild exploration of unconventional paths',
        'Exotic particle dynamics',
        'stochastic'
    ),
    (
        'yocto',
        10,
        -24,
        'Knowledge Compression',
        'Distill patterns from the massive solution space',
        'Field interactions',
        'clustering'
    ),
    (
        'ronto',
        11,
        -27,
        'Meta-Reasoning',
        'Reflect on how the problem-solving process itself is being done',
        'Hypothetical constructs',
        'meta_learning'
    ),
    (
        'quecto',
        12,
        -30,
        'Chaos & Breakthroughs',
        'Last resort — chaos-based exploration for breakthrough insights',
        'Is this even the right framing of reality to solve this?',
        'quantum_chaos'
    );

-- ============================================================================
-- PROBLEM TRACKING (Enhanced)
-- ============================================================================

-- Enhanced problems table for refinement tracking
CREATE TABLE problems (
    problem_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    current_layer_id UUID REFERENCES layers (layer_id),
    status VARCHAR(20) DEFAULT 'open' CHECK (
        status IN (
            'open',
            'in_progress',
            'closed',
            'escalated'
        )
    ),
    confidence_threshold DECIMAL(3, 2) DEFAULT 0.85,
    completeness_threshold DECIMAL(3, 2) DEFAULT 0.80,
    max_revolutions_per_layer INTEGER DEFAULT 3,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- LAYER RUNS (Complete ROYGBV cycles per layer)
-- ============================================================================

-- Track complete ROYGBV cycles at each layer
CREATE TABLE layer_runs (
    layer_run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL REFERENCES problems (problem_id) ON DELETE CASCADE,
    layer_id UUID NOT NULL REFERENCES layers (layer_id),
    revolution INTEGER NOT NULL DEFAULT 1, -- Which revolution at this layer (1, 2, 3...)
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'in_progress',
            'completed',
            'failed'
        )
    ),
    started_at TIMESTAMP
    WITH
        TIME ZONE,
        finished_at TIMESTAMP
    WITH
        TIME ZONE,
        total_cost_usd DECIMAL(10, 2) DEFAULT 0.0,
        total_latency_ms INTEGER DEFAULT 0,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECTOR RUNS (Individual ROYGBV sector executions)
-- ============================================================================

-- Track individual sector executions within a layer run
CREATE TABLE sector_runs (
    sector_run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    layer_run_id UUID NOT NULL REFERENCES layer_runs (layer_run_id) ON DELETE CASCADE,
    sector VARCHAR(20) NOT NULL CHECK (
        sector IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ),
    sector_order INTEGER NOT NULL CHECK (
        sector_order >= 1
        AND sector_order <= 6
    ),
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'in_progress',
            'completed',
            'failed'
        )
    ),
    started_at TIMESTAMP
    WITH
        TIME ZONE,
        finished_at TIMESTAMP
    WITH
        TIME ZONE,
        output_json JSONB,
        metrics JSONB, -- {cost, latency_ms, novelty, confidence, completeness}
        error_message TEXT,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- REFINEMENTS (Layer descent decisions)
-- ============================================================================

-- Track when and why problems are refined to deeper layers
CREATE TABLE refinements (
    refinement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL REFERENCES problems (problem_id) ON DELETE CASCADE,
    from_layer_id UUID NOT NULL REFERENCES layers (layer_id),
    to_layer_id UUID NOT NULL REFERENCES layers (layer_id),
    rationale TEXT NOT NULL,
    refined_question TEXT NOT NULL,
    escalator_decision JSONB, -- Full escalator decision context
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ANSWERS (Final solutions)
-- ============================================================================

-- Store final answers and solutions
CREATE TABLE answers (
    answer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL REFERENCES problems (problem_id) ON DELETE CASCADE,
    layer_id UUID NOT NULL REFERENCES layers (layer_id),
    solution_json JSONB NOT NULL,
    confidence_score DECIMAL(3, 2) NOT NULL CHECK (
        confidence_score >= 0.0
        AND confidence_score <= 1.0
    ),
    completeness_score DECIMAL(3, 2) NOT NULL CHECK (
        completeness_score >= 0.0
        AND completeness_score <= 1.0
    ),
    novelty_score DECIMAL(3, 2) DEFAULT 0.0,
    alignment_score DECIMAL(3, 2) DEFAULT 1.0,
    net_benefit_score DECIMAL(3, 2) DEFAULT 0.0,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- LAYER POLICIES (Per-layer configuration)
-- ============================================================================

-- Configuration for each layer (budgets, SLOs, etc.)
CREATE TABLE layer_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    layer_id UUID NOT NULL REFERENCES layers (layer_id),
    max_revolutions INTEGER DEFAULT 3,
    budget_usd DECIMAL(10, 2) DEFAULT 100.0,
    carbon_ceiling_gco2e DECIMAL(10, 4) DEFAULT 0.1,
    p95_latency_ms INTEGER DEFAULT 30000,
    confidence_threshold DECIMAL(3, 2) DEFAULT 0.85,
    completeness_threshold DECIMAL(3, 2) DEFAULT 0.80,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Insert default policies for each layer
INSERT INTO
    layer_policies (
        layer_id,
        max_revolutions,
        budget_usd,
        carbon_ceiling_gco2e,
        p95_latency_ms,
        confidence_threshold,
        completeness_threshold
    )
SELECT
    l.layer_id,
    CASE
        WHEN l.order_idx <= 3 THEN 5 -- Higher layers get more revolutions
        WHEN l.order_idx <= 6 THEN 3 -- Middle layers
        ELSE 2 -- Lower layers get fewer revolutions
    END,
    CASE
        WHEN l.order_idx <= 3 THEN 200.0 -- Higher layers get more budget
        WHEN l.order_idx <= 6 THEN 100.0
        ELSE 50.0 -- Lower layers get less budget
    END,
    CASE
        WHEN l.order_idx <= 3 THEN 0.2
        WHEN l.order_idx <= 6 THEN 0.1
        ELSE 0.05
    END,
    CASE
        WHEN l.order_idx <= 3 THEN 60000 -- Higher layers can take longer
        WHEN l.order_idx <= 6 THEN 30000
        ELSE 15000 -- Lower layers should be faster
    END,
    CASE
        WHEN l.order_idx <= 3 THEN 0.80 -- Higher layers can have lower confidence
        WHEN l.order_idx <= 6 THEN 0.85
        ELSE 0.90 -- Lower layers need higher confidence
    END,
    CASE
        WHEN l.order_idx <= 3 THEN 0.75
        WHEN l.order_idx <= 6 THEN 0.80
        ELSE 0.85
    END
FROM layers l;

-- ============================================================================
-- HANDOFFS (Inter-sector communication)
-- ============================================================================

-- Track handoffs between sectors
CREATE TABLE handoffs (
    handoff_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    sector_run_id UUID NOT NULL REFERENCES sector_runs (sector_run_id) ON DELETE CASCADE,
    from_sector VARCHAR(20) NOT NULL,
    to_sector VARCHAR(20) NOT NULL,
    handoff_data JSONB NOT NULL, -- {evidence_refs, assumptions, constraints, context}
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- TELEMETRY (Performance and monitoring)
-- ============================================================================

-- Track telemetry data for monitoring and optimization
CREATE TABLE telemetry (
    telemetry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID REFERENCES problems (problem_id),
    layer_run_id UUID REFERENCES layer_runs (layer_run_id),
    sector_run_id UUID REFERENCES sector_runs (sector_run_id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 4) NOT NULL,
    metric_unit VARCHAR(50),
    metadata JSONB,
    recorded_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Problems indexes
CREATE INDEX idx_problems_status ON problems (status);

CREATE INDEX idx_problems_current_layer ON problems (current_layer_id);

CREATE INDEX idx_problems_created_at ON problems (created_at);

-- Layer runs indexes
CREATE INDEX idx_layer_runs_problem_id ON layer_runs (problem_id);

CREATE INDEX idx_layer_runs_layer_id ON layer_runs (layer_id);

CREATE INDEX idx_layer_runs_status ON layer_runs (status);

CREATE INDEX idx_layer_runs_revolution ON layer_runs (
    problem_id,
    layer_id,
    revolution
);

-- Sector runs indexes
CREATE INDEX idx_sector_runs_layer_run_id ON sector_runs (layer_run_id);

CREATE INDEX idx_sector_runs_sector ON sector_runs (sector);

CREATE INDEX idx_sector_runs_status ON sector_runs (status);

CREATE INDEX idx_sector_runs_order ON sector_runs (layer_run_id, sector_order);

-- Refinements indexes
CREATE INDEX idx_refinements_problem_id ON refinements (problem_id);

CREATE INDEX idx_refinements_from_layer ON refinements (from_layer_id);

CREATE INDEX idx_refinements_to_layer ON refinements (to_layer_id);

-- Answers indexes
CREATE INDEX idx_answers_problem_id ON answers (problem_id);

CREATE INDEX idx_answers_layer_id ON answers (layer_id);

CREATE INDEX idx_answers_confidence ON answers (confidence_score);

-- Handoffs indexes
CREATE INDEX idx_handoffs_sector_run_id ON handoffs (sector_run_id);

CREATE INDEX idx_handoffs_sectors ON handoffs (from_sector, to_sector);

-- Telemetry indexes
CREATE INDEX idx_telemetry_problem_id ON telemetry (problem_id);

CREATE INDEX idx_telemetry_metric_name ON telemetry (metric_name);

CREATE INDEX idx_telemetry_recorded_at ON telemetry (recorded_at);

-- ============================================================================
-- TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers
CREATE TRIGGER update_problems_updated_at 
    BEFORE UPDATE ON problems 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_layer_policies_updated_at 
    BEFORE UPDATE ON layer_policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to validate sector order
CREATE OR REPLACE FUNCTION validate_sector_order()
RETURNS TRIGGER AS $$
DECLARE
    expected_order INTEGER;
    sector_order_map JSONB := '{"red": 1, "orange": 2, "yellow": 3, "green": 4, "blue": 5, "purple": 6}';
BEGIN
    expected_order := (sector_order_map ->> NEW.sector)::INTEGER;
    
    IF NEW.sector_order != expected_order THEN
        RAISE EXCEPTION 'Invalid sector order: % should be %, got %', NEW.sector, expected_order, NEW.sector_order;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply sector order validation trigger
CREATE TRIGGER validate_sector_order_trigger 
    BEFORE INSERT OR UPDATE ON sector_runs 
    FOR EACH ROW EXECUTE FUNCTION validate_sector_order();

-- Function to ensure layer run completion before refinement
CREATE OR REPLACE FUNCTION validate_refinement_timing()
RETURNS TRIGGER AS $$
DECLARE
    layer_run_status VARCHAR(20);
BEGIN
    -- Check if the from_layer has a completed layer_run
    SELECT lr.status INTO layer_run_status
    FROM layer_runs lr
    WHERE lr.problem_id = NEW.problem_id 
    AND lr.layer_id = NEW.from_layer_id
    ORDER BY lr.revolution DESC
    LIMIT 1;
    
    IF layer_run_status != 'completed' THEN
        RAISE EXCEPTION 'Cannot refine from layer % - no completed layer run found', NEW.from_layer_id;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply refinement timing validation trigger
CREATE TRIGGER validate_refinement_timing_trigger 
    BEFORE INSERT ON refinements 
    FOR EACH ROW EXECUTE FUNCTION validate_refinement_timing();

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to get next layer
CREATE OR REPLACE FUNCTION get_next_layer(current_layer_name VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    next_layer_name VARCHAR;
BEGIN
    SELECT l2.name INTO next_layer_name
    FROM layers l1
    JOIN layers l2 ON l2.order_idx = l1.order_idx + 1
    WHERE l1.name = current_layer_name;
    
    RETURN next_layer_name;
END;
$$ LANGUAGE plpgsql;

-- Function to get layer by name
CREATE OR REPLACE FUNCTION get_layer_by_name(layer_name VARCHAR)
RETURNS UUID AS $$
DECLARE
    layer_uuid UUID;
BEGIN
    SELECT layer_id INTO layer_uuid
    FROM layers
    WHERE name = layer_name;
    
    RETURN layer_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to check if layer has next
CREATE OR REPLACE FUNCTION layer_has_next(layer_name VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    has_next BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM layers l1
        JOIN layers l2 ON l2.order_idx = l1.order_idx + 1
        WHERE l1.name = layer_name
    ) INTO has_next;
    
    RETURN has_next;
END;
$$ LANGUAGE plpgsql;

-- Function to get problem refinement genealogy
CREATE OR REPLACE FUNCTION get_problem_genealogy(p_problem_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'problem_id', p_problem_id,
        'refinements', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'refinement_id', r.refinement_id,
                    'from_layer', l1.name,
                    'to_layer', l2.name,
                    'rationale', r.rationale,
                    'refined_question', r.refined_question,
                    'created_at', r.created_at
                )
            )
            FROM refinements r
            JOIN layers l1 ON r.from_layer_id = l1.layer_id
            JOIN layers l2 ON r.to_layer_id = l2.layer_id
            WHERE r.problem_id = p_problem_id
            ORDER BY r.created_at
        ),
        'layer_runs', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'layer_run_id', lr.layer_run_id,
                    'layer', l.name,
                    'revolution', lr.revolution,
                    'status', lr.status,
                    'started_at', lr.started_at,
                    'finished_at', lr.finished_at,
                    'total_cost', lr.total_cost_usd,
                    'total_latency', lr.total_latency_ms
                )
            )
            FROM layer_runs lr
            JOIN layers l ON lr.layer_id = l.layer_id
            WHERE lr.problem_id = p_problem_id
            ORDER BY l.order_idx, lr.revolution
        ),
        'answers', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'answer_id', a.answer_id,
                    'layer', l.name,
                    'confidence', a.confidence_score,
                    'completeness', a.completeness_score,
                    'created_at', a.created_at
                )
            )
            FROM answers a
            JOIN layers l ON a.layer_id = l.layer_id
            WHERE a.problem_id = p_problem_id
            ORDER BY a.created_at
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to get layer run summary
CREATE OR REPLACE FUNCTION get_layer_run_summary(p_layer_run_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'layer_run_id', p_layer_run_id,
        'problem_id', lr.problem_id,
        'layer', l.name,
        'revolution', lr.revolution,
        'status', lr.status,
        'started_at', lr.started_at,
        'finished_at', lr.finished_at,
        'total_cost', lr.total_cost_usd,
        'total_latency', lr.total_latency_ms,
        'sectors', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'sector', sr.sector,
                    'order', sr.sector_order,
                    'status', sr.status,
                    'started_at', sr.started_at,
                    'finished_at', sr.finished_at,
                    'metrics', sr.metrics
                )
            )
            FROM sector_runs sr
            WHERE sr.layer_run_id = p_layer_run_id
            ORDER BY sr.sector_order
        )
    ) INTO result
    FROM layer_runs lr
    JOIN layers l ON lr.layer_id = l.layer_id
    WHERE lr.layer_run_id = p_layer_run_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;