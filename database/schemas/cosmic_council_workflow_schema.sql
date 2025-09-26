-- Cosmic Council Workflow Database Schema
-- Implements cascading ROYGBV workflow with individual stage tables
-- Based on Airtable conversation requirements adapted for PostgreSQL

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- CORE WORKFLOW TABLES
-- ============================================================================

-- Master Cycles Table - Tracks high-level cycle information
CREATE TABLE workflow_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_number INTEGER NOT NULL,
    problem_statement TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'archived')),

-- Cycle metadata
started_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    total_duration INTEGER, -- Duration in seconds

-- Feedback loop data
previous_cycle_id UUID REFERENCES workflow_cycles (id),
feedback_summary TEXT,
next_cycle_focus TEXT,

-- Configuration
max_iterations INTEGER DEFAULT 3,
current_iteration INTEGER DEFAULT 1,

-- Metadata
created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Constraints
UNIQUE(cycle_number) );

-- ============================================================================
-- STAGE-SPECIFIC TABLES (ROYGBV - Red Owl, Orange Orangutan, Yellow Honeybee, Green Tortoise, Blue Dolphin, Violet Elephant)
-- ============================================================================

-- Red Owl - Research & Inquiry
CREATE TABLE research_stage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES workflow_cycles(id) ON DELETE CASCADE,

-- Research data
problem_statement TEXT NOT NULL,
    key_findings TEXT,
    prioritized_questions TEXT[],
    research_sources TEXT[],
    root_cause_analysis JSONB,

-- Research metadata
research_depth VARCHAR(20) DEFAULT 'standard' CHECK (
    research_depth IN (
        'surface',
        'standard',
        'deep',
        'comprehensive'
    )
),
confidence_score DECIMAL(3, 2) CHECK (
    confidence_score >= 0
    AND confidence_score <= 1
),

-- Status tracking
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'in_progress',
        'completed',
        'failed'
    )
),
next_stage_ready BOOLEAN DEFAULT FALSE,

-- Timestamps
started_at TIMESTAMP
WITH
    TIME ZONE,
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Agent integration
agent_id VARCHAR(100),
    ai_model_used VARCHAR(100),
    ai_tokens_used INTEGER,
    ai_processing_time DECIMAL(10,3)
);

-- Orange Orangutan - Planning & Logistics
CREATE TABLE planning_stage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES workflow_cycles(id) ON DELETE CASCADE,
    research_stage_id UUID REFERENCES research_stage(id),

-- Planning data
action_plan JSONB NOT NULL,
    resource_requirements TEXT[],
    dependencies TEXT[],
    timelines JSONB,
    risk_assessment JSONB,

-- Planning metadata
planning_scope VARCHAR(20) DEFAULT 'standard' CHECK (
    planning_scope IN (
        'minimal',
        'standard',
        'comprehensive',
        'enterprise'
    )
),
confidence_score DECIMAL(3, 2) CHECK (
    confidence_score >= 0
    AND confidence_score <= 1
),

-- Status tracking
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'in_progress',
        'completed',
        'failed'
    )
),
next_stage_ready BOOLEAN DEFAULT FALSE,

-- Timestamps
started_at TIMESTAMP
WITH
    TIME ZONE,
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Agent integration
agent_id VARCHAR(100),
    ai_model_used VARCHAR(100),
    ai_tokens_used INTEGER,
    ai_processing_time DECIMAL(10,3)
);

-- Yellow Honeybee - Development & Creativity
CREATE TABLE development_stage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES workflow_cycles(id) ON DELETE CASCADE,
    planning_stage_id UUID REFERENCES planning_stage(id),

-- Development data
prototype_description TEXT,
    creative_solutions TEXT[],
    experimental_data JSONB,
    test_results JSONB,
    innovation_metrics JSONB,

-- Development metadata
development_approach VARCHAR(20) DEFAULT 'standard' CHECK (
    development_approach IN (
        'conservative',
        'standard',
        'innovative',
        'experimental'
    )
),
confidence_score DECIMAL(3, 2) CHECK (
    confidence_score >= 0
    AND confidence_score <= 1
),

-- Status tracking
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'in_progress',
        'completed',
        'failed'
    )
),
next_stage_ready BOOLEAN DEFAULT FALSE,

-- Timestamps
started_at TIMESTAMP
WITH
    TIME ZONE,
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Agent integration
agent_id VARCHAR(100),
    ai_model_used VARCHAR(100),
    ai_tokens_used INTEGER,
    ai_processing_time DECIMAL(10,3)
);

