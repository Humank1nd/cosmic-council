-- Cosmic Council Refinement Engine - Database Initialization
-- This script initializes the database with the required schema

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS cosmic_council_db;

-- Use the database
\c cosmic_council_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create the layers table
CREATE TABLE IF NOT EXISTS layers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    purpose TEXT,
    example_reframing TEXT,
    capabilities JSONB,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create the problems table
CREATE TABLE IF NOT EXISTS problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    initial_layer VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    max_iterations INTEGER DEFAULT 100,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        created_by UUID,
        metadata JSONB DEFAULT '{}',
        FOREIGN KEY (initial_layer) REFERENCES layers (name)
);

-- Create the layer_runs table
CREATE TABLE IF NOT EXISTS layer_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL,
    layer VARCHAR(50) NOT NULL,
    iteration INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP
    WITH
        TIME ZONE,
        finished_at TIMESTAMP
    WITH
        TIME ZONE,
        total_cost_usd DECIMAL(10, 4) DEFAULT 0.0,
        total_latency_ms INTEGER DEFAULT 0,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE,
        FOREIGN KEY (layer) REFERENCES layers (name)
);

-- Create the sector_runs table
CREATE TABLE IF NOT EXISTS sector_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    layer_run_id UUID NOT NULL,
    sector VARCHAR(50) NOT NULL,
    iteration INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP
    WITH
        TIME ZONE,
        finished_at TIMESTAMP
    WITH
        TIME ZONE,
        output_json JSONB,
        metrics JSONB,
        error_message TEXT,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (layer_run_id) REFERENCES layer_runs (id) ON DELETE CASCADE
);

-- Create the refinements table
CREATE TABLE IF NOT EXISTS refinements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL,
    from_layer VARCHAR(50) NOT NULL,
    to_layer VARCHAR(50) NOT NULL,
    rationale TEXT NOT NULL,
    refined_question TEXT NOT NULL,
    decision_metadata JSONB,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE,
        FOREIGN KEY (from_layer) REFERENCES layers (name),
        FOREIGN KEY (to_layer) REFERENCES layers (name)
);

-- Create the answers table
CREATE TABLE IF NOT EXISTS answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    problem_id UUID NOT NULL,
    layer VARCHAR(50) NOT NULL,
    solution_json JSONB NOT NULL,
    confidence_score DECIMAL(3, 2) NOT NULL,
    completeness_score DECIMAL(3, 2) NOT NULL,
    novelty_score DECIMAL(3, 2) NOT NULL,
    alignment_score DECIMAL(3, 2) NOT NULL,
    net_benefit_score DECIMAL(3, 2) NOT NULL,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE,
        FOREIGN KEY (layer) REFERENCES layers (name)
);

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    WITH
        TIME ZONE
);

-- Create the api_keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    permissions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP
    WITH
        TIME ZONE,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Create the audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Insert default layers
INSERT INTO
    layers (
        name,
        description,
        purpose,
        example_reframing,
        capabilities
    )
VALUES (
        'deci',
        'Decide - Strategic decision making',
        'High-level strategic decisions and problem framing',
        'How can we strategically approach this problem?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["llm", "rag"]}'
    ),
    (
        'centi',
        'Center - Core problem analysis',
        'Core problem analysis and solution design',
        'What is the core problem we need to solve?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["llm", "rag", "graph_analysis"]}'
    ),
    (
        'milli',
        'Mill - Detailed implementation planning',
        'Detailed implementation planning and resource allocation',
        'How do we implement this solution in detail?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["llm", "rag", "optimization"]}'
    ),
    (
        'micro',
        'Micro - Granular optimization',
        'Granular optimization and fine-tuning',
        'How can we optimize this solution at a granular level?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["llm", "optimization", "graph_analysis"]}'
    ),
    (
        'nano',
        'Nano - Atomic-level analysis',
        'Atomic-level analysis and precision',
        'What are the atomic components of this solution?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["llm", "symbolic_ai", "optimization"]}'
    ),
    (
        'pico',
        'Pico - Sub-atomic precision',
        'Sub-atomic precision and micro-optimization',
        'How can we achieve sub-atomic precision?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["symbolic_ai", "optimization", "quantum_inspired"]}'
    ),
    (
        'femto',
        'Femto - Quantum-inspired analysis',
        'Quantum-inspired analysis and parallel processing',
        'How can we use quantum-inspired methods?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["quantum_inspired", "parallel_processing", "symbolic_ai"]}'
    ),
    (
        'atto',
        'Atto - Ultra-precise modeling',
        'Ultra-precise modeling and simulation',
        'How can we model this with ultra-precision?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["quantum_inspired", "simulation", "parallel_processing"]}'
    ),
    (
        'zepto',
        'Zepto - Extreme precision',
        'Extreme precision and micro-simulation',
        'How can we achieve extreme precision?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["quantum_inspired", "micro_simulation", "extreme_precision"]}'
    ),
    (
        'yocto',
        'Yocto - Maximum precision',
        'Maximum precision and nano-simulation',
        'How can we achieve maximum precision?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["quantum_inspired", "nano_simulation", "maximum_precision"]}'
    ),
    (
        'ronto',
        'Ronto - Ultimate precision',
        'Ultimate precision and pico-simulation',
        'How can we achieve ultimate precision?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["quantum_inspired", "pico_simulation", "ultimate_precision"]}'
    ),
    (
        'quecto',
        'Quecto - Absolute precision',
        'Absolute precision and femto-simulation',
        'How can we achieve absolute precision?',
        '{"ai_providers": ["openai", "anthropic"], "tools": ["quantum_inspired", "femto_simulation", "absolute_precision"]}'
    ) ON CONFLICT (name) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_problems_status ON problems (status);

CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems (created_at);

CREATE INDEX IF NOT EXISTS idx_problems_initial_layer ON problems (initial_layer);

CREATE INDEX IF NOT EXISTS idx_layer_runs_problem_id ON layer_runs (problem_id);

CREATE INDEX IF NOT EXISTS idx_layer_runs_layer ON layer_runs (layer);

CREATE INDEX IF NOT EXISTS idx_layer_runs_status ON layer_runs (status);

CREATE INDEX IF NOT EXISTS idx_sector_runs_layer_run_id ON sector_runs (layer_run_id);

CREATE INDEX IF NOT EXISTS idx_sector_runs_sector ON sector_runs (sector);

CREATE INDEX IF NOT EXISTS idx_sector_runs_status ON sector_runs (status);

CREATE INDEX IF NOT EXISTS idx_refinements_problem_id ON refinements (problem_id);

CREATE INDEX IF NOT EXISTS idx_refinements_from_layer ON refinements (from_layer);

CREATE INDEX IF NOT EXISTS idx_refinements_to_layer ON refinements (to_layer);

CREATE INDEX IF NOT EXISTS idx_answers_problem_id ON answers (problem_id);

CREATE INDEX IF NOT EXISTS idx_answers_layer ON answers (layer);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys (key_hash);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys (user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs (action);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_problems_updated_at BEFORE UPDATE ON problems FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_layer_runs_updated_at BEFORE UPDATE ON layer_runs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sector_runs_updated_at BEFORE UPDATE ON sector_runs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_refinements_updated_at BEFORE UPDATE ON refinements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_answers_updated_at BEFORE UPDATE ON answers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a default admin user (password: AdminPassword123!)
INSERT INTO
    users (
        username,
        email,
        hashed_password,
        role
    )
VALUES (
        'admin',
        'admin@cosmiccouncil.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K.8K.8K',
        'admin'
    ) ON CONFLICT (username) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cosmic_council;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cosmic_council;

GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO cosmic_council;

-- Create a view for problem genealogy
CREATE OR REPLACE VIEW problem_genealogy AS
SELECT
    p.id as problem_id,
    p.title,
    p.description,
    p.status,
    p.created_at,
    json_agg (
        json_build_object (
            'id',
            lr.id,
            'layer',
            lr.layer,
            'iteration',
            lr.iteration,
            'status',
            lr.status,
            'started_at',
            lr.started_at,
            'finished_at',
            lr.finished_at,
            'total_cost_usd',
            lr.total_cost_usd,
            'total_latency_ms',
            lr.total_latency_ms
        )
        ORDER BY lr.iteration
    ) as layer_runs,
    json_agg (
        json_build_object (
            'id',
            r.id,
            'from_layer',
            r.from_layer,
            'to_layer',
            r.to_layer,
            'rationale',
            r.rationale,
            'refined_question',
            r.refined_question,
            'created_at',
            r.created_at
        )
        ORDER BY r.created_at
    ) as refinements,
    json_agg (
        json_build_object (
            'id',
            a.id,
            'layer',
            a.layer,
            'solution_json',
            a.solution_json,
            'confidence_score',
            a.confidence_score,
            'completeness_score',
            a.completeness_score,
            'novelty_score',
            a.novelty_score,
            'alignment_score',
            a.alignment_score,
            'net_benefit_score',
            a.net_benefit_score,
            'created_at',
            a.created_at
        )
        ORDER BY a.created_at
    ) as answers
FROM
    problems p
    LEFT JOIN layer_runs lr ON p.id = lr.problem_id
    LEFT JOIN refinements r ON p.id = r.problem_id
    LEFT JOIN answers a ON p.id = a.problem_id
GROUP BY
    p.id,
    p.title,
    p.description,
    p.status,
    p.created_at;

-- Create a view for system metrics
CREATE OR REPLACE VIEW system_metrics AS
SELECT
    'problems' as metric_type,
    COUNT(*) as count,
    COUNT(*) FILTER (
        WHERE
            status = 'open'
    ) as open_count,
    COUNT(*) FILTER (
        WHERE
            status = 'processing'
    ) as processing_count,
    COUNT(*) FILTER (
        WHERE
            status = 'resolved'
    ) as resolved_count,
    COUNT(*) FILTER (
        WHERE
            status = 'failed'
    ) as failed_count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (updated_at - created_at)
        )
    ) as avg_processing_time_seconds
