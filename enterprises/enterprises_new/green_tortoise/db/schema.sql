-- 🟢 Green Budget Schema
-- Budget & Resources Enterprise Database Schema

-- Resource inventory
CREATE TABLE IF NOT EXISTS resource_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    resource_name VARCHAR(200) NOT NULL,
    resource_type VARCHAR(100),
    quantity DECIMAL(15, 2),
    unit VARCHAR(50),
    cost_per_unit DECIMAL(15, 2),
    total_cost DECIMAL(15, 2),
    availability_status VARCHAR(50) DEFAULT 'available' CHECK (
        availability_status IN (
            'available',
            'allocated',
            'depleted'
        )
    ),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Budget allocations for prototypes
CREATE TABLE IF NOT EXISTS budget_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    prototype_id UUID NOT NULL REFERENCES yellow_development.prototypes (id),
    resource_id UUID REFERENCES resource_inventory (id),
    allocated_amount DECIMAL(15, 2) NOT NULL,
    actual_amount DECIMAL(15, 2),
    allocation_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'allocated' CHECK (
        status IN (
            'allocated',
            'spent',
            'returned'
        )
    ),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_cycle_id UUID REFERENCES cycles (id),
    previous_stage_output_id UUID REFERENCES yellow_development.prototypes (id)
);

-- Time and cost analysis
CREATE TABLE IF NOT EXISTS time_cost_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    allocation_id UUID NOT NULL REFERENCES budget_allocations (id),
    hours_spent DECIMAL(8, 2),
    cost_per_hour DECIMAL(10, 2),
    total_cost DECIMAL(15, 2),
    delta_from_estimate DECIMAL(15, 2),
    analysis_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_resource_inventory_type ON resource_inventory (resource_type);

CREATE INDEX IF NOT EXISTS idx_resource_inventory_status ON resource_inventory (availability_status);

CREATE INDEX IF NOT EXISTS idx_budget_allocations_prototype ON budget_allocations (prototype_id);

CREATE INDEX IF NOT EXISTS idx_budget_allocations_resource ON budget_allocations (resource_id);

CREATE INDEX IF NOT EXISTS idx_budget_allocations_status ON budget_allocations (status);

CREATE INDEX IF NOT EXISTS idx_budget_allocations_cycle ON budget_allocations (source_cycle_id);

CREATE INDEX IF NOT EXISTS idx_time_cost_analysis_allocation ON time_cost_analysis (allocation_id);

-- Audit triggers
CREATE TRIGGER update_resource_inventory_updated_at BEFORE UPDATE ON resource_inventory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_allocations_updated_at BEFORE UPDATE ON budget_allocations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();