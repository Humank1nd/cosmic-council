# Service Agent Orchestrator (Cosmic Council)

ROYGBV multi-agent orchestration system for problem-solving workflows.

## Features

- Six-agent ROYGBV cycle (Red, Orange, Yellow, Green, Blue, Violet)
- Perpetual thinking with reflective loops
- Enterprise-grade guardrails and policy engine
- LLM-agnostic architecture via Supra-GPTR

## Agents

| Agent | Role | Enterprise |
|-------|------|------------|
| Red Owl | Research & Analysis | Deep research, data gathering |
| Orange Orangutan | Strategy & Planning | Solution architecture |
| Yellow Honeybee | Optimization | Efficiency improvements |
| Green Tortoise | Implementation | Code generation, execution |
| Blue Dolphin | Testing & QA | Validation, testing |
| Purple Elephant | Wisdom & Synthesis | Final review, crystallization |

## Getting Started

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

The orchestrator calls an LLM backend through Supra-GPTR (default `http://localhost:8005`)
using OpenAI-compatible `/v1/chat/completions` endpoints.

## Architecture

```
Cosmic Council/
├── api/
│   ├── src/
│   │   ├── council.py     # CosmicCouncil orchestrator (async cycle engine)
│   │   ├── models.py      # Enterprise, Problem, CycleResult, Solution models
│   │   └── api.py         # FastAPI routes
│   ├── run.py             # API entry point
│   ├── requirements.txt
│   └── Dockerfile
└── .github/workflows/ci.yml
```

## Related Repositories

- [core-llm-router-supra](../core-llm-router-supra) - LLM routing
- [core-service-mesh-hub](../core-service-mesh-hub) - Service mesh

## License

Proprietary - E8-Engine
