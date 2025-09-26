# Cosmic Council Refinement Engine

A sophisticated problem-refinement ladder system that implements the Cosmic Council's fractal approach to problem-solving. The system uses 12 refinement layers (Deci → Quecto) with complete ROYGBV cycles at each layer, automatically deciding when to refine deeper or resolve based on solution quality.

## 🏛️ Core Concept

The Deci → Quecto scale is not about raw granularity everywhere at once. It's a **problem-refinement ladder** where:

1. **Every problem starts at Deci** (broad framing)
2. **Complete ROYGBV cycles** are executed at each layer
3. **Purple Elephant evaluation** determines if the solution is sufficient
4. **If insufficient**, the system fractals downward to the next layer
5. **Refinement continues** until the problem is solved or reaches Quecto

## 🔢 The 12 Refinement Layers

| Layer | Scale | Purpose | Toolchain | Example |
|-------|-------|---------|-----------|---------|
| **Deci** | 10⁻¹ | Surface Reasoning | LLM | "How do we reduce carbon emissions globally?" |
| **Centi** | 10⁻² | Problem Decomposition | Graph Analysis | "Which industries account for the largest share?" |
| **Milli** | 10⁻³ | Focused Research | RAG | "How can steel production be made cleaner?" |
| **Micro** | 10⁻⁶ | Detailed Analysis | Statistical | "What innovations in smelting could cut energy?" |
| **Nano** | 10⁻⁹ | Symbolic & Formal Methods | Symbolic AI | "What catalysts can reduce CO₂ in steel reactions?" |
| **Pico** | 10⁻¹² | Algorithmic Optimization | Optimization | "What quantum properties affect catalyst efficiency?" |
| **Femto** | 10⁻¹⁵ | Micro-Mechanistic Modeling | Simulation | "What resonance effects matter in the reaction?" |
| **Atto** | 10⁻¹⁸ | Edge Case Exploration | Adversarial | "How could quantum algorithms optimize this?" |
| **Zepto** | 10⁻²¹ | Creative Divergence | Stochastic | "Exotic particle dynamics" |
| **Yocto** | 10⁻²⁴ | Knowledge Compression | Clustering | "Field interactions" |
| **Ronto** | 10⁻²⁷ | Meta-Reasoning | Meta-Learning | "Hypothetical constructs" |
| **Quecto** | 10⁻³⁰ | Chaos & Breakthroughs | Quantum Chaos | "Is this even the right framing of reality?" |

## 🔄 ROYGBV Cycle

Each layer executes a complete **ROYGBV cycle**:

- **🔴 Red**: Research & Inquiry
- **🟠 Orange**: Planning & Logistics  
- **🟡 Yellow**: Development & Creativity
- **🟢 Green**: Budget & Resources
- **🔵 Blue**: Market & Communication
- **🟣 Purple**: Support & Feedback (evaluation)

## ⚙️ Escalator Function

The **Escalator** decides the next action after each complete ROYGBV cycle:

- **RESOLVE**: Solution meets confidence and completeness thresholds
- **REFINE**: Drop to next deeper layer for more precise analysis
- **STAY**: Retry current layer with alternative approach

## 🚀 Quick Start

### Basic Usage

```python
from refinement_engine import create_refinement_engine

# Create the engine
orchestrator, tracker, escalator, sector_engine = create_refinement_engine()

# Submit a problem
problem_context = await orchestrator.process_problem_continuously(
    problem_id="carbon-reduction-001",
    title="Global Carbon Reduction",
    description="How can we reduce global carbon emissions by 50% by 2030?",
    max_iterations=50
)

# Check status
status = orchestrator.get_problem_status("carbon-reduction-001")
print(f"Status: {status['status']}")
print(f"Current layer: {status['current_layer']}")
print(f"Layer runs: {status['layer_runs_count']}")
```

### Using the REST API

```bash
# Start the API server
python -m refinement_engine.api

# Submit a problem
curl -X POST "http://localhost:8000/problems" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Global Carbon Reduction",
    "description": "How can we reduce global carbon emissions by 50% by 2030?",
    "initial_layer": "deci"
  }'

# Check status
curl "http://localhost:8000/problems/{problem_id}/status"

# Get genealogy
curl "http://localhost:8000/problems/{problem_id}/genealogy"

# Get explanation
curl "http://localhost:8000/problems/{problem_id}/explain"
```

## 📊 Database Schema

The system uses PostgreSQL with the following key tables:

- **`problems`**: Problem tracking and current layer
- **`layer_runs`**: Complete ROYGBV cycles per layer
- **`sector_runs`**: Individual sector executions
- **`refinements`**: Layer descent decisions and rationale
- **`answers`**: Final solutions with confidence scores
- **`layers`**: Layer definitions and capabilities

## 🧪 Governance and Testing

The system includes comprehensive governance tests to ensure:

