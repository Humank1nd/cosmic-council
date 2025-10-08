-- 🔴 Red Research Schema
-- Research & Inquiry Enterprise Database Schema

-- Core problem definition
CREATE TABLE IF NOT EXISTS core_problem (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
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
    previous_stage_output_id UUID -- FK to previous enterprise's main table
);

-- Research findings from investigation
CREATE TABLE IF NOT EXISTS research_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    problem_id UUID NOT NULL REFERENCES core_problem (id),
    summary TEXT NOT NULL,
    evidence JSONB NOT NULL,
    confidence DECIMAL(3, 2) CHECK (
        confidence >= 0
        AND confidence <= 1
    ),
    source_url VARCHAR(1000),
    source_type VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prioritized questions for next stage
CREATE TABLE IF NOT EXISTS prioritized_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    finding_id UUID NOT NULL REFERENCES research_findings (id),
    question TEXT NOT NULL,
    priority INTEGER CHECK (
        priority >= 1
        AND priority <= 10
    ),
    category VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_core_problem_status ON core_problem (status);

CREATE INDEX IF NOT EXISTS idx_core_problem_cycle ON core_problem (source_cycle_id);

CREATE INDEX IF NOT EXISTS idx_research_findings_problem ON research_findings (problem_id);

CREATE INDEX IF NOT EXISTS idx_prioritized_questions_finding ON prioritized_questions (finding_id);

CREATE INDEX IF NOT EXISTS idx_prioritized_questions_priority ON prioritized_questions (priority);

-- Audit trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_core_problem_updated_at BEFORE UPDATE ON core_problem
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_research_findings_updated_at BEFORE UPDATE ON research_findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();