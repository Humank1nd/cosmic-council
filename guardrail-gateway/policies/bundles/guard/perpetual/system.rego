package guard.perpetual.system

import rego.v1

# Default deny for system access
default allow = false

# Allow system access if basic requirements are met
allow {
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_system_access
}

# Deny system access if action is not allowed
deny_system_access {
    input.resource.action == "delete"
    input.context.resource_type == "critical_system"
}

# Deny system access if risk level is too high
deny_system_access {
    input.context.risk_level == "critical"
}

# Deny system access if data sensitivity is too high
deny_system_access {
    input.context.data_sensitivity == "top_secret"
}

# Deny system access if user is not authorized
deny_system_access {
    not input.context.user_authorized
}

# Obligations for read access
obligations := o {
    allow
    input.resource.action == "read"
    o := ["log_system_access", "audit_read_operations"]
}

# Obligations for write access
obligations := o {
    allow
    input.resource.action == "update"
    o := ["log_system_access", "audit_write_operations", "validate_changes", "backup_before_changes"]
}

# Obligations for execute access
obligations := o {
    allow
    input.resource.action == "execute"
    o := ["log_system_access", "audit_execute_operations", "monitor_execution", "enforce_timeout"]
}

# Additional obligations for critical system access
obligations := o {
    allow
    input.context.resource_type == "critical_system"
    o := ["log_system_access", "audit_operations", "require_approval", "monitor_impact", "rollback_plan"]
}

# Additional obligations for high-risk operations
obligations := o {
    allow
    input.context.risk_level == "high"
    o := ["log_system_access", "audit_operations", "require_approval", "monitor_impact", "peer_review"]
}
