-- Cosmic Council Governance Database Schema
-- Extends existing database models with governance-specific tables

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- GOVERNANCE AGENT MANAGEMENT
-- ============================================================================

-- Agent profiles and performance tracking
CREATE TABLE governance_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    stage VARCHAR(50) NOT NULL CHECK (stage IN ('research', 'planning', 'development', 'budget', 'market', 'support')),
    level VARCHAR(20) NOT NULL CHECK (level IN ('novice', 'apprentice', 'journeyman', 'master', 'grandmaster')),

-- Performance metrics
cycles_completed INTEGER DEFAULT 0,
violations_count JSONB DEFAULT '{"minor": 0, "major": 0, "critical": 0}',
performance_score DECIMAL(5, 2) DEFAULT 100.0 CHECK (
    performance_score >= 0
    AND performance_score <= 100
),
suspension_count INTEGER DEFAULT 0,

-- Activity tracking
last_violation TIMESTAMP
WITH
    TIME ZONE,
    last_activity TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

-- Metadata
created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_governance_agents_agent_id UNIQUE (agent_id),
    CONSTRAINT idx_governance_agents_stage CHECK (stage IN ('research', 'planning', 'development', 'budget', 'market', 'support')),
    CONSTRAINT idx_governance_agents_level CHECK (level IN ('novice', 'apprentice', 'journeyman', 'master', 'grandmaster'))
);

-- Agent achievements tracking
CREATE TABLE governance_agent_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL REFERENCES governance_agents(agent_id) ON DELETE CASCADE,
    achievement_id VARCHAR(100) NOT NULL,
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    progress JSONB DEFAULT '{}',
    is_completed BOOLEAN DEFAULT TRUE,

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

-- Constraints
CONSTRAINT idx_governance_agent_achievements_unique UNIQUE (agent_id, achievement_id)
);

-- ============================================================================
-- ACHIEVEMENT SYSTEM
-- ============================================================================

-- Achievement definitions
CREATE TABLE governance_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    achievement_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    achievement_type VARCHAR(50) NOT NULL CHECK (achievement_type IN ('cycle_completion', 'code_quality', 'innovation', 'collaboration', 'leadership', 'special')),
    rarity VARCHAR(20) NOT NULL CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary')),
    icon VARCHAR(10),
    points INTEGER NOT NULL CHECK (points >= 0),
    requirements JSONB NOT NULL,

-- Status
is_active BOOLEAN DEFAULT TRUE,

-- Metadata
created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_governance_achievements_achievement_id UNIQUE (achievement_id),
    CONSTRAINT idx_governance_achievements_type CHECK (achievement_type IN ('cycle_completion', 'code_quality', 'innovation', 'collaboration', 'leadership', 'special')),
    CONSTRAINT idx_governance_achievements_rarity CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary'))
);

-- ============================================================================
-- ENFORCEMENT SYSTEM
-- ============================================================================

-- Enforcement records
CREATE TABLE governance_enforcement_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id VARCHAR(100) UNIQUE NOT NULL,
    agent_id VARCHAR(100) NOT NULL REFERENCES governance_agents(agent_id) ON DELETE CASCADE,
    violation_type VARCHAR(20) NOT NULL CHECK (violation_type IN ('minor', 'major', 'critical')),
    action_taken VARCHAR(20) NOT NULL CHECK (action_taken IN ('warning', 'block', 'suspend', 'ban')),
    reason TEXT NOT NULL,
    duration_hours INTEGER, -- For suspensions
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    notes TEXT,

-- Violation details
violations JSONB DEFAULT '[]',
file_path VARCHAR(500),
line_number INTEGER,

-- Metadata
timestamp TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_governance_enforcement_records_record_id UNIQUE (record_id),
    CONSTRAINT idx_governance_enforcement_records_violation_type CHECK (violation_type IN ('minor', 'major', 'critical')),
    CONSTRAINT idx_governance_enforcement_records_action_taken CHECK (action_taken IN ('warning', 'block', 'suspend', 'ban'))
);

-- ============================================================================
-- TURN-BASED PROCESSING
-- ============================================================================

-- Turn-based cycles
CREATE TABLE governance_turn_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id VARCHAR(100) UNIQUE NOT NULL,
    problem_statement TEXT NOT NULL,
    energy_budget INTEGER NOT NULL CHECK (energy_budget > 0),
    current_turn_index INTEGER DEFAULT 0,
    victory_condition VARCHAR(20) CHECK (victory_condition IN ('solved', 'evolved', 'escalated')),
    feedback_for_next_cycle TEXT,