-- Green Tortoise - Budget & Resources
CREATE TABLE budget_stage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES workflow_cycles(id) ON DELETE CASCADE,
    development_stage_id UUID REFERENCES development_stage(id),

-- Budget data
budget_allocation JSONB NOT NULL,
    cost_analysis JSONB,
    resource_planning JSONB,
    financial_constraints TEXT[],
    sustainability_metrics JSONB,

-- Budget metadata
budget_scope VARCHAR(20) DEFAULT 'standard' CHECK (
    budget_scope IN (
        'minimal',
        'standard',
        'comprehensive',
        'enterprise'
    )
),
confidence_score DECIMAL(3, 2) CHECK (
    confidence_score >= 0
    AND confidence_score <= 1
),

-- Status tracking
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'in_progress',
        'completed',
        'failed'
    )
),
next_stage_ready BOOLEAN DEFAULT FALSE,

-- Timestamps
started_at TIMESTAMP
WITH
    TIME ZONE,
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Agent integration
agent_id VARCHAR(100),
    ai_model_used VARCHAR(100),
    ai_tokens_used INTEGER,
    ai_processing_time DECIMAL(10,3)
);

-- Blue Dolphin - Market & Communication
CREATE TABLE market_stage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES workflow_cycles(id) ON DELETE CASCADE,
    budget_stage_id UUID REFERENCES budget_stage(id),

-- Market data
target_audience JSONB,
communication_strategy TEXT,
marketing_plan JSONB,
engagement_metrics JSONB,
market_research JSONB,

-- Market metadata
market_scope VARCHAR(20) DEFAULT 'standard' CHECK (
    market_scope IN (
        'local',
        'standard',
        'regional',
        'global'
    )
),
confidence_score DECIMAL(3, 2) CHECK (
    confidence_score >= 0
    AND confidence_score <= 1
),

-- Status tracking
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'in_progress',
        'completed',
        'failed'
    )
),
next_stage_ready BOOLEAN DEFAULT FALSE,

-- Timestamps
started_at TIMESTAMP
WITH
    TIME ZONE,
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Agent integration
agent_id VARCHAR(100),
    ai_model_used VARCHAR(100),
    ai_tokens_used INTEGER,
    ai_processing_time DECIMAL(10,3)
);

-- Violet Elephant - Support & Feedback
CREATE TABLE support_stage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES workflow_cycles(id) ON DELETE CASCADE,
    market_stage_id UUID REFERENCES market_stage(id),

-- Support data
feedback_collected JSONB,
    support_insights TEXT[],
    performance_metrics JSONB,
    continuous_improvement_notes TEXT,
    next_cycle_recommendations TEXT,

-- Support metadata
support_scope VARCHAR(20) DEFAULT 'standard' CHECK (
    support_scope IN (
        'minimal',
        'standard',
        'comprehensive',
        'enterprise'
    )
),
confidence_score DECIMAL(3, 2) CHECK (
    confidence_score >= 0
    AND confidence_score <= 1
),

-- Status tracking
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'in_progress',
        'completed',
        'failed'
    )
),
cycle_complete BOOLEAN DEFAULT FALSE,

-- Timestamps
started_at TIMESTAMP
WITH
    TIME ZONE,
    completed_at TIMESTAMP
WITH
    TIME ZONE,
    created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Agent integration
agent_id VARCHAR(100),
    ai_model_used VARCHAR(100),
    ai_tokens_used INTEGER,
    ai_processing_time DECIMAL(10,3)
);

-- ============================================================================
-- AGENT AND INTEGRATION TABLES
-- ============================================================================

-- Agent Sessions - Track individual agent interactions
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES workflow_cycles(id) ON DELETE CASCADE,
    stage_type VARCHAR(20) NOT NULL CHECK (stage_type IN ('research', 'planning', 'development', 'budget', 'market', 'support')),
    stage_id UUID NOT NULL,

-- Agent data
agent_id VARCHAR(100) NOT NULL,
agent_type VARCHAR(50) NOT NULL, -- 'openai_assistant', 'make_com_workflow', 'custom'
session_data JSONB,

-- AI integration
ai_model_used VARCHAR(100),
ai_tokens_used INTEGER,
ai_processing_time DECIMAL(10, 3),
ai_confidence DECIMAL(3, 2),

-- Status
status VARCHAR(20) DEFAULT 'active' CHECK (
    status IN (
        'active',
        'completed',
        'failed',
        'cancelled'
    )
),

