-- Migration: 003_create_solution_tables.sql
-- Create solution-related tables

-- Create solutions table
CREATE TABLE IF NOT EXISTS solutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES problems(id),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    approach TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    confidence_score FLOAT DEFAULT 0.0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for solutions
CREATE INDEX IF NOT EXISTS idx_solutions_problem_id ON solutions (problem_id);

CREATE INDEX IF NOT EXISTS idx_solutions_title ON solutions (title);

CREATE INDEX IF NOT EXISTS idx_solutions_status ON solutions (status);

CREATE INDEX IF NOT EXISTS idx_solutions_confidence_score ON solutions (confidence_score);

CREATE INDEX IF NOT EXISTS idx_solutions_created_by ON solutions (created_by);

-- Create solution components table
CREATE TABLE IF NOT EXISTS solution_components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solution_id UUID NOT NULL REFERENCES solutions(id),
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    component_type VARCHAR(100) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    estimated_effort FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for solution components
CREATE INDEX IF NOT EXISTS idx_solution_components_solution_id ON solution_components (solution_id);

CREATE INDEX IF NOT EXISTS idx_solution_components_name ON solution_components (name);

CREATE INDEX IF NOT EXISTS idx_solution_components_type ON solution_components (component_type);

CREATE INDEX IF NOT EXISTS idx_solution_components_priority ON solution_components (priority);

CREATE INDEX IF NOT EXISTS idx_solution_components_estimated_effort ON solution_components (estimated_effort);

-- Create solution component relationships table
CREATE TABLE IF NOT EXISTS solution_component_relationships (
    solution_id UUID NOT NULL REFERENCES solutions (id),
    component_id UUID NOT NULL REFERENCES solution_components (id),
    relationship_type VARCHAR(50),
    PRIMARY KEY (solution_id, component_id)
);

-- Create implementation tracking table
CREATE TABLE IF NOT EXISTS implementation_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solution_id UUID NOT NULL REFERENCES solutions(id),
    component_id UUID REFERENCES solution_components(id),
    status VARCHAR(20) NOT NULL,
    progress_percentage VARCHAR(10) DEFAULT '0',
    notes TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for implementation tracking
CREATE INDEX IF NOT EXISTS idx_implementation_tracking_solution_id ON implementation_tracking (solution_id);

CREATE INDEX IF NOT EXISTS idx_implementation_tracking_component_id ON implementation_tracking (component_id);

CREATE INDEX IF NOT EXISTS idx_implementation_tracking_status ON implementation_tracking (status);

-- Create triggers for updated_at
CREATE TRIGGER update_solutions_updated_at 
    BEFORE UPDATE ON solutions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solution_components_updated_at 
    BEFORE UPDATE ON solution_components 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_implementation_tracking_updated_at 
    BEFORE UPDATE ON implementation_tracking 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();