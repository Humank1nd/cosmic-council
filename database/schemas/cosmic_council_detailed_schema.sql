-- Cosmic Council Detailed Database Schema
-- Comprehensive PostgreSQL implementation of the Airtable-style database structure
-- Implements all sub-tables and automation mechanisms for each ROYGBV stage

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- RESEARCH DATABASE (Red Owl - Research & Inquiry)
-- ============================================================================

-- Core Problem Table - Captures the main problem statement and context
CREATE TABLE research_core_problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_reference_id VARCHAR(50) UNIQUE NOT NULL, -- Formula-generated reference
    main_problem_statement TEXT NOT NULL,
    context TEXT,
    initial_observations TEXT,
    date_identified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_by VARCHAR(100),
    associated_themes TEXT[],
    severity_priority_rating VARCHAR(20) CHECK (severity_priority_rating IN ('low', 'medium', 'high', 'critical')),
    problem_status VARCHAR(20) DEFAULT 'active' CHECK (problem_status IN ('active', 'in_review', 'resolved', 'archived')),

-- Metadata
created_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),

-- Indexes
CONSTRAINT idx_research_core_problems_reference UNIQUE (problem_reference_id),
    CONSTRAINT idx_research_core_problems_status CHECK (problem_status IN ('active', 'in_review', 'resolved', 'archived'))
);

-- Research Findings Table - Repository for detailed research entries
CREATE TABLE research_findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    core_problem_id UUID NOT NULL REFERENCES research_core_problems(id) ON DELETE CASCADE,

-- Finding details
source VARCHAR(500),
    author VARCHAR(200),
    date_of_publication DATE,
    summary TEXT NOT NULL,
    relevance_to_problem TEXT,
    keywords_tags TEXT[],
    date_added TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

-- Ratings
credibility_rating INTEGER CHECK (
    credibility_rating >= 1
    AND credibility_rating <= 5
),
relevance_rating INTEGER CHECK (
    relevance_rating >= 1
    AND relevance_rating <= 5
),
impact_rating INTEGER CHECK (
    impact_rating >= 1
    AND impact_rating <= 5
),

-- Additional data
notes TEXT,
attachments JSONB, -- Store file references and metadata

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prioritized Questions Table - Critical questions for Planning stage
CREATE TABLE research_prioritized_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    core_problem_id UUID NOT NULL REFERENCES research_core_problems(id) ON DELETE CASCADE,

-- Question details
question_text TEXT NOT NULL,
    supporting_research_links UUID[] DEFAULT '{}', -- Array of research_findings IDs
    importance_rating INTEGER CHECK (importance_rating >= 1 AND importance_rating <= 5),
    relevance_to_core_problem TEXT,
    date_added TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    category_theme VARCHAR(100),

-- Status tracking
status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending',
        'in_planning',
        'addressed',
        'archived'
    )
),

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PLANNING DATABASE (Orange Orangutan - Planning & Logistics)
-- ============================================================================

-- Related Questions Table - Pulls prioritized questions from Research
CREATE TABLE planning_related_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    research_question_id UUID NOT NULL REFERENCES research_prioritized_questions(id) ON DELETE CASCADE,

-- Question details (copied from research)
question_text TEXT NOT NULL,
importance_rating INTEGER,
category_theme VARCHAR(100),

-- Planning status
planning_status VARCHAR(20) DEFAULT 'pending' CHECK (
    planning_status IN (
        'pending',
        'in_planning',
        'planned',
        'implemented'
    )
),
assigned_to VARCHAR(100),

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Action Plan Table - High-level objectives and detailed steps
CREATE TABLE planning_action_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    related_question_id UUID NOT NULL REFERENCES planning_related_questions(id) ON DELETE CASCADE,

-- Plan details
high_level_objective TEXT NOT NULL,
detailed_steps JSONB NOT NULL, -- Array of step objects
timeline_estimate INTEGER, -- Days
priority_level VARCHAR(20) CHECK (
    priority_level IN (
        'low',
        'medium',
        'high',
        'critical'
    )
),

-- Status tracking
plan_status VARCHAR(20) DEFAULT 'draft' CHECK (
    plan_status IN (
        'draft',
        'review',
        'approved',
        'in_progress',
        'completed'
    )
),
completion_percentage DECIMAL(5, 2) DEFAULT 0.0,

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dependencies Identified Table - Critical resources and knowledge areas
CREATE TABLE planning_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_plan_id UUID NOT NULL REFERENCES planning_action_plans(id) ON DELETE CASCADE,

