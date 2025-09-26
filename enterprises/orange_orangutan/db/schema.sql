-- 🟠 Orange Logistics Schema
-- Planning & Logistics Enterprise Database Schema

-- Action plans based on research questions
CREATE TABLE IF NOT EXISTS action_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    question_id UUID NOT NULL REFERENCES red_research.prioritized_questions (id),
    steps_json JSONB NOT NULL,
    owner VARCHAR(200),
    status VARCHAR(50) DEFAULT 'draft' CHECK (
        status IN (
            'draft',
            'active',
            'completed',
            'failed'
        )
    ),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_cycle_id UUID REFERENCES cycles (id),
    previous_stage_output_id UUID REFERENCES red_research.core_problem (id)
);

-- Dependencies between action plans
CREATE TABLE IF NOT EXISTS dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    plan_id UUID NOT NULL REFERENCES action_plans (id),
    dependency_name VARCHAR(500) NOT NULL,
    dependency_type VARCHAR(100),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evaluation notes for action plans
CREATE TABLE IF NOT EXISTS evaluation_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    plan_id UUID NOT NULL REFERENCES action_plans (id),
    evaluation_text TEXT NOT NULL,
    reviewer VARCHAR(200),
    evaluation_score DECIMAL(3, 2) CHECK (
        evaluation_score >= 0
        AND evaluation_score <= 1
    ),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_action_plans_question ON action_plans (question_id);

CREATE INDEX IF NOT EXISTS idx_action_plans_status ON action_plans (status);

CREATE INDEX IF NOT EXISTS idx_action_plans_cycle ON action_plans (source_cycle_id);

CREATE INDEX IF NOT EXISTS idx_dependencies_plan ON dependencies (plan_id);

CREATE INDEX IF NOT EXISTS idx_dependencies_resolved ON dependencies (resolved);

CREATE INDEX IF NOT EXISTS idx_evaluation_notes_plan ON evaluation_notes (plan_id);

-- Audit trigger
CREATE TRIGGER update_action_plans_updated_at BEFORE UPDATE ON action_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();