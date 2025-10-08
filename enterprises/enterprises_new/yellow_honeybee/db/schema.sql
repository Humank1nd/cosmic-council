-- 🟡 Yellow Development Schema
-- Development & Creativity Enterprise Database Schema

-- Prototypes created from action plans
CREATE TABLE IF NOT EXISTS prototypes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    plan_id UUID NOT NULL REFERENCES orange_logistics.action_plans (id),
    prototype_link VARCHAR(1000),
    description TEXT NOT NULL,
    prototype_type VARCHAR(100),
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
    previous_stage_output_id UUID REFERENCES orange_logistics.action_plans (id)
);

-- Internal testing results
CREATE TABLE IF NOT EXISTS internal_testing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    prototype_id UUID NOT NULL REFERENCES prototypes (id),
    test_name VARCHAR(200) NOT NULL,
    result TEXT NOT NULL,
    confidence_score DECIMAL(3, 2) CHECK (
        confidence_score >= 0
        AND confidence_score <= 1
    ),
    test_type VARCHAR(100),
    test_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Creative notes and insights
CREATE TABLE IF NOT EXISTS creative_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    prototype_id UUID NOT NULL REFERENCES prototypes (id),
    note TEXT NOT NULL,
    author VARCHAR(200),
    note_type VARCHAR(100),
    inspiration_source VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_prototypes_plan ON prototypes (plan_id);

CREATE INDEX IF NOT EXISTS idx_prototypes_status ON prototypes (status);

CREATE INDEX IF NOT EXISTS idx_prototypes_cycle ON prototypes (source_cycle_id);

CREATE INDEX IF NOT EXISTS idx_internal_testing_prototype ON internal_testing (prototype_id);

CREATE INDEX IF NOT EXISTS idx_internal_testing_date ON internal_testing (test_date);

CREATE INDEX IF NOT EXISTS idx_creative_notes_prototype ON creative_notes (prototype_id);

-- Audit trigger
CREATE TRIGGER update_prototypes_updated_at BEFORE UPDATE ON prototypes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();