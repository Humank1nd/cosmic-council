"""
Case Study Templates for Agent Orchestrator Problem-Solving
Comprehensive templates for business, personal, and global scenarios
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime, timezone
import json

from src.core.types import ProblemStatement, ProblemComplexity

class CaseStudyCategory(Enum):
    """Categories of case studies"""
    BUSINESS = "business"
    PERSONAL = "personal"
    GLOBAL = "global"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"

class CaseStudyComplexity(Enum):
    """Complexity levels for case studies"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class CaseStudyTemplate:
    """Template for a case study"""
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
    tags: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CaseStudyTemplateLibrary:
    """Library of case study templates"""
    
    def __init__(self):
        self.templates: Dict[str, CaseStudyTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize all case study templates"""
        self._add_business_templates()
        self._add_personal_templates()
        self._add_global_templates()
        self._add_technical_templates()
        self._add_educational_templates()
    
    def _add_business_templates(self):
        """Add business case study templates"""
        
        # Digital Transformation
        self.templates["business_digital_transformation"] = CaseStudyTemplate(
            id="business_digital_transformation",
            title="Digital Transformation for Traditional Manufacturing Company",
            description="A 50-year-old manufacturing company needs to modernize its operations, integrate IoT sensors, implement AI-driven predictive maintenance, and transform its customer experience while maintaining production continuity.",
            category=CaseStudyCategory.BUSINESS,
            complexity=CaseStudyComplexity.ADVANCED,
            estimated_duration="4-6 hours",
            learning_objectives=[
                "Understand digital transformation challenges in traditional industries",
                "Learn to balance innovation with operational continuity",
                "Develop strategies for change management in established organizations",
                "Apply technology integration planning methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Digital Transformation for Traditional Manufacturing",
                description="Transform a traditional manufacturing company into a modern, data-driven, customer-centric organization while maintaining production continuity and employee satisfaction.",
                complexity=ProblemComplexity.COMPLEX,
                domain="Manufacturing & Digital Transformation",
                stakeholders=[
                    "Executive Leadership", "Production Teams", "IT Department", 
                    "Customers", "Suppliers", "Regulatory Bodies", "Employees"
                ],
                constraints={
                    "budget": "$10M over 3 years",
                    "timeline": "3-year phased approach",
                    "compliance": "Industry regulations must be maintained",
                    "continuity": "Zero production downtime during transition"
                },
                success_criteria=[
                    "30% improvement in operational efficiency",
                    "50% reduction in maintenance costs",
                    "95% employee adoption of new systems",
                    "25% increase in customer satisfaction",
                    "Full regulatory compliance maintained"
                ]
            ),
            expected_outcomes=[
                "Comprehensive digital transformation roadmap",
                "Technology integration strategy",
                "Change management plan",
                "Risk mitigation strategies",
                "ROI analysis and business case"
            ],
            key_insights=[
                "Digital transformation requires cultural change, not just technology",
                "Employee engagement is critical for successful adoption",
                "Phased approach reduces risk and allows for learning",
                "Customer experience should drive technology decisions",
                "Data governance is essential for AI implementation"
            ],
            resources_needed=[
                "Digital transformation expertise",
                "Change management consultants",
                "Technology vendors and partners",
                "Employee training programs",
                "Project management tools"
            ],
            success_metrics=[
                "Employee adoption rate > 90%",
                "System uptime > 99.5%",
                "Customer satisfaction score > 4.5/5",
                "ROI > 200% within 3 years",
                "Zero regulatory violations"
            ],
            tags=["digital-transformation", "manufacturing", "change-management", "technology-integration"]
        )
        
        # Startup Scaling
        self.templates["business_startup_scaling"] = CaseStudyTemplate(
            id="business_startup_scaling",
            title="Scaling a Tech Startup from 10 to 100 Employees",
            description="A successful tech startup with 10 employees and $2M ARR needs to scale to 100 employees while maintaining culture, product quality, and customer satisfaction. The challenge includes hiring, processes, infrastructure, and market expansion.",
            category=CaseStudyCategory.BUSINESS,
            complexity=CaseStudyComplexity.INTERMEDIATE,
            estimated_duration="3-4 hours",
            learning_objectives=[
                "Understand scaling challenges in high-growth companies",
                "Learn to balance growth with culture preservation",
                "Develop hiring and onboarding strategies",
                "Apply operational scaling methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Tech Startup Scaling Challenge",
                description="Scale a successful tech startup from 10 to 100 employees while maintaining company culture, product quality, and customer satisfaction.",
                complexity=ProblemComplexity.COMPLEX,
                domain="Technology & Business Scaling",
                stakeholders=[
                    "Founders", "Early Employees", "New Hires", "Customers", 
                    "Investors", "Board Members", "Partners"
                ],
                constraints={
                    "budget": "$5M for 18 months",
                    "timeline": "18-month scaling period",
                    "culture": "Maintain startup culture and values",
                    "quality": "No degradation in product quality"
                },
                success_criteria=[
                    "Successful hiring of 90 new employees",
                    "Maintain 95% employee satisfaction",
                    "Achieve $20M ARR",
                    "Preserve company culture and values",
                    "Expand to 3 new markets"
                ]
            ),
            expected_outcomes=[
                "Scaling strategy and roadmap",
                "Hiring and onboarding plan",
                "Culture preservation strategy",
                "Operational process improvements",
                "Market expansion plan"
            ],
            key_insights=[
                "Culture is the foundation of successful scaling",
                "Hiring the right people is more important than hiring quickly",
                "Processes should evolve with company size",
                "Communication becomes critical at scale",
                "Customer focus must remain central during growth"
            ],
            resources_needed=[
                "HR and recruiting expertise",
                "Leadership development programs",
                "Process improvement consultants",
                "Technology infrastructure",
                "Market research and analysis"
            ],
            success_metrics=[
                "Employee retention rate > 90%",
                "Time to productivity for new hires < 30 days",
                "Customer satisfaction maintained > 4.5/5",
                "Revenue growth rate > 100% annually",
                "Culture survey score > 4.0/5"
            ],
            tags=["startup", "scaling", "hiring", "culture", "growth"]
        )
        
        # Market Entry Strategy
        self.templates["business_market_entry"] = CaseStudyTemplate(
            id="business_market_entry",
            title="International Market Entry Strategy",
            description="A successful domestic software company wants to expand into three international markets (Europe, Asia, Latin America) while adapting to local regulations, cultures, and competitive landscapes.",
            category=CaseStudyCategory.BUSINESS,
            complexity=CaseStudyComplexity.ADVANCED,
            estimated_duration="5-6 hours",
            learning_objectives=[
                "Understand international market entry challenges",
                "Learn to adapt products for different markets",
                "Develop localization and compliance strategies",
                "Apply market analysis and competitive intelligence"
            ],
            problem_statement=ProblemStatement(
                title="International Market Entry Strategy",
                description="Develop and execute a strategy to enter three international markets while adapting to local requirements and maintaining competitive advantage.",
                complexity=ProblemComplexity.SYSTEMIC,
                domain="International Business & Market Expansion",
                stakeholders=[
                    "Executive Team", "Product Team", "Sales Team", "Legal Team",
                    "Local Partners", "Regulatory Bodies", "Customers", "Investors"
                ],
                constraints={
                    "budget": "$15M over 2 years",
                    "timeline": "2-year market entry plan",
                    "compliance": "Full regulatory compliance in each market",
                    "resources": "Limited internal expertise in target markets"
                },
                success_criteria=[
                    "Successful entry into all three markets",
                    "Achieve 10% market share in each region",
                    "Generate $50M revenue within 2 years",
                    "Establish local partnerships and presence",
                    "Maintain product quality and brand consistency"
                ]
            ),
            expected_outcomes=[
                "Market entry strategy for each region",
                "Localization and adaptation plan",
                "Partnership and distribution strategy",
                "Regulatory compliance roadmap",
                "Financial projections and risk analysis"
            ],
            key_insights=[
                "Local partnerships are crucial for market entry",
                "Cultural adaptation goes beyond language translation",
                "Regulatory compliance varies significantly by region",
                "Competitive landscape analysis is essential",
                "Phased approach reduces risk and allows learning"
            ],
            resources_needed=[
                "Market research and analysis",
                "Legal and compliance expertise",
                "Local partnership development",
                "Product localization resources",
                "International business consultants"
            ],
            success_metrics=[
                "Market penetration rate > 10% in each region",
                "Revenue target achievement > 90%",
                "Regulatory compliance score = 100%",
                "Partner satisfaction > 4.0/5",
                "Customer acquisition cost < $500"
            ],
            tags=["international", "market-entry", "localization", "partnerships", "expansion"]
        )
    
    def _add_personal_templates(self):
        """Add personal development case study templates"""
        
        # Career Transition
        self.templates["personal_career_transition"] = CaseStudyTemplate(
            id="personal_career_transition",
            title="Mid-Career Professional Transition to Tech Industry",
            description="A 35-year-old marketing professional with 10 years of experience wants to transition into the technology industry as a product manager. The challenge includes skill development, networking, and managing the transition while maintaining financial stability.",
            category=CaseStudyCategory.PERSONAL,
            complexity=CaseStudyComplexity.INTERMEDIATE,
            estimated_duration="2-3 hours",
            learning_objectives=[
                "Understand career transition challenges and strategies",
                "Learn to identify and develop transferable skills",
                "Develop networking and personal branding strategies",
                "Apply goal-setting and planning methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Mid-Career Transition to Tech Industry",
                description="Successfully transition from marketing to product management in the technology industry while maintaining financial stability and professional growth.",
                complexity=ProblemComplexity.MODERATE,
                domain="Personal Development & Career Transition",
                stakeholders=[
                    "Individual", "Family", "Current Employer", "Target Employers",
                    "Professional Network", "Mentors", "Industry Contacts"
                ],
                constraints={
                    "timeline": "12-18 months transition period",
                    "financial": "Maintain current income level",
                    "family": "Minimize disruption to family life",
                    "experience": "Limited direct tech industry experience"
                },
                success_criteria=[
                    "Secure product management role in tech company",
                    "Maintain or increase current salary level",
                    "Develop relevant technical and product skills",
                    "Build strong professional network in tech industry",
                    "Achieve work-life balance during transition"
                ]
            ),
            expected_outcomes=[
                "Personal development plan and timeline",
                "Skill development strategy",
                "Networking and relationship building plan",
                "Job search and interview preparation strategy",
                "Financial planning and risk management"
            ],
            key_insights=[
                "Transferable skills are more valuable than direct experience",
                "Networking is crucial for career transitions",
                "Continuous learning and skill development are essential",
                "Personal branding helps differentiate in competitive markets",
                "Patience and persistence are key to successful transitions"
            ],
            resources_needed=[
                "Professional development courses",
                "Networking events and conferences",
                "Mentorship and coaching",
                "Industry certifications",
                "Personal branding tools and resources"
            ],
            success_metrics=[
                "Skill assessment score improvement > 50%",
                "Network size increase > 200%",
                "Interview success rate > 30%",
                "Salary maintenance or increase",
                "Job satisfaction score > 4.0/5"
            ],
            tags=["career-transition", "personal-development", "networking", "skill-development"]
        )
        
        # Work-Life Balance
        self.templates["personal_work_life_balance"] = CaseStudyTemplate(
            id="personal_work_life_balance",
            title="Achieving Sustainable Work-Life Balance",
            description="A high-performing executive struggling with work-life balance needs to redesign their approach to work, family, and personal well-being while maintaining career success and family relationships.",
            category=CaseStudyCategory.PERSONAL,
            complexity=CaseStudyComplexity.INTERMEDIATE,
            estimated_duration="2-3 hours",
            learning_objectives=[
                "Understand work-life balance challenges and solutions",
                "Learn to set boundaries and priorities",
                "Develop time management and delegation strategies",
                "Apply stress management and wellness techniques"
            ],
            problem_statement=ProblemStatement(
                title="Achieving Sustainable Work-Life Balance",
                description="Redesign work and personal life to achieve sustainable balance while maintaining career success and family relationships.",
                complexity=ProblemComplexity.MODERATE,
                domain="Personal Development & Life Management",
                stakeholders=[
                    "Individual", "Spouse/Partner", "Children", "Employer",
                    "Colleagues", "Friends", "Healthcare Providers"
                ],
                constraints={
                    "career": "Maintain current performance level",
                    "family": "Preserve family relationships and time",
                    "health": "Improve physical and mental well-being",
                    "time": "Limited time for personal activities"
                },
                success_criteria=[
                    "Reduce work hours to 45-50 per week",
                    "Increase quality time with family by 50%",
                    "Improve physical and mental health metrics",
                    "Maintain or improve job performance",
                    "Achieve personal fulfillment and satisfaction"
                ]
            ),
            expected_outcomes=[
                "Work-life balance strategy and plan",
                "Time management and prioritization system",
                "Boundary setting and communication plan",
                "Wellness and self-care routine",
                "Family and relationship improvement plan"
            ],
            key_insights=[
                "Work-life balance is about integration, not separation",
                "Boundaries are essential for sustainable balance",
                "Delegation and trust are key to reducing workload",
                "Self-care is not selfish but necessary",
                "Communication with family and employer is crucial"
            ],
            resources_needed=[
                "Time management tools and techniques",
                "Stress management and wellness programs",
                "Family counseling or therapy",
                "Executive coaching",
                "Health and fitness resources"
            ],
            success_metrics=[
                "Work hours reduction > 20%",
                "Family time increase > 50%",
                "Stress level reduction > 40%",
                "Job performance maintained or improved",
                "Life satisfaction score > 4.0/5"
            ],
            tags=["work-life-balance", "time-management", "wellness", "family", "stress-management"]
        )
        
        # Skill Development
        self.templates["personal_skill_development"] = CaseStudyTemplate(
            id="personal_skill_development",
            title="Comprehensive Skill Development for Leadership Role",
            description="A mid-level manager preparing for a senior leadership role needs to develop critical leadership skills including strategic thinking, emotional intelligence, communication, and team management while managing current responsibilities.",
            category=CaseStudyCategory.PERSONAL,
            complexity=CaseStudyComplexity.ADVANCED,
            estimated_duration="3-4 hours",
            learning_objectives=[
                "Understand leadership skill development requirements",
                "Learn to assess and develop emotional intelligence",
                "Develop strategic thinking and decision-making abilities",
                "Apply leadership development methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Leadership Skill Development Program",
                description="Develop comprehensive leadership skills to prepare for senior leadership role while maintaining current job performance.",
                complexity=ProblemComplexity.COMPLEX,
                domain="Personal Development & Leadership",
                stakeholders=[
                    "Individual", "Current Manager", "Team Members", "HR Department",
                    "Mentors", "Leadership Development Program", "Future Employer"
                ],
                constraints={
                    "time": "Limited time for development activities",
                    "resources": "Budget constraints for training and development",
                    "performance": "Must maintain current job performance",
                    "timeline": "18-month development timeline"
                },
                success_criteria=[
                    "Demonstrate improved leadership competencies",
                    "Successfully lead cross-functional projects",
                    "Receive positive feedback from team and management",
                    "Be considered for senior leadership positions",
                    "Develop mentoring and coaching abilities"
                ]
            ),
            expected_outcomes=[
                "Personal leadership development plan",
                "Skill assessment and gap analysis",
                "Learning and development strategy",
                "Mentoring and coaching plan",
                "Performance improvement roadmap"
            ],
            key_insights=[
                "Leadership development is a continuous process",
                "Emotional intelligence is as important as technical skills",
                "Feedback and reflection are essential for growth",
                "Mentoring others develops your own leadership skills",
                "Practice and application are key to skill development"
            ],
            resources_needed=[
                "Leadership assessment tools",
                "Training and development programs",
                "Mentoring and coaching resources",
                "360-degree feedback systems",
                "Leadership books and resources"
            ],
            success_metrics=[
                "Leadership competency score improvement > 40%",
                "Team engagement score > 4.0/5",
                "Project success rate > 90%",
                "360-degree feedback improvement > 30%",
                "Promotion readiness assessment > 85%"
            ],
            tags=["leadership", "skill-development", "emotional-intelligence", "mentoring", "career-advancement"]
        )
    
    def _add_global_templates(self):
        """Add global/societal case study templates"""
        
        # Climate Change Mitigation
        self.templates["global_climate_change"] = CaseStudyTemplate(
            id="global_climate_change",
            title="City-Level Climate Change Mitigation Strategy",
            description="A major metropolitan city needs to develop and implement a comprehensive climate change mitigation strategy that addresses carbon emissions, renewable energy adoption, transportation, and community engagement while balancing economic growth and social equity.",
            category=CaseStudyCategory.GLOBAL,
            complexity=CaseStudyComplexity.EXPERT,
            estimated_duration="6-8 hours",
            learning_objectives=[
                "Understand climate change mitigation challenges and solutions",
                "Learn to balance environmental, economic, and social factors",
                "Develop stakeholder engagement and community involvement strategies",
                "Apply systems thinking to complex global problems"
            ],
            problem_statement=ProblemStatement(
                title="City-Level Climate Change Mitigation",
                description="Develop and implement a comprehensive climate change mitigation strategy for a major metropolitan city that addresses environmental, economic, and social challenges.",
                complexity=ProblemComplexity.SYSTEMIC,
                domain="Environmental Policy & Urban Planning",
                stakeholders=[
                    "City Government", "Residents", "Business Community", "Environmental Groups",
                    "Transportation Agencies", "Energy Providers", "Federal Government", "International Organizations"
                ],
                constraints={
                    "budget": "$500M over 10 years",
                    "timeline": "10-year implementation plan",
                    "equity": "Ensure social equity and environmental justice",
                    "economy": "Maintain economic growth and competitiveness"
                },
                success_criteria=[
                    "Reduce carbon emissions by 50% by 2030",
                    "Achieve 80% renewable energy by 2035",
                    "Improve air quality to WHO standards",
                    "Create 50,000 green jobs",
                    "Ensure equitable distribution of benefits and costs"
                ]
            ),
            expected_outcomes=[
                "Comprehensive climate action plan",
                "Renewable energy transition strategy",
                "Transportation and mobility plan",
                "Community engagement and education program",
                "Economic development and job creation plan"
            ],
            key_insights=[
                "Climate action requires systems thinking and integration",
                "Community engagement is essential for successful implementation",
                "Economic incentives can drive environmental behavior change",
                "Equity and justice must be central to climate solutions",
                "Partnerships across sectors are crucial for success"
            ],
            resources_needed=[
                "Environmental and climate science expertise",
                "Urban planning and policy development",
                "Community engagement and education resources",
                "Economic analysis and modeling tools",
                "International best practices and case studies"
            ],
            success_metrics=[
                "Carbon emissions reduction > 50%",
                "Renewable energy adoption > 80%",
                "Air quality improvement > 40%",
                "Green job creation > 50,000",
                "Community satisfaction with climate action > 4.0/5"
            ],
            tags=["climate-change", "sustainability", "urban-planning", "environmental-policy", "community-engagement"]
        )
        
        # Digital Divide
        self.templates["global_digital_divide"] = CaseStudyTemplate(
            id="global_digital_divide",
            title="Bridging the Digital Divide in Rural Communities",
            description="A developing country needs to address the digital divide in rural communities by providing internet access, digital literacy training, and technology infrastructure while ensuring affordability and sustainability.",
            category=CaseStudyCategory.GLOBAL,
            complexity=CaseStudyComplexity.ADVANCED,
            estimated_duration="5-6 hours",
            learning_objectives=[
                "Understand digital divide challenges and solutions",
                "Learn to develop inclusive technology policies",
                "Develop community engagement and capacity building strategies",
                "Apply social impact assessment methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Bridging the Digital Divide in Rural Communities",
                description="Develop and implement a comprehensive strategy to bridge the digital divide in rural communities through infrastructure, education, and policy interventions.",
                complexity=ProblemComplexity.COMPLEX,
                domain="Digital Inclusion & Rural Development",
                stakeholders=[
                    "Government", "Rural Communities", "Telecommunications Companies",
                    "Educational Institutions", "NGOs", "International Donors", "Technology Vendors"
                ],
                constraints={
                    "budget": "$200M over 5 years",
                    "infrastructure": "Limited existing infrastructure",
                    "affordability": "Must be affordable for low-income communities",
                    "sustainability": "Must be economically sustainable long-term"
                },
                success_criteria=[
                    "Provide internet access to 90% of rural population",
                    "Achieve 70% digital literacy rate in rural areas",
                    "Create 10,000 digital economy jobs",
                    "Improve educational outcomes by 30%",
                    "Ensure gender equity in digital access and skills"
                ]
            ),
            expected_outcomes=[
                "Digital infrastructure development plan",
                "Digital literacy and education program",
                "Economic development and job creation strategy",
                "Policy and regulatory framework",
                "Community engagement and capacity building plan"
            ],
            key_insights=[
                "Digital divide is about more than just access to technology",
                "Community ownership and participation are crucial",
                "Education and training are as important as infrastructure",
                "Gender equity must be addressed in digital inclusion",
                "Public-private partnerships can accelerate progress"
            ],
            resources_needed=[
                "Telecommunications and infrastructure expertise",
                "Education and training resources",
                "Community development and engagement tools",
                "Policy and regulatory development",
                "International funding and technical assistance"
            ],
            success_metrics=[
                "Internet access rate > 90%",
                "Digital literacy rate > 70%",
                "Digital economy job creation > 10,000",
                "Educational improvement > 30%",
                "Gender equity in digital access > 80%"
            ],
            tags=["digital-divide", "rural-development", "digital-inclusion", "education", "infrastructure"]
        )
        
        # Healthcare Access
        self.templates["global_healthcare_access"] = CaseStudyTemplate(
            id="global_healthcare_access",
            title="Improving Healthcare Access in Underserved Communities",
            description="A developing region needs to improve healthcare access for underserved communities through telemedicine, mobile health clinics, community health workers, and health education while addressing cultural, linguistic, and economic barriers.",
            category=CaseStudyCategory.GLOBAL,
            complexity=CaseStudyComplexity.ADVANCED,
            estimated_duration="5-6 hours",
            learning_objectives=[
                "Understand healthcare access challenges and solutions",
                "Learn to develop culturally sensitive health programs",
                "Develop community-based health intervention strategies",
                "Apply health equity and social determinants frameworks"
            ],
            problem_statement=ProblemStatement(
                title="Improving Healthcare Access in Underserved Communities",
                description="Develop and implement a comprehensive strategy to improve healthcare access for underserved communities through innovative delivery models and community engagement.",
                complexity=ProblemComplexity.COMPLEX,
                domain="Public Health & Healthcare Access",
                stakeholders=[
                    "Government Health Agencies", "Healthcare Providers", "Community Leaders",
                    "Patients and Families", "NGOs", "International Health Organizations", "Technology Providers"
                ],
                constraints={
                    "budget": "$100M over 5 years",
                    "infrastructure": "Limited healthcare infrastructure",
                    "cultural": "Must respect cultural and linguistic diversity",
                    "sustainability": "Must be economically sustainable"
                },
                success_criteria=[
                    "Increase healthcare access by 60%",
                    "Reduce maternal and child mortality by 40%",
                    "Improve health literacy by 50%",
                    "Achieve 80% vaccination coverage",
                    "Ensure cultural and linguistic appropriateness"
                ]
            ),
            expected_outcomes=[
                "Healthcare delivery model and strategy",
                "Telemedicine and technology integration plan",
                "Community health worker program",
                "Health education and literacy program",
                "Cultural competency and language access plan"
            ],
            key_insights=[
                "Healthcare access is about more than just availability",
                "Community health workers are crucial for reaching underserved populations",
                "Cultural competency is essential for effective healthcare delivery",
                "Technology can extend healthcare reach but cannot replace human connection",
                "Health education and prevention are as important as treatment"
            ],
            resources_needed=[
                "Healthcare and public health expertise",
                "Technology and telemedicine solutions",
                "Community engagement and cultural competency training",
                "Health education and literacy resources",
                "International health best practices and funding"
            ],
            success_metrics=[
                "Healthcare access improvement > 60%",
                "Maternal and child mortality reduction > 40%",
                "Health literacy improvement > 50%",
                "Vaccination coverage > 80%",
                "Cultural competency score > 4.0/5"
            ],
            tags=["healthcare-access", "public-health", "telemedicine", "community-health", "health-equity"]
        )
    
    def _add_technical_templates(self):
        """Add technical case study templates"""
        
        # AI Implementation
        self.templates["technical_ai_implementation"] = CaseStudyTemplate(
            id="technical_ai_implementation",
            title="Enterprise AI Implementation Strategy",
            description="A large enterprise needs to implement AI capabilities across multiple business functions including customer service, operations, and decision-making while ensuring data governance, ethics, and employee adoption.",
            category=CaseStudyCategory.TECHNICAL,
            complexity=CaseStudyComplexity.EXPERT,
            estimated_duration="6-8 hours",
            learning_objectives=[
                "Understand AI implementation challenges and best practices",
                "Learn to develop AI governance and ethics frameworks",
                "Develop change management strategies for AI adoption",
                "Apply data science and machine learning methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Enterprise AI Implementation Strategy",
                description="Develop and implement a comprehensive AI strategy across multiple business functions while ensuring governance, ethics, and successful adoption.",
                complexity=ProblemComplexity.SYSTEMIC,
                domain="Artificial Intelligence & Enterprise Technology",
                stakeholders=[
                    "Executive Leadership", "IT Department", "Data Science Team", "Business Units",
                    "Employees", "Customers", "Regulatory Bodies", "AI Vendors"
                ],
                constraints={
                    "budget": "$50M over 3 years",
                    "timeline": "3-year implementation plan",
                    "governance": "Must comply with AI ethics and regulations",
                    "adoption": "Must achieve high employee adoption rates"
                },
                success_criteria=[
                    "Implement AI in 5 major business functions",
                    "Achieve 90% employee adoption of AI tools",
                    "Improve operational efficiency by 40%",
                    "Ensure 100% compliance with AI ethics guidelines",
                    "Generate $100M in AI-driven value"
                ]
            ),
            expected_outcomes=[
                "AI strategy and implementation roadmap",
                "Data governance and ethics framework",
                "Change management and adoption plan",
                "Technology architecture and infrastructure plan",
                "ROI analysis and value measurement framework"
            ],
            key_insights=[
                "AI success depends on data quality and governance",
                "Change management is crucial for AI adoption",
                "Ethics and transparency are essential for AI trust",
                "AI should augment human capabilities, not replace them",
                "Cross-functional collaboration is key to AI success"
            ],
            resources_needed=[
                "AI and machine learning expertise",
                "Data governance and ethics specialists",
                "Change management and training resources",
                "Technology infrastructure and platforms",
                "AI vendors and consulting partners"
            ],
            success_metrics=[
                "AI implementation in business functions > 5",
                "Employee adoption rate > 90%",
                "Operational efficiency improvement > 40%",
                "AI ethics compliance = 100%",
                "AI-driven value generation > $100M"
            ],
            tags=["artificial-intelligence", "enterprise-technology", "data-governance", "change-management", "ethics"]
        )
        
        # Cybersecurity
        self.templates["technical_cybersecurity"] = CaseStudyTemplate(
            id="technical_cybersecurity",
            title="Comprehensive Cybersecurity Transformation",
            description="A financial services company needs to transform its cybersecurity posture to address evolving threats, regulatory requirements, and digital transformation while maintaining business continuity and customer trust.",
            category=CaseStudyCategory.TECHNICAL,
            complexity=CaseStudyComplexity.EXPERT,
            estimated_duration="6-8 hours",
            learning_objectives=[
                "Understand cybersecurity challenges and threat landscape",
                "Learn to develop comprehensive security strategies",
                "Develop incident response and business continuity plans",
                "Apply risk management and compliance methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Comprehensive Cybersecurity Transformation",
                description="Transform cybersecurity posture to address evolving threats, regulatory requirements, and digital transformation while maintaining business continuity.",
                complexity=ProblemComplexity.SYSTEMIC,
                domain="Cybersecurity & Risk Management",
                stakeholders=[
                    "Executive Leadership", "IT Security Team", "Business Units", "Customers",
                    "Regulatory Bodies", "Security Vendors", "Auditors", "Board of Directors"
                ],
                constraints={
                    "budget": "$30M over 2 years",
                    "timeline": "2-year transformation plan",
                    "compliance": "Must meet all regulatory requirements",
                    "continuity": "Zero business disruption during implementation"
                },
                success_criteria=[
                    "Achieve 99.9% security incident prevention rate",
                    "Meet 100% regulatory compliance requirements",
                    "Reduce security incident response time by 70%",
                    "Improve security awareness to 95%",
                    "Maintain customer trust and business continuity"
                ]
            ),
            expected_outcomes=[
                "Cybersecurity strategy and transformation plan",
                "Security architecture and technology roadmap",
                "Incident response and business continuity plan",
                "Compliance and risk management framework",
                "Security awareness and training program"
            ],
            key_insights=[
                "Cybersecurity is a business risk, not just a technical issue",
                "Defense in depth requires multiple layers of protection",
                "Employee awareness is the first line of defense",
                "Incident response planning is as important as prevention",
                "Continuous monitoring and improvement are essential"
            ],
            resources_needed=[
                "Cybersecurity expertise and specialists",
                "Security technology and tools",
                "Compliance and risk management resources",
                "Training and awareness programs",
                "Incident response and forensics capabilities"
            ],
            success_metrics=[
                "Security incident prevention rate > 99.9%",
                "Regulatory compliance = 100%",
                "Incident response time reduction > 70%",
                "Security awareness rate > 95%",
                "Customer trust score > 4.5/5"
            ],
            tags=["cybersecurity", "risk-management", "compliance", "incident-response", "security-awareness"]
        )
    
    def _add_educational_templates(self):
        """Add educational case study templates"""
        
        # Curriculum Development
        self.templates["educational_curriculum_development"] = CaseStudyTemplate(
            id="educational_curriculum_development",
            title="21st Century Skills Curriculum Development",
            description="A school district needs to develop and implement a comprehensive curriculum that integrates 21st century skills (critical thinking, creativity, collaboration, communication) with traditional academic subjects while meeting state standards and preparing students for future careers.",
            category=CaseStudyCategory.EDUCATIONAL,
            complexity=CaseStudyComplexity.ADVANCED,
            estimated_duration="5-6 hours",
            learning_objectives=[
                "Understand 21st century skills and their importance",
                "Learn to integrate skills with traditional curriculum",
                "Develop assessment and evaluation strategies",
                "Apply educational design and implementation methodologies"
            ],
            problem_statement=ProblemStatement(
                title="21st Century Skills Curriculum Development",
                description="Develop and implement a comprehensive curriculum that integrates 21st century skills with traditional academic subjects while meeting educational standards.",
                complexity=ProblemComplexity.COMPLEX,
                domain="Education & Curriculum Development",
                stakeholders=[
                    "School Administrators", "Teachers", "Students", "Parents",
                    "State Education Department", "Community Members", "Future Employers"
                ],
                constraints={
                    "budget": "$5M over 3 years",
                    "timeline": "3-year implementation plan",
                    "standards": "Must meet all state educational standards",
                    "resources": "Limited teacher training and development resources"
                },
                success_criteria=[
                    "Integrate 21st century skills into all subject areas",
                    "Achieve 90% teacher adoption of new curriculum",
                    "Improve student engagement by 40%",
                    "Meet all state educational standards",
                    "Prepare students for future career success"
                ]
            ),
            expected_outcomes=[
                "Comprehensive curriculum framework",
                "Teacher training and development plan",
                "Assessment and evaluation strategy",
                "Implementation and rollout plan",
                "Student success measurement framework"
            ],
            key_insights=[
                "21st century skills complement rather than replace traditional subjects",
                "Teacher training and support are crucial for successful implementation",
                "Assessment methods must evolve to measure new skills",
                "Student engagement increases with relevant, skills-based learning",
                "Community and parent involvement are essential for success"
            ],
            resources_needed=[
                "Educational design and curriculum expertise",
                "Teacher training and professional development",
                "Assessment and evaluation tools",
                "Technology and learning resources",
                "Community engagement and communication"
            ],
            success_metrics=[
                "Curriculum integration across all subjects = 100%",
                "Teacher adoption rate > 90%",
                "Student engagement improvement > 40%",
                "State standards compliance = 100%",
                "Student career readiness score > 4.0/5"
            ],
            tags=["education", "curriculum-development", "21st-century-skills", "teacher-training", "student-engagement"]
        )
        
        # Online Learning
        self.templates["educational_online_learning"] = CaseStudyTemplate(
            id="educational_online_learning",
            title="Hybrid Learning Model Implementation",
            description="A university needs to implement a hybrid learning model that combines online and in-person instruction to improve accessibility, flexibility, and learning outcomes while maintaining academic quality and student engagement.",
            category=CaseStudyCategory.EDUCATIONAL,
            complexity=CaseStudyComplexity.ADVANCED,
            estimated_duration="4-5 hours",
            learning_objectives=[
                "Understand hybrid learning models and best practices",
                "Learn to design engaging online learning experiences",
                "Develop student support and engagement strategies",
                "Apply educational technology and assessment methodologies"
            ],
            problem_statement=ProblemStatement(
                title="Hybrid Learning Model Implementation",
                description="Implement a hybrid learning model that combines online and in-person instruction to improve accessibility and learning outcomes.",
                complexity=ProblemComplexity.COMPLEX,
                domain="Higher Education & Online Learning",
                stakeholders=[
                    "University Administration", "Faculty", "Students", "IT Department",
                    "Academic Support Services", "Accreditation Bodies", "Employers"
                ],
                constraints={
                    "budget": "$20M over 3 years",
                    "timeline": "3-year implementation plan",
                    "quality": "Must maintain academic quality and standards",
                    "accessibility": "Must ensure accessibility for all students"
                },
                success_criteria=[
                    "Implement hybrid learning in 80% of courses",
                    "Achieve 95% student satisfaction with hybrid model",
                    "Improve learning outcomes by 25%",
                    "Increase accessibility and enrollment by 30%",
                    "Maintain academic quality and accreditation"
                ]
            ),
            expected_outcomes=[
                "Hybrid learning model and framework",
                "Technology infrastructure and platform plan",
                "Faculty training and development program",
                "Student support and engagement strategy",
                "Assessment and quality assurance framework"
            ],
            key_insights=[
                "Hybrid learning requires careful design and planning",
                "Faculty training and support are essential for success",
                "Student engagement strategies must be adapted for online environments",
                "Technology should enhance, not replace, human interaction",
                "Assessment methods must be adapted for hybrid environments"
            ],
            resources_needed=[
                "Educational technology and platforms",
                "Faculty training and development resources",
                "Student support and engagement tools",
                "Assessment and evaluation systems",
                "IT infrastructure and support"
            ],
            success_metrics=[
                "Hybrid course implementation > 80%",
                "Student satisfaction > 95%",
                "Learning outcomes improvement > 25%",
                "Accessibility and enrollment increase > 30%",
                "Academic quality maintenance = 100%"
            ],
            tags=["online-learning", "hybrid-education", "educational-technology", "student-engagement", "accessibility"]
        )
    
    def get_template(self, template_id: str) -> Optional[CaseStudyTemplate]:
        """Get a specific case study template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: CaseStudyCategory) -> List[CaseStudyTemplate]:
        """Get all templates in a specific category"""
        return [template for template in self.templates.values() if template.category == category]
    
    def get_templates_by_complexity(self, complexity: CaseStudyComplexity) -> List[CaseStudyTemplate]:
        """Get all templates with a specific complexity level"""
        return [template for template in self.templates.values() if template.complexity == complexity]
    
    def get_templates_by_tags(self, tags: List[str]) -> List[CaseStudyTemplate]:
        """Get templates that match any of the specified tags"""
        matching_templates = []
        for template in self.templates.values():
            if any(tag in template.tags for tag in tags):
                matching_templates.append(template)
        return matching_templates
    
    def list_all_templates(self) -> List[CaseStudyTemplate]:
        """Get all available templates"""
        return list(self.templates.values())
    
    def search_templates(self, query: str) -> List[CaseStudyTemplate]:
        """Search templates by title, description, or tags"""
        query_lower = query.lower()
        matching_templates = []
        
        for template in self.templates.values():
            if (query_lower in template.title.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                matching_templates.append(template)
        
        return matching_templates
    
    def export_template(self, template_id: str) -> Dict[str, Any]:
        """Export a template as a dictionary for JSON serialization"""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        return {
            "id": template.id,
            "title": template.title,
            "description": template.description,
            "category": template.category.value,
            "complexity": template.complexity.value,
            "estimated_duration": template.estimated_duration,
            "learning_objectives": template.learning_objectives,
            "problem_statement": {
                "title": template.problem_statement.title,
                "description": template.problem_statement.description,
                "complexity": template.problem_statement.complexity.value,
                "domain": template.problem_statement.domain,
                "stakeholders": template.problem_statement.stakeholders,
                "constraints": template.problem_statement.constraints,
                "success_criteria": template.problem_statement.success_criteria
            },
            "expected_outcomes": template.expected_outcomes,
            "key_insights": template.key_insights,
            "resources_needed": template.resources_needed,
            "success_metrics": template.success_metrics,
            "tags": template.tags,
            "created_date": template.created_date.isoformat()
        }
    
    def export_all_templates(self) -> Dict[str, Any]:
        """Export all templates as a dictionary"""
        return {
            template_id: self.export_template(template_id)
            for template_id in self.templates.keys()
        }

# Demo function
def demo_case_study_templates():
    """Demonstrate the case study template library"""
    print("🌌 Agent Orchestrator Case Study Templates")
    print("=" * 60)
    
    # Create template library
    library = CaseStudyTemplateLibrary()
    
    print(f"Total templates available: {len(library.list_all_templates())}")
    print()
    
    # Show templates by category
    categories = [CaseStudyCategory.BUSINESS, CaseStudyCategory.PERSONAL, 
                  CaseStudyCategory.GLOBAL, CaseStudyCategory.TECHNICAL, 
                  CaseStudyCategory.EDUCATIONAL]
    
    for category in categories:
        templates = library.get_templates_by_category(category)
        print(f"📁 {category.value.upper()} Templates ({len(templates)}):")
        for template in templates:
            print(f"   • {template.title} ({template.complexity.value})")
        print()
    
    # Show a detailed example
    print("📋 Detailed Example - Digital Transformation:")
    print("-" * 50)
    template = library.get_template("business_digital_transformation")
    if template:
        print(f"Title: {template.title}")
        print(f"Category: {template.category.value}")
        print(f"Complexity: {template.complexity.value}")
        print(f"Duration: {template.estimated_duration}")
        print(f"Domain: {template.problem_statement.domain}")
        print(f"Stakeholders: {len(template.problem_statement.stakeholders)}")
        print(f"Success Criteria: {len(template.problem_statement.success_criteria)}")
        print(f"Key Insights: {len(template.key_insights)}")
        print(f"Tags: {', '.join(template.tags)}")
    
    print("\n🔍 Search Example - 'AI':")
    print("-" * 30)
    ai_templates = library.search_templates("AI")
    for template in ai_templates:
        print(f"   • {template.title} ({template.category.value})")
    
    print("\n✅ Case study template library ready for use!")

if __name__ == "__main__":
    demo_case_study_templates()
