-- Cosmic Council Enterprise Architecture Migration
-- Implements the fractal multi-agent corporate structure

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "vector";
-- For pgvector if available

-- ============================================================================
-- RED OWL - Knowledge Lake
-- ============================================================================

-- Vector embeddings for semantic search
CREATE TABLE IF NOT EXISTS knowledge_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    content TEXT NOT NULL,
    embedding VECTOR (1536), -- OpenAI embedding dimension
    metadata JSONB DEFAULT '{}',
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ),
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Structured knowledge base
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_url TEXT,
    confidence_score FLOAT DEFAULT 0.0,
    enterprise TEXT CHECK (enterprise IN ('red','orange','yellow','green','blue','purple')),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- ORANGE ORANGUTAN - Event Log & Planning
-- ============================================================================

-- Temporal event tracking
CREATE TABLE IF NOT EXISTS event_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    event_type TEXT NOT NULL,
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    agent_id UUID REFERENCES common_agents (agent_id),
    payload JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT now(),
    correlation_id UUID,
    severity TEXT CHECK (
        severity IN (
            'low',
            'medium',
            'high',
            'critical'
        )
    ) DEFAULT 'low'
);

-- Strategic planning cycles
CREATE TABLE IF NOT EXISTS planning_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    cycle_name TEXT NOT NULL,
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    objectives JSONB DEFAULT '{}',
    timeline JSONB DEFAULT '{}',
    status TEXT CHECK (
        status IN (
            'planning',
            'active',
            'completed',
            'cancelled'
        )
    ) DEFAULT 'planning',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- YELLOW HONEYBEE - Experiment Registry
-- ============================================================================

-- ML experiment tracking
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name TEXT NOT NULL,
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    agent_id UUID REFERENCES common_agents (agent_id),
    parameters JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    artifacts JSONB DEFAULT '{}',
    status TEXT CHECK (
        status IN (
            'planned',
            'running',
            'completed',
            'failed',
            'cancelled'
        )
    ) DEFAULT 'planned',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Prototype outputs
