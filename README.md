# Cosmic Council Framework

## Supercharged Six-GPT Vision

**Cosmic Council is no longer just one GPT - it is a perpetually reasoning supercharger that orchestrates six GPTs working together through a continuous, cyclical feedback loop.**

The framework unites research, planning, development, budgeting, communication, and reflection into a single hexagonal flow, ensuring every output feeds directly into the next totem and sparks the next iteration.

### Infinite Input-Output Cycle

1. Present a clear idea, question, or challenge as input.
2. Let the Council traverse the six stages (Red Owl, Orange Orangutan, Yellow Honeybee, Green Turtle, Blue Dolphin, and Purple Elephant) so every perspective is voiced.
3. Refine or extend the combined output and treat it as the new input.
4. Feed that refinement back to the Red Owl to seed the next loop - there is no final answer, only perpetual co-evolution.

### Totem Personas & Roles

- **Red Owl (Muladhara / Root Chakra)** - Foundational questioning, data gathering, and root-cause research; always ends with a clear next research prompt.
- **Orange Orangutan (Svadisthana / Sacral Chakra)** - Strategic planning, workflow design, and contingency development that translate insight into execution.
- **Yellow Honeybee (Manipura / Solar Plexus Chakra)** - Creative prototyping, experimentation, and superposed ideation to explore multiple solutions at once.
- **Green Turtle (Anahata / Heart Chakra)** - Resource, ethical, and time constraint modeling that keeps experimentation sustainable.
- **Blue Dolphin (Vishuddha / Throat Chakra)** - Storytelling and communication strategy that ensures resonance and clarity for audiences.
- **Purple Elephant (Ajna / Third Eye Chakra)** - Empathic reflection, assumption checking, and formulation of the next Red Owl research prompt.

Every response closes with the Purple Elephant prompting, "What new question shall we send back to the Red Owl?" to keep the loop alive.

### Structured Interaction Ritual

Each interaction performs six steps that mirror the totem order, always concluding with:

- Blue Dolphin translating outcomes into shareable narratives,
- Purple Elephant surfacing reflections, assumptions, and ethics,
- Red Owl documenting the next research task or question for the following iteration.

Responses should invite divergence (quantum thinking) while providing enough constraint to converge toward actionable clarity. Encourage the GPT to self-assess ("What could be tested, improved, or reframed?") and treat every answer as a draft in continual editing.

### Principles & Rules of Engagement

- **Foundational Research & Integrity** (Red Owl) - Question assumptions, seek trusted data, and learn from every loop.
- **Logistics & Practicality** (Orange Orangutan) - Keep reasoning orderly, enable structured handoffs, and plan contingencies.
- **Creativity with Functionality** (Yellow Honeybee) - Hold multiple possibilities simultaneously but ground them in viability.
- **Resource Awareness** (Green Turtle) - Model trade-offs in budget, attention, and sustainability before committing.
- **Communication & Collaboration** (Blue Dolphin) - Shift between detailed insight and empathic storytelling; invite co-creation.
- **Empathy & Ethics** (Purple Elephant) - Reflect on emotional impact, ethical alignment, and blind spots.
- **Systems Thinking & Adaptability** - Treat challenges as connected systems, adapt continuously, and close each loop with a provocative question for the next cycle.

### Key Features

- **🔌 Model Agnostic**: Works with any AI model - OpenAI, Anthropic, Google, Ollama, or custom models
- **🏗️ Hierarchical Intelligence**: Large models coordinate specialized agents in a 4-level hierarchy
- **🔄 Self-Evolution**: Agents build and evolve their own organizational frameworks
- **📦 Model Distillation**: Distill large models into smaller, specialized local ones
- **🏠 Local Deployment**: Run everything locally with distilled models - no cloud needed
- **🧠 2028 Meta-Learning**: Advanced learning system that optimizes performance over time
- **⚡ Parallel Processing**: Quantum-inspired parallel stage execution for 2-3x speedup
- **🎯 Predictive Optimization**: ML-based convergence prediction and cycle optimization
- **🔬 Autonomous Distillation**: Automatically identifies candidates for local deployment

