# 🏗️ Cosmic Council Engineering Blueprint

This is the **authoritative structure** for organizing the Cosmic Council's GitHub repository, codebase, and PostgreSQL database. It encodes the **linear clockwise flow (ROYGBV)**, allows **fractal recursion** (nested micro-councils), and ensures **auditability, modularity, and scalability**.

## 📂 **Repository Structure**

```
cosmic-council/
├── red_research/              # 🔴 Research & Inquiry
│   ├── db/                    # Schema: core_problem, findings, questions
│   ├── tools/                 # Scrapers, analyzers, validators
│   └── docs/                  # Research protocols, architecture
│
├── orange_logistics/          # 🟠 Planning & Logistics
│   ├── db/                    # Schema: action_plans, dependencies
│   ├── tools/                 # Planners, schedulers
│   └── docs/                  # Planning protocols, architecture
│
├── yellow_development/        # 🟡 Development & Creativity
│   ├── db/                    # Schema: prototypes, testing, creative notes
│   ├── tools/                 # Prototyping frameworks
│   └── docs/                  # Development protocols, architecture
│
├── green_budget/              # 🟢 Budget & Resources
│   ├── db/                    # Schema: budget, resources, cost tracking
│   ├── tools/                 # Forecasting, ROI calculators
│   └── docs/                  # Budget protocols, architecture
│
├── blue_market/               # 🔵 Communication & Marketing
│   ├── db/                    # Schema: market analysis, comms, metrics
│   ├── tools/                 # Campaign pipelines, dashboards
│   └── docs/                  # Marketing protocols, architecture
│
├── purple_support/            # 🟣 Support & Empathy
│   ├── db/                    # Schema: feedback, performance, improvements
│   ├── tools/                 # Feedback pipelines, analysis
│   └── docs/                  # Support protocols, architecture
│
├── shared/                    # Common utilities & libraries
│   ├── auth/                  # Authentication & authorization
│   ├── logging/               # Centralized logging
│   ├── nlp/                   # Natural language processing
│   ├── utils/                 # Common utilities
│   └── security/              # Security policies & encryption
│
├── council/                   # Core framework (nervous system)
│   ├── hexagon.py             # Linear ROYGBV processing
│   ├── cycles.py              # 108-cycle fractal orchestration
│   ├── reflection.py          # Purple-led continuous improvement
│   ├── explain.py             # Explainability utilities
│   └── policies/              # Guardrail Gateway (OPA/Rego)
│
├── workflows/                 # N8N orchestration
│   ├── n8n/                   # Workflow JSON files
│   └── tests/                 # Workflow E2E tests
│
├── database/                  # Global database management
│   ├── migrations/            # Alembic migrations
│   ├── seeds/                 # Seed data scripts
│   ├── views/                 # Database views
│   └── triggers/              # Database triggers
│
├── tests/                     # Comprehensive testing
│   ├── unit/                  # Unit tests per enterprise
│   ├── integration/           # Cross-enterprise tests
│   ├── e2e/                   # End-to-end cycle tests
│   └── performance/           # Load & scalability tests
│
└── docs/                      # Global documentation
    ├── architecture/          # System architecture
    ├── protocols/             # Enterprise protocols
    └── decisions/             # Architecture decisions
```

## 🗄️ **Database Schema (PostgreSQL)**

### **Enterprise Schemas**

Each enterprise owns its schema with strict data ownership:

#### 🔴 Red Research Schema
- `core_problem(id, title, description, status, created_at, updated_at)`
- `research_findings(id, problem_id, summary, evidence, confidence, created_at)`
- `prioritized_questions(id, finding_id, question, priority, created_at)`

#### 🟠 Orange Logistics Schema
- `action_plans(id, question_id, steps_json, owner, status)`
- `dependencies(id, plan_id, dependency_name, resolved, created_at)`
- `evaluation_notes(id, plan_id, evaluation_text, reviewer)`

#### 🟡 Yellow Development Schema
- `prototypes(id, plan_id, prototype_link, description, created_at)`
- `internal_testing(id, prototype_id, result, confidence_score)`
- `creative_notes(id, prototype_id, note, author)`

#### 🟢 Green Budget Schema
- `resource_inventory(id, resource_name, quantity, cost)`
- `budget_allocations(id, prototype_id, allocated_amount, actual_amount)`
- `time_cost_analysis(id, allocation_id, hours_spent, delta)`

#### 🔵 Blue Market Schema
- `audience_targeting(id, plan_id, segment, strategy_json)`
- `communication_strategy(id, audience_id, message, channel, schedule)`
- `performance_metrics(id, strategy_id, impressions, engagement, conversion)`

#### 🟣 Purple Support Schema
- `feedback_collection(id, strategy_id, feedback_text, sentiment, source)`
- `performance_assessments(id, feedback_id, rating, category)`
- `improvement_recommendations(id, assessment_id, recommendation_text, priority)`

### **Global Control Tables**

- `cycles(id, objective_ref, status, started_at, completed_at, parent_cycle_id, cycle_depth)`
- `stage_executions(id, cycle_id, stage_code, status, started_at, completed_at, execution_order)`
- `audit_log(id, entity_type, entity_id, action, actor, timestamp, details_json)`
- `performance_metrics(id, cycle_id, metric_name, metric_value, measurement_timestamp)`
- `system_config(id, config_key, config_value, config_type, is_active)`