FROM problems
UNION ALL
SELECT
    'layer_runs' as metric_type,
    COUNT(*) as count,
    COUNT(*) FILTER (
        WHERE
            status = 'pending'
    ) as open_count,
    COUNT(*) FILTER (
        WHERE
            status = 'running'
    ) as processing_count,
    COUNT(*) FILTER (
        WHERE
            status = 'completed'
    ) as resolved_count,
    COUNT(*) FILTER (
        WHERE
            status = 'failed'
    ) as failed_count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (finished_at - started_at)
        )
    ) as avg_processing_time_seconds
FROM layer_runs
UNION ALL
SELECT
    'sector_runs' as metric_type,
    COUNT(*) as count,
    COUNT(*) FILTER (
        WHERE
            status = 'pending'
    ) as open_count,
    COUNT(*) FILTER (
        WHERE
            status = 'running'
    ) as processing_count,
    COUNT(*) FILTER (
        WHERE
            status = 'completed'
    ) as resolved_count,
    COUNT(*) FILTER (
        WHERE
            status = 'failed'
    ) as failed_count,
    AVG(
        EXTRACT(
            EPOCH
            FROM (finished_at - started_at)
        )
    ) as avg_processing_time_seconds
FROM sector_runs;

-- Create a function to get problem statistics
CREATE OR REPLACE FUNCTION get_problem_statistics(problem_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'problem_id', p.id,
        'title', p.title,
        'status', p.status,
        'created_at', p.created_at,
        'updated_at', p.updated_at,
        'total_layer_runs', COUNT(lr.id),
        'total_sector_runs', COUNT(sr.id),
        'total_refinements', COUNT(r.id),
        'total_answers', COUNT(a.id),
        'total_cost_usd', COALESCE(SUM(lr.total_cost_usd), 0),
        'total_latency_ms', COALESCE(SUM(lr.total_latency_ms), 0),
        'current_layer', (
            SELECT lr.layer 
            FROM layer_runs lr 
            WHERE lr.problem_id = p.id 
            ORDER BY lr.iteration DESC 
            LIMIT 1
        ),
        'latest_answer', (
            SELECT json_build_object(
                'confidence_score', a.confidence_score,
                'completeness_score', a.completeness_score,
                'novelty_score', a.novelty_score,
                'alignment_score', a.alignment_score,
                'net_benefit_score', a.net_benefit_score
            )
            FROM answers a 
            WHERE a.problem_id = p.id 
            ORDER BY a.created_at DESC 
            LIMIT 1
        )
    ) INTO result
    FROM problems p
    LEFT JOIN layer_runs lr ON p.id = lr.problem_id
    LEFT JOIN sector_runs sr ON lr.id = sr.layer_run_id
    LEFT JOIN refinements r ON p.id = r.problem_id
    LEFT JOIN answers a ON p.id = a.problem_id
    WHERE p.id = problem_uuid
    GROUP BY p.id, p.title, p.status, p.created_at, p.updated_at;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create a function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete old audit logs
    DELETE FROM audit_logs WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Delete old completed problems (optional - uncomment if needed)
    -- DELETE FROM problems WHERE status = 'resolved' AND updated_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to clean up old data (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data(30);');

-- Final message
DO $$
BEGIN
    RAISE NOTICE 'Cosmic Council Refinement Engine database initialized successfully!';
    RAISE NOTICE 'Default admin user created: admin / AdminPassword123!';
    RAISE NOTICE 'Database schema created with all required tables, indexes, and functions.';
END $$;