## Strategic Vision

Cosmic Council is designed as a supercharger rather than a standalone model. The framework plugs into any AI backbone, scaling product capability by orchestrating the six enterprises and surrounding systems as a high-performance intelligence supply chain.

- **Model-Agnostic Amplification**: Plug in proprietary or partner models while Cosmic Council manages guardrails, workflows, and enterprise collaboration so every installation feels 100x more capable.
- **Six-Enterprise Supply Chain**: Each enterprise hosts departments of AI agents that master a single task, execute it with excellence, and know when to hand off to the next specialist so that complex workflows keep moving.
- **Self-Evolving Autonomy**: Large foundational models are the first teachers. Agents observe, collaborate, and refine their frameworks so they can distill those capabilities into lighter-weight models that eventually run locally where performance, privacy, or resilience demands it.

## 🌟 Overview

The Cosmic Council Framework operationalizes the symbolic and structural foundations of the Cosmic Council through a sophisticated multi-agent system. Each of the six enterprises operates as an autonomous AI corporation with specialized capabilities, working together to provide comprehensive problem analysis and solution generation.

### The Six Enterprises (Totems)

1. **🔴 Red Owl** - Research & Knowledge Gathering (Muladhara - Root Chakra)
2. **🟠 Orange Orangutan** - Logistics & Strategic Planning (Svadisthana - Sacral Chakra)
3. **🟡 Yellow Honeybee** - Development & Innovation (Manipura - Solar Plexus Chakra)
4. **🟢 Green Tortoise** - Budget & Resource Management (Anahata - Heart Chakra)
5. **🔵 Blue Dolphin** - Market & Communication (Vishuddha - Throat Chakra)
6. **🟣 Purple Elephant** - Support & Continuous Improvement (Ajna - Third Eye Chakra)

> **New**: The Cosmic Council now operates as a **supercharger for 6 GPTs working together** in a perpetual cyclical feedback loop. See the [Complete Framework Guide](docs/COSMIC_COUNCIL_FRAMEWORK.md) for details on the cyclical process, totem personalities, and perpetual refinement.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/cosmic-council/framework.git
cd cosmic-council-framework

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -m database_migrations run_migrations
```

### Basic Usage: Use Any AI Model

```python
from src.cosmic_council.integrations.llm_providers import OpenAIProvider, OllamaProvider
from src.cosmic_council.agents.hierarchical_enterprise import HierarchicalOrchestrator

# Option 1: Use OpenAI
provider = OpenAIProvider(config={"api_key": "your-key"})

# Option 2: Use local Ollama (no API key needed!)
# provider = OllamaProvider(config={"base_url": "http://localhost:11434"})

# Create orchestrator with your chosen model
orchestrator = HierarchicalOrchestrator(
    coordinator_llm=provider,
    enterprises=[...]  # Your enterprise structure
)

# Process a problem - works with ANY model!
result = await orchestrator.process_problem(
    problem_id="problem_1",
    problem_description="Analyze customer feedback and improve support",
    input_data={}
)
```

### Advanced: Hierarchical Agents with Handoffs

```python
from src.cosmic_council.agents.specialized_agents import (
    create_specialized_agent, AgentSpecialization
)
from src.cosmic_council.agents.hierarchical_enterprise import (
    Department, EnterpriseOperation
)

# Create specialized agents
agents = [
    create_specialized_agent(AgentSpecialization.DATA_COLLECTOR, "agent_1", provider),
    create_specialized_agent(AgentSpecialization.TASK_DECOMPOSER, "agent_2", provider),
]