-- Dependency details
dependency_type VARCHAR(50) CHECK (
    dependency_type IN (
        'resource',
        'knowledge',
        'personnel',
        'external',
        'technical'
    )
),
dependency_description TEXT NOT NULL,
criticality_level VARCHAR(20) CHECK (
    criticality_level IN (
        'low',
        'medium',
        'high',
        'critical'
    )
),
estimated_cost DECIMAL(12, 2),
estimated_time_days INTEGER,

-- Status tracking
dependency_status VARCHAR(20) DEFAULT 'identified' CHECK (
    dependency_status IN (
        'identified',
        'acquired',
        'in_progress',
        'completed',
        'blocked'
    )
),

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- DEVELOPMENT DATABASE (Yellow Honeybee - Development & Creativity)
-- ============================================================================

-- Prototype Table - Designs and initial concepts
CREATE TABLE development_prototypes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_plan_id UUID NOT NULL REFERENCES planning_action_plans(id) ON DELETE CASCADE,

-- Prototype details
prototype_name VARCHAR(200) NOT NULL,
    prototype_description TEXT NOT NULL,
    design_specifications JSONB,
    technical_requirements TEXT[],
    creative_concepts TEXT[],

-- Status tracking
prototype_status VARCHAR(20) DEFAULT 'concept' CHECK (
    prototype_status IN (
        'concept',
        'design',
        'development',
        'testing',
        'completed',
        'archived'
    )
),
development_stage VARCHAR(50),

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Internal Testing Table - Evaluates prototypes against criteria
CREATE TABLE development_internal_testing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prototype_id UUID NOT NULL REFERENCES development_prototypes(id) ON DELETE CASCADE,

-- Testing details
test_name VARCHAR(200) NOT NULL,
test_type VARCHAR(50) CHECK (
    test_type IN (
        'functional',
        'performance',
        'usability',
        'security',
        'compatibility'
    )
),
test_criteria JSONB NOT NULL,
test_results JSONB,
pass_fail_status VARCHAR(10) CHECK (
    pass_fail_status IN ('pass', 'fail', 'partial')
),

-- Performance metrics
performance_score DECIMAL(5, 2),
efficiency_rating INTEGER CHECK (
    efficiency_rating >= 1
    AND efficiency_rating <= 5
),

-- Metadata
test_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tested_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Creative Notes Table - Brainstorming and refinement ideas
CREATE TABLE development_creative_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prototype_id UUID REFERENCES development_prototypes(id) ON DELETE CASCADE,
    testing_id UUID REFERENCES development_internal_testing(id) ON DELETE CASCADE,

-- Note details
note_type VARCHAR(50) CHECK (
    note_type IN (
        'brainstorm',
        'refinement',
        'innovation',
        'improvement',
        'observation'
    )
),
note_content TEXT NOT NULL,
inspiration_source VARCHAR(200),
feasibility_rating INTEGER CHECK (
    feasibility_rating >= 1
    AND feasibility_rating <= 5
),

-- Status
implementation_status VARCHAR(20) DEFAULT 'idea' CHECK (
    implementation_status IN (
        'idea',
        'evaluating',
        'implementing',
        'implemented',
        'rejected'
    )
),

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- ============================================================================
-- BUDGET DATABASE (Green Tortoise - Budget & Resources)
-- ============================================================================

-- Resource Inventory Table - Tracks available resources
CREATE TABLE budget_resource_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

-- Resource details
resource_name VARCHAR(200) NOT NULL,
resource_type VARCHAR(50) CHECK (
    resource_type IN (
        'personnel',
        'material',
        'equipment',
        'software',
        'external_service',
        'facility'
    )
),
resource_description TEXT,
current_availability VARCHAR(20) CHECK (
    current_availability IN (
        'available',
        'limited',
        'unavailable',
        'depleted'
    )
),
quantity_available INTEGER,
unit_cost DECIMAL(12, 2),

-- Metadata
last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Budget Allocation Table - Allocates funding for projects
CREATE TABLE budget_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prototype_id UUID NOT NULL REFERENCES development_prototypes(id) ON DELETE CASCADE,