-- Timestamps
started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Integration Logs - Track external system interactions
CREATE TABLE integration_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID REFERENCES workflow_cycles(id) ON DELETE CASCADE,
    stage_id UUID,
    stage_type VARCHAR(20),

-- Integration data
integration_type VARCHAR(50) NOT NULL, -- 'openai_api', 'make_com', 'airtable', 'google_sheets'
integration_name VARCHAR(100) NOT NULL,
operation VARCHAR(50) NOT NULL, -- 'read', 'write', 'update', 'delete'

-- Request/Response data
request_data JSONB, response_data JSONB, error_data JSONB,

-- Status
status VARCHAR(20) NOT NULL CHECK (
    status IN (
        'success',
        'error',
        'timeout',
        'cancelled'
    )
),

-- Timestamps
executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    duration_ms INTEGER
);

-- ============================================================================
-- AUTOMATION AND TRIGGERS
-- ============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers to all stage tables
CREATE TRIGGER update_research_stage_updated_at BEFORE UPDATE ON research_stage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_planning_stage_updated_at BEFORE UPDATE ON planning_stage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_development_stage_updated_at BEFORE UPDATE ON development_stage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_stage_updated_at BEFORE UPDATE ON budget_stage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_stage_updated_at BEFORE UPDATE ON market_stage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_stage_updated_at BEFORE UPDATE ON support_stage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_cycles_updated_at BEFORE UPDATE ON workflow_cycles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically create next stage when current stage is completed
CREATE OR REPLACE FUNCTION create_next_stage()
RETURNS TRIGGER AS $$
DECLARE
    next_stage_id UUID;
BEGIN
    -- Only proceed if the stage is marked as completed and next_stage_ready is TRUE
    IF NEW.status = 'completed' AND NEW.next_stage_ready = TRUE THEN
        
        -- Determine next stage based on current stage
        IF TG_TABLE_NAME = 'research_stage' THEN
            -- Create planning stage
            INSERT INTO planning_stage (cycle_id, research_stage_id, status, started_at)
            VALUES (NEW.cycle_id, NEW.id, 'pending', NOW())
            RETURNING id INTO next_stage_id;
            
        ELSIF TG_TABLE_NAME = 'planning_stage' THEN
            -- Create development stage
            INSERT INTO development_stage (cycle_id, planning_stage_id, status, started_at)
            VALUES (NEW.cycle_id, NEW.id, 'pending', NOW())
            RETURNING id INTO next_stage_id;
            
        ELSIF TG_TABLE_NAME = 'development_stage' THEN
            -- Create budget stage
            INSERT INTO budget_stage (cycle_id, development_stage_id, status, started_at)
            VALUES (NEW.cycle_id, NEW.id, 'pending', NOW())
            RETURNING id INTO next_stage_id;
            
        ELSIF TG_TABLE_NAME = 'budget_stage' THEN
            -- Create market stage
            INSERT INTO market_stage (cycle_id, budget_stage_id, status, started_at)
            VALUES (NEW.cycle_id, NEW.id, 'pending', NOW())
            RETURNING id INTO next_stage_id;
            
        ELSIF TG_TABLE_NAME = 'market_stage' THEN
            -- Create support stage
            INSERT INTO support_stage (cycle_id, market_stage_id, status, started_at)
            VALUES (NEW.cycle_id, NEW.id, 'pending', NOW())
            RETURNING id INTO next_stage_id;
            
        ELSIF TG_TABLE_NAME = 'support_stage' THEN
            -- Mark cycle as complete and prepare for next cycle
            UPDATE workflow_cycles 
            SET status = 'completed', completed_at = NOW()
            WHERE id = NEW.cycle_id;
            
            -- Log the completion
            INSERT INTO integration_logs (cycle_id, stage_type, integration_type, integration_name, operation, status, request_data)
            VALUES (NEW.cycle_id, 'support', 'system', 'cycle_completion', 'complete_cycle', 'success', 
                   jsonb_build_object('cycle_id', NEW.cycle_id, 'completed_at', NOW()));
        END IF;
        
        -- Log the stage creation
        IF next_stage_id IS NOT NULL THEN
            INSERT INTO integration_logs (cycle_id, stage_id, stage_type, integration_type, integration_name, operation, status, request_data)
            VALUES (NEW.cycle_id, next_stage_id, 
                   CASE TG_TABLE_NAME 
                       WHEN 'research_stage' THEN 'planning'
                       WHEN 'planning_stage' THEN 'development'
                       WHEN 'development_stage' THEN 'budget'
                       WHEN 'budget_stage' THEN 'market'
                       WHEN 'market_stage' THEN 'support'
                   END,
                   'system', 'stage_creation', 'create_stage', 'success', 
                   jsonb_build_object('previous_stage_id', NEW.id, 'next_stage_id', next_stage_id));
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the next stage creation trigger to all stage tables
CREATE TRIGGER create_next_stage_after_research AFTER UPDATE ON research_stage FOR EACH ROW EXECUTE FUNCTION create_next_stage();