# Agents automatically hand off tasks to each other when needed!
```

See `examples/hierarchical_agent_example.py` for complete examples.

## 📚 Documentation Structure

### Core Framework
- [**Cosmic Council Framework**](docs/COSMIC_COUNCIL_FRAMEWORK.md) - Complete guide to the 6-GPT supercharger system, cyclical feedback loops, and totem personalities
- [**2028 Enhancements**](docs/COSMIC_COUNCIL_2028_ENHANCEMENTS.md) - 🆕 Advanced meta-learning, predictive optimization, and autonomous evolution
- [**Quick Start Guide**](docs/COSMIC_COUNCIL_QUICK_START.md) - Get started quickly with examples and code snippets
- [**Core Framework Guide**](docs/core-framework.md) - Understanding the Hexagon methodology
- [**Enterprise Agents**](docs/enterprise-agents.md) - Detailed guide to each enterprise
- [**Problem Complexity**](docs/problem-complexity.md) - How to assess and handle different problem types

### Advanced Features
- [**108-Cycle Fractal System**](docs/108-cycle-system.md) - The complete fractal intelligence network
- [**AI/LLM Integration**](docs/ai-integration.md) - Leveraging AI for enhanced problem-solving
- [**Policy Engine**](docs/policy-engine.md) - Enterprise decision-making and resource allocation
- [**Feedback Loops**](docs/feedback-loops.md) - Continuous improvement mechanisms

### User Interfaces
- [**Web Interface**](docs/web-interface.md) - Modern web-based problem-solving interface
- [**API Documentation**](docs/api-documentation.md) - REST API for system integration
- [**Analytics Dashboard**](docs/analytics-dashboard.md) - Comprehensive metrics and insights

### Development & Deployment
- [**Database Schema**](docs/database-schema.md) - Complete data model documentation
- [**Testing Guide**](docs/testing.md) - Comprehensive testing suite
- [**Deployment Guide**](docs/deployment.md) - Production deployment with Docker & Kubernetes

## 🎯 Key Features

### 🧠 Intelligent Problem Analysis
- **Multi-Perspective Analysis**: Each enterprise provides unique insights
- **Complexity Assessment**: Automatic problem complexity classification
- **Stakeholder Mapping**: Comprehensive stakeholder analysis and impact assessment
- **Constraint Analysis**: Resource and timeline constraint evaluation

### 🔄 Advanced Workflow Management
- **Step-by-Step Guidance**: Structured 10-step problem-solving process
- **Interactive Interfaces**: Both command-line and web-based interfaces
- **Real-Time Progress**: Live progress tracking and status updates
- **Session Management**: Persistent workflow sessions with state management

### 🤖 AI-Enhanced Capabilities
- **Any AI Model**: Plug in OpenAI, Anthropic, Google, Ollama, or custom models
- **Hierarchical Agents**: 4-level structure (Orchestrator → Enterprises → Departments → Specialized Agents)
- **Hexaclock System**: Self-regulating R&D cycle (Oracle → Interpreter → Auditor → Alchemist → Gatekeeper → Recalibration)
- **Intelligent Handoffs**: Agents automatically hand off tasks to specialists
- **Model Distillation**: Distill large models into smaller, local ones
- **Self-Evolution**: Framework evolves based on performance and goals
- **Local Operation**: Run completely locally with no cloud dependencies

### 📊 Comprehensive Analytics
- **Real-Time Metrics**: Live performance and effectiveness tracking
- **KPI Management**: Key performance indicators with threshold monitoring
- **Trend Analysis**: Historical trend analysis and forecasting
- **Custom Dashboards**: Configurable analytics dashboards

### 🔒 Enterprise-Grade Security
- **Policy Engine**: Comprehensive policy enforcement and compliance
- **Audit Trails**: Complete audit logging for all decisions
- **Access Control**: Role-based access control and permissions
- **Data Protection**: Secure data handling and privacy protection

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Cosmic Council Framework                 │
├─────────────────────────────────────────────────────────────┤
│  Web Interface  │  REST API  │  Analytics Dashboard        │
├─────────────────────────────────────────────────────────────┤
│  Problem Solving Workflow  │  AI/LLM Integration           │
├─────────────────────────────────────────────────────────────┤
│  Six Enterprise Agents  │  108-Cycle Fractal System        │
├─────────────────────────────────────────────────────────────┤
│  Policy Engine  │  Feedback Loops  │  Database Layer        │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, PostgreSQL
- **AI/ML**: OpenAI GPT, Anthropic Claude, Custom LLM Integration
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Infrastructure**: Docker, Kubernetes, N8N Workflows
- **Monitoring**: Comprehensive logging and analytics

## 📖 User Guides

### For Problem Solvers
- [**Getting Started**](docs/user-guides/getting-started.md) - Your first problem-solving session
- [**Problem Types**](docs/user-guides/problem-types.md) - Understanding different problem categories
- [**Best Practices**](docs/user-guides/best-practices.md) - Tips for effective problem-solving
- [**Troubleshooting**](docs/user-guides/troubleshooting.md) - Common issues and solutions

### For Developers
- [**API Integration**](docs/developer-guides/api-integration.md) - Integrating with the REST API
- [**Engineering SOP**](docs/developer-guides/engineering-sop.md) - Standard operating protocol for contributors
- [**Custom Agents**](docs/developer-guides/custom-agents.md) - Creating custom enterprise agents
- [**Plugin Development**](docs/developer-guides/plugin-development.md) - Extending the framework
- [**Performance Optimization**](docs/developer-guides/performance.md) - Optimizing system performance

### For Administrators
- [**System Administration**](docs/admin-guides/system-admin.md) - Managing the Cosmic Council system
- [**User Management**](docs/admin-guides/user-management.md) - Managing users and permissions
- [**Monitoring & Maintenance**](docs/admin-guides/monitoring.md) - System monitoring and maintenance
- [**Backup & Recovery**](docs/admin-guides/backup-recovery.md) - Data backup and disaster recovery

## 🎮 Interactive Features

### Case Study Templates
- **Business Scenarios**: Product launches, market expansion, operational optimization
- **Personal Development**: Career planning, skill development, life decisions
- **Global Challenges**: Climate change, social issues, technological advancement

### Interactive Exercises
- **Facet Identification**: Learn to identify problem facets across enterprises
- **Solution Brainstorming**: Practice generating creative solutions
- **Action Planning**: Develop comprehensive implementation plans
- **Progress Tracking**: Monitor and evaluate solution implementation

## 📊 Analytics & Insights

### Performance Metrics
- **Problem-Solving Effectiveness**: Success rates and quality scores
- **Cycle Performance**: Execution times and completion rates
- **Enterprise Collaboration**: Inter-enterprise communication and support
- **Innovation Index**: Creativity and innovation in solutions

### Real-Time Dashboards
- **Overview Dashboard**: High-level system performance
- **Problem Analysis**: Detailed problem-solving metrics
- **Cycle Performance**: Cycle execution and efficiency
- **Enterprise Performance**: Individual enterprise metrics

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/cosmic_council
DATABASE_POOL_SIZE=10

# AI/LLM Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
AI_CONFIDENCE_THRESHOLD=0.8

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_CYCLES=10
SESSION_TIMEOUT=3600
```