-- Cycle metadata
is_sub_council BOOLEAN DEFAULT FALSE,
parent_cycle_id VARCHAR(100),
sub_councils JSONB DEFAULT '[]',

-- Status
status VARCHAR(20) DEFAULT 'active' CHECK (
    status IN (
        'active',
        'completed',
        'failed',
        'escalated'
    )
),

-- Metadata
created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP
WITH
    TIME ZONE,

-- Indexes
CONSTRAINT idx_governance_turn_cycles_cycle_id UNIQUE (cycle_id),
    CONSTRAINT idx_governance_turn_cycles_status CHECK (status IN ('active', 'completed', 'failed', 'escalated')),
    CONSTRAINT idx_governance_turn_cycles_victory_condition CHECK (victory_condition IN ('solved', 'evolved', 'escalated'))
);

-- Turn execution records
CREATE TABLE governance_turns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    turn_id VARCHAR(100) UNIQUE NOT NULL,
    cycle_id VARCHAR(100) NOT NULL REFERENCES governance_turn_cycles(cycle_id) ON DELETE CASCADE,
    stage VARCHAR(50) NOT NULL CHECK (stage IN ('research', 'planning', 'development', 'budget', 'market', 'support')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('waiting', 'active', 'completed', 'failed', 'escalated')),

-- Turn data
input_data JSONB DEFAULT '{}',
output_data JSONB DEFAULT '{}',
energy_budget INTEGER NOT NULL CHECK (energy_budget > 0),
energy_used INTEGER DEFAULT 0 CHECK (energy_used >= 0),
feedback_score DECIMAL(3, 2) CHECK (
    feedback_score >= 0
    AND feedback_score <= 1
),

-- Action points
action_points JSONB DEFAULT '[]',

-- Metadata
started_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    notes TEXT,

-- Indexes
CONSTRAINT idx_governance_turns_turn_id UNIQUE (turn_id),
    CONSTRAINT idx_governance_turns_stage CHECK (stage IN ('research', 'planning', 'development', 'budget', 'market', 'support')),
    CONSTRAINT idx_governance_turns_status CHECK (status IN ('waiting', 'active', 'completed', 'failed', 'escalated'))
);

-- Turn actions
CREATE TABLE governance_turn_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_id VARCHAR(100) UNIQUE NOT NULL,
    turn_id VARCHAR(100) NOT NULL REFERENCES governance_turns(turn_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('query', 'plan', 'prototype', 'allocate', 'communicate', 'reflect')),
    action_data JSONB DEFAULT '{}',
    result JSONB DEFAULT '{}',
    energy_cost INTEGER NOT NULL CHECK (energy_cost >= 0),
    success BOOLEAN NOT NULL,
    error_message TEXT,

-- Metadata
executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_governance_turn_actions_action_id UNIQUE (action_id),
    CONSTRAINT idx_governance_turn_actions_action_type CHECK (action_type IN ('query', 'plan', 'prototype', 'allocate', 'communicate', 'reflect'))
);

-- ============================================================================
-- CODE REVIEW SYSTEM
-- ============================================================================

-- Code review records
CREATE TABLE governance_code_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id VARCHAR(100) UNIQUE NOT NULL,
    agent_id VARCHAR(100) NOT NULL REFERENCES governance_agents(agent_id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_content TEXT,
    violations JSONB DEFAULT '[]',
    compliance_score DECIMAL(5,2) CHECK (compliance_score >= 0 AND compliance_score <= 100),

-- Review metadata
review_type VARCHAR(50) DEFAULT 'pull_request' CHECK (
    review_type IN (
        'pull_request',
        'commit',
        'file_upload'
    )
),
pr_number INTEGER,
commit_hash VARCHAR(100),

-- Status
status VARCHAR(20) DEFAULT 'completed' CHECK (
    status IN (
        'pending',
        'in_progress',
        'completed',
        'failed'
    )
),

-- Metadata
reviewed_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_governance_code_reviews_review_id UNIQUE (review_id),
    CONSTRAINT idx_governance_code_reviews_review_type CHECK (review_type IN ('pull_request', 'commit', 'file_upload')),
    CONSTRAINT idx_governance_code_reviews_status CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'))
);

-- ============================================================================
-- NOTIFICATION SYSTEM
-- ============================================================================