CREATE TRIGGER create_next_stage_after_planning AFTER UPDATE ON planning_stage FOR EACH ROW EXECUTE FUNCTION create_next_stage();

CREATE TRIGGER create_next_stage_after_development AFTER UPDATE ON development_stage FOR EACH ROW EXECUTE FUNCTION create_next_stage();

CREATE TRIGGER create_next_stage_after_budget AFTER UPDATE ON budget_stage FOR EACH ROW EXECUTE FUNCTION create_next_stage();

CREATE TRIGGER create_next_stage_after_market AFTER UPDATE ON market_stage FOR EACH ROW EXECUTE FUNCTION create_next_stage();

CREATE TRIGGER create_next_stage_after_support AFTER UPDATE ON support_stage FOR EACH ROW EXECUTE FUNCTION create_next_stage();

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Cycle indexes
CREATE INDEX idx_workflow_cycles_status ON workflow_cycles (status);

CREATE INDEX idx_workflow_cycles_started_at ON workflow_cycles (started_at);

CREATE INDEX idx_workflow_cycles_cycle_number ON workflow_cycles (cycle_number);

-- Stage indexes
CREATE INDEX idx_research_stage_cycle_id ON research_stage (cycle_id);

CREATE INDEX idx_research_stage_status ON research_stage (status);

CREATE INDEX idx_planning_stage_cycle_id ON planning_stage (cycle_id);

CREATE INDEX idx_planning_stage_status ON planning_stage (status);

CREATE INDEX idx_development_stage_cycle_id ON development_stage (cycle_id);

CREATE INDEX idx_development_stage_status ON development_stage (status);

CREATE INDEX idx_budget_stage_cycle_id ON budget_stage (cycle_id);

CREATE INDEX idx_budget_stage_status ON budget_stage (status);

CREATE INDEX idx_market_stage_cycle_id ON market_stage (cycle_id);

CREATE INDEX idx_market_stage_status ON market_stage (status);

CREATE INDEX idx_support_stage_cycle_id ON support_stage (cycle_id);

CREATE INDEX idx_support_stage_status ON support_stage (status);

-- Agent and integration indexes
CREATE INDEX idx_agent_sessions_cycle_id ON agent_sessions (cycle_id);

CREATE INDEX idx_agent_sessions_stage_type ON agent_sessions (stage_type);

CREATE INDEX idx_integration_logs_cycle_id ON integration_logs (cycle_id);

CREATE INDEX idx_integration_logs_integration_type ON integration_logs (integration_type);

CREATE INDEX idx_integration_logs_executed_at ON integration_logs (executed_at);

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

-- View to see complete cycle with all stages
CREATE VIEW cycle_complete_view AS
SELECT
    wc.id as cycle_id,
    wc.cycle_number,
    wc.problem_statement,
    wc.status as cycle_status,
    wc.started_at as cycle_started_at,
    wc.completed_at as cycle_completed_at,

-- Research stage
rs.id as research_id,
rs.status as research_status,
rs.confidence_score as research_confidence,
rs.completed_at as research_completed_at,

-- Planning stage
ps.id as planning_id,
ps.status as planning_status,
ps.confidence_score as planning_confidence,
ps.completed_at as planning_completed_at,

-- Development stage
ds.id as development_id,
ds.status as development_status,
ds.confidence_score as development_confidence,
ds.completed_at as development_completed_at,

-- Budget stage
bs.id as budget_id,
bs.status as budget_status,
bs.confidence_score as budget_confidence,
bs.completed_at as budget_completed_at,

-- Market stage
ms.id as market_id,
ms.status as market_status,
ms.confidence_score as market_confidence,
ms.completed_at as market_completed_at,

-- Support stage
ss.id as support_id,
ss.status as support_status,
ss.confidence_score as support_confidence,
ss.completed_at as support_completed_at
FROM
    workflow_cycles wc
    LEFT JOIN research_stage rs ON wc.id = rs.cycle_id
    LEFT JOIN planning_stage ps ON wc.id = ps.cycle_id
    LEFT JOIN development_stage ds ON wc.id = ds.cycle_id
    LEFT JOIN budget_stage bs ON wc.id = bs.cycle_id
    LEFT JOIN market_stage ms ON wc.id = ms.cycle_id
    LEFT JOIN support_stage ss ON wc.id = ss.cycle_id;

