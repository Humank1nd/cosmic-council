-- 🔵 Blue Market Schema
-- Communication & Marketing Enterprise Database Schema

-- Audience targeting based on budget allocations
CREATE TABLE IF NOT EXISTS audience_targeting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    plan_id UUID NOT NULL REFERENCES orange_logistics.action_plans (id),
    segment VARCHAR(200) NOT NULL,
    strategy_json JSONB NOT NULL,
    target_size INTEGER,
    engagement_potential DECIMAL(3, 2) CHECK (
        engagement_potential >= 0
        AND engagement_potential <= 1
    ),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_cycle_id UUID REFERENCES cycles (id),
    previous_stage_output_id UUID REFERENCES green_budget.budget_allocations (id)
);

-- Communication strategies
CREATE TABLE IF NOT EXISTS communication_strategy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    audience_id UUID NOT NULL REFERENCES audience_targeting (id),
    message TEXT NOT NULL,
    channel VARCHAR(100) NOT NULL,
    schedule TIMESTAMPTZ,
    frequency VARCHAR(50),
    status VARCHAR(50) DEFAULT 'draft' CHECK (
        status IN (
            'draft',
            'active',
            'completed',
            'failed'
        )
    ),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    strategy_id UUID NOT NULL REFERENCES communication_strategy (id),
    metric_name VARCHAR(200) NOT NULL,
    impressions INTEGER,
    engagement INTEGER,
    conversion INTEGER,
    conversion_rate DECIMAL(5, 4),
    measurement_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_audience_targeting_plan ON audience_targeting (plan_id);

CREATE INDEX IF NOT EXISTS idx_audience_targeting_cycle ON audience_targeting (source_cycle_id);

CREATE INDEX IF NOT EXISTS idx_communication_strategy_audience ON communication_strategy (audience_id);

CREATE INDEX IF NOT EXISTS idx_communication_strategy_status ON communication_strategy (status);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_strategy ON performance_metrics (strategy_id);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_date ON performance_metrics (measurement_date);

-- Audit triggers
CREATE TRIGGER update_audience_targeting_updated_at BEFORE UPDATE ON audience_targeting
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_communication_strategy_updated_at BEFORE UPDATE ON communication_strategy
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();