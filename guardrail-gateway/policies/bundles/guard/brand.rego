package guard.brand

default allow = false

allow {
  input.resource.service == "comms_publish"
  not has_violations
}

has_violations {
  input.context.brand_safety.flags[_] == "hate_speech"
}

has_violations {
  input.context.brand_safety.flags[_] == "toxicity"
}

violations := v {
  input.resource.service == "comms_publish"
  v := [
    {
      "code": "BRAND_HATE_SPEECH",
      "description": "Content contains hate speech or discriminatory language",
      "severity": "high",
      "suggested_remediation": "Remove flagged content or escalate to Purple Elephant for review"
    }
  ]
  input.context.brand_safety.flags[_] == "hate_speech"
}

violations := v {
  input.resource.service == "comms_publish"
  v := [
    {
      "code": "BRAND_TOXICITY", 
      "description": "Content shows high toxicity levels",
      "severity": "medium",
      "suggested_remediation": "Revise content to reduce toxicity or add content warnings"
    }
  ]
  input.context.brand_safety.flags[_] == "toxicity"
}

obligations := ["log_brand_safety_check", "notify_comms_team"]
