package guard.perpetual.ai

import rego.v1

# Default deny for AI integration
default allow = false

# Allow AI integration if basic requirements are met
allow {
    input.agent.enterprise == "perpetual"
    input.agent.squad == "thinking_engine"
    not deny_ai_integration
}

# Deny AI integration if model is not allowed
deny_ai_integration {
    input.context.ai_model in restricted_models
}

# Deny AI integration if cost budget is exceeded
deny_ai_integration {
    input.context.cost_budget > 100.0  # $100
}

# Deny AI integration if risk level is critical
deny_ai_integration {
    input.context.risk_level == "critical"
}

# Deny AI integration if ethical considerations are not addressed
deny_ai_integration {
    not input.context.ethical_considerations
}

# Deny AI integration if model bias is detected
deny_ai_integration {
    input.context.model_bias_detected == true
}

# Deny AI integration if safety checks failed
deny_ai_integration {
    input.context.safety_checks_passed == false
}

# Restricted AI models
restricted_models := [
    "gpt-4-turbo",
    "claude-3-opus",
    "gemini-pro-ultra"
]

# Obligations for AI integration
obligations := o {
    allow
    o := ["log_ai_integration", "monitor_ai_usage", "audit_ai_operations", "ethical_review"]
}

# Additional obligations for high-cost AI models
obligations := o {
    allow
    input.context.cost_budget > 50.0
    o := ["log_ai_integration", "monitor_ai_usage", "audit_ai_operations", "ethical_review", "cost_monitoring", "usage_limits"]
}

# Additional obligations for AI safety operations
obligations := o {
    allow
    "ai_safety" in input.context.ethical_considerations
    o := ["log_ai_integration", "monitor_ai_usage", "audit_ai_operations", "ethical_review", "ai_safety_review", "alignment_check", "capability_limits"]
}

# Additional obligations for bias detection
obligations := o {
    allow
    "bias_detection" in input.context.ethical_considerations
    o := ["log_ai_integration", "monitor_ai_usage", "audit_ai_operations", "ethical_review", "bias_detection", "fairness_validation"]
}

# Additional obligations for model training
obligations := o {
    allow
    input.resource.action == "train"
    o := ["log_ai_integration", "monitor_ai_usage", "audit_ai_operations", "ethical_review", "model_validation", "training_monitoring", "data_quality_check"]
}

# Additional obligations for model inference
obligations := o {
    allow
    input.resource.action == "inference"
    o := ["log_ai_integration", "monitor_ai_usage", "audit_ai_operations", "ethical_review", "inference_monitoring", "output_validation"]
}
