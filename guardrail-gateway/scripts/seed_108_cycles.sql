-- Seed Data for 108-Cycle Fractal System
-- Generates all 108 stages (6 enterprises × 6 squads × 3 redundancy passes)
-- Based on Cosmic Council's symbolic and structural foundations

-- ============================================================================
-- DIMENSION DATA SEEDING
-- ============================================================================

-- Insert enterprises (6 enterprises)
INSERT INTO
    enterprises (
        enterprise_id,
        code,
        name,
        description
    )
VALUES (
        1,
        'red',
        'Red Owl',
        'Library of Origins - Knowledge and inquiry foundation'
    ),
    (
        2,
        'orange',
        'Orange Orangutan',
        'Logistics of Progress - Planning and coordination'
    ),
    (
        3,
        'yellow',
        'Yellow Honeybee',
        'Superposition Lab - Creative experimentation'
    ),
    (
        4,
        'green',
        'Green Turtle',
        'Vault of Prosperity - Resource stewardship'
    ),
    (
        5,
        'blue',
        'Blue Dolphin',
        'Ocean of Exchange - Communication and influence'
    ),
    (
        6,
        'purple',
        'Purple Elephant',
        'Sanctuary of Empathy - Reflection and ethics'
    ) ON CONFLICT (enterprise_id) DO
UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- Insert squads (6 squads, fractal structure mirroring enterprises)
INSERT INTO
    squads (
        squad_id,
        code,
        name,
        description
    )
VALUES (
        1,
        'red',
        'Inquiry/Root',
        'Deep questioning and foundational analysis'
    ),
    (
        2,
        'orange',
        'Logistics/Routing',
        'Process optimization and flow management'
    ),
    (
        3,
        'yellow',
        'Creative/Labs',
        'Innovation and experimental development'
    ),
    (
        4,
        'green',
        'Stewardship/Core',
        'Resource management and sustainability'
    ),
    (
        5,
        'blue',
        'Exchange/Comms',
        'Communication and relationship building'
    ),
    (
        6,
        'purple',
        'Reflection/Ethics',
        'Ethical review and continuous improvement'
    ) ON CONFLICT (squad_id) DO
UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- Insert redundancy passes (3 passes)
INSERT INTO
    redundancy_pass (pass_id, code, description)
VALUES (
        1,
        'decide',
        'Primary decision pass - Initial reasoning and action'
    ),
    (
        2,
        'validate',
        'Independent validation pass - Cross-checking and verification'
    ),
    (
        3,
        'reflect',
        'Retrospective reflection pass - Learning and improvement'
    ) ON CONFLICT (pass_id) DO
UPDATE
SET
    description = EXCLUDED.description;

-- ============================================================================
-- 108 STAGES GENERATION
-- ============================================================================

-- Generate all 108 stages using a recursive approach
-- Pattern: 6 enterprises × 6 squads × 3 passes = 108 stages
-- Each stage gets a unique ordinal (1-108) and code (enterprise:squad:pass:ordinal)

WITH stage_generator AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY e.enterprise_id, s.squad_id, rp.pass_id) as stage_id,
        e.enterprise_id,
        s.squad_id,
        rp.pass_id,
        ROW_NUMBER() OVER (ORDER BY e.enterprise_id, s.squad_id, rp.pass_id) as ordinal,
        e.code as enterprise_code,
        s.code as squad_code,
        rp.code as pass_code,
        e.name as enterprise_name,
        s.name as squad_name,
        rp.description as pass_description
    FROM enterprises e
    CROSS JOIN squads s
    CROSS JOIN redundancy_pass rp
    ORDER BY e.enterprise_id, s.squad_id, rp.pass_id
)
INSERT INTO cycle_stages (
    stage_id, enterprise_id, squad_id, pass_id, ordinal, code, name, description, expected_duration_ms
)
SELECT 
    stage_id,
    enterprise_id,
    squad_id,
    pass_id,
    ordinal,
    enterprise_code || ':' || squad_code || ':' || pass_code || ':' || LPAD(ordinal::TEXT, 3, '0') as code,
    enterprise_name || ' — ' || squad_name || ' — ' || INITCAP(pass_code) || ' #' || ordinal as name,
    'Stage ' || ordinal || ': ' || enterprise_name || ' ' || squad_name || ' ' || pass_description as description,
    CASE 
        WHEN pass_code = 'decide' THEN 3000  -- Primary decisions are faster
        WHEN pass_code = 'validate' THEN 4000  -- Validation takes more time
        WHEN pass_code = 'reflect' THEN 5000   -- Reflection takes the most time
    END as expected_duration_ms
FROM stage_generator
ON CONFLICT (stage_id) DO UPDATE SET
    code = EXCLUDED.code,
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    expected_duration_ms = EXCLUDED.expected_duration_ms;

-- ============================================================================
-- CYCLE STAGE TRANSITIONS
-- ============================================================================

-- Create clockwise transitions (normal flow through stages)
INSERT INTO
    cycle_stage_transitions (
        from_stage_id,
        to_stage_id,
        kind,
        priority
    )
SELECT
    cs1.stage_id as from_stage_id,
    cs2.stage_id as to_stage_id,
    'clockwise' as kind,
    1 as priority
FROM
    cycle_stages cs1
    JOIN cycle_stages cs2 ON cs2.ordinal = cs1.ordinal + 1
WHERE
    cs2.ordinal <= 108 ON CONFLICT (
        from_stage_id,
        to_stage_id,
        kind
    ) DO NOTHING;

