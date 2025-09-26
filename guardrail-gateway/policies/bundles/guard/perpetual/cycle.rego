package guard.perpetual.cycle

import rego.v1

# Default deny for cycle execution
default allow = false

# Allow cycle execution if basic requirements are met
allow {
    input.resource.action == "execute"
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_cycle_execution
}

# Deny cycle execution if processing time limit is exceeded
deny_cycle_execution {
    input.context.processing_time_limit > 300  # 5 minutes
}

# Deny cycle execution if cost budget is exceeded
deny_cycle_execution {
    input.context.cost_budget > 100.0  # $100
}

# Deny cycle execution if input complexity is too high
deny_cycle_execution {
    input.context.input_complexity > 5.0
}

# Deny cycle execution if risk level is critical
deny_cycle_execution {
    input.context.risk_level == "critical"
}

# Deny cycle execution if resource requirements are too high
deny_cycle_execution {
    input.context.resource_requirements.memory_mb > 2000  # 2GB
}

# Deny cycle execution if CPU requirements are too high
deny_cycle_execution {
    input.context.resource_requirements.cpu_cores > 4
}

# Obligations for standard cycle execution
obligations := o {
    allow
    input.context.risk_level == "low"
    o := ["log_cycle_execution", "monitor_performance", "enforce_timeout"]
}

# Additional obligations for medium risk cycles
obligations := o {
    allow
    input.context.risk_level == "medium"
    o := ["log_cycle_execution", "monitor_performance", "enforce_timeout", "validate_output", "audit_operations"]
}

# Additional obligations for high risk cycles
obligations := o {
    allow
    input.context.risk_level == "high"
    o := ["log_cycle_execution", "monitor_performance", "enforce_timeout", "validate_output", "audit_operations", "require_approval", "encrypt_data"]
}

# Additional obligations for breakthrough cycles
obligations := o {
    allow
    input.context.cycle_type == "breakthrough"
    o := ["log_cycle_execution", "monitor_performance", "enforce_timeout", "validate_output", "audit_operations", "require_approval", "encrypt_data", "ethical_review"]
}

# Additional obligations for meta cycles
obligations := o {
    allow
    input.context.cycle_type == "meta"
    o := ["log_cycle_execution", "monitor_performance", "enforce_timeout", "validate_output", "audit_operations", "require_approval", "encrypt_data", "ethical_review", "system_impact_assessment"]
}