-- Notification records
CREATE TABLE governance_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id VARCHAR(100) UNIQUE NOT NULL,
    agent_id VARCHAR(100) REFERENCES governance_agents(agent_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('achievement', 'violation', 'enforcement', 'system', 'reminder')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',

-- Delivery
channels JSONB DEFAULT '[]', -- ['slack', 'email', 'n8n']
sent_at TIMESTAMP
WITH
    TIME ZONE,
    delivered_at TIMESTAMP
WITH
    TIME ZONE,
    read_at TIMESTAMP
WITH
    TIME ZONE,

-- Status
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'sent',
        'delivered',
        'read',
        'failed'
    )
),

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_governance_notifications_notification_id UNIQUE (notification_id),
    CONSTRAINT idx_governance_notifications_notification_type CHECK (notification_type IN ('achievement', 'violation', 'enforcement', 'system', 'reminder')),
    CONSTRAINT idx_governance_notifications_status CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed'))
);

-- ============================================================================
-- SYSTEM METRICS AND ANALYTICS
-- ============================================================================

-- Governance system metrics
CREATE TABLE governance_system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN ('counter', 'gauge', 'histogram', 'summary')),
    metric_value DECIMAL(15,2) NOT NULL,
    metric_unit VARCHAR(20),
    context JSONB DEFAULT '{}',
    tags JSONB DEFAULT '{}',

-- Metadata
recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_governance_system_metrics_name_type CHECK (metric_type IN ('counter', 'gauge', 'histogram', 'summary'))
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Agent indexes
CREATE INDEX idx_governance_agents_stage ON governance_agents (stage);

CREATE INDEX idx_governance_agents_level ON governance_agents (level);

CREATE INDEX idx_governance_agents_performance_score ON governance_agents (performance_score);

CREATE INDEX idx_governance_agents_last_activity ON governance_agents (last_activity);

CREATE INDEX idx_governance_agents_is_active ON governance_agents (is_active);

-- Achievement indexes
CREATE INDEX idx_governance_achievements_type ON governance_achievements (achievement_type);

CREATE INDEX idx_governance_achievements_rarity ON governance_achievements (rarity);

CREATE INDEX idx_governance_achievements_points ON governance_achievements (points);

CREATE INDEX idx_governance_achievements_is_active ON governance_achievements (is_active);

-- Enforcement indexes
CREATE INDEX idx_governance_enforcement_records_agent_id ON governance_enforcement_records (agent_id);

CREATE INDEX idx_governance_enforcement_records_violation_type ON governance_enforcement_records (violation_type);

CREATE INDEX idx_governance_enforcement_records_action_taken ON governance_enforcement_records (action_taken);

CREATE INDEX idx_governance_enforcement_records_timestamp ON governance_enforcement_records (timestamp);

CREATE INDEX idx_governance_enforcement_records_resolved ON governance_enforcement_records (resolved);

-- Turn-based processing indexes
CREATE INDEX idx_governance_turn_cycles_status ON governance_turn_cycles (status);

CREATE INDEX idx_governance_turn_cycles_is_sub_council ON governance_turn_cycles (is_sub_council);

CREATE INDEX idx_governance_turn_cycles_parent_cycle_id ON governance_turn_cycles (parent_cycle_id);

CREATE INDEX idx_governance_turn_cycles_created_at ON governance_turn_cycles (created_at);

CREATE INDEX idx_governance_turns_cycle_id ON governance_turns (cycle_id);

CREATE INDEX idx_governance_turns_stage ON governance_turns (stage);

CREATE INDEX idx_governance_turns_status ON governance_turns (status);

CREATE INDEX idx_governance_turns_started_at ON governance_turns (started_at);

CREATE INDEX idx_governance_turn_actions_turn_id ON governance_turn_actions (turn_id);

CREATE INDEX idx_governance_turn_actions_action_type ON governance_turn_actions (action_type);

CREATE INDEX idx_governance_turn_actions_executed_at ON governance_turn_actions (executed_at);

-- Code review indexes
CREATE INDEX idx_governance_code_reviews_agent_id ON governance_code_reviews (agent_id);

CREATE INDEX idx_governance_code_reviews_file_path ON governance_code_reviews (file_path);

CREATE INDEX idx_governance_code_reviews_review_type ON governance_code_reviews (review_type);

CREATE INDEX idx_governance_code_reviews_reviewed_at ON governance_code_reviews (reviewed_at);

-- Notification indexes
CREATE INDEX idx_governance_notifications_agent_id ON governance_notifications (agent_id);

CREATE INDEX idx_governance_notifications_notification_type ON governance_notifications (notification_type);

CREATE INDEX idx_governance_notifications_status ON governance_notifications (status);

CREATE INDEX idx_governance_notifications_created_at ON governance_notifications (created_at);

-- System metrics indexes
CREATE INDEX idx_governance_system_metrics_name ON governance_system_metrics (metric_name);

