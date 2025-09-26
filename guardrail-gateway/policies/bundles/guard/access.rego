package guard.access

default allow = false

allow {
  input.resource.service == "raw_intel_feed"
  input.resource.action == "read"
  input.agent.enterprise == "red"
  input.agent.squad == "data_miner"
  not deny_high_risk
}

deny_high_risk {
  input.context.risk >= 0.7
}

obligations := o {
  allow
  o := ["log_source_provenance", "attach_citation_requirements"]
}
