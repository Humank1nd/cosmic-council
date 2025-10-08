-- Migration: 002_create_problem_tables.sql
-- Create problem-related tables

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    permissions TEXT,
    preferences TEXT,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active VARCHAR(10) DEFAULT 'true',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);

CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active);

-- Create stakeholders table
CREATE TABLE IF NOT EXISTS stakeholders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(100),
    organization VARCHAR(255),
    influence_level VARCHAR(20) DEFAULT 'medium',
    interest_level VARCHAR(20) DEFAULT 'medium',
    contact_info TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create constraints table
CREATE TABLE IF NOT EXISTS constraints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    constraint_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create success criteria table
CREATE TABLE IF NOT EXISTS success_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    measurement_type VARCHAR(50) NOT NULL,
    target_value VARCHAR(255),
    measurement_method TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create problems table
CREATE TABLE IF NOT EXISTS problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    domain VARCHAR(200) NOT NULL,
    complexity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    priority VARCHAR(20) DEFAULT 'medium',
    created_by UUID REFERENCES users(id),
    due_date VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for problems
CREATE INDEX IF NOT EXISTS idx_problems_title ON problems (title);

CREATE INDEX IF NOT EXISTS idx_problems_domain ON problems (domain);

CREATE INDEX IF NOT EXISTS idx_problems_complexity ON problems (complexity);

CREATE INDEX IF NOT EXISTS idx_problems_status ON problems (status);

CREATE INDEX IF NOT EXISTS idx_problems_priority ON problems (priority);

CREATE INDEX IF NOT EXISTS idx_problems_created_by ON problems (created_by);

-- Create problem statements table
CREATE TABLE IF NOT EXISTS problem_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES problems(id),
    statement TEXT NOT NULL,
    context TEXT,
    assumptions TEXT,
    questions TEXT,
    analysis_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create association tables for many-to-many relationships
CREATE TABLE IF NOT EXISTS problem_stakeholders (
    problem_id UUID NOT NULL REFERENCES problems (id),
    stakeholder_id UUID NOT NULL REFERENCES stakeholders (id),
    role VARCHAR(100),
    influence_level VARCHAR(20),
    PRIMARY KEY (problem_id, stakeholder_id)
);

CREATE TABLE IF NOT EXISTS problem_constraints (
    problem_id UUID NOT NULL REFERENCES problems (id),
    constraint_id UUID NOT NULL REFERENCES constraints (id),
    constraint_value TEXT,
    PRIMARY KEY (problem_id, constraint_id)
);

CREATE TABLE IF NOT EXISTS problem_success_criteria (
    problem_id UUID NOT NULL REFERENCES problems (id),
    criterion_id UUID NOT NULL REFERENCES success_criteria (id),
    target_value VARCHAR(255),
    measurement_method TEXT,
    PRIMARY KEY (problem_id, criterion_id)
);

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stakeholders_updated_at 
    BEFORE UPDATE ON stakeholders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_constraints_updated_at 
    BEFORE UPDATE ON constraints 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_success_criteria_updated_at 
    BEFORE UPDATE ON success_criteria 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_problems_updated_at 
    BEFORE UPDATE ON problems 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_problem_statements_updated_at 
    BEFORE UPDATE ON problem_statements 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();