CREATE TABLE IF NOT EXISTS prototypes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    experiment_id UUID REFERENCES experiments (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    code_repo TEXT,
    deployment_url TEXT,
    performance_metrics JSONB DEFAULT '{}',
    status TEXT CHECK (
        status IN (
            'development',
            'testing',
            'deployed',
            'archived'
        )
    ) DEFAULT 'development',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- GREEN TURTLE - Resource Ledger
-- ============================================================================

-- Budget and resource tracking
CREATE TABLE IF NOT EXISTS resource_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    agent_id UUID REFERENCES common_agents (agent_id),
    resource_type TEXT NOT NULL, -- compute, storage, api_calls, etc.
    amount DECIMAL NOT NULL,
    cost_per_unit DECIMAL NOT NULL,
    total_cost DECIMAL GENERATED ALWAYS AS (amount * cost_per_unit) STORED,
    budget_period TEXT NOT NULL,
    status TEXT CHECK (
        status IN (
            'allocated',
            'used',
            'exhausted',
            'cancelled'
        )
    ) DEFAULT 'allocated',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Sustainability metrics
CREATE TABLE IF NOT EXISTS sustainability_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    metric_type TEXT NOT NULL, -- carbon_footprint, energy_usage, etc.
    value DECIMAL NOT NULL,
    unit TEXT NOT NULL,
    measurement_date DATE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- BLUE DOLPHIN - Communication Graph
-- ============================================================================

-- Message and influence tracking
CREATE TABLE IF NOT EXISTS communications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    sender_enterprise TEXT CHECK (
        sender_enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    receiver_enterprise TEXT CHECK (
        receiver_enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ),
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    sentiment_score FLOAT,
    influence_score FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Brand safety and compliance
CREATE TABLE IF NOT EXISTS brand_safety_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    safety_score FLOAT NOT NULL,
    violations TEXT[] DEFAULT '{}',
    approved BOOLEAN,
    reviewed_by UUID REFERENCES common_agents(agent_id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- PURPLE ELEPHANT - Empathy Index
-- ============================================================================

-- Sentiment and reflection tracking
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    enterprise TEXT CHECK (enterprise IN ('red','orange','yellow','green','blue','purple')) NOT NULL,
    agent_id UUID REFERENCES common_agents(agent_id),
    content TEXT NOT NULL,
    sentiment_score FLOAT NOT NULL,
    emotion_labels TEXT[] DEFAULT '{}',
    confidence FLOAT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Continuous reflection and feedback
CREATE TABLE IF NOT EXISTS reflection_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    enterprise TEXT CHECK (
        enterprise IN (
            'red',
            'orange',
            'yellow',
            'green',
            'blue',
            'purple'
        )
    ) NOT NULL,
    decision_id UUID REFERENCES decisions (decision_id),
    reflection_type TEXT NOT NULL,
    insights JSONB DEFAULT '{}',
    improvement_suggestions JSONB DEFAULT '{}',
    action_items JSONB DEFAULT '{}',
    status TEXT CHECK (
        status IN (
            'pending',
            'in_progress',
            'completed',
            'archived'
        )
    ) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Knowledge embeddings indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_enterprise ON knowledge_embeddings (enterprise);

CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_created_at ON knowledge_embeddings (created_at);

-- Knowledge base indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_base_enterprise ON knowledge_base (enterprise);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags ON knowledge_base USING GIN (tags);

-- Event log indexes
CREATE INDEX IF NOT EXISTS idx_event_log_enterprise ON event_log (enterprise);

CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log (timestamp);

CREATE INDEX IF NOT EXISTS idx_event_log_correlation_id ON event_log (correlation_id);

-- Planning cycles indexes
CREATE INDEX IF NOT EXISTS idx_planning_cycles_enterprise ON planning_cycles (enterprise);

CREATE INDEX IF NOT EXISTS idx_planning_cycles_status ON planning_cycles (status);

-- Experiments indexes
CREATE INDEX IF NOT EXISTS idx_experiments_enterprise ON experiments (enterprise);

CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments (status);

-- Resource allocations indexes
CREATE INDEX IF NOT EXISTS idx_resource_allocations_enterprise ON resource_allocations (enterprise);

CREATE INDEX IF NOT EXISTS idx_resource_allocations_budget_period ON resource_allocations (budget_period);

-- Communications indexes
CREATE INDEX IF NOT EXISTS idx_communications_sender ON communications (sender_enterprise);

CREATE INDEX IF NOT EXISTS idx_communications_receiver ON communications (receiver_enterprise);

CREATE INDEX IF NOT EXISTS idx_communications_created_at ON communications (created_at);

-- Sentiment analysis indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_enterprise ON sentiment_analysis (enterprise);

CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_created_at ON sentiment_analysis (created_at);

-- Reflection cycles indexes
CREATE INDEX IF NOT EXISTS idx_reflection_cycles_enterprise ON reflection_cycles (enterprise);

CREATE INDEX IF NOT EXISTS idx_reflection_cycles_status ON reflection_cycles (status);

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample agents for each enterprise
INSERT INTO
    common_agents (
        agent_id,
        name,
        enterprise,
        squad
    )
VALUES (
        '11111111-1111-1111-1111-111111111111',
        'Red Data Miner',
        'red',
        'data_miner'
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'Orange Logistics Planner',
        'orange',
        'logistics'
    ),
    (
        '33333333-3333-3333-3333-333333333333',
        'Yellow Prototype Developer',
        'yellow',
        'prototype'
    ),
    (
        '44444444-4444-4444-4444-444444444444',
        'Green Budget Manager',
        'green',
        'budget'
    ),
    (
        '55555555-5555-5555-5555-555555555555',
        'Blue Communication Specialist',
        'blue',
        'comms'
    ),
    (
        '66666666-6666-6666-6666-666666666666',
        'Purple Empathy Analyst',
        'purple',
        'empathy'
    ) ON CONFLICT (agent_id) DO NOTHING;