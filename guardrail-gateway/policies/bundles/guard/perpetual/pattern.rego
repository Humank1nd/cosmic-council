package guard.perpetual.pattern

import rego.v1

# Default deny for pattern recognition
default allow = false

# Allow pattern recognition if basic requirements are met
allow {
    input.resource.action == "analyze"
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_pattern_recognition
}

# Deny pattern recognition if data sensitivity is too high
deny_pattern_recognition {
    input.context.data_sensitivity == "top_secret"
}

# Deny pattern recognition if risk level is critical
deny_pattern_recognition {
    input.context.risk_level == "critical"
}

# Deny pattern recognition if pattern data is incomplete
deny_pattern_recognition {
    not input.context.pattern_data
}

# Deny pattern recognition if pattern data is corrupted
deny_pattern_recognition {
    input.context.pattern_data.integrity_check == false
}

# Deny pattern recognition if privacy concerns exist
deny_pattern_recognition {
    input.context.pattern_data.contains_personal_data == true
    not input.context.privacy_consent
}

# Obligations for pattern recognition
obligations := o {
    allow
    o := ["log_pattern_recognition", "encrypt_pattern_data", "audit_analysis_process", "validate_patterns"]
}

# Additional obligations for high-confidence patterns
obligations := o {
    allow
    input.context.pattern_data.confidence_score > 0.9
    o := ["log_pattern_recognition", "encrypt_pattern_data", "audit_analysis_process", "validate_patterns", "peer_review", "pattern_validation"]
}

# Additional obligations for personal data patterns
obligations := o {
    allow
    input.context.pattern_data.contains_personal_data == true
    o := ["log_pattern_recognition", "encrypt_pattern_data", "audit_analysis_process", "validate_patterns", "privacy_protection", "data_anonymization"]
}

# Additional obligations for behavioral patterns
obligations := o {
    allow
    input.context.pattern_data.pattern_type == "behavioral"
    o := ["log_pattern_recognition", "encrypt_pattern_data", "audit_analysis_process", "validate_patterns", "ethical_review", "bias_detection"]
}

# Additional obligations for system patterns
obligations := o {
    allow
    input.context.pattern_data.pattern_type == "system"
    o := ["log_pattern_recognition", "encrypt_pattern_data", "audit_analysis_process", "validate_patterns", "system_impact_assessment"]
}
