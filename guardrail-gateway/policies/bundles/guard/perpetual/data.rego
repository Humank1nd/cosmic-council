package guard.perpetual.data

import rego.v1

# Default deny for data access
default allow = false

# Allow data access if basic requirements are met
allow {
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_data_access
}

# Deny data access if data sensitivity is too high
deny_data_access {
    input.context.data_sensitivity == "top_secret"
}

# Deny data access if action is not allowed for data type
deny_data_access {
    input.resource.action == "delete"
    input.context.data_type == "personal_data"
}

# Deny data access if risk level is critical
deny_data_access {
    input.context.risk_level == "critical"
}

# Deny data access if user is not authorized
deny_data_access {
    not input.context.user_authorized
}

# Deny data access if data is restricted
deny_data_access {
    input.context.data_restricted == true
}

# Obligations for read access
obligations := o {
    allow
    input.resource.action == "read"
    o := ["log_data_access", "audit_read_operations"]
}

# Obligations for write access
obligations := o {
    allow
    input.resource.action == "update"
    o := ["log_data_access", "audit_write_operations", "validate_data", "backup_data"]
}

# Obligations for delete access
obligations := o {
    allow
    input.resource.action == "delete"
    o := ["log_data_access", "audit_delete_operations", "require_approval", "soft_delete", "retention_policy"]
}

# Additional obligations for personal data
obligations := o {
    allow
    input.context.data_type == "personal_data"
    o := ["log_data_access", "audit_operations", "privacy_protection", "data_encryption", "consent_verification"]
}

# Additional obligations for confidential data
obligations := o {
    allow
    input.context.data_sensitivity == "confidential"
    o := ["log_data_access", "audit_operations", "data_encryption", "access_restriction", "audit_trail"]
}

# Additional obligations for high-risk data operations
obligations := o {
    allow
    input.context.risk_level == "high"
    o := ["log_data_access", "audit_operations", "require_approval", "monitor_impact", "data_integrity_check"]
}