-- Allocation details
allocation_name VARCHAR(200) NOT NULL,
allocated_amount DECIMAL(12, 2) NOT NULL,
allocation_category VARCHAR(50) CHECK (
    allocation_category IN (
        'development',
        'testing',
        'materials',
        'personnel',
        'external',
        'contingency'
    )
),
approved_by VARCHAR(100),
approval_date TIMESTAMP
WITH
    TIME ZONE,

-- Status tracking
allocation_status VARCHAR(20) DEFAULT 'pending' CHECK (
    allocation_status IN (
        'pending',
        'approved',
        'active',
        'completed',
        'cancelled'
    )
),
spent_amount DECIMAL(12, 2) DEFAULT 0.0,

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Time and Cost Analysis Table - Cost-effectiveness assessment
CREATE TABLE budget_time_cost_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_allocation_id UUID NOT NULL REFERENCES budget_allocations(id) ON DELETE CASCADE,

-- Analysis details
analysis_type VARCHAR(50) CHECK (
    analysis_type IN (
        'initial_estimate',
        'revised_estimate',
        'actual_cost',
        'variance_analysis'
    )
),
estimated_cost DECIMAL(12, 2),
actual_cost DECIMAL(12, 2),
estimated_time_days INTEGER,
actual_time_days INTEGER,
cost_effectiveness_rating INTEGER CHECK (
    cost_effectiveness_rating >= 1
    AND cost_effectiveness_rating <= 5
),

-- Analysis results
variance_analysis TEXT, recommendations TEXT,

-- Metadata
analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analyzed_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MARKET DATABASE (Blue Dolphin - Market & Communication)
-- ============================================================================

-- Market Insights Table - Trends, consumer behavior, competitor analysis
CREATE TABLE market_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prototype_id UUID NOT NULL REFERENCES development_prototypes(id) ON DELETE CASCADE,

-- Insight details
insight_type VARCHAR(50) CHECK (
    insight_type IN (
        'trend',
        'consumer_behavior',
        'competitor',
        'market_size',
        'opportunity',
        'threat'
    )
),
insight_title VARCHAR(200) NOT NULL,
insight_description TEXT NOT NULL,
data_source VARCHAR(200),
confidence_level INTEGER CHECK (
    confidence_level >= 1
    AND confidence_level <= 5
),

-- Market data
target_audience JSONB,
market_size_estimate DECIMAL(15, 2),
growth_potential VARCHAR(20) CHECK (
    growth_potential IN (
        'low',
        'medium',
        'high',
        'exponential'
    )
),

-- Metadata
insight_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Communication Strategy Table - Engagement plans based on market insights
CREATE TABLE market_communication_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    market_insight_id UUID NOT NULL REFERENCES market_insights(id) ON DELETE CASCADE,

-- Strategy details
strategy_name VARCHAR(200) NOT NULL,
    target_audience JSONB NOT NULL,
    communication_channels TEXT[],
    key_messages TEXT[],
    engagement_approach TEXT,

-- Implementation details
implementation_timeline INTEGER, -- Days
estimated_reach INTEGER,
budget_required DECIMAL(12, 2),

-- Status tracking
strategy_status VARCHAR(20) DEFAULT 'draft' CHECK (
    strategy_status IN (
        'draft',
        'approved',
        'active',
        'completed',
        'paused'
    )
),

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Metrics Table - Measures communication effectiveness
CREATE TABLE market_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    communication_strategy_id UUID NOT NULL REFERENCES market_communication_strategies(id) ON DELETE CASCADE,

-- Metric details
metric_name VARCHAR(200) NOT NULL,
metric_type VARCHAR(50) CHECK (
    metric_type IN (
        'reach',
        'engagement',
        'conversion',
        'satisfaction',
        'awareness'
    )
),
metric_value DECIMAL(15, 2),
metric_unit VARCHAR(50),
target_value DECIMAL(15, 2),

-- Performance data
measurement_date TIMESTAMP
WITH
    TIME ZONE DEFAULT NOW(),
    performance_rating INTEGER CHECK (
        performance_rating >= 1
        AND performance_rating <= 5
    ),
    notes TEXT,

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() );

-- ============================================================================
-- SUPPORT DATABASE (Violet Elephant - Support & Feedback)
-- ============================================================================