-- View for stage progression tracking
CREATE VIEW stage_progression_view AS
SELECT
    cycle_id,
    cycle_number,
    problem_statement,
    cycle_status,

-- Calculate stage completion percentage
CASE
    WHEN research_status = 'completed' THEN 16.67
    WHEN planning_status = 'completed' THEN 33.33
    WHEN development_status = 'completed' THEN 50.00
    WHEN budget_status = 'completed' THEN 66.67
    WHEN market_status = 'completed' THEN 83.33
    WHEN support_status = 'completed' THEN 100.00
    ELSE 0.00
END as completion_percentage,

-- Current stage
CASE
    WHEN research_status = 'in_progress'
    OR research_status = 'pending' THEN 'research'
    WHEN planning_status = 'in_progress'
    OR planning_status = 'pending' THEN 'planning'
    WHEN development_status = 'in_progress'
    OR development_status = 'pending' THEN 'development'
    WHEN budget_status = 'in_progress'
    OR budget_status = 'pending' THEN 'budget'
    WHEN market_status = 'in_progress'
    OR market_status = 'pending' THEN 'market'
    WHEN support_status = 'in_progress'
    OR support_status = 'pending' THEN 'support'
    ELSE 'completed'
END as current_stage
FROM cycle_complete_view;

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to start a new cycle
CREATE OR REPLACE FUNCTION start_new_cycle(
    p_problem_statement TEXT,
    p_cycle_number INTEGER DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    new_cycle_id UUID;
    cycle_num INTEGER;
BEGIN
    -- Get next cycle number if not provided
    IF p_cycle_number IS NULL THEN
        SELECT COALESCE(MAX(cycle_number), 0) + 1 INTO cycle_num FROM workflow_cycles;
    ELSE
        cycle_num := p_cycle_number;
    END IF;
    
    -- Create new cycle
    INSERT INTO workflow_cycles (cycle_number, problem_statement, status, started_at)
    VALUES (cycle_num, p_problem_statement, 'in_progress', NOW())
    RETURNING id INTO new_cycle_id;
    
    -- Create initial research stage
    INSERT INTO research_stage (cycle_id, problem_statement, status, started_at)
    VALUES (new_cycle_id, p_problem_statement, 'pending', NOW());
    
    RETURN new_cycle_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get cycle status summary
CREATE OR REPLACE FUNCTION get_cycle_status(p_cycle_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'cycle_id', wc.id,
        'cycle_number', wc.cycle_number,
        'problem_statement', wc.problem_statement,
        'status', wc.status,
        'started_at', wc.started_at,
        'completed_at', wc.completed_at,
        'stages', jsonb_build_object(
            'research', jsonb_build_object(
                'id', rs.id,
                'status', rs.status,
                'confidence_score', rs.confidence_score,
                'completed_at', rs.completed_at
            ),
            'planning', jsonb_build_object(
                'id', ps.id,
                'status', ps.status,
                'confidence_score', ps.confidence_score,
                'completed_at', ps.completed_at
            ),
            'development', jsonb_build_object(
                'id', ds.id,
                'status', ds.status,
                'confidence_score', ds.confidence_score,
                'completed_at', ds.completed_at
            ),
            'budget', jsonb_build_object(
                'id', bs.id,
                'status', bs.status,
                'confidence_score', bs.confidence_score,
                'completed_at', bs.completed_at
            ),
            'market', jsonb_build_object(
                'id', ms.id,
                'status', ms.status,
                'confidence_score', ms.confidence_score,
                'completed_at', ms.completed_at
            ),
            'support', jsonb_build_object(
                'id', ss.id,
                'status', ss.status,
                'confidence_score', ss.confidence_score,
                'completed_at', ss.completed_at
            )
        )
    ) INTO result
    FROM workflow_cycles wc
    LEFT JOIN research_stage rs ON wc.id = rs.cycle_id
    LEFT JOIN planning_stage ps ON wc.id = ps.cycle_id
    LEFT JOIN development_stage ds ON wc.id = ds.cycle_id
    LEFT JOIN budget_stage bs ON wc.id = bs.cycle_id
    LEFT JOIN market_stage ms ON wc.id = ms.cycle_id
    LEFT JOIN support_stage ss ON wc.id = ss.cycle_id
    WHERE wc.id = p_cycle_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;