## 🔄 **Processing Flow**

### **1. Strict ROYGBV Order**
- Red → Orange → Yellow → Green → Blue → Purple → back to Red
- No skipping or out-of-order execution
- Each stage must complete before the next begins

### **2. Stage Execution**
- Every stage writes to its DB tables
- Once a stage's output is `completed`, an **N8N trigger** launches the next stage's workflow
- All stage executions are logged in `stage_executions` table

### **3. Cycle Control**
- A `cycles` record is created at initiation
- Each stage adds a `stage_executions` row linked to that cycle
- At the end of Purple, feedback is logged and fed back to Red for the next cycle

### **4. Fractal Recursion**
- Any stage can spin off a **sub-cycle** (`child_cycle_id`) if deeper exploration is needed
- Sub-cycles must **resolve and merge** into the parent before the parent continues
- This ensures the **linear order remains unbroken** even within recursion

### **5. Audit & Explainability**
- Every row in every table has provenance (cycle, stage, parent entity)
- `audit_log` captures every insert/update/delete with `actor` (human, agent, or system)
- `/v1/explain/{id}` endpoint retrieves a complete chain of reasoning for any entity

## ⚙️ **Engineering Best Practices**

### **1. Coding Standards**
- Use domain-driven file naming: `research_findings_loader.py`
- All DB access through repository classes (no raw SQL in business logic)
- Type hints required in all functions
- No cross-imports between enterprises; only `shared/` may be imported across

### **2. Database Practices**
- Each enterprise schema has its **own Alembic migration path**
- All migrations must add forward **and backward** compatibility
- Data retention via **soft deletes** and status enums
- All tables have `id`, `created_at`, `updated_at`, `status`, `source_cycle_id`, `previous_stage_output_id`

### **3. Workflows & Automation**
- Stage transitions = **N8N workflows** (saved JSON in `/workflows/`)
- Workflows must log status in `stage_executions`
- On failure, N8N must rollback, log error in `audit_log`, and notify maintainers

### **4. Testing**
- **Unit tests** inside each enterprise folder (`/tests/[enterprise]/`)
- **Integration tests** between two consecutive enterprises
- **E2E tests** to simulate an entire cycle
- Minimum 80% coverage enforced in CI

### **5. Security**
- All DB connections via env vars
- Sensitive data encrypted with pgcrypto
- Access control rules stored in `shared/security`
- All actions logged in `audit_log` with actor identification

## 🧩 **Engineer's Mental Model**

Think of the repo as:

- **Six gears in a clock** (ROYGBV)
- **One always hands the output forward** to the next gear
- **Cycles spin until feedback aligns** with the objective
- **Sub-cycles are smaller gears inside one gear**, but still spin clockwise
- **The audit log is the watch face**, showing exactly what happened, when, and why

## 🚀 **Getting Started**

### **1. Environment Setup**
```bash
# Clone repository
git clone https://github.com/cosmic-council/framework.git
cd cosmic-council-framework

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### **2. Database Setup**
```bash
# Create database
createdb cosmic_council

# Run migrations
alembic upgrade head

# Seed initial data
python database/seeds/seed_initial_data.py
```

### **3. Run Tests**
```bash
# Run all tests
pytest

# Run enterprise-specific tests
pytest tests/red_research/
pytest tests/orange_logistics/
# ... etc
```

### **4. Start Development**
```bash
# Start the council core
python council/hexagon.py

# Start enterprise services
python red_research/tools/research_service.py
python orange_logistics/tools/planning_service.py
# ... etc
```

## 📊 **Monitoring & Observability**

### **Performance Metrics**
- Cycle completion time
- Stage execution time
- Enterprise confidence scores
- Breakthrough detection rate
- Consciousness evolution tracking

### **Audit Trail**
- Complete action history in `audit_log`
- Entity provenance tracking
- Actor identification (human, agent, system)
- Decision reasoning chains

### **Health Checks**
- Database connection health
- Enterprise service availability
- Workflow execution status
- Resource utilization

## 🔮 **Future Enhancements**

### **Planned Features**
- **3D Visualization**: Three-dimensional hexagon rendering
- **VR/AR Support**: Virtual and augmented reality interfaces
- **Mobile Apps**: Native mobile applications
- **Advanced Analytics**: Detailed performance metrics and insights
- **Custom Themes**: User-customizable visual themes
- **Export Capabilities**: Export visualizations as images/videos

### **Integration Roadmap**
- **AI/LLM Integration**: Enhanced analysis with AI insights
- **Database Integration**: Persistent state storage
- **Cloud Deployment**: Scalable cloud-based deployment
- **Enterprise Features**: Advanced enterprise management capabilities

---

## 🏛️ **The Sacred Architecture**

This structure transforms the Cosmic Council from a **collection of files** into a **living, breathing organism** that:

- **Grows organically** through fractal expansion
- **Learns continuously** through reflection and audit trails
- **Scales infinitely** through microservices architecture
- **Maintains integrity** through strict boundaries and testing
- **Evolves consciously** through policy evolution and improvement

The repository becomes a **digital temple** where each enterprise is a **sacred space** for its specialized wisdom, all connected through the **nervous system** of the council core.

**This is not just code organization - it's a philosophy of how consciousness should be structured in digital form.** 🏛️✨