-- Create redundancy transitions (from decide -> validate -> reflect)
INSERT INTO
    cycle_stage_transitions (
        from_stage_id,
        to_stage_id,
        kind,
        priority
    )
SELECT
    cs1.stage_id as from_stage_id,
    cs2.stage_id as to_stage_id,
    'redundancy' as kind,
    2 as priority
FROM
    cycle_stages cs1
    JOIN cycle_stages cs2 ON (
        cs2.enterprise_id = cs1.enterprise_id
        AND cs2.squad_id = cs1.squad_id
        AND cs2.pass_id = cs1.pass_id + 1
    )
WHERE
    cs1.pass_id IN (1, 2) -- Only from decide and validate
    ON CONFLICT (
        from_stage_id,
        to_stage_id,
        kind
    ) DO NOTHING;

-- Create fallback transitions (from reflect back to decide for same enterprise/squad)
INSERT INTO
    cycle_stage_transitions (
        from_stage_id,
        to_stage_id,
        kind,
        priority
    )
SELECT
    cs1.stage_id as from_stage_id,
    cs2.stage_id as to_stage_id,
    'fallback' as kind,
    3 as priority
FROM
    cycle_stages cs1
    JOIN cycle_stages cs2 ON (
        cs2.enterprise_id = cs1.enterprise_id
        AND cs2.squad_id = cs1.squad_id
        AND cs2.pass_id = 1 -- Back to decide
    )
WHERE
    cs1.pass_id = 3 -- From reflect
    ON CONFLICT (
        from_stage_id,
        to_stage_id,
        kind
    ) DO NOTHING;

-- Create error transitions (from any stage to error handling)
INSERT INTO
    cycle_stage_transitions (
        from_stage_id,
        to_stage_id,
        kind,
        priority
    )
SELECT
    cs.stage_id as from_stage_id,
    cs.stage_id as to_stage_id, -- Self-loop for error handling
    'error' as kind,
    10 as priority
FROM
    cycle_stages cs ON CONFLICT (
        from_stage_id,
        to_stage_id,
        kind
    ) DO NOTHING;

-- ============================================================================
-- DEFAULT CYCLE TEMPLATE
-- ============================================================================

-- Create the default 108-stage cycle template
INSERT INTO
    cycles (
        cycle_id,
        title,
        description,
        version
    )
VALUES (
        '00000000-0000-0000-0000-000000000001',
        'Default 108-Stage Fractal Cycle',
        'The complete Cosmic Council fractal cycle with 6 enterprises × 6 squads × 3 redundancy passes',
        '1.0.0'
    ) ON CONFLICT (cycle_id) DO
UPDATE
SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    version = EXCLUDED.version;

-- ============================================================================
-- N8N WORKFLOW TEMPLATES
-- ============================================================================

-- Insert default N8N workflow templates
INSERT INTO n8n_workflow_templates (template_id, name, description, workflow_json, version) VALUES
('00000000-0000-0000-0000-000000000001', 'Cycle Run Starter', 
 'Initiates a new 108-stage cycle run', 
 '{"name": "Cycle Run Starter", "nodes": [], "connections": {}}'::jsonb, '1.0.0'),
('00000000-0000-0000-0000-000000000002', 'Stage Runner', 
 'Executes individual cycle stages with Guardrail Gateway integration', 
 '{"name": "Stage Runner", "nodes": [], "connections": {}}'::jsonb, '1.0.0'),
('00000000-0000-0000-0000-000000000003', 'Reflection & Policy Evolution', 
 'Purple Elephant reflection and policy improvement workflows', 
 '{"name": "Reflection & Policy Evolution", "nodes": [], "connections": {}}'::jsonb, '1.0.0'),
('00000000-0000-0000-0000-000000000004', 'Run Completer', 
 'Completes cycle runs and calculates final metrics', 
 '{"name": "Run Completer", "nodes": [], "connections": {}}'::jsonb, '1.0.0')
ON CONFLICT (template_id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    workflow_json = EXCLUDED.workflow_json,
    version = EXCLUDED.version;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify we have exactly 108 stages
DO $$
DECLARE
    stage_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO stage_count FROM cycle_stages;
    IF stage_count != 108 THEN
        RAISE EXCEPTION 'Expected 108 stages, but found %', stage_count;
    ELSE
        RAISE NOTICE 'Successfully created % stages', stage_count;
    END IF;
END $$;

-- Verify we have the correct number of transitions
DO $$
DECLARE
    transition_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO transition_count FROM cycle_stage_transitions;
    RAISE NOTICE 'Created % stage transitions', transition_count;
END $$;

-- Display stage distribution by enterprise and pass
SELECT
    e.name as enterprise,
    rp.description as pass_type,
    COUNT(*) as stage_count
FROM
    cycle_stages cs
    JOIN enterprises e ON cs.enterprise_id = e.enterprise_id
    JOIN redundancy_pass rp ON cs.pass_id = rp.pass_id
GROUP BY
    e.name,
    rp.description,
    e.enterprise_id,
    rp.pass_id
ORDER BY e.enterprise_id, rp.pass_id;

-- Display first few stages as examples
SELECT
    stage_id,
    code,
    name,
    expected_duration_ms
FROM cycle_stages
ORDER BY ordinal
LIMIT 10;

RAISE NOTICE '108-Cycle Fractal System seeding completed successfully!';

RAISE NOTICE 'Created: 6 enterprises, 6 squads, 3 redundancy passes, 108 stages, and transition rules';

RAISE NOTICE 'Ready for N8N workflow orchestration and Guardrail Gateway integration';