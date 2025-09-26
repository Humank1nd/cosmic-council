# Cosmic Council Core Framework

## Overview

The Cosmic Council Core Framework implements the hexagonal problem-solving system described in "The Book of the Cosmic Council". This framework breaks complex problems into six distinct facets, each handled by specialized enterprise agents that work together in a systematic, clockwise processing cycle.

## The Six Enterprises

The framework consists of six enterprise agents, each with unique roles and capabilities:

### 🔴 Red Owl (Research & Inquiry)
- **Animal Symbol**: Owl
- **Core Principle**: Curiosity
- **Role**: Knowledge gathering, research, and inquiry
- **Color**: #FF0000
- **Focus**: Root cause analysis, data gathering, stakeholder research

### 🟠 Orange Orangutan (Logistics & Planning)
- **Animal Symbol**: Orangutan
- **Core Principle**: Planning
- **Role**: Logistics, planning, and strategy
- **Color**: #FFA500
- **Focus**: Project planning, resource allocation, timeline development

### 🟡 Yellow Honeybee (Development & Creativity)
- **Animal Symbol**: Honeybee
- **Core Principle**: Creativity
- **Role**: Development, prototyping, and creativity
- **Color**: #FFFF00
- **Focus**: Solution design, innovation, prototype development

### 🟢 Green Tortoise (Budget & Resources)
- **Animal Symbol**: Tortoise
- **Core Principle**: Sustainability
- **Role**: Budget, resources, and sustainability
- **Color**: #008000
- **Focus**: Financial planning, resource optimization, sustainability

### 🔵 Blue Dolphin (Communication & Marketing)
- **Animal Symbol**: Dolphin
- **Core Principle**: Clarity
- **Role**: Communication, marketing, and clarity
- **Color**: #0000FF
- **Focus**: Stakeholder communication, marketing strategy, message clarity

### 🟣 Purple Elephant (Support & Empathy)
- **Animal Symbol**: Elephant
- **Core Principle**: Empathy
- **Role**: Support, feedback, and empathy
- **Color**: #4B0082
- **Focus**: Human-centered design, support systems, feedback loops

## Processing Flow

The framework follows a systematic clockwise processing cycle:

```
Red Owl → Orange Orangutan → Yellow Honeybee → Green Tortoise → Blue Dolphin → Purple Elephant → Feedback Loop
```

Each enterprise builds upon the insights from previous enterprises, creating a comprehensive, multi-perspective analysis of the problem.

## Key Features

### 1. Problem Complexity Handling
- **Simple**: Straightforward problems with clear solutions
- **Moderate**: Multi-faceted problems requiring coordination
- **Complex**: Interconnected problems with multiple stakeholders
- **Systemic**: Large-scale problems affecting entire systems

### 2. Comprehensive Analysis
Each enterprise provides:
- **Insights**: Domain-specific analysis and findings
- **Recommendations**: Actionable next steps
- **Confidence Score**: Assessment of analysis quality
- **Next Actions**: Specific tasks for implementation

### 3. Feedback Loops
The Purple Elephant enterprise implements continuous feedback loops for:
- Overall sentiment analysis
- Improvement suggestions
- Process refinements
- Knowledge retention

### 4. Final Synthesis
The framework synthesizes all enterprise inputs into:
- Comprehensive implementation plan
- Risk mitigation strategies
- Success metrics
- Timeline and resource requirements

## Usage Examples

### Business Case Study: New Product Development
```python
problem = ProblemStatement(
    title="Sustainable Product Launch",
    description="Launch a new sustainable product...",
    complexity=ProblemComplexity.COMPLEX,
    domain="Product Development & Marketing",
    stakeholders=["Product Team", "Marketing", "Finance", "Customers"],
    constraints={"budget": "$500K", "timeline": "6 months"},
    success_criteria=["Market adoption > 10K units", "Positive ROI"]
)

council = CosmicCouncil()
result = await council.solve_problem(problem)
```

### Personal Case Study: Career Transition
```python
problem = ProblemStatement(
    title="Career Change to Tech Industry",
    description="Transition from current career to technology industry...",
    complexity=ProblemComplexity.MODERATE,
    domain="Personal Development & Career Planning",
    stakeholders=["Self", "Family", "Mentors", "Potential Employers"],
    constraints={"time_available": "20 hours/week", "budget": "$5K"},
    success_criteria=["Land tech job", "Salary increase > 20%"]
)
```

### Global Issue Case Study: Climate Change
```python
problem = ProblemStatement(
    title="Community Climate Action Plan",
    description="Develop comprehensive climate action plan...",
    complexity=ProblemComplexity.SYSTEMIC,
    domain="Environmental Policy & Urban Planning",
    stakeholders=["City Government", "Residents", "Businesses", "Environmental Groups"],
    constraints={"budget": "$10M", "timeline": "5 years"},
    success_criteria=["40% emission reduction", "Community engagement > 70%"]
)
```

## Framework Architecture

### Core Classes

#### `ProblemStatement`
Represents a problem to be solved with:
- Title and description
- Complexity level
- Domain and stakeholders
- Constraints and success criteria
- Metadata and timestamps

#### `EnterpriseResult`
Contains results from enterprise processing:
- Enterprise type and status
- Insights and recommendations
- Confidence score and processing time
- Next actions and dependencies

#### `CycleResult`
Complete cycle execution result with:
- Problem statement
- All enterprise results
- Final synthesis
- Feedback loop analysis
- Overall metrics

#### `CosmicCouncil`
Main orchestrator that:
- Manages all six enterprises
- Executes processing cycles
- Synthesizes final decisions
- Handles feedback loops

## Performance Metrics

The framework tracks:
- **Processing Time**: Total cycle execution time
- **Confidence Scores**: Per-enterprise and overall confidence
- **Success Rates**: Completion and failure rates
- **Quality Metrics**: Analysis depth and recommendation quality

## Integration Points

The core framework integrates with:
- **Guardrail Gateway**: Policy enforcement and decision logging
- **108-Cycle System**: Fractal processing with redundancy
- **Database Schema**: Persistent storage of problems and results
- **API Endpoints**: RESTful interface for external systems
- **AI/LLM Integration**: Enhanced analysis capabilities

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install asyncio dataclasses
   ```

2. **Run the Demo**:
   ```bash
   python demo_cosmic_council.py
   ```

3. **Use in Your Code**:
   ```python
   from cosmic_council_core import CosmicCouncil, ProblemStatement, ProblemComplexity
   
   council = CosmicCouncil()
   problem = ProblemStatement(title="Your Problem", ...)
   result = await council.solve_problem(problem)
   ```

## Next Steps

The core framework provides the foundation for:
- Interactive hexagon visualization
- Web-based user interface
- AI/LLM integration
- Advanced analytics
- Enterprise deployment

## Contributing

This framework is part of the larger Cosmic Council project. Contributions should align with the hexagonal methodology and maintain the systematic, multi-perspective approach to problem-solving.

## License

Part of the Cosmic Council project - see main project documentation for licensing information.
