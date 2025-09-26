package guard.perpetual.breakthrough

import rego.v1

# Default deny for breakthrough analysis
default allow = false

# Allow breakthrough analysis if basic requirements are met
allow {
    input.resource.action == "analyze"
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_breakthrough_analysis
}

# Deny breakthrough analysis if data sensitivity is too high
deny_breakthrough_analysis {
    input.context.data_sensitivity == "top_secret"
}

# Deny breakthrough analysis if ethical considerations are not addressed
deny_breakthrough_analysis {
    not input.context.ethical_considerations
}

# Deny breakthrough analysis if risk level is critical
deny_breakthrough_analysis {
    input.context.risk_level == "critical"
}

# Deny breakthrough analysis if breakthrough data is incomplete
deny_breakthrough_analysis {
    not input.context.breakthrough_data
}

# Deny breakthrough analysis if breakthrough data is corrupted
deny_breakthrough_analysis {
    input.context.breakthrough_data.integrity_check == false
}

# Obligations for breakthrough analysis
obligations := o {
    allow
    o := ["log_breakthrough_analysis", "encrypt_breakthrough_data", "audit_analysis_process", "ethical_review", "bias_detection"]
}

# Additional obligations for high-impact breakthroughs
obligations := o {
    allow
    input.context.breakthrough_data.impact_score > 0.8
    o := ["log_breakthrough_analysis", "encrypt_breakthrough_data", "audit_analysis_process", "ethical_review", "bias_detection", "peer_review", "safety_assessment"]
}

# Additional obligations for AI safety breakthroughs
obligations := o {
    allow
    "ai_safety" in input.context.ethical_considerations
    o := ["log_breakthrough_analysis", "encrypt_breakthrough_data", "audit_analysis_process", "ethical_review", "bias_detection", "ai_safety_review", "alignment_check"]
}

# Additional obligations for system modification breakthroughs
obligations := o {
    allow
    "system_modification" in input.context.ethical_considerations
    o := ["log_breakthrough_analysis", "encrypt_breakthrough_data", "audit_analysis_process", "ethical_review", "bias_detection", "system_impact_assessment", "rollback_plan"]
}