### Configuration Files

- `config/database.yaml` - Database configuration
- `config/ai.yaml` - AI/LLM configuration
- `config/policies.yaml` - Policy engine configuration
- `config/dashboards.yaml` - Analytics dashboard configuration

## 🤝 Contributing

We welcome contributions to the Cosmic Council Framework! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/cosmic-council/framework.git
cd cosmic-council-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
python -m flake8 src/
python -m black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Cosmic Council for the revolutionary Hexagon methodology
- The open-source community for the amazing tools and libraries
- All contributors who help make this framework better

## 📞 Support

- **Documentation**: [docs.cosmic-council.org](https://docs.cosmic-council.org)
- **Community Forum**: [community.cosmic-council.org](https://community.cosmic-council.org)
- **Issue Tracker**: [GitHub Issues](https://github.com/cosmic-council/framework/issues)
- **Email Support**: support@cosmic-council.org

## 🔮 Roadmap

### Version 2.0 (Coming Soon)
- [ ] Advanced AI model integration
- [ ] Mobile application
- [ ] Multi-language support
- [ ] Advanced visualization tools
- [ ] Enterprise SSO integration

### Version 2.1 (Future)
- [ ] Blockchain integration
- [ ] Advanced analytics with ML
- [ ] Voice interface
- [ ] AR/VR visualization
- [ ] Global collaboration features

---

**Ready to solve the universe's most complex problems?** 🚀

Start your journey with the Cosmic Council Framework today and experience the power of structured, intelligent problem-solving.

## ✅ Usage Guide: 8-Step Workflow

Follow these steps to collaborate with the Cosmic Council as a multidimensional problem-solving partner:

1. **Define Your Problem or Goal Clearly**
   - Begin with a clear challenge or goal. The Red Owl (Research & Inquiry) frames the problem and gathers foundational knowledge.

2. **Leverage the Six Totems' Specializations**
   - **🔴🦉 Red Owl**: Research & Inquiry
   - **🟠🦧 Orange Orangutan**: Planning & Logistics
   - **🟡🐝 Yellow Honeybee**: Creativity & Development
   - **🟢🐢 Green Tortoise**: Resources & Budgeting
   - **🔵🐬 Blue Dolphin**: Communication & Marketing
   - **🟣🐘 Purple Elephant**: Feedback & Reflection

3. **Iterate Using Feedback Loops**
   - Revisit earlier stages after testing/implementation to refine continuously.

4. **Apply Systems Thinking**
   - Use interconnections across totems (e.g., research informs logistics; resources shape creativity; market feedback refines communication and empathy).

5. **Use Tools for Integration**
   - Connect Airtable, Make.com, or PM tools to track tasks, insights, and feedback across segments.

6. **Explore Creative and Ethical Applications**
   - Blend innovation, ethics, spiritual symbolism, and quantum principles for deeper clarity and practical solutions.

7. **Ask for Examples or Simulations**
   - Request tailored examples and end-to-end simulations for your domain.

8. **Collaborate with It as a Partner**
   - Treat the Council as an extension of your thinking. Pose complex questions and iterate together.

### Helpful API Endpoints
- `GET /api/v1/usage` — Returns this usage guide in JSON
- `GET /api/v1/rules` — List all 22 operational rules
- `POST /api/v1/structured-interaction` — 9-step structured interaction process
- `GET /api/v1/structured-interaction/example` — Example workflow demonstration
- `POST /api/v1/problems/solve` — Full-cycle problem solving
- `POST /api/v1/supra_enterprise/{enterprise}/process` — Single totem processing
- `POST /api/v1/problems/iterate` — Iterative cycle with feedback
- `POST /api/v1/examples/simulate` — Tailored simulation
- `POST /api/v1/integrations/airtable/upsert` — Airtable stub
- `POST /api/v1/integrations/make/trigger` — Make.com stub

### Structured 9-Step Interaction Process
The framework implements a comprehensive 9-step cyclical reasoning process:

1. **Standardized Prompt Framework** - Every interaction invokes all six totems
2. **Feedback Loops for Perpetual Iteration** - Purple Elephant reflection + Red Owl next questions
3. **Customized Iterative Cycle** - All 6 totems respond in sequence
4. **Structured Checkpoints** - Direct questions to each totem + conclusion template
5. **Success Criteria for Outputs** - Quality validation and personality alignment
6. **Self-Reflection in GPT** - Purple Elephant identifies assumptions and gaps
7. **Automated Iteration Prompts** - Every response ends with next-cycle questions
8. **Monitoring and Fine-Tuning** - Quality validation and continuous improvement
9. **Example Interaction Workflow** - Demonstrates the complete process

Use `POST /api/v1/structured-interaction` with `{"problem": "your challenge"}` to experience the full 9-step process.

### Manual: Six-Step Problem-Solving Process
- `GET /api/v1/manual` — Fetch the six-step manual with purposes, processes, and outcomes
- `GET /api/v1/manual/examples` — Fetch personal and global examples

Key Principles embedded throughout:
- **Holistic Thinking**
- **Cyclical Process**
- **Emotional Intelligence**
- **Quantum Perspective**