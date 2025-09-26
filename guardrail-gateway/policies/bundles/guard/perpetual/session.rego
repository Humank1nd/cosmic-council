package guard.perpetual.session

import rego.v1

# Default deny for session creation
default allow = false

# Allow session creation if basic requirements are met
allow {
    input.resource.action == "create"
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_session_creation
}

# Deny session creation if input is too complex
deny_session_creation {
    input.context.input_complexity > 10.0
}

# Deny session creation if user has exceeded limits
deny_session_creation {
    input.context.user_id in user_session_limits
    user_session_limits[input.context.user_id] >= 5
}

# Deny session creation if risk level is too high
deny_session_creation {
    input.context.risk_level == "critical"
}

# Obligations for session creation
obligations := o {
    allow
    o := ["log_session_creation", "monitor_session_activity", "enforce_time_limits"]
}

# Additional obligations for high-risk sessions
obligations := o {
    allow
    input.context.risk_level == "high"
    o := ["log_session_creation", "monitor_session_activity", "enforce_time_limits", "require_approval", "audit_all_operations"]
}

# Additional obligations for confidential data
obligations := o {
    allow
    input.context.data_sensitivity == "confidential"
    o := ["log_session_creation", "monitor_session_activity", "enforce_time_limits", "encrypt_data", "restrict_access"]
}

# User session limits (in production, this would come from a database)
user_session_limits := {
    "user_1": 3,
    "user_2": 1,
    "user_3": 0
}