CREATE INDEX idx_governance_system_metrics_type ON governance_system_metrics (metric_type);

CREATE INDEX idx_governance_system_metrics_recorded_at ON governance_system_metrics (recorded_at);

-- ============================================================================
-- TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_governance_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers
CREATE TRIGGER update_governance_agents_updated_at BEFORE UPDATE ON governance_agents FOR EACH ROW EXECUTE FUNCTION update_governance_updated_at_column();

CREATE TRIGGER update_governance_achievements_updated_at BEFORE UPDATE ON governance_achievements FOR EACH ROW EXECUTE FUNCTION update_governance_updated_at_column();

-- Function to update agent performance score
CREATE OR REPLACE FUNCTION update_agent_performance_score()
RETURNS TRIGGER AS $$
DECLARE
    agent_record RECORD;
    violation_penalty DECIMAL(5,2);
    suspension_penalty DECIMAL(5,2);
    cycle_bonus DECIMAL(5,2);
    new_score DECIMAL(5,2);
BEGIN
    -- Get agent record
    SELECT * INTO agent_record FROM governance_agents WHERE agent_id = NEW.agent_id;
    
    -- Calculate penalties
    violation_penalty := (agent_record.violations_count->>'minor')::INTEGER * 2 +
                        (agent_record.violations_count->>'major')::INTEGER * 10 +
                        (agent_record.violations_count->>'critical')::INTEGER * 25;
    
    suspension_penalty := agent_record.suspension_count * 15;
    
    -- Calculate bonus
    cycle_bonus := LEAST(agent_record.cycles_completed * 0.5, 20);
    
    -- Calculate new score
    new_score := GREATEST(0.0, LEAST(100.0, 100.0 - violation_penalty - suspension_penalty + cycle_bonus));
    
    -- Update agent performance score
    UPDATE governance_agents 
    SET performance_score = new_score, updated_at = NOW()
    WHERE agent_id = NEW.agent_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply performance score trigger
CREATE TRIGGER update_agent_performance_score_trigger 
    AFTER INSERT OR UPDATE ON governance_enforcement_records 
    FOR EACH ROW EXECUTE FUNCTION update_agent_performance_score();

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to get agent statistics
CREATE OR REPLACE FUNCTION get_agent_statistics(p_agent_id VARCHAR(100))
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'agent_id', ga.agent_id,
        'name', ga.name,
        'stage', ga.stage,
        'level', ga.level,
        'cycles_completed', ga.cycles_completed,
        'performance_score', ga.performance_score,
        'violations_count', ga.violations_count,
        'suspension_count', ga.suspension_count,
        'achievements_count', (
            SELECT COUNT(*) FROM governance_agent_achievements gaa 
            WHERE gaa.agent_id = p_agent_id
        ),
        'total_points', (
            SELECT COALESCE(SUM(g.points), 0) 
            FROM governance_achievements g
            JOIN governance_agent_achievements gaa ON g.achievement_id = gaa.achievement_id
            WHERE gaa.agent_id = p_agent_id
        ),
        'last_violation', ga.last_violation,
        'last_activity', ga.last_activity,
        'is_active', ga.is_active
    ) INTO result
    FROM governance_agents ga
    WHERE ga.agent_id = p_agent_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to get system statistics
CREATE OR REPLACE FUNCTION get_governance_system_statistics()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_agents', (SELECT COUNT(*) FROM governance_agents),
        'active_agents', (SELECT COUNT(*) FROM governance_agents WHERE is_active = TRUE),
        'total_achievements', (SELECT COUNT(*) FROM governance_achievements),
        'total_enforcements', (SELECT COUNT(*) FROM governance_enforcement_records),
        'active_cycles', (SELECT COUNT(*) FROM governance_turn_cycles WHERE status = 'active'),
        'completed_cycles', (SELECT COUNT(*) FROM governance_turn_cycles WHERE status = 'completed'),
        'level_distribution', (
            SELECT jsonb_object_agg(level, count)
            FROM (
                SELECT level, COUNT(*) as count
                FROM governance_agents
                GROUP BY level
            ) level_counts
        ),
        'violation_summary', (
            SELECT jsonb_build_object(
                'minor', SUM((violations_count->>'minor')::INTEGER),
                'major', SUM((violations_count->>'major')::INTEGER),
                'critical', SUM((violations_count->>'critical')::INTEGER)
            )
            FROM governance_agents
        ),
        'average_performance_score', (
            SELECT ROUND(AVG(performance_score), 2)
            FROM governance_agents
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;