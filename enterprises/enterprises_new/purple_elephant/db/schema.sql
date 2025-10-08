-- 🟣 Purple Support Schema
-- Support & Empathy Enterprise Database Schema

-- Feedback collection from communication strategies
CREATE TABLE IF NOT EXISTS feedback_collection (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    strategy_id UUID NOT NULL REFERENCES blue_market.communication_strategy (id),
    feedback_text TEXT NOT NULL,
    sentiment VARCHAR(50) CHECK (
        sentiment IN (
            'positive',
            'neutral',
            'negative'
        )
    ),
    sentiment_score DECIMAL(3, 2) CHECK (
        sentiment_score >= -1
        AND sentiment_score <= 1
    ),
    source VARCHAR(200),
    source_type VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_cycle_id UUID REFERENCES cycles (id),
    previous_stage_output_id UUID REFERENCES blue_market.performance_metrics (id)
);

-- Performance assessments
CREATE TABLE IF NOT EXISTS performance_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    feedback_id UUID NOT NULL REFERENCES feedback_collection (id),
    rating DECIMAL(3, 2) CHECK (
        rating >= 0
        AND rating <= 1
    ),
    category VARCHAR(100),
    assessment_criteria JSONB,
    assessor VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Improvement recommendations
CREATE TABLE IF NOT EXISTS improvement_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    assessment_id UUID NOT NULL REFERENCES performance_assessments (id),
    recommendation_text TEXT NOT NULL,
    priority INTEGER CHECK (
        priority >= 1
        AND priority <= 10
    ),
    implementation_effort VARCHAR(50),
    expected_impact VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'in_progress',
            'completed',
            'rejected'
        )
    ),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_feedback_collection_strategy ON feedback_collection (strategy_id);

CREATE INDEX IF NOT EXISTS idx_feedback_collection_sentiment ON feedback_collection (sentiment);

CREATE INDEX IF NOT EXISTS idx_feedback_collection_cycle ON feedback_collection (source_cycle_id);

CREATE INDEX IF NOT EXISTS idx_performance_assessments_feedback ON performance_assessments (feedback_id);

CREATE INDEX IF NOT EXISTS idx_performance_assessments_rating ON performance_assessments (rating);

CREATE INDEX IF NOT EXISTS idx_improvement_recommendations_assessment ON improvement_recommendations (assessment_id);

CREATE INDEX IF NOT EXISTS idx_improvement_recommendations_priority ON improvement_recommendations (priority);

CREATE INDEX IF NOT EXISTS idx_improvement_recommendations_status ON improvement_recommendations (status);

-- Audit triggers
CREATE TRIGGER update_feedback_collection_updated_at BEFORE UPDATE ON feedback_collection
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_improvement_recommendations_updated_at BEFORE UPDATE ON improvement_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();