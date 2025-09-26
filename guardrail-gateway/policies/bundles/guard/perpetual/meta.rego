package guard.perpetual.meta

import rego.v1

# Default deny for meta-cycle execution
default allow = false

# Allow meta-cycle execution if basic requirements are met
allow {
    input.resource.action == "execute"
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_meta_cycle_execution
}

# Deny meta-cycle execution if processing time limit is exceeded
deny_meta_cycle_execution {
    input.context.processing_time_limit > 600  # 10 minutes
}

# Deny meta-cycle execution if cost budget is exceeded
deny_meta_cycle_execution {
    input.context.cost_budget > 200.0  # $200
}

# Deny meta-cycle execution if risk level is critical
deny_meta_cycle_execution {
    input.context.risk_level == "critical"
}

# Deny meta-cycle execution if ethical considerations are not addressed
deny_meta_cycle_execution {
    not input.context.ethical_considerations
}

# Deny meta-cycle execution if system modification is involved without approval
deny_meta_cycle_execution {
    "system_modification" in input.context.ethical_considerations
    not input.context.approval_granted
}

# Deny meta-cycle execution if self-improvement is involved without safety checks
deny_meta_cycle_execution {
    "self_improvement" in input.context.ethical_considerations
    not input.context.safety_checks_passed
}

# Obligations for meta-cycle execution
obligations := o {
    allow
    o := ["log_meta_cycle_execution", "monitor_system_impact", "enforce_timeout", "validate_changes", "audit_operations", "ethical_review"]
}

# Additional obligations for system modification meta-cycles
obligations := o {
    allow
    "system_modification" in input.context.ethical_considerations
    o := ["log_meta_cycle_execution", "monitor_system_impact", "enforce_timeout", "validate_changes", "audit_operations", "ethical_review", "system_impact_assessment", "rollback_plan", "approval_required"]
}

# Additional obligations for self-improvement meta-cycles
obligations := o {
    allow
    "self_improvement" in input.context.ethical_considerations
    o := ["log_meta_cycle_execution", "monitor_system_impact", "enforce_timeout", "validate_changes", "audit_operations", "ethical_review", "safety_assessment", "alignment_check", "capability_limits"]
}

# Additional obligations for parameter optimization meta-cycles
obligations := o {
    allow
    input.context.meta_cycle_type == "parameter_optimization"
    o := ["log_meta_cycle_execution", "monitor_system_impact", "enforce_timeout", "validate_changes", "audit_operations", "ethical_review", "performance_validation", "stability_check"]
}

# Additional obligations for architecture evolution meta-cycles
obligations := o {
    allow
    input.context.meta_cycle_type == "architecture_evolution"
    o := ["log_meta_cycle_execution", "monitor_system_impact", "enforce_timeout", "validate_changes", "audit_operations", "ethical_review", "system_impact_assessment", "rollback_plan", "approval_required", "peer_review"]
}
