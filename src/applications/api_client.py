"""
Cosmic Council API Client
Python client for interacting with the Cosmic Council REST API
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CosmicCouncilAPIClient:
    """Client for interacting with the Cosmic Council API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API server
            api_key: API key for authentication (optional for demo)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = response_data.get('message', 'Unknown error')
                    raise APIException(f"API Error {response.status}: {error_msg}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            raise APIException(f"Network error: {str(e)}")
    
    # Health and Status
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return await self._make_request("GET", "/health")
    
    async def get_api_info(self) -> Dict[str, Any]:
        """Get API information"""
        return await self._make_request("GET", "/")
    
    # Problem Management
    
    async def create_problem(
        self,
        title: str,
        description: str,
        domain: str,
        complexity: str,
        priority: str = "medium",
        stakeholders: List[str] = None,
        constraints: Dict[str, Any] = None,
        success_criteria: List[str] = None,
        due_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create a new problem"""
        data = {
            "title": title,
            "description": description,
            "domain": domain,
            "complexity": complexity,
            "priority": priority,
            "stakeholders": stakeholders or [],
            "constraints": constraints or {},
            "success_criteria": success_criteria or []
        }
        
        if due_date:
            data["due_date"] = due_date.isoformat()
        
        return await self._make_request("POST", "/api/v1/problems", data=data)
    
    async def get_problems(
        self,
        domain: Optional[str] = None,
        complexity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get problems with filtering"""
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if domain:
            params["domain"] = domain
        if complexity:
            params["complexity"] = complexity
        if status:
            params["status"] = status
        
        return await self._make_request("GET", "/api/v1/problems", params=params)
    
    async def get_problem(self, problem_id: str) -> Dict[str, Any]:
        """Get a specific problem by ID"""
        return await self._make_request("GET", f"/api/v1/problems/{problem_id}")
    
    async def update_problem(
        self,
        problem_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        domain: Optional[str] = None,
        complexity: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Update a problem"""
        data = {}
        
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if domain is not None:
            data["domain"] = domain
        if complexity is not None:
            data["complexity"] = complexity
        if priority is not None:
            data["priority"] = priority
        if status is not None:
            data["status"] = status
        if due_date is not None:
            data["due_date"] = due_date.isoformat()
        
        return await self._make_request("PUT", f"/api/v1/problems/{problem_id}", data=data)
    
    # Cycle Management
    
    async def create_cycle(
        self,
        problem_id: str,
        cycle_number: int,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Create a new cycle"""
        data = {
            "problem_id": problem_id,
            "cycle_number": cycle_number,
            "max_iterations": max_iterations
        }
        
        return await self._make_request("POST", "/api/v1/cycles", data=data)
    
    async def get_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """Get a specific cycle by ID"""
        return await self._make_request("GET", f"/api/v1/cycles/{cycle_id}")
    
    async def execute_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """Execute a cycle (start problem-solving process)"""
        return await self._make_request("POST", f"/api/v1/cycles/{cycle_id}/execute")
    
    # Solution Management
    
    async def create_solution(
        self,
        problem_id: str,
        cycle_id: str,
        title: str,
        description: str,
        approach: Optional[str] = None,
        confidence_score: Optional[float] = None,
        feasibility_score: Optional[float] = None,
        impact_score: Optional[float] = None,
        estimated_cost: Optional[float] = None,
        estimated_duration: Optional[int] = None,
        risk_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new solution"""
        data = {
            "problem_id": problem_id,
            "cycle_id": cycle_id,
            "title": title,
            "description": description
        }
        
        if approach is not None:
            data["approach"] = approach
        if confidence_score is not None:
            data["confidence_score"] = confidence_score
        if feasibility_score is not None:
            data["feasibility_score"] = feasibility_score
        if impact_score is not None:
            data["impact_score"] = impact_score
        if estimated_cost is not None:
            data["estimated_cost"] = estimated_cost
        if estimated_duration is not None:
            data["estimated_duration"] = estimated_duration
        if risk_level is not None:
            data["risk_level"] = risk_level
        
        return await self._make_request("POST", "/api/v1/solutions", data=data)
    
    async def get_solutions(
        self,
        problem_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get solutions with filtering"""
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if problem_id:
            params["problem_id"] = problem_id
        if cycle_id:
            params["cycle_id"] = cycle_id
        
        return await self._make_request("GET", "/api/v1/solutions", params=params)
    
    # Analytics
    
    async def get_problem_analytics(self) -> Dict[str, Any]:
        """Get problem analytics and statistics"""
        return await self._make_request("GET", "/api/v1/analytics/problems")
    
    async def get_cycle_analytics(self) -> Dict[str, Any]:
        """Get cycle analytics and statistics"""
        return await self._make_request("GET", "/api/v1/analytics/cycles")
    
    async def get_solution_analytics(self) -> Dict[str, Any]:
        """Get solution analytics and statistics"""
        return await self._make_request("GET", "/api/v1/analytics/solutions")
    
    # Enterprises
    
    async def get_enterprises(self) -> Dict[str, Any]:
        """Get all enterprises"""
        return await self._make_request("GET", "/api/v1/supra_enterprise")
    
    # Perpetual Thinking System
    
    async def create_perpetual_session(
        self,
        session_name: str,
        initial_input: str,
        mode: str = "collaborative",
        goals: List[str] = None,
        success_criteria: List[str] = None,
        ai_enhancement_level: str = "enhanced",
        ai_learning_enabled: bool = True,
        ai_adaptation_enabled: bool = True,
        ai_breakthrough_detection: bool = True
    ) -> Dict[str, Any]:
        """Create a new perpetual thinking session"""
        data = {
            "session_name": session_name,
            "initial_input": initial_input,
            "mode": mode,
            "goals": goals or [],
            "success_criteria": success_criteria or [],
            "ai_enhancement_level": ai_enhancement_level,
            "ai_learning_enabled": ai_learning_enabled,
            "ai_adaptation_enabled": ai_adaptation_enabled,
            "ai_breakthrough_detection": ai_breakthrough_detection
        }
        return await self._make_request("POST", "/api/v1/perpetual/sessions", data=data)
    
    async def get_perpetual_sessions(self) -> Dict[str, Any]:
        """Get all perpetual thinking sessions"""
        return await self._make_request("GET", "/api/v1/perpetual/sessions")
    
    async def get_perpetual_session(self, session_id: str) -> Dict[str, Any]:
        """Get a specific perpetual thinking session"""
        return await self._make_request("GET", f"/api/v1/perpetual/sessions/{session_id}")
    
    async def pause_perpetual_session(self, session_id: str) -> Dict[str, Any]:
        """Pause a perpetual thinking session"""
        return await self._make_request("POST", f"/api/v1/perpetual/sessions/{session_id}/pause")
    
    async def stop_perpetual_session(self, session_id: str) -> Dict[str, Any]:
        """Stop a perpetual thinking session"""
        return await self._make_request("POST", f"/api/v1/perpetual/sessions/{session_id}/stop")
    
    async def get_perpetual_system_status(self) -> Dict[str, Any]:
        """Get perpetual thinking system status"""
        return await self._make_request("GET", "/api/v1/perpetual/status")
    
    # AI-Enhanced Perpetual Thinking
    
    async def get_ai_sessions(self, ai_enhancement_level: Optional[str] = None) -> Dict[str, Any]:
        """Get AI-enhanced perpetual thinking sessions"""
        params = {}
        if ai_enhancement_level:
            params["ai_enhancement_level"] = ai_enhancement_level
        return await self._make_request("GET", "/api/v1/perpetual/ai/sessions", params=params)
    
    async def get_ai_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for an AI-enhanced perpetual session"""
        return await self._make_request("GET", f"/api/v1/perpetual/ai/sessions/{session_id}/analytics")
    
    async def get_ai_enhanced_cycle_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of the current AI-enhanced cycle for a session"""
        return await self._make_request("GET", f"/api/v1/perpetual/ai/sessions/{session_id}/status")

class APIException(Exception):
    """Exception raised for API errors"""
    pass

# Demo and Testing Functions

async def demo_api_client():
    """Demonstrate API client usage"""
    print("🌐 Cosmic Council API Client Demo")
    print("=" * 60)
    
    async with CosmicCouncilAPIClient() as client:
        try:
            # Check API health
            print("🔍 Checking API Health...")
            health = await client.health_check()
            print(f"   Status: {'✅ Healthy' if health['success'] else '❌ Unhealthy'}")
            if health['data']:
                print(f"   Database: {'✅' if health['data'].get('database') else '❌'}")
                print(f"   Workflow Engine: {'✅' if health['data'].get('workflow_engine') else '❌'}")
                print(f"   AI Integration: {'✅' if health['data'].get('ai_integration') else '❌'}")
            print()
            
            # Get API info
            print("📋 Getting API Information...")
            info = await client.get_api_info()
            print(f"   Version: {info['data']['version']}")
            print(f"   Description: {info['data']['description']}")
            print()
            
            # Get enterprises
            print("🏢 Getting Enterprises...")
            enterprises = await client.get_enterprises()
            if enterprises['success']:
                enterprise_list = enterprises['data']['enterprises']
                print(f"   Found {len(enterprise_list)} enterprises:")
                for enterprise in enterprise_list:
                    print(f"     • {enterprise['name']} ({enterprise['type']})")
            print()
            
            # Create a problem
            print("📋 Creating a Problem...")
            problem = await client.create_problem(
                title="API Demo Problem",
                description="A demonstration problem created via API client",
                domain="API Testing",
                complexity="moderate",
                priority="medium",
                stakeholders=["API Tester", "System Administrator"],
                constraints={"time_limit": "1 hour", "resources": "limited"},
                success_criteria=["API works correctly", "Data is stored properly"]
            )
            
            if problem['success']:
                problem_id = problem['data']['problem_id']
                print(f"   ✅ Problem created: {problem_id}")
                print(f"   Title: {problem['data']['title']}")
                print(f"   Domain: {problem['data']['domain']}")
                print()
                
                # Get the problem
                print("📖 Retrieving Problem...")
                retrieved_problem = await client.get_problem(problem_id)
                if retrieved_problem['success']:
                    problem_data = retrieved_problem['data']['problem']
                    print(f"   ✅ Problem retrieved successfully")
                    print(f"   Description: {problem_data['description'][:100]}...")
                    print(f"   Stakeholders: {problem_data['stakeholder_count']}")
                    print(f"   Constraints: {problem_data['constraint_count']}")
                    print()
                
                # Create a cycle
                print("🔄 Creating a Cycle...")
                cycle = await client.create_cycle(
                    problem_id=problem_id,
                    cycle_number=1,
                    max_iterations=3
                )
                
                if cycle['success']:
                    cycle_id = cycle['data']['cycle_id']
                    print(f"   ✅ Cycle created: {cycle_id}")
                    print(f"   Cycle Number: {cycle['data']['cycle_number']}")
                    print(f"   Status: {cycle['data']['status']}")
                    print()
                    
                    # Execute the cycle
                    print("🚀 Executing Cycle...")
                    execution = await client.execute_cycle(cycle_id)
                    if execution['success']:
                        print(f"   ✅ Cycle execution started")
                        print(f"   Status: {execution['data']['status']}")
                        print(f"   Message: {execution['data']['message']}")
                        print()
                    
                    # Create a solution
                    print("💡 Creating a Solution...")
                    solution = await client.create_solution(
                        problem_id=problem_id,
                        cycle_id=cycle_id,
                        title="API Demo Solution",
                        description="A demonstration solution created via API client",
                        approach="Systematic API testing approach",
                        confidence_score=0.85,
                        feasibility_score=0.90,
                        impact_score=0.80,
                        estimated_cost=10000.0,
                        estimated_duration=30,
                        risk_level="low"
                    )
                    
                    if solution['success']:
                        solution_id = solution['data']['solution_id']
                        print(f"   ✅ Solution created: {solution_id}")
                        print(f"   Title: {solution['data']['title']}")
                        print(f"   Confidence: {solution['data']['confidence_score']}")
                        print(f"   Feasibility: {solution['data']['feasibility_score']}")
                        print()
                
                # Get analytics
                print("📊 Getting Analytics...")
                
                # Problem analytics
                problem_analytics = await client.get_problem_analytics()
                if problem_analytics['success']:
                    stats = problem_analytics['data']
                    print(f"   Problem Statistics:")
                    print(f"     Total Problems: {stats.get('total_problems', 0)}")
                    print(f"     By Complexity: {stats.get('by_complexity', {})}")
                    print(f"     By Status: {stats.get('by_status', {})}")
                
                # Cycle analytics
                cycle_analytics = await client.get_cycle_analytics()
                if cycle_analytics['success']:
                    stats = cycle_analytics['data']
                    print(f"   Cycle Statistics:")
                    print(f"     Total Cycles: {stats.get('total_cycles', 0)}")
                    print(f"     By Status: {stats.get('by_status', {})}")
                    print(f"     Average Duration: {stats.get('average_duration', 0):.2f}s")
                
                # Solution analytics
                solution_analytics = await client.get_solution_analytics()
                if solution_analytics['success']:
                    stats = solution_analytics['data']
                    print(f"   Solution Statistics:")
                    print(f"     Total Solutions: {stats.get('total_solutions', 0)}")
                    print(f"     By Status: {stats.get('by_status', {})}")
                    print(f"     Average Confidence: {stats.get('average_confidence', 0):.2f}")
                print()
            
            print("✅ API Client demonstration completed successfully!")
            
        except APIException as e:
            print(f"❌ API Error: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

async def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing API Endpoints")
    print("=" * 60)
    
    async with CosmicCouncilAPIClient() as client:
        endpoints_tested = 0
        endpoints_passed = 0
        
        # Test health endpoint
        try:
            await client.health_check()
            print("✅ Health check endpoint")
            endpoints_passed += 1
        except Exception as e:
            print(f"❌ Health check endpoint: {str(e)}")
        endpoints_tested += 1
        
        # Test API info endpoint
        try:
            await client.get_api_info()
            print("✅ API info endpoint")
            endpoints_passed += 1
        except Exception as e:
            print(f"❌ API info endpoint: {str(e)}")
        endpoints_tested += 1
        
        # Test enterprises endpoint
        try:
            await client.get_enterprises()
            print("✅ Enterprises endpoint")
            endpoints_passed += 1
        except Exception as e:
            print(f"❌ Enterprises endpoint: {str(e)}")
        endpoints_tested += 1
        
        # Test analytics endpoints
        try:
            await client.get_problem_analytics()
            print("✅ Problem analytics endpoint")
            endpoints_passed += 1
        except Exception as e:
            print(f"❌ Problem analytics endpoint: {str(e)}")
        endpoints_tested += 1
        
        try:
            await client.get_cycle_analytics()
            print("✅ Cycle analytics endpoint")
            endpoints_passed += 1
        except Exception as e:
            print(f"❌ Cycle analytics endpoint: {str(e)}")
        endpoints_tested += 1
        
        try:
            await client.get_solution_analytics()
            print("✅ Solution analytics endpoint")
            endpoints_passed += 1
        except Exception as e:
            print(f"❌ Solution analytics endpoint: {str(e)}")
        endpoints_tested += 1
        
        print(f"\n📊 Test Results: {endpoints_passed}/{endpoints_tested} endpoints passed")
        print(f"Success Rate: {(endpoints_passed/endpoints_tested)*100:.1f}%")

if __name__ == "__main__":
    print("🌐 Cosmic Council API Client")
    print("Choose an option:")
    print("1. Demo API Client")
    print("2. Test API Endpoints")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(demo_api_client())
    elif choice == "2":
        asyncio.run(test_api_endpoints())
    else:
        print("Invalid choice. Running demo...")
        asyncio.run(demo_api_client())