-- User Feedback Table - Input from users and stakeholders
CREATE TABLE support_user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    communication_strategy_id UUID REFERENCES market_communication_strategies(id) ON DELETE CASCADE,

-- Feedback details
feedback_type VARCHAR(50) CHECK (
    feedback_type IN (
        'user_experience',
        'feature_request',
        'bug_report',
        'satisfaction',
        'suggestion'
    )
),
feedback_content TEXT NOT NULL,
user_type VARCHAR(50) CHECK (
    user_type IN (
        'end_user',
        'stakeholder',
        'internal_team',
        'external_partner'
    )
),
user_identifier VARCHAR(200), -- Anonymous or identified user

-- Feedback ratings
satisfaction_rating INTEGER CHECK (
    satisfaction_rating >= 1
    AND satisfaction_rating <= 5
),
priority_level VARCHAR(20) CHECK (
    priority_level IN (
        'low',
        'medium',
        'high',
        'critical'
    )
),

-- Status tracking
feedback_status VARCHAR(20) DEFAULT 'received' CHECK (
    feedback_status IN (
        'received',
        'acknowledged',
        'in_review',
        'addressed',
        'resolved',
        'closed'
    )
),

-- Metadata
feedback_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Assessment Table - Reviews feedback against objectives
CREATE TABLE support_performance_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_feedback_id UUID REFERENCES support_user_feedback(id) ON DELETE CASCADE,

-- Assessment details
assessment_type VARCHAR(50) CHECK (
    assessment_type IN (
        'objective_review',
        'performance_analysis',
        'gap_analysis',
        'improvement_opportunity'
    )
),
assessment_criteria JSONB NOT NULL,
assessment_results JSONB,
performance_score DECIMAL(5, 2),

-- Analysis
strengths_identified TEXT[],
    areas_for_improvement TEXT[],
    recommendations TEXT,

-- Status
assessment_status VARCHAR(20) DEFAULT 'in_progress' CHECK (
    assessment_status IN (
        'in_progress',
        'completed',
        'reviewed',
        'approved'
    )
),

-- Metadata
assessment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assessed_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Continuous Improvement Table - Actionable recommendations for future cycles
CREATE TABLE support_continuous_improvements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    performance_assessment_id UUID REFERENCES support_performance_assessments(id) ON DELETE CASCADE,

-- Improvement details
improvement_title VARCHAR(200) NOT NULL,
improvement_description TEXT NOT NULL,
improvement_category VARCHAR(50) CHECK (
    improvement_category IN (
        'process',
        'product',
        'communication',
        'resource',
        'strategy'
    )
),
priority_level VARCHAR(20) CHECK (
    priority_level IN (
        'low',
        'medium',
        'high',
        'critical'
    )
),

-- Implementation details
estimated_effort VARCHAR(50) CHECK (
    estimated_effort IN (
        'low',
        'medium',
        'high',
        'very_high'
    )
),
estimated_impact VARCHAR(50) CHECK (
    estimated_impact IN (
        'low',
        'medium',
        'high',
        'transformational'
    )
),
implementation_timeline INTEGER, -- Days

-- Status tracking
improvement_status VARCHAR(20) DEFAULT 'identified' CHECK (
    improvement_status IN (
        'identified',
        'planned',
        'in_progress',
        'implemented',
        'validated',
        'archived'
    )
),

-- Next cycle linkage
next_cycle_focus BOOLEAN DEFAULT FALSE,
research_priority BOOLEAN DEFAULT FALSE,

