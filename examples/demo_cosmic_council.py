"""
Cosmic Council Framework Demo
Demonstrates the hexagonal problem-solving system
"""

import asyncio
from src.cosmic_council import (
    CosmicCouncil, ProblemStatement, ProblemComplexity, 
    EnterpriseType, CycleStatus
)
from src.cosmic_council.core.core import EnhancedCosmicCouncil

async def demo_business_problem():
    """Demo: Business case study - New Product Development"""
    print("=== Business Case Study: New Product Development ===")
    
    problem = ProblemStatement(
        title="Sustainable Product Launch",
        description="Launch a new sustainable product that addresses consumer needs while maintaining profitability and environmental responsibility.",
        complexity=ProblemComplexity.COMPLEX,
        domain="Product Development & Marketing",
        stakeholders=["Product Team", "Marketing", "Finance", "Customers", "Environmental Groups"],
        constraints={"budget": "$500K", "timeline": "6 months", "sustainability_requirements": "high"},
        success_criteria=["Market adoption > 10K units", "Positive ROI", "Environmental certification"]
    )
    
    council = CosmicCouncil()
    result = await council.solve_problem(problem)
    
    print(f"Problem: {result.problem.title}")
    print(f"Status: {result.status.value}")
    print(f"Overall Confidence: {result.overall_confidence:.2f}")
    
    print("\nEnterprise Processing Results:")
    for enterprise_type, enterprise_result in result.enterprise_results.items():
        enterprise_name = enterprise_result.enterprise.value.replace('_', ' ').title()
        print(f"  {enterprise_name}: {enterprise_result.status} (Confidence: {enterprise_result.confidence_score:.2f})")
    
    print(f"\nFinal Recommendation: {result.final_synthesis.get('recommendation', 'N/A')}")
    print(f"Timeline: {result.final_synthesis.get('implementation_plan', {}).get('timeline', 'N/A')}")

async def demo_personal_problem():
    """Demo: Personal case study - Career Transition"""
    print("\n=== Personal Case Study: Career Transition ===")
    
    problem = ProblemStatement(
        title="Career Change to Tech Industry",
        description="Transition from current career to technology industry, acquiring necessary skills and finding suitable opportunities.",
        complexity=ProblemComplexity.MODERATE,
        domain="Personal Development & Career Planning",
        stakeholders=["Self", "Family", "Mentors", "Potential Employers", "Professional Network"],
        constraints={"time_available": "20 hours/week", "budget": "$5K", "timeline": "12 months"},
        success_criteria=["Land tech job", "Salary increase > 20%", "Work-life balance maintained"]
    )
    
    council = CosmicCouncil()
    result = await council.solve_problem(problem)
    
    print(f"Problem: {result.problem.title}")
    print(f"Status: {result.status.value}")
    print(f"Overall Confidence: {result.overall_confidence:.2f}")
    
    print("\nKey Recommendations by Enterprise:")
    for enterprise_type, enterprise_result in result.enterprise_results.items():
        enterprise_name = enterprise_result.enterprise.value.replace('_', ' ').title()
        if enterprise_result.recommendations:
            print(f"  {enterprise_name}: {enterprise_result.recommendations[0]}")

async def demo_global_problem():
    """Demo: Global issue case study - Climate Change"""
    print("\n=== Global Issue Case Study: Climate Change Mitigation ===")
    
    problem = ProblemStatement(
        title="Community Climate Action Plan",
        description="Develop and implement a comprehensive climate action plan for a mid-sized city to reduce carbon emissions and build climate resilience.",
        complexity=ProblemComplexity.SYSTEMIC,
        domain="Environmental Policy & Urban Planning",
        stakeholders=["City Government", "Residents", "Businesses", "Environmental Groups", "Utilities", "Transportation Authority"],
        constraints={"budget": "$10M", "timeline": "5 years", "regulatory_compliance": "required"},
        success_criteria=["40% emission reduction", "Community engagement > 70%", "Economic benefits maintained"]
    )
    
    council = CosmicCouncil()
    result = await council.solve_problem(problem)
    
    print(f"Problem: {result.problem.title}")
    print(f"Status: {result.status.value}")
    print(f"Overall Confidence: {result.overall_confidence:.2f}")
    
    print("\nImplementation Plan:")
    implementation_plan = result.final_synthesis.get('implementation_plan', {})
    print(f"  Phases: {', '.join(implementation_plan.get('phases', []))}")
    print(f"  Timeline: {implementation_plan.get('timeline', 'N/A')}")
    print(f"  Success Metrics: {', '.join(implementation_plan.get('success_metrics', []))}")
    
    print("\nRisk Mitigation:")
    risk_mitigation = result.final_synthesis.get('risk_mitigation', {})
    print(f"  Identified Risks: {', '.join(risk_mitigation.get('identified_risks', []))}")
    print(f"  Mitigation Strategies: {', '.join(risk_mitigation.get('mitigation_strategies', []))}")

async def demo_enterprise_info():
    """Demo: Display enterprise information"""
    print("\n=== Cosmic Council Enterprise Information ===")
    
    council = CosmicCouncil()
    enterprise_info = council.get_enterprise_info()
    processing_order = council.get_processing_order()
    
    print("Processing Order:")
    for i, enterprise in enumerate(processing_order, 1):
        info = enterprise_info[enterprise]
        print(f"  {i}. {info['name']} ({info['animal']}) - {info['principle']}")
    
    print("\nEnterprise Details:")
    for enterprise, info in enterprise_info.items():
        print(f"\n{info['name']}:")
        print(f"  Animal Symbol: {info['animal']}")
        print(f"  Core Principle: {info['principle']}")
        print(f"  Role: {info['role']}")
        print(f"  Color: {info['color']}")

async def main():
    """Run all demos"""
    print("Cosmic Council Framework Demonstration")
    print("=" * 50)
    
    # Show enterprise information first
    await demo_enterprise_info()
    
    # Run the three case study demos
    await demo_business_problem()
    await demo_personal_problem()
    await demo_global_problem()
    
    print("\n" + "=" * 50)
    print("Demo completed! The Cosmic Council framework successfully")
    print("processed problems through all six enterprises:")
    print("Red Owl → Orange Orangutan → Yellow Honeybee →")
    print("Green Tortoise → Blue Dolphin → Purple Elephant")
    print("with feedback loops for continuous improvement.")

if __name__ == "__main__":
    asyncio.run(main())
