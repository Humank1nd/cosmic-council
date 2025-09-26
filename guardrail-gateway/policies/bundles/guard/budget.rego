package guard.budget

default allow = false

allow {
  input.resource.service == "compute_job"
  input.context.estimated_cost <= input.context.budget_cap
}

obligations := ["tag_cost_center", "emit_budget_usage"]