- **Sector Order Integrity**: ROYGBV sectors execute in correct order
- **Layer Run Completion**: Only complete when Purple sector finishes
- **Refinement Timing**: Refinements only after completed layer runs
- **Escalator Decision Logic**: Decisions based on valid metrics
- **Handoff Integrity**: Data properly passed between sectors
- **Metrics Consistency**: Layer metrics match sector results

```python
from refinement_engine import GovernanceTests

# Run all governance tests
tests = GovernanceTests()
results = await tests.run_all_tests()

print(f"Overall passed: {results['overall_passed']}")
print(f"Tests passed: {results['summary']['passed_tests']}/{results['summary']['total_tests']}")
```

## 🔍 Monitoring and Analytics

### Problem Genealogy

Track the complete refinement path:

```python
genealogy = orchestrator.get_problem_genealogy("carbon-reduction-001")
print(f"Layers visited: {genealogy['layers_visited']}")
print(f"Max depth: {genealogy['max_depth']}")
print(f"Total refinements: {len(genealogy['refinements'])}")
```

### Refinement Analytics

Get detailed performance metrics:

```python
analytics = tracker.get_refinement_analytics("carbon-reduction-001")
print(f"Total cost: ${analytics['total_cost']:.2f}")
print(f"Success rate: {analytics['success_rate']:.1%}")
print(f"Refinement efficiency: {analytics['refinement_efficiency']:.2f}")
```

### Audit Trail

Complete event tracking:

```python
audit_trail = tracker.get_audit_trail("carbon-reduction-001")
for event in audit_trail:
    print(f"{event['timestamp']}: {event['event_type']}")
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Orchestration  │    │   Tracking      │
│   (FastAPI)     │◄──►│   (Layers)      │◄──►│   (Genealogy)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Escalator     │    │  Sector Engine  │    │   Database      │
│   (Decisions)   │    │   (ROYGBV)      │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Layer Policies

Each layer has configurable policies:

```python
config = {
    "confidence_threshold": 0.85,
    "completeness_threshold": 0.80,
    "max_revolutions_per_layer": 3,
    "cost_threshold_multiplier": 1.5,
    "latency_threshold_multiplier": 2.0
}

orchestrator = LayerOrchestrator(config)
```

### Custom Sector Executors

Implement custom sector logic:

```python
class CustomRedSectorExecutor(RedSectorExecutor):
    async def _execute_sector_logic(self, input_data, handoff, layer_capability):
        # Custom research logic
        return await super()._execute_sector_logic(input_data, handoff, layer_capability)

# Register custom executor
sector_engine.register_executor(SectorType.RED, "custom_layer", CustomRedSectorExecutor)
```

## 📈 Performance Optimization

### Layer-Specific Toolchains

Each layer uses optimized toolchains:

- **Deci-Centi**: LLM and graph analysis for broad thinking
- **Milli-Micro**: RAG and statistical analysis for focused research
- **Nano-Pico**: Symbolic AI and optimization for precise modeling
- **Femto-Atto**: Simulation and adversarial testing for edge cases
- **Zepto-Quecto**: Stochastic and quantum methods for breakthrough insights

### Cost and Latency Management

- **Budget caps** per layer prevent runaway costs
- **Latency limits** ensure timely responses
- **Revolution limits** prevent infinite loops
- **Quality thresholds** ensure solution adequacy

## 🛡️ Security and Governance

### Invariant Enforcement

The system enforces critical invariants:

1. **Order Integrity**: Sectors must execute in ROYGBV order
2. **Completion Integrity**: Layer runs only complete after Purple
3. **Refinement Timing**: Refinements only after completed runs
4. **Decision Logic**: Escalator decisions based on valid metrics
5. **Data Integrity**: Handoffs preserve evidence and context

### Audit and Compliance

- **Complete audit trails** for all decisions
- **Genealogy tracking** for problem evolution
- **Performance metrics** for optimization
- **Governance tests** for system integrity

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "refinement_engine.api"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: refinement-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: refinement-engine
  template:
    metadata:
      labels:
        app: refinement-engine
    spec:
      containers:
      - name: refinement-engine
        image: cosmic-council/refinement-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 📚 Examples

See the `examples/` directory for:

- **Basic problem solving**: Simple carbon reduction example
- **Complex multi-layer**: Advanced optimization problem
- **Custom sectors**: Implementing domain-specific logic
- **API integration**: REST API usage patterns
- **Monitoring**: Analytics and genealogy tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all governance tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- The Cosmic Council for the fractal problem-solving framework
- The ROYGBV enterprise model for systematic thinking
- The Deci → Quecto scale for refinement depth
- The Purple Elephant for evaluation and reflection

---

**The Cosmic Council Refinement Engine** - Where problems meet their perfect solutions through fractal refinement and systematic thinking.
