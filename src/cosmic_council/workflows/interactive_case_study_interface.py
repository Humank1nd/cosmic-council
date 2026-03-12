"""
Interactive Case Study Interface
User-friendly interface for browsing, selecting, and customizing case studies
"""

import asyncio
from typing import Dict, Any, List, Optional
from case_study_templates import CaseStudyTemplateLibrary, CaseStudyTemplate, CaseStudyCategory, CaseStudyComplexity
from case_study_generator import CaseStudyGenerator, CaseStudyGenerationRequest, GeneratedCaseStudy
from src.core.types import ProblemStatement, ProblemComplexity

class InteractiveCaseStudyInterface:
    """Interactive interface for case study management"""
    
    def __init__(self):
        self.template_library = CaseStudyTemplateLibrary()
        self.generator = CaseStudyGenerator()
        self.current_session = None
    
    async def start_interactive_session(self):
        """Start an interactive case study session"""
        print("🌌 Agent Orchestrator Case Study Interface")
        print("=" * 60)
        print("Welcome to the interactive case study system!")
        print("You can browse templates, generate custom case studies, or create your own.")
        print()
        
        while True:
            print("\n📋 Main Menu:")
            print("1. Browse Case Study Templates")
            print("2. Generate Custom Case Study")
            print("3. Create New Case Study from Scratch")
            print("4. View Generated Case Studies")
            print("5. Search Case Studies")
            print("6. Export Case Study")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == "0":
                print("Thank you for using the Agent Orchestrator Case Study Interface! 🌌")
                break
            elif choice == "1":
                await self._browse_templates()
            elif choice == "2":
                await self._generate_custom_case_study()
            elif choice == "3":
                await self._create_from_scratch()
            elif choice == "4":
                await self._view_generated_studies()
            elif choice == "5":
                await self._search_case_studies()
            elif choice == "6":
                await self._export_case_study()
            else:
                print("Invalid choice. Please try again.")
    
    async def _browse_templates(self):
        """Browse available case study templates"""
        print("\n📁 Browse Case Study Templates")
        print("-" * 40)
        
        # Show categories
        categories = [CaseStudyCategory.BUSINESS, CaseStudyCategory.PERSONAL, 
                      CaseStudyCategory.GLOBAL, CaseStudyCategory.TECHNICAL, 
                      CaseStudyCategory.EDUCATIONAL]
        
        print("Available Categories:")
        for i, category in enumerate(categories, 1):
            templates = self.template_library.get_templates_by_category(category)
            print(f"  {i}. {category.value.title()} ({len(templates)} templates)")
        
        print("  6. Show All Templates")
        print("  0. Back to Main Menu")
        
        choice = input("\nSelect category (0-6): ").strip()
        
        if choice == "0":
            return
        elif choice == "6":
            await self._show_all_templates()
        elif choice.isdigit() and 1 <= int(choice) <= 5:
            category = categories[int(choice) - 1]
            await self._show_templates_by_category(category)
        else:
            print("Invalid choice.")
    
    async def _show_templates_by_category(self, category: CaseStudyCategory):
        """Show templates in a specific category"""
        templates = self.template_library.get_templates_by_category(category)
        
        print(f"\n📁 {category.value.title()} Templates")
        print("-" * 50)
        
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template.title}")
            print(f"   Complexity: {template.complexity.value}")
            print(f"   Duration: {template.estimated_duration}")
            print(f"   Domain: {template.problem_statement.domain}")
            print(f"   Stakeholders: {len(template.problem_statement.stakeholders)}")
            print()
        
        print("Enter template number to view details, or 0 to go back:")
        choice = input("Choice: ").strip()
        
        if choice == "0":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(templates):
            template = templates[int(choice) - 1]
            await self._show_template_details(template)
        else:
            print("Invalid choice.")
    
    async def _show_all_templates(self):
        """Show all available templates"""
        templates = self.template_library.list_all_templates()
        
        print(f"\n📁 All Templates ({len(templates)})")
        print("-" * 50)
        
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template.title}")
            print(f"   Category: {template.category.value}")
            print(f"   Complexity: {template.complexity.value}")
            print(f"   Duration: {template.estimated_duration}")
            print()
        
        print("Enter template number to view details, or 0 to go back:")
        choice = input("Choice: ").strip()
        
        if choice == "0":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(templates):
            template = templates[int(choice) - 1]
            await self._show_template_details(template)
        else:
            print("Invalid choice.")
    
    async def _show_template_details(self, template: CaseStudyTemplate):
        """Show detailed information about a template"""
        print(f"\n📋 {template.title}")
        print("=" * 60)
        print(f"Category: {template.category.value}")
        print(f"Complexity: {template.complexity.value}")
        print(f"Duration: {template.estimated_duration}")
        print(f"Domain: {template.problem_statement.domain}")
        print()
        
        print("Description:")
        print(template.description)
        print()
        
        print("Problem Statement:")
        print(f"  Title: {template.problem_statement.title}")
        print(f"  Complexity: {template.problem_statement.complexity.value}")
        print(f"  Stakeholders: {', '.join(template.problem_statement.stakeholders)}")
        print()
        
        print("Constraints:")
        for key, value in template.problem_statement.constraints.items():
            print(f"  {key}: {value}")
        print()
        
        print("Success Criteria:")
        for i, criterion in enumerate(template.problem_statement.success_criteria, 1):
            print(f"  {i}. {criterion}")
        print()
        
        print("Learning Objectives:")
        for i, objective in enumerate(template.learning_objectives, 1):
            print(f"  {i}. {objective}")
        print()
        
        print("Expected Outcomes:")
        for i, outcome in enumerate(template.expected_outcomes, 1):
            print(f"  {i}. {outcome}")
        print()
        
        print("Key Insights:")
        for i, insight in enumerate(template.key_insights, 1):
            print(f"  {i}. {insight}")
        print()
        
        print("Resources Needed:")
        for i, resource in enumerate(template.resources_needed, 1):
            print(f"  {i}. {resource}")
        print()
        
        print("Success Metrics:")
        for i, metric in enumerate(template.success_metrics, 1):
            print(f"  {i}. {metric}")
        print()
        
        print("Tags:")
        print(f"  {', '.join(template.tags)}")
        print()
        
        print("Options:")
        print("1. Use this template as-is")
        print("2. Customize this template")
        print("3. Generate similar case study")
        print("0. Back to templates")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            await self._use_template_as_is(template)
        elif choice == "2":
            await self._customize_template(template)
        elif choice == "3":
            await self._generate_similar_case_study(template)
        elif choice == "0":
            return
        else:
            print("Invalid choice.")
    
    async def _use_template_as_is(self, template: CaseStudyTemplate):
        """Use a template as-is"""
        print(f"\n✅ Using template: {template.title}")
        print("This template is ready to use for your problem-solving workflow.")
        print("You can now proceed with the Agent Orchestrator workflow using this case study.")
        print()
        
        # Here you would integrate with the workflow system
        print("🚀 Ready to start the Agent Orchestrator workflow with this case study!")
        input("Press Enter to continue...")
    
    async def _customize_template(self, template: CaseStudyTemplate):
        """Customize a template"""
        print(f"\n🔧 Customizing template: {template.title}")
        print("You can modify various aspects of this template to better fit your needs.")
        print()
        
        # Get customization inputs
        new_title = input(f"Title (current: {template.title}): ").strip() or template.title
        new_description = input(f"Description (current: {template.description[:100]}...): ").strip() or template.description
        
        print("\nStakeholders (current):")
        for i, stakeholder in enumerate(template.problem_statement.stakeholders, 1):
            print(f"  {i}. {stakeholder}")
        
        print("\nEnter new stakeholders (one per line, press Enter twice when done):")
        new_stakeholders = []
        while True:
            stakeholder = input()
            if stakeholder.strip() == '' and new_stakeholders:
                break
            if stakeholder.strip():
                new_stakeholders.append(stakeholder.strip())
        
        if not new_stakeholders:
            new_stakeholders = template.problem_statement.stakeholders
        
        # Create generation request
        request = CaseStudyGenerationRequest(
            category=template.category,
            complexity=template.complexity,
            domain=template.problem_statement.domain,
            title=new_title,
            description=new_description,
            stakeholders=new_stakeholders,
            constraints=template.problem_statement.constraints,
            success_criteria=template.problem_statement.success_criteria,
            custom_requirements={"tags": template.tags}
        )
        
        # Generate customized case study
        print("\n🔄 Generating customized case study...")
        case_study = self.generator.generate_case_study(request)
        
        print("✅ Customized case study generated!")
        print(f"ID: {case_study.id}")
        print(f"Title: {case_study.title}")
        print(f"Stakeholders: {len(case_study.problem_statement.stakeholders)}")
        
        input("Press Enter to continue...")
    
    async def _generate_similar_case_study(self, template: CaseStudyTemplate):
        """Generate a similar case study based on a template"""
        print(f"\n🔄 Generating similar case study to: {template.title}")
        print("This will create a new case study with similar characteristics but different details.")
        print()
        
        # Get basic customization
        new_title = input("New title: ").strip()
        new_domain = input(f"Domain (current: {template.problem_statement.domain}): ").strip() or template.problem_statement.domain
        
        # Create generation request
        request = CaseStudyGenerationRequest(
            category=template.category,
            complexity=template.complexity,
            domain=new_domain,
            title=new_title,
            description=f"Similar to {template.title} but adapted for {new_domain}",
            stakeholders=template.problem_statement.stakeholders,
            constraints=template.problem_statement.constraints,
            success_criteria=template.problem_statement.success_criteria,
            custom_requirements={"tags": template.tags}
        )
        
        # Generate similar case study
        print("\n🔄 Generating similar case study...")
        case_study = self.generator.generate_case_study(request)
        
        print("✅ Similar case study generated!")
        print(f"ID: {case_study.id}")
        print(f"Title: {case_study.title}")
        print(f"Base Template: {template.title}")
        
        input("Press Enter to continue...")
    
    async def _generate_custom_case_study(self):
        """Generate a completely custom case study"""
        print("\n🔄 Generate Custom Case Study")
        print("-" * 40)
        
        # Get basic information
        title = input("Case study title: ").strip()
        description = input("Description: ").strip()
        
        # Get category
        print("\nCategories:")
        categories = [CaseStudyCategory.BUSINESS, CaseStudyCategory.PERSONAL, 
                      CaseStudyCategory.GLOBAL, CaseStudyCategory.TECHNICAL, 
                      CaseStudyCategory.EDUCATIONAL]
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category.value.title()}")
        
        category_choice = input("Select category (1-5): ").strip()
        if not category_choice.isdigit() or not 1 <= int(category_choice) <= 5:
            print("Invalid choice.")
            return
        
        category = categories[int(category_choice) - 1]
        
        # Get complexity
        print("\nComplexity levels:")
        complexities = [CaseStudyComplexity.BEGINNER, CaseStudyComplexity.INTERMEDIATE, 
                        CaseStudyComplexity.ADVANCED, CaseStudyComplexity.EXPERT]
        for i, complexity in enumerate(complexities, 1):
            print(f"  {i}. {complexity.value.title()}")
        
        complexity_choice = input("Select complexity (1-4): ").strip()
        if not complexity_choice.isdigit() or not 1 <= int(complexity_choice) <= 4:
            print("Invalid choice.")
            return
        
        complexity = complexities[int(complexity_choice) - 1]
        
        # Get domain
        domain = input("Domain/Industry: ").strip()
        
        # Get stakeholders
        print("\nStakeholders (one per line, press Enter twice when done):")
        stakeholders = []
        while True:
            stakeholder = input()
            if stakeholder.strip() == '' and stakeholders:
                break
            if stakeholder.strip():
                stakeholders.append(stakeholder.strip())
        
        # Get constraints
        print("\nConstraints (one per line, press Enter twice when done):")
        constraints = {}
        while True:
            constraint = input()
            if constraint.strip() == '' and constraints:
                break
            if constraint.strip():
                key, value = constraint.split(':', 1) if ':' in constraint else (constraint, "Specified")
                constraints[key.strip()] = value.strip()
        
        # Get success criteria
        print("\nSuccess criteria (one per line, press Enter twice when done):")
        success_criteria = []
        while True:
            criterion = input()
            if criterion.strip() == '' and success_criteria:
                break
            if criterion.strip():
                success_criteria.append(criterion.strip())
        
        # Create generation request
        request = CaseStudyGenerationRequest(
            category=category,
            complexity=complexity,
            domain=domain,
            title=title,
            description=description,
            stakeholders=stakeholders,
            constraints=constraints,
            success_criteria=success_criteria
        )
        
        # Generate case study
        print("\n🔄 Generating custom case study...")
        case_study = self.generator.generate_case_study(request)
        
        print("✅ Custom case study generated!")
        print(f"ID: {case_study.id}")
        print(f"Title: {case_study.title}")
        print(f"Category: {case_study.category.value}")
        print(f"Complexity: {case_study.complexity.value}")
        print(f"Duration: {case_study.estimated_duration}")
        
        input("Press Enter to continue...")
    
    async def _create_from_scratch(self):
        """Create a case study from scratch"""
        print("\n🆕 Create Case Study from Scratch")
        print("-" * 40)
        print("This will guide you through creating a completely new case study.")
        print("Note: This is similar to generating a custom case study but with more guidance.")
        print()
        
        # Use the same flow as generate_custom_case_study
        await self._generate_custom_case_study()
    
    async def _view_generated_studies(self):
        """View all generated case studies"""
        generated_studies = self.generator.list_generated_case_studies()
        
        if not generated_studies:
            print("\n📁 No generated case studies found.")
            print("Generate some case studies first!")
            input("Press Enter to continue...")
            return
        
        print(f"\n📁 Generated Case Studies ({len(generated_studies)})")
        print("-" * 50)
        
        for i, case_study in enumerate(generated_studies, 1):
            print(f"{i}. {case_study.title}")
            print(f"   Category: {case_study.category.value}")
            print(f"   Complexity: {case_study.complexity.value}")
            print(f"   Generated: {case_study.generated_date.strftime('%Y-%m-%d %H:%M')}")
            print()
        
        print("Enter case study number to view details, or 0 to go back:")
        choice = input("Choice: ").strip()
        
        if choice == "0":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(generated_studies):
            case_study = generated_studies[int(choice) - 1]
            await self._show_generated_case_study_details(case_study)
        else:
            print("Invalid choice.")
    
    async def _show_generated_case_study_details(self, case_study: GeneratedCaseStudy):
        """Show details of a generated case study"""
        print(f"\n📋 {case_study.title}")
        print("=" * 60)
        print(f"ID: {case_study.id}")
        print(f"Category: {case_study.category.value}")
        print(f"Complexity: {case_study.complexity.value}")
        print(f"Duration: {case_study.estimated_duration}")
        print(f"Generated: {case_study.generated_date.strftime('%Y-%m-%d %H:%M')}")
        if case_study.base_template_id:
            print(f"Based on template: {case_study.base_template_id}")
        print()
        
        print("Description:")
        print(case_study.description)
        print()
        
        print("Problem Statement:")
        print(f"  Domain: {case_study.problem_statement.domain}")
        print(f"  Complexity: {case_study.problem_statement.complexity.value}")
        print(f"  Stakeholders: {', '.join(case_study.problem_statement.stakeholders)}")
        print()
        
        print("Constraints:")
        for key, value in case_study.problem_statement.constraints.items():
            print(f"  {key}: {value}")
        print()
        
        print("Success Criteria:")
        for i, criterion in enumerate(case_study.problem_statement.success_criteria, 1):
            print(f"  {i}. {criterion}")
        print()
        
        print("Learning Objectives:")
        for i, objective in enumerate(case_study.learning_objectives, 1):
            print(f"  {i}. {objective}")
        print()
        
        print("Expected Outcomes:")
        for i, outcome in enumerate(case_study.expected_outcomes, 1):
            print(f"  {i}. {outcome}")
        print()
        
        print("Key Insights:")
        for i, insight in enumerate(case_study.key_insights, 1):
            print(f"  {i}. {insight}")
        print()
        
        print("Resources Needed:")
        for i, resource in enumerate(case_study.resources_needed, 1):
            print(f"  {i}. {resource}")
        print()
        
        print("Success Metrics:")
        for i, metric in enumerate(case_study.success_metrics, 1):
            print(f"  {i}. {metric}")
        print()
        
        print("Tags:")
        print(f"  {', '.join(case_study.tags)}")
        print()
        
        print("Options:")
        print("1. Use this case study")
        print("2. Export this case study")
        print("3. Modify this case study")
        print("0. Back to generated studies")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            await self._use_generated_case_study(case_study)
        elif choice == "2":
            await self._export_specific_case_study(case_study)
        elif choice == "3":
            await self._modify_generated_case_study(case_study)
        elif choice == "0":
            return
        else:
            print("Invalid choice.")
    
    async def _use_generated_case_study(self, case_study: GeneratedCaseStudy):
        """Use a generated case study"""
        print(f"\n✅ Using case study: {case_study.title}")
        print("This case study is ready to use for your problem-solving workflow.")
        print("You can now proceed with the Agent Orchestrator workflow using this case study.")
        print()
        
        # Here you would integrate with the workflow system
        print("🚀 Ready to start the Agent Orchestrator workflow with this case study!")
        input("Press Enter to continue...")
    
    async def _export_specific_case_study(self, case_study: GeneratedCaseStudy):
        """Export a specific case study"""
        print(f"\n📤 Exporting case study: {case_study.title}")
        
        export_data = self.generator.export_case_study(case_study.id)
        
        # Save to file
        filename = f"case_study_{case_study.id[:8]}.json"
        import json
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Case study exported to: {filename}")
        input("Press Enter to continue...")
    
    async def _modify_generated_case_study(self, case_study: GeneratedCaseStudy):
        """Modify a generated case study"""
        print(f"\n🔧 Modifying case study: {case_study.title}")
        print("This feature would allow you to modify the generated case study.")
        print("For now, you can generate a new similar case study with different parameters.")
        print()
        
        # This would be implemented to allow modification of existing case studies
        print("Modification feature coming soon!")
        input("Press Enter to continue...")
    
    async def _search_case_studies(self):
        """Search case studies"""
        print("\n🔍 Search Case Studies")
        print("-" * 30)
        
        query = input("Enter search term: ").strip()
        
        if not query:
            print("No search term provided.")
            return
        
        # Search templates
        template_results = self.template_library.search_templates(query)
        
        # Search generated studies
        generated_results = []
        for case_study in self.generator.list_generated_case_studies():
            if (query.lower() in case_study.title.lower() or
                query.lower() in case_study.description.lower() or
                any(query.lower() in tag.lower() for tag in case_study.tags)):
                generated_results.append(case_study)
        
        print(f"\n📊 Search Results for '{query}':")
        print(f"Templates: {len(template_results)}")
        print(f"Generated: {len(generated_results)}")
        print()
        
        if template_results:
            print("📁 Template Results:")
            for i, template in enumerate(template_results, 1):
                print(f"  {i}. {template.title} ({template.category.value})")
            print()
        
        if generated_results:
            print("🔄 Generated Results:")
            for i, case_study in enumerate(generated_results, 1):
                print(f"  {i}. {case_study.title} ({case_study.category.value})")
            print()
        
        if not template_results and not generated_results:
            print("No results found.")
        
        input("Press Enter to continue...")
    
    async def _export_case_study(self):
        """Export case study"""
        print("\n📤 Export Case Study")
        print("-" * 30)
        
        print("1. Export template")
        print("2. Export generated case study")
        print("0. Back to main menu")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            await self._export_template()
        elif choice == "2":
            await self._export_generated_study()
        elif choice == "0":
            return
        else:
            print("Invalid choice.")
    
    async def _export_template(self):
        """Export a template"""
        print("\n📤 Export Template")
        print("-" * 30)
        
        templates = self.template_library.list_all_templates()
        
        print("Available templates:")
        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template.title}")
        
        choice = input("\nSelect template to export (0 to cancel): ").strip()
        
        if choice == "0":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(templates):
            template = templates[int(choice) - 1]
            export_data = self.template_library.export_template(template.id)
            
            filename = f"template_{template.id}.json"
            import json
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Template exported to: {filename}")
        else:
            print("Invalid choice.")
        
        input("Press Enter to continue...")
    
    async def _export_generated_study(self):
        """Export a generated case study"""
        print("\n📤 Export Generated Case Study")
        print("-" * 30)
        
        generated_studies = self.generator.list_generated_case_studies()
        
        if not generated_studies:
            print("No generated case studies found.")
            input("Press Enter to continue...")
            return
        
        print("Available generated case studies:")
        for i, case_study in enumerate(generated_studies, 1):
            print(f"  {i}. {case_study.title}")
        
        choice = input("\nSelect case study to export (0 to cancel): ").strip()
        
        if choice == "0":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(generated_studies):
            case_study = generated_studies[int(choice) - 1]
            await self._export_specific_case_study(case_study)
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

# Demo function
async def demo_interactive_interface():
    """Demonstrate the interactive case study interface"""
    interface = InteractiveCaseStudyInterface()
    await interface.start_interactive_session()

if __name__ == "__main__":
    asyncio.run(demo_interactive_interface())
