"""
Airtable + Make.com Synchronization Orchestrator.
Implements recursive iterative loops and automated data flow between the six totem databases.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone

from ..utils.integrations import AirtableClient, MakeClient

logger = logging.getLogger(__name__)

class TotemDatabase(Enum):
    RESEARCH = "Research_RedOwl"
    STRATEGY = "Strategy_OrangeOrangutan"
    DEVELOPMENT = "Development_YellowHoneybee"
    RESOURCES = "Resources_GreenTurtle"
    COMMUNICATION = "Communication_BlueDolphin"
    REFLECTION = "Reflection_PurpleElephant"

class AirtableMakeOrchestrator:
    """
    Orchestrates the dynamic data flow across 6 Airtable Totem Databases.
    
    Features:
    - Recursive Iterative Loops: Completed improvements trigger new research.
    - Automated Handoffs: Data moves between databases via Make.com triggers.
    - Historical Cross-Referencing: Dynamically links past insights to new cycles.
    - Intelligent Data Transfer: Filters and forwards only high-impact insights.
    """

    def __init__(self, airtable: AirtableClient, make: MakeClient):
        self.airtable = airtable
        self.make = make

    async def sync_stage_result(self, stage: str, result_data: Dict[str, Any], cycle_id: str):
        """
        Syncs a stage result to its dedicated Airtable database and triggers the next step.
        Implements Intelligent Data Transfer (Goal 2.2).
        """
        totem_db = self._map_stage_to_db(stage)
        logger.info(f"🔄 Syncing {stage} result to {totem_db.value}")

        # Intelligent Filter: Forward only high-scoring insights (Goal 2.2)
        filtered_payload = self._filter_high_impact_data(result_data)

        # 1. Upsert to Airtable
        record = {
            "Cycle_ID": cycle_id,
            "Timestamp": datetime.now(timezone.utc).isoformat(),
            "Payload": filtered_payload,
            "Status": "Completed",
            "Resonance_Score": result_data.get("confidence_score", 0.0)
        }
        await self.airtable.upsert_record(totem_db.value, record)

        # 2. Trigger Make.com for downstream automation
        await self.make.trigger_scenario(
            scenario_id=f"sync_{stage.lower()}_downstream",
            data={"cycle_id": cycle_id, "totem": stage, "high_impact_summary": str(filtered_payload)[:500]}
        )

        # 3. Check for "Insight Required" flag (Goal 2.1)
        if result_data.get("status") == "insight_required" or result_data.get("needs_refinement"):
            await self.trigger_retroactive_feedback(result_data, cycle_id)

    async def trigger_retroactive_feedback(self, improvement_data: Dict[str, Any], original_cycle_id: str):
        """
        Implements the 'Loop Back' logic where Reflection (Purple) influences Research (Red).
        Automates self-adjusting workflows (Goal 2.1).
        """
        logger.info(f"🔙 Triggering retroactive feedback loop for cycle {original_cycle_id}")
        
        # Automatically generate new Research Query in Red Owl DB
        new_research_query = {
            "Parent_Cycle_ID": original_cycle_id,
            "Query_Text": improvement_data.get("next_cycle_focus", "Refine based on previous feedback"),
            "Priority": "High",
            "Type": "Iterative_Refinement",
            "Source_Totem": improvement_data.get("enterprise", "Support")
        }
        
        await self.airtable.upsert_record(TotemDatabase.RESEARCH.value, new_research_query)
        
        # Notify Make.com to start a new automated cycle
        await self.make.trigger_scenario(
            scenario_id="start_iterative_refinement",
            data={"original_cycle_id": original_cycle_id, "focus": new_research_query["Query_Text"]}
        )

    async def archive_cycle_insights(self, cycle_results: List[Dict[str, Any]], problem_id: str):
        """
        Ensures previous iterations are preserved and cross-referenced (Goal 2.4).
        """
        logger.info(f"📦 Archiving insights for problem {problem_id}")
        
        for result in cycle_results:
            archive_record = {
                "Problem_ID": problem_id,
                "Cycle_ID": result.get("cycle_id"),
                "Totem": result.get("enterprise"),
                "Key_Insights": result.get("insights", []),
                "Final_Status": result.get("status"),
                "Archived_At": datetime.now(timezone.utc).isoformat(),
                "Tags": self._generate_insight_tags(result)
            }
            # Upsert to a dedicated Cross-Cycle Reference Table
            await self.airtable.upsert_record("Cross_Cycle_References", archive_record)

    def _filter_high_impact_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts only the highest scoring insights/hypotheses."""
        # Simplified filtering logic: extract top 3 items if they are lists
        filtered = {}
        for k, v in data.items():
            if isinstance(v, list) and len(v) > 3:
                filtered[k] = v[:3] # Forwards only top 3
            else:
                filtered[k] = v
        return filtered

    def _generate_insight_tags(self, result: Dict[str, Any]) -> List[str]:
        """Generates tags for easier cross-referencing."""
        tags = [result.get("enterprise", "Unknown")]
        if result.get("overall_confidence", 0) > 0.8:
            tags.append("High_Confidence")
        if result.get("status") == "completed":
            tags.append("Success")
        return tags

    def _map_stage_to_db(self, stage: str) -> TotemDatabase:
        mapping = {
            "research": TotemDatabase.RESEARCH,
            "planning": TotemDatabase.STRATEGY,
            "development": TotemDatabase.DEVELOPMENT,
            "budget": TotemDatabase.RESOURCES,
            "market": TotemDatabase.COMMUNICATION,
            "support": TotemDatabase.REFLECTION
        }
        return mapping.get(stage.lower(), TotemDatabase.RESEARCH)

from enum import Enum
