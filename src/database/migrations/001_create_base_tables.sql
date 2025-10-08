-- Migration: 001_create_base_tables.sql
-- Create base tables and common structures

-- Create base model table structure
CREATE TABLE IF NOT EXISTS base_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for base model
CREATE INDEX IF NOT EXISTS idx_base_models_created_at ON base_models (created_at);

CREATE INDEX IF NOT EXISTS idx_base_models_updated_at ON base_models (updated_at);

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for audit log
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs (action);

CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs (resource_type);

CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON audit_logs (resource_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs (timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id);

-- Create system metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    tags TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for system metrics
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics (metric_name);

CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics (timestamp);

CREATE INDEX IF NOT EXISTS idx_system_metrics_type ON system_metrics (metric_type);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for base_models
CREATE TRIGGER update_base_models_updated_at 
    BEFORE UPDATE ON base_models 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for audit_logs
CREATE TRIGGER update_audit_logs_updated_at 
    BEFORE UPDATE ON audit_logs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for system_metrics
CREATE TRIGGER update_system_metrics_updated_at 
    BEFORE UPDATE ON system_metrics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();