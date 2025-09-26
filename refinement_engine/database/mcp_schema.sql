-- Model Context Protocols (MCP) Database Schema
-- Stores MCP definitions, contexts, and transitions for the Cosmic Council

-- MCP Definitions Table
CREATE TABLE mcp_definitions (
    mcp_id UUID PRIMARY KEY,
    sector TEXT NOT NULL CHECK (
        sector IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ),
    layer TEXT NOT NULL CHECK (
        layer IN (
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
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    constraints JSONB NOT NULL,
    transformation_rules JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE (sector, layer)
);

-- MCP Contexts Table (Runtime instances)
CREATE TABLE mcp_contexts (
    context_id UUID PRIMARY KEY,
    mcp_id UUID REFERENCES mcp_definitions (mcp_id),
    sector TEXT NOT NULL,
    layer TEXT NOT NULL,
    inputs JSONB NOT NULL,
    outputs JSONB,
    constraints JSONB NOT NULL,
    metadata JSONB,
    status TEXT DEFAULT 'active' CHECK (
        status IN (
            'active',
            'completed',
            'failed',
            'archived'
        )
    ),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- MCP Transitions Table (Context handoffs between sectors/layers)
CREATE TABLE mcp_transitions (
    transition_id UUID PRIMARY KEY,
    from_context_id UUID REFERENCES mcp_contexts (context_id),
    to_context_id UUID REFERENCES mcp_contexts (context_id),
    from_sector TEXT NOT NULL,
    to_sector TEXT NOT NULL,
    from_layer TEXT NOT NULL,
    to_layer TEXT NOT NULL,
    context_data JSONB NOT NULL,
    transformation_applied TEXT NOT NULL,
    transition_type TEXT NOT NULL CHECK (
        transition_type IN (
            'sector',
            'layer',
            'recursive'
        )
    ),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- MCP Performance Metrics Table
CREATE TABLE mcp_performance (
    performance_id UUID PRIMARY KEY,
    context_id UUID REFERENCES mcp_contexts (context_id),
    sector TEXT NOT NULL,
    layer TEXT NOT NULL,
    processing_time_ms INTEGER,
    context_size_bytes INTEGER,
    quality_score NUMERIC,
    resource_usage JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- MCP Quality Assessments Table
CREATE TABLE mcp_quality_assessments (
    assessment_id UUID PRIMARY KEY,
    context_id UUID REFERENCES mcp_contexts (context_id),
    sector TEXT NOT NULL,
    layer TEXT NOT NULL,
    confidence_score NUMERIC,
    completeness_score NUMERIC,
    accuracy_score NUMERIC,
    relevance_score NUMERIC,
    overall_quality NUMERIC,
    assessment_details JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- MCP Recursive Descent Tracking Table
CREATE TABLE mcp_recursive_descents (
    descent_id UUID PRIMARY KEY,
    problem_id UUID REFERENCES problems (problem_id),
    original_context_id UUID REFERENCES mcp_contexts (context_id),
    failing_sector TEXT NOT NULL,
    original_layer TEXT NOT NULL,
    target_layer TEXT NOT NULL,
    descent_reason TEXT NOT NULL,
    context_refinement JSONB,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_mcp_definitions_sector_layer ON mcp_definitions (sector, layer);

CREATE INDEX idx_mcp_contexts_sector_layer ON mcp_contexts (sector, layer);

CREATE INDEX idx_mcp_contexts_status ON mcp_contexts (status);

CREATE INDEX idx_mcp_transitions_from_context ON mcp_transitions (from_context_id);

CREATE INDEX idx_mcp_transitions_to_context ON mcp_transitions (to_context_id);

CREATE INDEX idx_mcp_transitions_type ON mcp_transitions (transition_type);

CREATE INDEX idx_mcp_performance_sector_layer ON mcp_performance (sector, layer);

CREATE INDEX idx_mcp_quality_sector_layer ON mcp_quality_assessments (sector, layer);

CREATE INDEX idx_mcp_recursive_problem ON mcp_recursive_descents (problem_id);

-- Insert default MCP definitions for all sector/layer combinations
INSERT INTO
    mcp_definitions (
        mcp_id,
        sector,
        layer,
        input_schema,
        output_schema,
        constraints,
        transformation_rules
    )
VALUES
    -- Red Owl MCPs
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'red',
        'deci',
        '{"problem_statement": {"type": "string", "required": true}, "hypotheses": {"type": "array", "max_items": 10}, "relevant_sources": {"type": "array", "max_items": 20}, "knowledge_gaps": {"type": "array", "max_items": 10}}',
        '{"evidence_blocks": {"type": "array", "max_items": 10}, "knowledge_summary": {"type": "object", "max_properties": 20}, "research_quality_score": {"type": "number"}, "gaps_identified": {"type": "array", "max_items": 10}}',
        '{"max_context_size": 10000, "processing_time_limit": 300, "quality_thresholds": {"min_confidence": 0.4, "min_completeness": 0.4, "min_accuracy": 0.7}}',
        '{"context_compression": ["summarize_key_points", "remove_redundancy", "highlight_critical_info"], "data_filtering": ["remove_irrelevant_data", "filter_by_relevance_score"], "format_conversion": ["standardize_data_types", "normalize_representations"], "validation_rules": ["validate_schema_compliance", "check_data_quality"]}'
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'red',
        'centi',
        '{"problem_statement": {"type": "string", "required": true}, "hypotheses": {"type": "array", "max_items": 8}, "relevant_sources": {"type": "array", "max_items": 15}, "knowledge_gaps": {"type": "array", "max_items": 8}}',
        '{"evidence_blocks": {"type": "array", "max_items": 8}, "knowledge_summary": {"type": "object", "max_properties": 15}, "research_quality_score": {"type": "number"}, "gaps_identified": {"type": "array", "max_items": 8}}',
        '{"max_context_size": 8000, "processing_time_limit": 240, "quality_thresholds": {"min_confidence": 0.5, "min_completeness": 0.5, "min_accuracy": 0.7}}',
        '{"context_compression": ["summarize_key_points", "remove_redundancy"], "data_filtering": ["remove_irrelevant_data", "filter_by_relevance_score"], "format_conversion": ["standardize_data_types"], "validation_rules": ["validate_schema_compliance"]}'
    ),

-- Orange Orangutan MCPs
(
    '550e8400-e29b-41d4-a716-446655440011',
    'orange',
    'deci',
    '{"research_summary": {"type": "object", "required": true, "max_properties": 20}, "constraints": {"type": "object", "required": true}, "dependencies": {"type": "array", "max_items": 20}, "timeline": {"type": "object", "required": true}}',
    '{"structured_plan": {"type": "object", "max_properties": 20}, "milestones": {"type": "array", "max_items": 10}, "dependencies_mapped": {"type": "object", "max_properties": 15}, "feasibility_score": {"type": "number"}}',
    '{"max_context_size": 10000, "processing_time_limit": 300, "quality_thresholds": {"min_confidence": 0.4, "min_completeness": 0.4, "min_accuracy": 0.7}}',
    '{"context_compression": ["summarize_key_points", "remove_redundancy", "highlight_critical_info"], "data_filtering": ["remove_irrelevant_data"], "format_conversion": ["standardize_data_types"], "validation_rules": ["validate_schema_compliance"]}'
),

-- Yellow Honeybee MCPs
(
    '550e8400-e29b-41d4-a716-446655440021',
    'yellow',
    'deci',
    '{"plan_doc": {"type": "object", "required": true, "max_properties": 20}, "design_constraints": {"type": "object", "required": true}, "prototype_options": {"type": "array", "max_items": 10}, "testing_results": {"type": "array", "max_items": 10}}',
    '{"prototypes": {"type": "array", "max_items": 5}, "assumptions_documented": {"type": "array", "max_items": 10}, "testing_results": {"type": "object", "max_properties": 15}, "innovation_score": {"type": "number"}}',
    '{"max_context_size": 10000, "processing_time_limit": 300, "quality_thresholds": {"min_confidence": 0.4, "min_completeness": 0.4, "min_accuracy": 0.7}}',
    '{"context_compression": ["summarize_key_points", "remove_redundancy"], "data_filtering": ["remove_irrelevant_data"], "format_conversion": ["standardize_data_types"], "validation_rules": ["validate_schema_compliance"]}'
),

-- Green Tortoise MCPs
(
    '550e8400-e29b-41d4-a716-446655440031',
    'green',
    'deci',
    '{"prototype_summary": {"type": "object", "required": true, "max_properties": 20}, "resource_request": {"type": "object", "required": true}, "budget_limits": {"type": "object", "required": true}, "sustainability_metrics": {"type": "object", "required": true}}',
    '{"resource_package": {"type": "object", "max_properties": 15}, "budget_approval": {"type": "object", "max_properties": 10}, "sustainability_report": {"type": "object", "max_properties": 15}, "cost_effectiveness_score": {"type": "number"}}',
    '{"max_context_size": 10000, "processing_time_limit": 300, "quality_thresholds": {"min_confidence": 0.4, "min_completeness": 0.4, "min_accuracy": 0.7}}',
    '{"context_compression": ["summarize_key_points", "remove_redundancy"], "data_filtering": ["remove_irrelevant_data"], "format_conversion": ["standardize_data_types"], "validation_rules": ["validate_schema_compliance"]}'
),

-- Blue Dolphin MCPs
(
    '550e8400-e29b-41d4-a716-446655440041',
    'blue',
    'deci',
    '{"approved_solution": {"type": "object", "required": true, "max_properties": 20}, "audience_profile": {"type": "object", "required": true}, "message_variants": {"type": "array", "max_items": 10}, "risk_assessment": {"type": "object", "required": true}}',
    '{"communication_packet": {"type": "object", "max_properties": 15}, "message_optimized": {"type": "object", "max_properties": 10}, "safety_verified": {"type": "boolean"}, "clarity_score": {"type": "number"}}',
    '{"max_context_size": 10000, "processing_time_limit": 300, "quality_thresholds": {"min_confidence": 0.4, "min_completeness": 0.4, "min_accuracy": 0.7}}',
    '{"context_compression": ["summarize_key_points", "remove_redundancy"], "data_filtering": ["remove_irrelevant_data"], "format_conversion": ["standardize_data_types"], "validation_rules": ["validate_schema_compliance"]}'
),

-- Purple Elephant MCPs
(
    '550e8400-e29b-41d4-a716-446655440051',
    'purple',
    'deci',
    '{"final_message": {"type": "object", "required": true, "max_properties": 20}, "feedback_signals": {"type": "array", "max_items": 10}, "user_satisfaction": {"type": "number", "required": true}, "cycle_outcome": {"type": "string", "required": true}}',
    '{"reflection_report": {"type": "object", "max_properties": 20}, "contradictions_detected": {"type": "array", "max_items": 10}, "routing_decision": {"type": "string"}, "solution_sufficiency_score": {"type": "number"}}',
    '{"max_context_size": 10000, "processing_time_limit": 300, "quality_thresholds": {"min_confidence": 0.4, "min_completeness": 0.4, "min_accuracy": 0.7}}',
    '{"context_compression": ["summarize_key_points", "remove_redundancy"], "data_filtering": ["remove_irrelevant_data"], "format_conversion": ["standardize_data_types"], "validation_rules": ["validate_schema_compliance"]}'
);

-- Add more MCP definitions for other layers as needed
-- (This is a sample - in practice, you'd have all 72 combinations: 6 sectors × 12 layers)

-- Views for common queries
CREATE VIEW mcp_context_summary AS
SELECT
    c.context_id,
    c.sector,
    c.layer,
    c.status,
    c.created_at,
    c.updated_at,
    jsonb_array_length (c.inputs) as input_count,
    jsonb_array_length (c.outputs) as output_count,
    d.constraints ->> 'max_context_size' as max_context_size
FROM
    mcp_contexts c
    JOIN mcp_definitions d ON c.sector = d.sector
    AND c.layer = d.layer;

CREATE VIEW mcp_transition_flow AS
SELECT
    t.transition_id,
    t.from_sector,
    t.to_sector,
    t.from_layer,
    t.to_layer,
    t.transition_type,
    t.success,
    t.created_at,
    fc.status as from_context_status,
    tc.status as to_context_status
FROM
    mcp_transitions t
    LEFT JOIN mcp_contexts fc ON t.from_context_id = fc.context_id
    LEFT JOIN mcp_contexts tc ON t.to_context_id = tc.context_id;

-- Functions for MCP management
CREATE OR REPLACE FUNCTION get_mcp_definition(p_sector TEXT, p_layer TEXT)
RETURNS TABLE(mcp_id UUID, input_schema JSONB, output_schema JSONB, constraints JSONB, transformation_rules JSONB)
LANGUAGE SQL
AS $$
    SELECT mcp_id, input_schema, output_schema, constraints, transformation_rules
    FROM mcp_definitions
    WHERE sector = p_sector AND layer = p_layer;
$$;

CREATE OR REPLACE FUNCTION create_mcp_context(
    p_mcp_id UUID,
    p_sector TEXT,
    p_layer TEXT,
    p_inputs JSONB,
    p_constraints JSONB,
    p_metadata JSONB DEFAULT '{}'::JSONB
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_context_id UUID;
BEGIN
    v_context_id := gen_random_uuid();
    
    INSERT INTO mcp_contexts (context_id, mcp_id, sector, layer, inputs, constraints, metadata)
    VALUES (v_context_id, p_mcp_id, p_sector, p_layer, p_inputs, p_constraints, p_metadata);
    
    RETURN v_context_id;
END;
$$;

CREATE OR REPLACE FUNCTION record_mcp_transition(
    p_from_context_id UUID,
    p_to_context_id UUID,
    p_from_sector TEXT,
    p_to_sector TEXT,
    p_from_layer TEXT,
    p_to_layer TEXT,
    p_context_data JSONB,
    p_transformation_applied TEXT,
    p_transition_type TEXT
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_transition_id UUID;
BEGIN
    v_transition_id := gen_random_uuid();
    
    INSERT INTO mcp_transitions (
        transition_id, from_context_id, to_context_id, from_sector, to_sector,
        from_layer, to_layer, context_data, transformation_applied, transition_type
    )
    VALUES (
        v_transition_id, p_from_context_id, p_to_context_id, p_from_sector, p_to_sector,
        p_from_layer, p_to_layer, p_context_data, p_transformation_applied, p_transition_type
    );
    
    RETURN v_transition_id;
END;
$$;