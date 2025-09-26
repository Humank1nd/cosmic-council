package guard.perpetual.default

import rego.v1

# Default deny for all perpetual thinking operations
default allow = false

# Allow operations if basic requirements are met
allow {
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_operation
}

# Deny operation if risk level is critical
deny_operation {
    input.context.risk_level == "critical"
}

# Deny operation if data sensitivity is too high
deny_operation {
    input.context.data_sensitivity == "top_secret"
}

# Deny operation if user is not authorized
deny_operation {
    not input.context.user_authorized
}

# Obligations for all operations
obligations := o {
    allow
    o := ["log_operation", "audit_operations"]
}

# Additional obligations for high-risk operations
obligations := o {
    allow
    input.context.risk_level == "high"
    o := ["log_operation", "audit_operations", "require_approval", "monitor_impact"]
}

# Additional obligations for confidential data
obligations := o {
    allow
    input.context.data_sensitivity == "confidential"
    o := ["log_operation", "audit_operations", "data_encryption", "access_restriction"]
}
