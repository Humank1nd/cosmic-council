-- Perpetual Thinking System Database Initialization
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create perpetual sessions table
CREATE TABLE IF NOT EXISTS perpetual_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    session_name VARCHAR(255) NOT NULL,
    initial_input TEXT NOT NULL,
    mode VARCHAR(50) DEFAULT 'collaborative',
    goals TEXT[],
    success_criteria TEXT[],
    ai_enhancement_level VARCHAR(50) DEFAULT 'enhanced',
    ai_learning_enabled BOOLEAN DEFAULT true,
    ai_adaptation_enabled BOOLEAN DEFAULT true,
    ai_breakthrough_detection BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create perpetual cycles table
CREATE TABLE IF NOT EXISTS perpetual_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL REFERENCES perpetual_sessions(session_id),
    cycle_id VARCHAR(255) UNIQUE NOT NULL,
    cycle_number INTEGER NOT NULL,
    cycle_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_data TEXT,
    output_data JSONB,
    next_questions TEXT[],
    confidence_score DECIMAL(3,2),
    creativity_score DECIMAL(3,2),
    wisdom_density DECIMAL(3,2),
    pattern_type VARCHAR(50),
    processing_time DECIMAL(10,3),
    learning_insights TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create AI cycle enhancements table
CREATE TABLE IF NOT EXISTS ai_cycle_enhancements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    enhancement_id VARCHAR(255) UNIQUE NOT NULL,
    cycle_id VARCHAR(255) NOT NULL REFERENCES perpetual_cycles (cycle_id),
    ai_enhancement_level VARCHAR(50) NOT NULL,
    ai_thinking_mode VARCHAR(50) NOT NULL,
    ai_prompt_used TEXT,
    ai_response_summary TEXT,
    ai_confidence DECIMAL(3, 2),
    ai_reasoning TEXT,
    ai_tokens_used INTEGER,
    ai_processing_time DECIMAL(10, 3),
    impact_score DECIMAL(3, 2) DEFAULT 0.0,
    learning_feedback TEXT,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create breakthrough moments table
CREATE TABLE IF NOT EXISTS breakthrough_moments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    session_id VARCHAR(255) NOT NULL REFERENCES perpetual_sessions (session_id),
    cycle_id VARCHAR(255) REFERENCES perpetual_cycles (cycle_id),
    breakthrough_type VARCHAR(50) NOT NULL,
    insight_description TEXT NOT NULL,
    impact_score DECIMAL(3, 2),
    context_data JSONB,
    trigger_pattern VARCHAR(50),
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create session metrics table
CREATE TABLE IF NOT EXISTS session_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    session_id VARCHAR(255) NOT NULL REFERENCES perpetual_sessions (session_id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10, 3),
    metric_data JSONB,
    recorded_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_perpetual_sessions_session_id ON perpetual_sessions (session_id);

CREATE INDEX IF NOT EXISTS idx_perpetual_sessions_status ON perpetual_sessions (status);

CREATE INDEX IF NOT EXISTS idx_perpetual_sessions_created_at ON perpetual_sessions (created_at);

CREATE INDEX IF NOT EXISTS idx_perpetual_cycles_session_id ON perpetual_cycles (session_id);

CREATE INDEX IF NOT EXISTS idx_perpetual_cycles_cycle_id ON perpetual_cycles (cycle_id);

CREATE INDEX IF NOT EXISTS idx_perpetual_cycles_cycle_number ON perpetual_cycles (cycle_number);

CREATE INDEX IF NOT EXISTS idx_perpetual_cycles_status ON perpetual_cycles (status);

CREATE INDEX IF NOT EXISTS idx_perpetual_cycles_created_at ON perpetual_cycles (created_at);

CREATE INDEX IF NOT EXISTS idx_ai_cycle_enhancements_cycle_id ON ai_cycle_enhancements (cycle_id);

CREATE INDEX IF NOT EXISTS idx_ai_cycle_enhancements_enhancement_id ON ai_cycle_enhancements (enhancement_id);

CREATE INDEX IF NOT EXISTS idx_ai_cycle_enhancements_created_at ON ai_cycle_enhancements (created_at);

CREATE INDEX IF NOT EXISTS idx_breakthrough_moments_session_id ON breakthrough_moments (session_id);

CREATE INDEX IF NOT EXISTS idx_breakthrough_moments_cycle_id ON breakthrough_moments (cycle_id);

CREATE INDEX IF NOT EXISTS idx_breakthrough_moments_created_at ON breakthrough_moments (created_at);

CREATE INDEX IF NOT EXISTS idx_session_metrics_session_id ON session_metrics (session_id);

CREATE INDEX IF NOT EXISTS idx_session_metrics_metric_name ON session_metrics (metric_name);

CREATE INDEX IF NOT EXISTS idx_session_metrics_recorded_at ON session_metrics (recorded_at);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_perpetual_cycles_output_data_gin ON perpetual_cycles USING GIN (output_data);

CREATE INDEX IF NOT EXISTS idx_ai_cycle_enhancements_context_data_gin ON ai_cycle_enhancements USING GIN (context_data);

CREATE INDEX IF NOT EXISTS idx_breakthrough_moments_context_data_gin ON breakthrough_moments USING GIN (context_data);

CREATE INDEX IF NOT EXISTS idx_session_metrics_metric_data_gin ON session_metrics USING GIN (metric_data);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_perpetual_sessions_updated_at 
    BEFORE UPDATE ON perpetual_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_perpetual_cycles_updated_at 
    BEFORE UPDATE ON perpetual_cycles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data
INSERT INTO perpetual_sessions (
    session_id, 
    session_name, 
    initial_input, 
    mode, 
    goals, 
    success_criteria,
    ai_enhancement_level,
    ai_learning_enabled,
    ai_adaptation_enabled,
    ai_breakthrough_detection,
    status
) VALUES (
    'system-init-session',
    'System Initialization Session',
    'Perpetual thinking system initialization and setup',
    'system',
    ARRAY['system_initialization', 'database_setup'],
    ARRAY['tables_created', 'indexes_created', 'triggers_created'],
    'enhanced',
    true,
    true,
    true,
    'completed'
) ON CONFLICT (session_id) DO NOTHING;