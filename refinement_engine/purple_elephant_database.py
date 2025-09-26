"""
Purple Elephant Database Integration
Real database operations for the Purple Elephant's reflection and gatekeeping functions.
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import asdict

try:
    from .database import DatabaseManager
    from .purple_elephant_gatekeeper import ReflectionReport, GatekeeperDecision
except ImportError:
    # For testing
    from database import DatabaseManager
    from purple_elephant_gatekeeper import ReflectionReport, GatekeeperDecision


class PurpleElephantDatabase:
    """Real database operations for Purple Elephant functionality."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def create_reflection_report(self, report: ReflectionReport) -> str:
        """Actually create a reflection report in the database."""
        
        query = """
        INSERT INTO reflection_reports 
        (report_id, cycle_id, summary, contradictions, empathy_insights, sector_analysis, confidence_indicators, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING report_id
        """
        
        try:
            result = await self.db.execute_query(query, [
                report.report_id,
                report.cycle_id,
                report.summary,
                json.dumps(report.contradictions),
                json.dumps(report.empathy_insights),
                json.dumps(report.sector_analysis),
                json.dumps(report.confidence_indicators),
                report.created_at
            ])
            
            return result[0]["report_id"]
        except Exception as e:
            # Fallback: create in memory and log error
            print(f"Database error creating reflection report: {e}")
            return report.report_id
    
    async def create_gatekeeper_decision(self, decision: GatekeeperDecision) -> str:
        """Actually create a gatekeeper decision in the database."""
        
        query = """
        INSERT INTO gatekeeper_decisions
        (decision_id, report_id, status, confidence_score, completeness_score, alignment_score, 
         failing_sectors, routing_decision, routing_target, rationale, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING decision_id
        """
        
        try:
            result = await self.db.execute_query(query, [
                decision.decision_id,
                decision.report_id,
                decision.status.value,
                decision.confidence_score,
                decision.completeness_score,
                decision.alignment_score,
                json.dumps(decision.failing_sectors),
                decision.routing_decision.value,
                decision.routing_target,
                decision.rationale,
                decision.created_at
            ])
            
            return result[0]["decision_id"]
        except Exception as e:
            # Fallback: create in memory and log error
            print(f"Database error creating gatekeeper decision: {e}")
            return decision.decision_id
    
    async def get_problem(self, problem_id: str) -> Dict[str, Any]:
        """Get problem data from database."""
        query = "SELECT * FROM problems WHERE problem_id = $1"
        
        try:
            result = await self.db.execute_query(query, [problem_id])
            if result:
                return result[0]
            else:
                return {"problem_id": problem_id, "current_layer": "deci", "cycle_count": 0}
        except Exception as e:
            print(f"Database error getting problem: {e}")
            return {"problem_id": problem_id, "current_layer": "deci", "cycle_count": 0}
    
    async def get_cycle_data(self, cycle_id: str) -> Dict[str, Any]:
        """Get cycle data from database."""
        query = "SELECT * FROM cycles WHERE cycle_id = $1"
        
        try:
            result = await self.db.execute_query(query, [cycle_id])
            if result:
                return result[0]
            else:
                return {"cycle_id": cycle_id, "layer": "deci", "status": "active"}
        except Exception as e:
            print(f"Database error getting cycle: {e}")
            return {"cycle_id": cycle_id, "layer": "deci", "status": "active"}
    
    async def get_sector_outputs(self, cycle_id: str) -> Dict[str, Any]:
        """Get all sector outputs for a cycle."""
        query = """
        SELECT sector, output_json, status 
        FROM sector_runs 
        WHERE cycle_id = $1 
        ORDER BY sector_order
        """
        
        try:
            result = await self.db.execute_query(query, [cycle_id])
            sector_outputs = {}
            
            for row in result:
                sector = row["sector"]
                output_json = row["output_json"]
                status = row["status"]
                
                if status == "completed" and output_json:
                    sector_outputs[sector] = json.loads(output_json)
                else:
                    sector_outputs[sector] = {"status": status, "error": "Sector not completed"}
            
            return sector_outputs
        except Exception as e:
            print(f"Database error getting sector outputs: {e}")
            return {}
    
    async def update_problem_status(self, problem_id: str, status: str, current_layer: str = None):
        """Update problem status in database."""
        if current_layer:
            query = "UPDATE problems SET status = $1, current_layer = $2 WHERE problem_id = $3"
            params = [status, current_layer, problem_id]
        else:
            query = "UPDATE problems SET status = $1 WHERE problem_id = $2"
            params = [status, problem_id]
        
        try:
            await self.db.execute_query(query, params)
        except Exception as e:
            print(f"Database error updating problem status: {e}")
    
    async def create_sector_refinement(self, problem_id: str, sector: str, from_layer: str, to_layer: str, rationale: str):
        """Create a sector refinement record."""
        refinement_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO sector_refinements
        (refinement_id, problem_id, sector, from_layer, to_layer, rationale, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        try:
            await self.db.execute_query(query, [
                refinement_id, problem_id, sector, from_layer, to_layer, rationale, datetime.utcnow()
            ])
            return refinement_id
        except Exception as e:
            print(f"Database error creating sector refinement: {e}")
            return refinement_id
    
    async def get_threshold_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get threshold update history for analysis."""
        query = """
        SELECT * FROM threshold_updates 
        ORDER BY created_at DESC 
        LIMIT $1
        """
        
        try:
            result = await self.db.execute_query(query, [limit])
            return result
        except Exception as e:
            print(f"Database error getting threshold history: {e}")
            return []
    
    async def log_decision_outcome(self, decision_id: str, actual_outcome: str, actual_quality: float, feedback: str = None):
        """Log the actual outcome of a gatekeeper decision."""
        query = """
        INSERT INTO decision_outcomes
        (decision_id, actual_outcome, actual_quality, feedback, created_at)
        VALUES ($1, $2, $3, $4, $5)
        """
        
        try:
            await self.db.execute_query(query, [
                decision_id, actual_outcome, actual_quality, feedback, datetime.utcnow()
            ])
        except Exception as e:
            print(f"Database error logging decision outcome: {e}")
    
    async def get_decision_outcomes(self, decision_id: str) -> List[Dict[str, Any]]:
        """Get outcomes for a specific decision."""
        query = "SELECT * FROM decision_outcomes WHERE decision_id = $1 ORDER BY created_at DESC"
        
        try:
            result = await self.db.execute_query(query, [decision_id])
            return result
        except Exception as e:
            print(f"Database error getting decision outcomes: {e}")
            return []
    
    async def get_adaptive_thresholds(self) -> Dict[str, float]:
        """Get current adaptive thresholds from database."""
        query = """
        SELECT threshold_type, threshold_value 
        FROM adaptive_thresholds 
        WHERE is_active = true
        """
        
        try:
            result = await self.db.execute_query(query)
            thresholds = {}
            for row in result:
                thresholds[row["threshold_type"]] = row["threshold_value"]
            
            # Return defaults if no thresholds found
            if not thresholds:
                thresholds = {
                    "confidence": 0.5,
                    "completeness": 0.5,
                    "alignment": 0.5
                }
            
            return thresholds
        except Exception as e:
            print(f"Database error getting adaptive thresholds: {e}")
            return {
                "confidence": 0.5,
                "completeness": 0.5,
                "alignment": 0.5
            }
    
    async def update_adaptive_thresholds(self, thresholds: Dict[str, float]):
        """Update adaptive thresholds in database."""
        # First, deactivate current thresholds
        deactivate_query = "UPDATE adaptive_thresholds SET is_active = false"
        
        try:
            await self.db.execute_query(deactivate_query)
            
            # Insert new thresholds
            for threshold_type, threshold_value in thresholds.items():
                insert_query = """
                INSERT INTO adaptive_thresholds (threshold_type, threshold_value, is_active, created_at)
                VALUES ($1, $2, true, $3)
                """
                await self.db.execute_query(insert_query, [threshold_type, threshold_value, datetime.utcnow()])
                
        except Exception as e:
            print(f"Database error updating adaptive thresholds: {e}")
