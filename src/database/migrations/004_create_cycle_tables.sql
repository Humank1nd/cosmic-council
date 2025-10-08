-- Migration: 004_create_cycle_tables.sql
-- Create cycle-related tables

-- Create enterprises table
CREATE TABLE IF NOT EXISTS enterprises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enterprise_type VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    configuration TEXT,
    performance_metrics TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for enterprises
CREATE INDEX IF NOT EXISTS idx_enterprises_type ON enterprises (enterprise_type);

CREATE INDEX IF NOT EXISTS idx_enterprises_status ON enterprises (status);

-- Create cycles table
CREATE TABLE IF NOT EXISTS cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES problems(id),
    status VARCHAR(20) DEFAULT 'pending',
    current_enterprise VARCHAR(50),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for cycles
CREATE INDEX IF NOT EXISTS idx_cycles_problem_id ON cycles (problem_id);

CREATE INDEX IF NOT EXISTS idx_cycles_status ON cycles (status);

CREATE INDEX IF NOT EXISTS idx_cycles_current_enterprise ON cycles (current_enterprise);

CREATE INDEX IF NOT EXISTS idx_cycles_started_at ON cycles (started_at);

CREATE INDEX IF NOT EXISTS idx_cycles_completed_at ON cycles (completed_at);

CREATE INDEX IF NOT EXISTS idx_cycles_created_by ON cycles (created_by);

-- Create cycle enterprises association table
CREATE TABLE IF NOT EXISTS cycle_enterprises (
    cycle_id UUID NOT NULL REFERENCES cycles (id),
    enterprise_id UUID NOT NULL REFERENCES enterprises (id),
    execution_order VARCHAR(10),
    status VARCHAR(20),
    started_at TIMESTAMP
    WITH
        TIME ZONE,
        completed_at TIMESTAMP
    WITH
        TIME ZONE,
        PRIMARY KEY (cycle_id, enterprise_id)
);

-- Create cycle results table
CREATE TABLE IF NOT EXISTS cycle_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES cycles(id),
    enterprise_type VARCHAR(50) NOT NULL,
    result_data TEXT,
    success VARCHAR(10) DEFAULT 'false',
    error_message TEXT,
    execution_time VARCHAR(20) DEFAULT '0.0',
    metrics TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for cycle results
CREATE INDEX IF NOT EXISTS idx_cycle_results_cycle_id ON cycle_results (cycle_id);

CREATE INDEX IF NOT EXISTS idx_cycle_results_enterprise_type ON cycle_results (enterprise_type);

CREATE INDEX IF NOT EXISTS idx_cycle_results_success ON cycle_results (success);

-- Create enterprise results table
CREATE TABLE IF NOT EXISTS enterprise_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES cycles(id),
    enterprise_id UUID NOT NULL REFERENCES enterprises(id),
    enterprise_type VARCHAR(50) NOT NULL,
    input_data TEXT,
    output_data TEXT,
    success VARCHAR(10) DEFAULT 'false',
    error_message TEXT,
    execution_time VARCHAR(20) DEFAULT '0.0',
    resources_used TEXT,
    quality_score VARCHAR(10) DEFAULT '0.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for enterprise results
CREATE INDEX IF NOT EXISTS idx_enterprise_results_cycle_id ON enterprise_results (cycle_id);

CREATE INDEX IF NOT EXISTS idx_enterprise_results_enterprise_id ON enterprise_results (enterprise_id);

CREATE INDEX IF NOT EXISTS idx_enterprise_results_enterprise_type ON enterprise_results (enterprise_type);

CREATE INDEX IF NOT EXISTS idx_enterprise_results_success ON enterprise_results (success);

-- Create cycle analytics table
CREATE TABLE IF NOT EXISTS cycle_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES cycles(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for cycle analytics
CREATE INDEX IF NOT EXISTS idx_cycle_analytics_cycle_id ON cycle_analytics (cycle_id);

CREATE INDEX IF NOT EXISTS idx_cycle_analytics_metric_name ON cycle_analytics (metric_name);

CREATE INDEX IF NOT EXISTS idx_cycle_analytics_timestamp ON cycle_analytics (timestamp);

-- Create triggers for updated_at
CREATE TRIGGER update_enterprises_updated_at 
    BEFORE UPDATE ON enterprises 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cycles_updated_at 
    BEFORE UPDATE ON cycles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cycle_results_updated_at 
    BEFORE UPDATE ON cycle_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enterprise_results_updated_at 
    BEFORE UPDATE ON enterprise_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cycle_analytics_updated_at 
    BEFORE UPDATE ON cycle_analytics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();