"""
Case Study Generator for Cosmic Council
Generates custom case studies based on user inputs and templates
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from case_study_templates import CaseStudyTemplateLibrary, CaseStudyTemplate, CaseStudyCategory, CaseStudyComplexity
from src.core.types import ProblemStatement, ProblemComplexity

@dataclass
class CaseStudyGenerationRequest:
    """Request for generating a custom case study"""
    category: CaseStudyCategory
    complexity: CaseStudyComplexity
    domain: str
    title: str
    description: str
    stakeholders: List[str]
    constraints: Dict[str, str]
    success_criteria: List[str]
    custom_requirements: Dict[str, Any] = field(default_factory=dict)
    estimated_duration: Optional[str] = None
    learning_objectives: Optional[List[str]] = None

@dataclass
class GeneratedCaseStudy:
    """Generated case study with all components"""
    id: str
    title: str
    description: str
    category: CaseStudyCategory
    complexity: CaseStudyComplexity
    estimated_duration: str
    learning_objectives: List[str]
    problem_statement: ProblemStatement
    expected_outcomes: List[str]
    key_insights: List[str]
    resources_needed: List[str]
    success_metrics: List[str]
    tags: List[str]
    generated_date: datetime
    base_template_id: Optional[str] = None

class CaseStudyGenerator:
    """Generator for custom case studies"""
    
    def __init__(self):
        self.template_library = CaseStudyTemplateLibrary()
        self.generated_studies: Dict[str, GeneratedCaseStudy] = {}
    
    def generate_case_study(self, request: CaseStudyGenerationRequest) -> GeneratedCaseStudy:
        """Generate a custom case study based on the request"""
        
        # Find the best matching template
        base_template = self._find_best_template(request)
        
        # Generate the case study
        case_study = GeneratedCaseStudy(
            id=str(uuid.uuid4()),
            title=request.title,
            description=request.description,
            category=request.category,
            complexity=request.complexity,
            estimated_duration=request.estimated_duration or self._estimate_duration(request.complexity),
            learning_objectives=request.learning_objectives or self._generate_learning_objectives(request),
            problem_statement=ProblemStatement(
                title=request.title,
                description=request.description,
                complexity=self._map_complexity(request.complexity),
                domain=request.domain,
                stakeholders=request.stakeholders,
                constraints=request.constraints,
                success_criteria=request.success_criteria
            ),
            expected_outcomes=self._generate_expected_outcomes(request, base_template),
            key_insights=self._generate_key_insights(request, base_template),
            resources_needed=self._generate_resources_needed(request, base_template),
            success_metrics=self._generate_success_metrics(request, base_template),
            tags=self._generate_tags(request),
            generated_date=datetime.now(timezone.utc),
            base_template_id=base_template.id if base_template else None
        )
        
        # Store the generated case study
        self.generated_studies[case_study.id] = case_study
        
        return case_study
    
    def _find_best_template(self, request: CaseStudyGenerationRequest) -> Optional[CaseStudyTemplate]:
        """Find the best matching template for the request"""
        # First, try to find templates in the same category and complexity
        category_templates = self.template_library.get_templates_by_category(request.category)
        complexity_templates = [t for t in category_templates if t.complexity == request.complexity]
        
        if complexity_templates:
            # If we have exact matches, return the first one
            return complexity_templates[0]
        
        # If no exact matches, try same category with different complexity
        if category_templates:
            return category_templates[0]
        
        # If no category matches, try any template with same complexity
        complexity_templates = self.template_library.get_templates_by_complexity(request.complexity)
        if complexity_templates:
            return complexity_templates[0]
        
        # Return None if no suitable template found
        return None
    
    def _map_complexity(self, complexity: CaseStudyComplexity) -> ProblemComplexity:
        """Map case study complexity to problem complexity"""
        mapping = {
            CaseStudyComplexity.BEGINNER: ProblemComplexity.SIMPLE,
            CaseStudyComplexity.INTERMEDIATE: ProblemComplexity.MODERATE,
            CaseStudyComplexity.ADVANCED: ProblemComplexity.COMPLEX,
            CaseStudyComplexity.EXPERT: ProblemComplexity.SYSTEMIC
        }
        return mapping.get(complexity, ProblemComplexity.MODERATE)
    
    def _estimate_duration(self, complexity: CaseStudyComplexity) -> str:
        """Estimate duration based on complexity"""
        duration_mapping = {
            CaseStudyComplexity.BEGINNER: "1-2 hours",
            CaseStudyComplexity.INTERMEDIATE: "2-3 hours",
            CaseStudyComplexity.ADVANCED: "4-6 hours",
            CaseStudyComplexity.EXPERT: "6-8 hours"
        }
        return duration_mapping.get(complexity, "3-4 hours")
    
    def _generate_learning_objectives(self, request: CaseStudyGenerationRequest) -> List[str]:
        """Generate learning objectives based on the request"""
        base_objectives = {
            CaseStudyCategory.BUSINESS: [
                "Understand business strategy and planning",
                "Develop problem-solving and decision-making skills",
                "Learn to analyze market conditions and opportunities",
                "Apply business frameworks and methodologies"
            ],
            CaseStudyCategory.PERSONAL: [
                "Develop personal growth and development strategies",
                "Learn to set and achieve personal goals",
                "Understand self-assessment and improvement techniques",
                "Apply personal development frameworks"
            ],
            CaseStudyCategory.GLOBAL: [
                "Understand global challenges and systemic thinking",
                "Develop policy analysis and implementation skills",
                "Learn to engage with diverse stakeholders",
                "Apply social impact assessment methodologies"
            ],
            CaseStudyCategory.TECHNICAL: [
                "Understand technical implementation challenges",
                "Develop system design and architecture skills",
                "Learn to manage technical projects and teams",
                "Apply technology integration methodologies"
            ],
            CaseStudyCategory.EDUCATIONAL: [
                "Understand educational design and implementation",
                "Develop curriculum and assessment strategies",
                "Learn to engage with diverse learning communities",
                "Apply educational technology and innovation"
            ]
        }
        
        objectives = base_objectives.get(request.category, [
            "Develop problem-solving and analytical skills",
            "Learn to work with diverse stakeholders",
            "Apply systematic thinking and planning",
            "Understand implementation challenges and solutions"
        ])
        
        # Add complexity-specific objectives
        if request.complexity == CaseStudyComplexity.EXPERT:
            objectives.append("Master advanced problem-solving techniques")
            objectives.append("Develop leadership and strategic thinking skills")
        elif request.complexity == CaseStudyComplexity.ADVANCED:
            objectives.append("Apply advanced analytical frameworks")
            objectives.append("Develop complex problem-solving skills")
        
        return objectives[:5]  # Limit to 5 objectives
    
    def _generate_expected_outcomes(self, request: CaseStudyGenerationRequest, 
                                  base_template: Optional[CaseStudyTemplate]) -> List[str]:
        """Generate expected outcomes based on the request"""
        if base_template:
            # Use base template outcomes as inspiration
            outcomes = base_template.expected_outcomes.copy()
        else:
            # Generate generic outcomes based on category
            outcomes = {
                CaseStudyCategory.BUSINESS: [
                    "Comprehensive strategy and implementation plan",
                    "Risk assessment and mitigation strategies",
                    "Stakeholder engagement and communication plan",
                    "Performance metrics and success measurement framework"
                ],
                CaseStudyCategory.PERSONAL: [
                    "Personal development plan and timeline",
                    "Skill development and improvement strategy",
                    "Goal setting and achievement framework",
                    "Self-assessment and reflection tools"
                ],
                CaseStudyCategory.GLOBAL: [
                    "Policy analysis and implementation strategy",
                    "Stakeholder engagement and community involvement plan",
                    "Impact assessment and measurement framework",
                    "Sustainability and long-term planning approach"
                ],
                CaseStudyCategory.TECHNICAL: [
                    "Technical architecture and implementation plan",
                    "System integration and deployment strategy",
                    "Quality assurance and testing framework",
                    "Performance monitoring and optimization plan"
                ],
                CaseStudyCategory.EDUCATIONAL: [
                    "Educational design and curriculum framework",
                    "Learning assessment and evaluation strategy",
                    "Student engagement and support plan",
                    "Implementation and rollout methodology"
                ]
            }.get(request.category, [
                "Comprehensive problem-solving approach",
                "Implementation strategy and timeline",
                "Stakeholder engagement plan",
                "Success measurement framework"
            ])
        
        return outcomes
    
    def _generate_key_insights(self, request: CaseStudyGenerationRequest, 
                             base_template: Optional[CaseStudyTemplate]) -> List[str]:
        """Generate key insights based on the request"""
        if base_template:
            insights = base_template.key_insights.copy()
        else:
            # Generate generic insights based on category and complexity
            insights = [
                "Understanding the problem is the first step to solving it",
                "Stakeholder engagement is crucial for successful implementation",
                "Systematic thinking leads to better solutions",
                "Continuous monitoring and adjustment are essential"
            ]
            
            if request.complexity in [CaseStudyComplexity.ADVANCED, CaseStudyComplexity.EXPERT]:
                insights.extend([
                    "Complex problems require multi-faceted approaches",
                    "Risk management and contingency planning are critical",
                    "Long-term thinking balances short-term needs"
                ])
        
        return insights[:6]  # Limit to 6 insights
    
    def _generate_resources_needed(self, request: CaseStudyGenerationRequest, 
                                 base_template: Optional[CaseStudyTemplate]) -> List[str]:
        """Generate resources needed based on the request"""
        if base_template:
            resources = base_template.resources_needed.copy()
        else:
            # Generate generic resources based on category
            resources = {
                CaseStudyCategory.BUSINESS: [
                    "Business analysis and strategy expertise",
                    "Project management and implementation tools",
                    "Stakeholder engagement and communication resources",
                    "Financial planning and budget management tools"
                ],
                CaseStudyCategory.PERSONAL: [
                    "Personal development and coaching resources",
                    "Skill assessment and development tools",
                    "Goal setting and tracking systems",
                    "Mentorship and support networks"
                ],
                CaseStudyCategory.GLOBAL: [
                    "Policy analysis and research resources",
                    "Community engagement and communication tools",
                    "Impact assessment and measurement frameworks",
                    "International best practices and case studies"
                ],
                CaseStudyCategory.TECHNICAL: [
                    "Technical expertise and development resources",
                    "System architecture and design tools",
                    "Testing and quality assurance frameworks",
                    "Technology infrastructure and platforms"
                ],
                CaseStudyCategory.EDUCATIONAL: [
                    "Educational design and curriculum expertise",
                    "Learning assessment and evaluation tools",
                    "Student engagement and support resources",
                    "Educational technology and innovation platforms"
                ]
            }.get(request.category, [
                "Problem-solving and analytical expertise",
                "Project management and implementation tools",
                "Stakeholder engagement resources",
                "Monitoring and evaluation frameworks"
            ])
        
        return resources
    
    def _generate_success_metrics(self, request: CaseStudyGenerationRequest, 
                                base_template: Optional[CaseStudyTemplate]) -> List[str]:
        """Generate success metrics based on the request"""
        if base_template:
            metrics = base_template.success_metrics.copy()
        else:
            # Generate generic metrics based on complexity
            metrics = [
                "Achievement of primary objectives > 90%",
                "Stakeholder satisfaction > 4.0/5",
                "Timeline adherence > 95%",
                "Budget compliance > 95%"
            ]
            
            if request.complexity in [CaseStudyComplexity.ADVANCED, CaseStudyComplexity.EXPERT]:
                metrics.extend([
                    "Quality standards maintained > 95%",
                    "Risk mitigation effectiveness > 90%",
                    "Long-term sustainability > 85%"
                ])
        
        return metrics
    
    def _generate_tags(self, request: CaseStudyGenerationRequest) -> List[str]:
        """Generate tags based on the request"""
        tags = [request.category.value]
        
        # Add complexity tag
        tags.append(request.complexity.value)
        
        # Add domain-related tags
        domain_words = request.domain.lower().split()
        tags.extend([word for word in domain_words if len(word) > 3])
        
        # Add custom tags from requirements
        if "tags" in request.custom_requirements:
            tags.extend(request.custom_requirements["tags"])
        
        # Remove duplicates and limit to 8 tags
        return list(set(tags))[:8]
    
    def get_generated_case_study(self, case_study_id: str) -> Optional[GeneratedCaseStudy]:
        """Get a generated case study by ID"""
        return self.generated_studies.get(case_study_id)
    
    def list_generated_case_studies(self) -> List[GeneratedCaseStudy]:
        """List all generated case studies"""
        return list(self.generated_studies.values())
    
    def export_case_study(self, case_study_id: str) -> Dict[str, Any]:
        """Export a generated case study as a dictionary"""
        case_study = self.get_generated_case_study(case_study_id)
        if not case_study:
            return {}
        
        return {
            "id": case_study.id,
            "title": case_study.title,
            "description": case_study.description,
            "category": case_study.category.value,
            "complexity": case_study.complexity.value,
            "estimated_duration": case_study.estimated_duration,
            "learning_objectives": case_study.learning_objectives,
            "problem_statement": {
                "title": case_study.problem_statement.title,
                "description": case_study.problem_statement.description,
                "complexity": case_study.problem_statement.complexity.value,
                "domain": case_study.problem_statement.domain,
                "stakeholders": case_study.problem_statement.stakeholders,
                "constraints": case_study.problem_statement.constraints,
                "success_criteria": case_study.problem_statement.success_criteria
            },
            "expected_outcomes": case_study.expected_outcomes,
            "key_insights": case_study.key_insights,
            "resources_needed": case_study.resources_needed,
            "success_metrics": case_study.success_metrics,
            "tags": case_study.tags,
            "generated_date": case_study.generated_date.isoformat(),
            "base_template_id": case_study.base_template_id
        }

# Demo function
def demo_case_study_generator():
    """Demonstrate the case study generator"""
    print("🌌 Cosmic Council Case Study Generator")
    print("=" * 60)
    
    # Create generator
    generator = CaseStudyGenerator()
    
    # Create a sample request
    request = CaseStudyGenerationRequest(
        category=CaseStudyCategory.BUSINESS,
        complexity=CaseStudyComplexity.INTERMEDIATE,
        domain="E-commerce & Customer Experience",
        title="Omnichannel Customer Experience Transformation",
        description="A traditional retail company needs to transform its customer experience by implementing an omnichannel strategy that seamlessly integrates online and offline touchpoints while improving customer satisfaction and increasing sales.",
        stakeholders=[
            "Executive Leadership", "Marketing Team", "IT Department", "Store Staff",
            "Customers", "Technology Vendors", "Data Analytics Team"
        ],
        constraints={
            "budget": "$5M over 18 months",
            "timeline": "18-month implementation",
            "integration": "Must integrate with existing systems",
            "training": "Staff training required for new processes"
        },
        success_criteria=[
            "Increase customer satisfaction by 40%",
            "Improve cross-channel conversion rates by 25%",
            "Reduce customer service response time by 50%",
            "Achieve 90% staff adoption of new systems",
            "Generate $20M additional revenue"
        ],
        custom_requirements={
            "tags": ["omnichannel", "customer-experience", "retail", "digital-transformation"]
        }
    )
    
    print("📋 Generating custom case study...")
    print(f"Title: {request.title}")
    print(f"Category: {request.category.value}")
    print(f"Complexity: {request.complexity.value}")
    print(f"Domain: {request.domain}")
    print()
    
    # Generate the case study
    case_study = generator.generate_case_study(request)
    
    print("✅ Case study generated successfully!")
    print(f"ID: {case_study.id}")
    print(f"Duration: {case_study.estimated_duration}")
    print(f"Learning Objectives: {len(case_study.learning_objectives)}")
    print(f"Expected Outcomes: {len(case_study.expected_outcomes)}")
    print(f"Key Insights: {len(case_study.key_insights)}")
    print(f"Resources Needed: {len(case_study.resources_needed)}")
    print(f"Success Metrics: {len(case_study.success_metrics)}")
    print(f"Tags: {', '.join(case_study.tags)}")
    print()
    
    print("📊 Generated Learning Objectives:")
    for i, objective in enumerate(case_study.learning_objectives, 1):
        print(f"   {i}. {objective}")
    print()
    
    print("🎯 Generated Expected Outcomes:")
    for i, outcome in enumerate(case_study.expected_outcomes, 1):
        print(f"   {i}. {outcome}")
    print()
    
    print("💡 Generated Key Insights:")
    for i, insight in enumerate(case_study.key_insights, 1):
        print(f"   {i}. {insight}")
    print()
    
    print("📈 Generated Success Metrics:")
    for i, metric in enumerate(case_study.success_metrics, 1):
        print(f"   {i}. {metric}")
    print()
    
    print(f"📁 Total generated case studies: {len(generator.list_generated_case_studies())}")
    print("✅ Case study generator ready for use!")

if __name__ == "__main__":
    demo_case_study_generator()
