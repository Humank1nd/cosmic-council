CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS common_agents (
  agent_id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  enterprise TEXT CHECK (enterprise IN ('red','orange','yellow','green','blue','purple')) NOT NULL,
  squad TEXT NOT NULL,
  scopes TEXT[] DEFAULT '{}',
  tools JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    scope TEXT,
    version INT NOT NULL,
    rego TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS policy_bindings (
    binding_id UUID PRIMARY KEY,
    policy_id UUID REFERENCES policies (policy_id) ON DELETE CASCADE,
    subject_selector JSONB NOT NULL,
    resource_selector JSONB NOT NULL,
    effect TEXT CHECK (
        effect IN ('enforce', 'monitor')
    ) DEFAULT 'enforce'
);

CREATE TABLE IF NOT EXISTS decisions (
  decision_id UUID PRIMARY KEY,
  time TIMESTAMPTZ DEFAULT now(),
  agent_id UUID REFERENCES common_agents(agent_id),
  request JSONB,
  allow BOOLEAN,
  policy_refs UUID[],
  explanation JSONB,
  latency_ms INT
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id UUID PRIMARY KEY,
    decision_id UUID REFERENCES decisions (decision_id) ON DELETE CASCADE,
    severity TEXT CHECK (
        severity IN (
            'low',
            'medium',
            'high',
            'critical'
        )
    ),
    status TEXT CHECK (
        status IN ('open', 'mitigated', 'closed')
    ) DEFAULT 'open',
    notes JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);