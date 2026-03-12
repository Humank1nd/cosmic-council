-- PostgreSQL initialization script for Cosmic Council Framework
-- This script sets up the initial database schema and configurations

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';

-- Create custom types
DO $$ BEGIN
    CREATE TYPE problem_complexity AS ENUM ('simple', 'moderate', 'complex', 'systemic');

EXCEPTION WHEN duplicate_object THEN null;

END $$;

DO $$ BEGIN
    CREATE TYPE problem_status AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE cycle_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE solution_status AS ENUM ('draft', 'review', 'approved', 'implemented', 'rejected');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE enterprise_type AS ENUM ('red_owl', 'orange_orangutan', 'yellow_honeybee', 'green_tortoise', 'blue_dolphin', 'purple_elephant');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems (created_at);

CREATE INDEX IF NOT EXISTS idx_problems_complexity ON problems (complexity);

CREATE INDEX IF NOT EXISTS idx_problems_status ON problems (status);

CREATE INDEX IF NOT EXISTS idx_problems_domain ON problems (domain);

CREATE INDEX IF NOT EXISTS idx_cycles_problem_id ON cycles (problem_id);

CREATE INDEX IF NOT EXISTS idx_cycles_status ON cycles (status);

CREATE INDEX IF NOT EXISTS idx_cycles_created_at ON cycles (created_at);

CREATE INDEX IF NOT EXISTS idx_solutions_cycle_id ON solutions (cycle_id);

CREATE INDEX IF NOT EXISTS idx_solutions_status ON solutions (status);

CREATE INDEX IF NOT EXISTS idx_enterprise_results_cycle_id ON enterprise_results (cycle_id);

CREATE INDEX IF NOT EXISTS idx_enterprise_results_enterprise_type ON enterprise_results (enterprise_type);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_problems_search ON problems USING gin (
    to_tsvector (
        'english',
        title || ' ' || description
    )
);

CREATE INDEX IF NOT EXISTS idx_solutions_search ON solutions USING gin (
    to_tsvector (
        'english',
        title || ' ' || description
    )
);

-- Create partial indexes for active records
CREATE INDEX IF NOT EXISTS idx_problems_active ON problems (created_at)
WHERE
    status IN ('pending', 'in_progress');

CREATE INDEX IF NOT EXISTS idx_cycles_active ON cycles (created_at)
WHERE
    status IN ('pending', 'running');

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_problems_complexity_status ON problems (complexity, status);

CREATE INDEX IF NOT EXISTS idx_cycles_problem_status ON cycles (problem_id, status);

CREATE INDEX IF NOT EXISTS idx_solutions_cycle_status ON solutions (cycle_id, status);

-- Create function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_problems_updated_at BEFORE UPDATE ON problems FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cycles_updated_at BEFORE UPDATE ON cycles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solutions_updated_at BEFORE UPDATE ON solutions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enterprise_results_updated_at BEFORE UPDATE ON enterprise_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for soft delete
CREATE OR REPLACE FUNCTION soft_delete_record()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = CURRENT_TIMESTAMP;
    NEW.status = 'deleted';
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create views for common queries
CREATE OR REPLACE VIEW active_problems AS
SELECT *
FROM problems
WHERE
    status IN ('pending', 'in_progress')
    AND deleted_at IS NULL;

CREATE OR REPLACE VIEW active_cycles AS
SELECT *
FROM cycles
WHERE
    status IN ('pending', 'running')
    AND deleted_at IS NULL;

CREATE OR REPLACE VIEW problem_statistics AS
SELECT
    complexity,
    status,
    COUNT(*) as count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (updated_at - created_at)
        )
    ) as avg_duration_seconds
FROM problems
WHERE
    deleted_at IS NULL
GROUP BY
    complexity,
    status;

CREATE OR REPLACE VIEW cycle_statistics AS
SELECT
    status,
    COUNT(*) as count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (end_time - start_time)
        )
    ) as avg_duration_seconds,
    AVG(overall_confidence) as avg_confidence