-- Metadata
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- AUTOMATION TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers to all tables with updated_at columns
CREATE TRIGGER update_research_core_problems_updated_at BEFORE UPDATE ON research_core_problems FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_research_findings_updated_at BEFORE UPDATE ON research_findings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_research_prioritized_questions_updated_at BEFORE UPDATE ON research_prioritized_questions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_planning_related_questions_updated_at BEFORE UPDATE ON planning_related_questions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_planning_action_plans_updated_at BEFORE UPDATE ON planning_action_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_planning_dependencies_updated_at BEFORE UPDATE ON planning_dependencies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_development_prototypes_updated_at BEFORE UPDATE ON development_prototypes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_allocations_updated_at BEFORE UPDATE ON budget_allocations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_communication_strategies_updated_at BEFORE UPDATE ON market_communication_strategies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_continuous_improvements_updated_at BEFORE UPDATE ON support_continuous_improvements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate problem reference ID
CREATE OR REPLACE FUNCTION generate_problem_reference_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.problem_reference_id IS NULL OR NEW.problem_reference_id = '' THEN
        NEW.problem_reference_id := 'PROB-' || TO_CHAR(NOW(), 'YYYY') || '-' || LPAD(EXTRACT(DOY FROM NOW())::TEXT, 3, '0') || '-' || LPAD(NEXTVAL('problem_sequence')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create sequence for problem reference IDs
CREATE SEQUENCE IF NOT EXISTS problem_sequence START 1;

-- Apply problem reference ID trigger
CREATE TRIGGER generate_problem_reference_id_trigger BEFORE INSERT ON research_core_problems FOR EACH ROW EXECUTE FUNCTION generate_problem_reference_id();

-- Function to automatically create prioritized questions for high-relevance research findings
CREATE OR REPLACE FUNCTION create_prioritized_questions_for_high_relevance_findings()
RETURNS TRIGGER AS $$
BEGIN
    -- If research finding has high relevance rating (4 or 5), create a prioritized question
    IF NEW.relevance_rating >= 4 THEN
        INSERT INTO research_prioritized_questions (
            core_problem_id,
            question_text,
            supporting_research_links,
            importance_rating,
            relevance_to_core_problem,
            category_theme
        ) VALUES (
            NEW.core_problem_id,
            'Key question derived from: ' || COALESCE(NEW.summary, 'Research finding'),
            ARRAY[NEW.id],
            NEW.relevance_rating,
            NEW.relevance_to_problem,
            'Auto-generated from research'
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger for automatic prioritized question creation
CREATE TRIGGER create_prioritized_questions_trigger AFTER INSERT ON research_findings FOR EACH ROW EXECUTE FUNCTION create_prioritized_questions_for_high_relevance_findings();

-- Function to sync prioritized questions to planning stage
CREATE OR REPLACE FUNCTION sync_questions_to_planning()
RETURNS TRIGGER AS $$
BEGIN
    -- When a prioritized question is created, also create a related question in planning
    INSERT INTO planning_related_questions (
        research_question_id,
        question_text,
        importance_rating,
        category_theme
    ) VALUES (
        NEW.id,
        NEW.question_text,
        NEW.importance_rating,
        NEW.category_theme
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger for syncing questions to planning
CREATE TRIGGER sync_questions_to_planning_trigger AFTER INSERT ON research_prioritized_questions FOR EACH ROW EXECUTE FUNCTION sync_questions_to_planning();

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Research Database indexes
CREATE INDEX idx_research_core_problems_status ON research_core_problems (problem_status);

CREATE INDEX idx_research_core_problems_severity ON research_core_problems (severity_priority_rating);

CREATE INDEX idx_research_findings_core_problem_id ON research_findings (core_problem_id);

CREATE INDEX idx_research_findings_relevance_rating ON research_findings (relevance_rating);

CREATE INDEX idx_research_prioritized_questions_core_problem_id ON research_prioritized_questions (core_problem_id);

CREATE INDEX idx_research_prioritized_questions_importance ON research_prioritized_questions (importance_rating);

-- Planning Database indexes
CREATE INDEX idx_planning_related_questions_research_id ON planning_related_questions (research_question_id);

CREATE INDEX idx_planning_action_plans_question_id ON planning_action_plans (related_question_id);

CREATE INDEX idx_planning_dependencies_action_plan_id ON planning_dependencies (action_plan_id);

-- Development Database indexes
CREATE INDEX idx_development_prototypes_action_plan_id ON development_prototypes (action_plan_id);

CREATE INDEX idx_development_internal_testing_prototype_id ON development_internal_testing (prototype_id);

CREATE INDEX idx_development_creative_notes_prototype_id ON development_creative_notes (prototype_id);

-- Budget Database indexes
CREATE INDEX idx_budget_allocations_prototype_id ON budget_allocations (prototype_id);

CREATE INDEX idx_budget_time_cost_analysis_allocation_id ON budget_time_cost_analysis (budget_allocation_id);

-- Market Database indexes
CREATE INDEX idx_market_insights_prototype_id ON market_insights (prototype_id);

CREATE INDEX idx_market_communication_strategies_insight_id ON market_communication_strategies (market_insight_id);

CREATE INDEX idx_market_performance_metrics_strategy_id ON market_performance_metrics (communication_strategy_id);

-- Support Database indexes
CREATE INDEX idx_support_user_feedback_strategy_id ON support_user_feedback (communication_strategy_id);

CREATE INDEX idx_support_performance_assessments_feedback_id ON support_performance_assessments (user_feedback_id);

CREATE INDEX idx_support_continuous_improvements_assessment_id ON support_continuous_improvements (performance_assessment_id);

CREATE INDEX idx_support_continuous_improvements_next_cycle ON support_continuous_improvements (next_cycle_focus);

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to get complete workflow status for a problem
CREATE OR REPLACE FUNCTION get_complete_workflow_status(p_problem_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'problem', jsonb_build_object(
            'id', rcp.id,
            'reference_id', rcp.problem_reference_id,
            'statement', rcp.main_problem_statement,
            'status', rcp.problem_status,
            'severity', rcp.severity_priority_rating
        ),
        'research', jsonb_build_object(
            'findings_count', (SELECT COUNT(*) FROM research_findings WHERE core_problem_id = p_problem_id),
            'questions_count', (SELECT COUNT(*) FROM research_prioritized_questions WHERE core_problem_id = p_problem_id),
            'high_priority_questions', (SELECT COUNT(*) FROM research_prioritized_questions WHERE core_problem_id = p_problem_id AND importance_rating >= 4)
        ),
        'planning', jsonb_build_object(
            'related_questions_count', (SELECT COUNT(*) FROM planning_related_questions prq JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id WHERE rpq.core_problem_id = p_problem_id),
            'action_plans_count', (SELECT COUNT(*) FROM planning_action_plans pap JOIN planning_related_questions prq ON pap.related_question_id = prq.id JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id WHERE rpq.core_problem_id = p_problem_id)
        ),
        'development', jsonb_build_object(
            'prototypes_count', (SELECT COUNT(*) FROM development_prototypes dp JOIN planning_action_plans pap ON dp.action_plan_id = pap.id JOIN planning_related_questions prq ON pap.related_question_id = prq.id JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id WHERE rpq.core_problem_id = p_problem_id)
        ),
        'budget', jsonb_build_object(
            'allocations_count', (SELECT COUNT(*) FROM budget_allocations ba JOIN development_prototypes dp ON ba.prototype_id = dp.id JOIN planning_action_plans pap ON dp.action_plan_id = pap.id JOIN planning_related_questions prq ON pap.related_question_id = prq.id JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id WHERE rpq.core_problem_id = p_problem_id)
        ),
        'market', jsonb_build_object(
            'insights_count', (SELECT COUNT(*) FROM market_insights mi JOIN development_prototypes dp ON mi.prototype_id = dp.id JOIN planning_action_plans pap ON dp.action_plan_id = pap.id JOIN planning_related_questions prq ON pap.related_question_id = prq.id JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id WHERE rpq.core_problem_id = p_problem_id)
        ),
        'support', jsonb_build_object(
            'feedback_count', (SELECT COUNT(*) FROM support_user_feedback suf JOIN market_communication_strategies mcs ON suf.communication_strategy_id = mcs.id JOIN market_insights mi ON mcs.market_insight_id = mi.id JOIN development_prototypes dp ON mi.prototype_id = dp.id JOIN planning_action_plans pap ON dp.action_plan_id = pap.id JOIN planning_related_questions prq ON pap.related_question_id = prq.id JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id WHERE rpq.core_problem_id = p_problem_id),
            'improvements_count', (SELECT COUNT(*) FROM support_continuous_improvements sci WHERE sci.next_cycle_focus = TRUE)
        )
    ) INTO result
    FROM research_core_problems rcp
    WHERE rcp.id = p_problem_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to get next cycle recommendations
CREATE OR REPLACE FUNCTION get_next_cycle_recommendations()
RETURNS TABLE (
    improvement_id UUID,
    improvement_title VARCHAR(200),
    improvement_description TEXT,
    priority_level VARCHAR(20),
    estimated_impact VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sci.id,
        sci.improvement_title,
        sci.improvement_description,
        sci.priority_level,
        sci.estimated_impact
    FROM support_continuous_improvements sci
    WHERE sci.next_cycle_focus = TRUE
    ORDER BY 
        CASE sci.priority_level 
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        CASE sci.estimated_impact
            WHEN 'transformational' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END;
END;
$$ LANGUAGE plpgsql;

-- Function to automatically create new problem from continuous improvements
CREATE OR REPLACE FUNCTION create_new_problem_from_improvements()
RETURNS TRIGGER AS $$
BEGIN
    -- When a continuous improvement is marked for next cycle focus, create a new problem
    IF NEW.next_cycle_focus = TRUE AND (OLD.next_cycle_focus IS NULL OR OLD.next_cycle_focus = FALSE) THEN
        INSERT INTO research_core_problems (
            main_problem_statement,
            context,
            initial_observations,
            submitted_by,
            associated_themes,
            severity_priority_rating,
            problem_status
        ) VALUES (
            NEW.improvement_title,
            'Generated from continuous improvement feedback loop',
            NEW.improvement_description,
            'Purple Elephant Feedback System',
            ARRAY[NEW.improvement_category],
            NEW.priority_level,
            'active'
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger for automatic problem creation from improvements
CREATE TRIGGER create_new_problem_from_improvements_trigger 
    AFTER UPDATE ON support_continuous_improvements 
    FOR EACH ROW 
    EXECUTE FUNCTION create_new_problem_from_improvements();

-- Function to cascade data between stages (Research -> Planning -> Development -> Budget -> Market -> Support)
CREATE OR REPLACE FUNCTION cascade_stage_data()
RETURNS TRIGGER AS $$
BEGIN
    -- This function will be called by N8N workflows to handle data cascading
    -- between stages in the ROYGBV sequence
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to get stage completion status for workflow orchestration
CREATE OR REPLACE FUNCTION get_stage_completion_status(p_problem_id UUID, p_stage VARCHAR)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    CASE p_stage
        WHEN 'research' THEN
            SELECT jsonb_build_object(
                'stage', 'research',
                'completed', (SELECT COUNT(*) > 0 FROM research_prioritized_questions WHERE core_problem_id = p_problem_id),
                'findings_count', (SELECT COUNT(*) FROM research_findings WHERE core_problem_id = p_problem_id),
                'questions_count', (SELECT COUNT(*) FROM research_prioritized_questions WHERE core_problem_id = p_problem_id),
                'ready_for_next', (SELECT COUNT(*) > 0 FROM research_prioritized_questions WHERE core_problem_id = p_problem_id AND importance_rating >= 3)
            ) INTO result;
        WHEN 'planning' THEN
            SELECT jsonb_build_object(
                'stage', 'planning',
                'completed', (SELECT COUNT(*) > 0 FROM planning_action_plans pap 
                             JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                             JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                             WHERE rpq.core_problem_id = p_problem_id),
                'action_plans_count', (SELECT COUNT(*) FROM planning_action_plans pap 
                                     JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                     JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                     WHERE rpq.core_problem_id = p_problem_id),
                'ready_for_next', (SELECT COUNT(*) > 0 FROM planning_action_plans pap 
                                 JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                 JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                 WHERE rpq.core_problem_id = p_problem_id AND pap.plan_status = 'approved')
            ) INTO result;
        WHEN 'development' THEN
            SELECT jsonb_build_object(
                'stage', 'development',
                'completed', (SELECT COUNT(*) > 0 FROM development_prototypes dp 
                             JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                             JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                             JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                             WHERE rpq.core_problem_id = p_problem_id),
                'prototypes_count', (SELECT COUNT(*) FROM development_prototypes dp 
                                   JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                   JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                   JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                   WHERE rpq.core_problem_id = p_problem_id),
                'ready_for_next', (SELECT COUNT(*) > 0 FROM development_prototypes dp 
                                 JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                 JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                 JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                 WHERE rpq.core_problem_id = p_problem_id AND dp.prototype_status = 'completed')
            ) INTO result;
        WHEN 'budget' THEN
            SELECT jsonb_build_object(
                'stage', 'budget',
                'completed', (SELECT COUNT(*) > 0 FROM budget_allocations ba 
                             JOIN development_prototypes dp ON ba.prototype_id = dp.id 
                             JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                             JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                             JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                             WHERE rpq.core_problem_id = p_problem_id),
                'allocations_count', (SELECT COUNT(*) FROM budget_allocations ba 
                                    JOIN development_prototypes dp ON ba.prototype_id = dp.id 
                                    JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                    JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                    JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                    WHERE rpq.core_problem_id = p_problem_id),
                'ready_for_next', (SELECT COUNT(*) > 0 FROM budget_allocations ba 
                                 JOIN development_prototypes dp ON ba.prototype_id = dp.id 
                                 JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                 JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                 JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                 WHERE rpq.core_problem_id = p_problem_id AND ba.allocation_status = 'approved')
            ) INTO result;
        WHEN 'market' THEN
            SELECT jsonb_build_object(
                'stage', 'market',
                'completed', (SELECT COUNT(*) > 0 FROM market_communication_strategies mcs 
                             JOIN market_insights mi ON mcs.market_insight_id = mi.id 
                             JOIN development_prototypes dp ON mi.prototype_id = dp.id 
                             JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                             JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                             JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                             WHERE rpq.core_problem_id = p_problem_id),
                'strategies_count', (SELECT COUNT(*) FROM market_communication_strategies mcs 
                                   JOIN market_insights mi ON mcs.market_insight_id = mi.id 
                                   JOIN development_prototypes dp ON mi.prototype_id = dp.id 
                                   JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                   JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                   JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                   WHERE rpq.core_problem_id = p_problem_id),
                'ready_for_next', (SELECT COUNT(*) > 0 FROM market_communication_strategies mcs 
                                 JOIN market_insights mi ON mcs.market_insight_id = mi.id 
                                 JOIN development_prototypes dp ON mi.prototype_id = dp.id 
                                 JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                 JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                 JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                 WHERE rpq.core_problem_id = p_problem_id AND mcs.strategy_status = 'active')
            ) INTO result;
        WHEN 'support' THEN
            SELECT jsonb_build_object(
                'stage', 'support',
                'completed', (SELECT COUNT(*) > 0 FROM support_continuous_improvements sci 
                             JOIN support_performance_assessments spa ON sci.performance_assessment_id = spa.id 
                             JOIN support_user_feedback suf ON spa.user_feedback_id = suf.id 
                             JOIN market_communication_strategies mcs ON suf.communication_strategy_id = mcs.id 
                             JOIN market_insights mi ON mcs.market_insight_id = mi.id 
                             JOIN development_prototypes dp ON mi.prototype_id = dp.id 
                             JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                             JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                             JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                             WHERE rpq.core_problem_id = p_problem_id),
                'improvements_count', (SELECT COUNT(*) FROM support_continuous_improvements sci 
                                     JOIN support_performance_assessments spa ON sci.performance_assessment_id = spa.id 
                                     JOIN support_user_feedback suf ON spa.user_feedback_id = suf.id 
                                     JOIN market_communication_strategies mcs ON suf.communication_strategy_id = mcs.id 
                                     JOIN market_insights mi ON mcs.market_insight_id = mi.id 
                                     JOIN development_prototypes dp ON mi.prototype_id = dp.id 
                                     JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                     JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                     JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                     WHERE rpq.core_problem_id = p_problem_id),
                'ready_for_next', (SELECT COUNT(*) > 0 FROM support_continuous_improvements sci 
                                 JOIN support_performance_assessments spa ON sci.performance_assessment_id = spa.id 
                                 JOIN support_user_feedback suf ON spa.user_feedback_id = suf.id 
                                 JOIN market_communication_strategies mcs ON suf.communication_strategy_id = mcs.id 
                                 JOIN market_insights mi ON mcs.market_insight_id = mi.id 
                                 JOIN development_prototypes dp ON mi.prototype_id = dp.id 
                                 JOIN planning_action_plans pap ON dp.action_plan_id = pap.id 
                                 JOIN planning_related_questions prq ON pap.related_question_id = prq.id 
                                 JOIN research_prioritized_questions rpq ON prq.research_question_id = rpq.id 
                                 WHERE rpq.core_problem_id = p_problem_id AND sci.next_cycle_focus = TRUE)
            ) INTO result;
        ELSE
            result := jsonb_build_object('error', 'Invalid stage name');
    END CASE;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;