FROM cycles
WHERE
    deleted_at IS NULL
GROUP BY
    status;

-- Create function for cleaning up old records
CREATE OR REPLACE FUNCTION cleanup_old_records()
RETURNS void AS $$
BEGIN
    -- Delete old completed cycles (older than 1 year)
    DELETE FROM cycles WHERE status = 'completed' AND end_time < NOW() - INTERVAL '1 year';
    
    -- Delete old failed cycles (older than 6 months)
    DELETE FROM cycles WHERE status = 'failed' AND end_time < NOW() - INTERVAL '6 months';
    
    -- Delete old logs (older than 3 months)
    DELETE FROM system_logs WHERE created_at < NOW() - INTERVAL '3 months';
END;
$$ language 'plpgsql';

-- Create scheduled job for cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-records', '0 2 * * *', 'SELECT cleanup_old_records();');

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dream_caesar TO dream_caesar;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dream_caesar;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dream_caesar;

GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO dream_caesar;

-- Insert initial data
INSERT INTO
    users (
        user_id,
        username,
        email,
        role,
        is_active
    )
VALUES (
        'admin',
        'admin',
        'admin@cosmic-council.org',
        'admin',
        true
    ) ON CONFLICT (user_id) DO NOTHING;

-- Insert default enterprise configurations
INSERT INTO
    enterprise_configurations (
        enterprise_type,
        name,
        role,
        description,
        color,
        is_active
    )
VALUES (
        'red_owl',
        'Red Owl',
        'Research & Knowledge Gathering',
        'Conducts comprehensive research and knowledge gathering',
        '#ef4444',
        true
    ),
    (
        'orange_orangutan',
        'Orange Orangutan',
        'Logistics & Strategic Planning',
        'Handles logistics and strategic planning',
        '#f97316',
        true
    ),
    (
        'yellow_honeybee',
        'Yellow Honeybee',
        'Development & Innovation',
        'Focuses on development and innovation',
        '#eab308',
        true
    ),
    (
        'green_tortoise',
        'Green Tortoise',
        'Budget & Resource Management',
        'Manages budget and resource allocation',
        '#22c55e',
        true
    ),
    (
        'blue_dolphin',
        'Blue Dolphin',
        'Market & Communication',
        'Handles market analysis and communication',
        '#3b82f6',
        true
    ),
    (
        'purple_elephant',
        'Purple Elephant',
        'Support & Continuous Improvement',
        'Provides support and continuous improvement',
        '#8b5cf6',
        true
    ) ON CONFLICT (enterprise_type) DO NOTHING;

-- Insert default policy rules
INSERT INTO
    policy_rules (
        rule_id,
        name,
        description,
        policy_type,
        condition,
        action,
        priority,
        is_active
    )
VALUES (
        'default_access_control',
        'Default Access Control',
        'Default access control policy',
        'access_control',
        'user.role == "admin"',
        'allow',
        1,
        true
    ),
    (
        'default_budget_limit',
        'Default Budget Limit',
        'Default budget limit policy',
        'budget_management',
        'request.amount <= 10000',
        'allow',
        1,
        true
    ),
    (
        'default_ethics_compliance',
        'Default Ethics Compliance',
        'Default ethics compliance policy',
        'ethics_compliance',
        'true',
        'allow',
        1,
        true
    ) ON CONFLICT (rule_id) DO NOTHING;

-- Create initial system metrics
INSERT INTO
    system_metrics (
        metric_name,
        metric_type,
        value,
        timestamp
    )
VALUES (
        'system_uptime',
        'gauge',
        0,
        NOW()
    ),
    (
        'total_problems',
        'counter',
        0,
        NOW()
    ),
    (
        'total_cycles',
        'counter',
        0,
        NOW()
    ),
    (
        'total_solutions',
        'counter',
        0,
        NOW()
    ),
    (
        'success_rate',
        'gauge',
        0,
        NOW()
    ) ON CONFLICT (metric_name, timestamp) DO NOTHING;