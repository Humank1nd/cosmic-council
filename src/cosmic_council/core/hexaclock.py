"""
Hexaclock: Self-Regulating, Multi-Concept Orchestration Layer
A digital Chief Strategy Officer (CSO) that maximizes viability and minimizes capital risk while plugging into any AI model.

The Hexaclock is the Executive Operating System that coordinates the 6-stage R&D cycle across the Agent Orchestrator supercharger supply chain:
1. Oracle (Red Owl) - Market Research
2. Interpreter (Orange Orangutan) - Data Translation
3. Auditor (Yellow Honeybee) - Verification (Primary)
4. Alchemist (Green Tortoise) - Prototype Generation
5. Auditor (Yellow Honeybee) - Light Verification (Secondary)
6. Gatekeeper (Blue Dolphin) - Budget Validation
7. Recalibration (Purple Elephant) - Loop Optimization (if needed)
"""

import asyncio
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any

from ..integrations.llm_provider import BaseLLMProvider
from ..agents.hierarchical_enterprise import HierarchicalOrchestrator, EnterpriseOperation

logger = logging.getLogger(__name__)


class HexaclockStage(Enum):
    """The 6 stages of the Hexaclock cycle"""
    ORACLE = "oracle"                    # Red Owl - Market Research
    INTERPRETER = "interpreter"           # Orange Orangutan - Data Translation
    AUDITOR_PRIMARY = "auditor_primary"   # Yellow Honeybee - Full Verification
    ALCHEMIST = "alchemist"               # Green Tortoise - Prototype Generation
    AUDITOR_SECONDARY = "auditor_secondary"  # Yellow Honeybee - Light Verification
    GATEKEEPER = "gatekeeper"             # Blue Dolphin - Budget Validation
    RECALIBRATION = "recalibration"        # Purple Elephant - Loop Optimization


class ConceptStatus(Enum):
    """Status of a concept in the Hexaclock"""
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    RECALIBRATING = "recalibrating"
    ARCHIVED = "archived"  # After 5 failed recalibrations


@dataclass
class StageReport:
    """Report from a stage execution"""
    stage: HexaclockStage
    timestamp: datetime
    action_taken: str
    resources_consumed: Dict[str, Any]
    processing_time: float
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailureReport:
    """Report when a concept is rejected by Gatekeeper"""
    concept_id: str
    rejection_reason: str
    failed_budget_variables: Dict[str, Any]
    roi_shortfall: Optional[float] = None
    viability_confidence_score: float = 0.0
    stage_history: List[StageReport] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class HexaPacket:
    """
    The atomic data object that flows through the Hexaclock stages.
    Contains all validated data, prototype drafts, and financial variables.
    """
    concept_id: str
    current_stage: HexaclockStage
    validated_data: Dict[str, Any] = field(default_factory=dict)
    prototype_draft: Optional[Dict[str, Any]] = None
    financial_variables: Dict[str, Any] = field(default_factory=dict)
    stage_reports: List[StageReport] = field(default_factory=list)
    digital_signature: Optional[str] = None
    recalibration_count: int = 0
    failure_reports: List[FailureReport] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_stage_report(self, report: StageReport):
        """Add a stage report and update digital signature"""
        self.stage_reports.append(report)
        self.updated_at = datetime.now(timezone.utc)
        self._update_signature()
    
    def _update_signature(self):
        """Update digital signature for chain-of-custody"""
        # Create hash of all packet contents
        packet_data = {
            "concept_id": self.concept_id,
            "validated_data": self.validated_data,
            "prototype_draft": self.prototype_draft,
            "financial_variables": self.financial_variables,
            "stage_reports": [
                {
                    "stage": r.stage.value,
                    "timestamp": r.timestamp.isoformat(),
                    "action": r.action_taken
                }
                for r in self.stage_reports
            ]
        }
        packet_json = json.dumps(packet_data, sort_keys=True)
        self.digital_signature = hashlib.sha256(packet_json.encode()).hexdigest()
    
    def verify_signature(self) -> bool:
        """Verify the packet's integrity"""
        if not self.digital_signature:
            return False
        old_signature = self.digital_signature
        self._update_signature()
        is_valid = self.digital_signature == old_signature
        self.digital_signature = old_signature  # Restore original
        return is_valid


@dataclass
class ConceptResult:
    """Final result of a concept through the Hexaclock"""
    concept_id: str
    status: ConceptStatus
    viability_confidence_score: float
    final_prototype: Optional[Dict[str, Any]] = None
    approved_budget: Optional[Dict[str, Any]] = None
    total_processing_time: float = 0.0
    total_recalibrations: int = 0
    stage_history: List[StageReport] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TemplateEquatter:
    """
    Generative Transformation Function (GTF)
    Maps validated data onto Business Model Canvases (BMCs)
    """
    
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider
        self.logger = logging.getLogger(__name__)
        # Pre-loaded Business Model Templates
        self.templates = {
            "enterprise_saas": {
                "target_market_size": 1000000,
                "revenue_model": "subscription",
                "pricing_tier": "enterprise"
            },
            "niche_service": {
                "target_market_size": 10000,
                "revenue_model": "service_fee",
                "pricing_tier": "niche"
            },
            "marketplace": {
                "target_market_size": 500000,
                "revenue_model": "commission",
                "pricing_tier": "marketplace"
            }
        }
    
    async def generate_prototype(
        self,
        validated_data: Dict[str, Any],
        financial_variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a theoretical business prototype using template equatters.
        
        Args:
            validated_data: Validated data from Auditor
            financial_variables: Financial variables from previous stages
            
        Returns:
            Complete business prototype with BMC filled in
        """
        # Determine which template to use
        market_size = validated_data.get("target_market_size", 0)
        
        if market_size > 1000000:
            template = self.templates["enterprise_saas"]
        elif market_size > 10000:
            template = self.templates["marketplace"]
        else:
            template = self.templates["niche_service"]
        
        # Use LLM to generate prototype if available
        if self.llm_provider:
            prompt = f"""
            Generate a complete business model prototype based on:
            
            Validated Data: {validated_data}
            Financial Variables: {financial_variables}
            Template Type: {template}
            
            Create a detailed business model canvas including:
            1. Value Proposition
            2. Customer Segments
            3. Revenue Streams
            4. Cost Structure
            5. Key Partnerships
            6. Key Activities
            7. Key Resources
            8. Channels
            9. Customer Relationships
            """
            
            from ..integrations.llm_provider import LLMRequest, LLMMessage
            
            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content="You are a business model generation expert."),
                    LLMMessage(role="user", content=prompt)
                ],
                temperature=0.7
            )
            
            response = await self.llm_provider.generate(request)
            
            # Parse and structure the response
            prototype = {
                "template_type": list(self.templates.keys())[list(self.templates.values()).index(template)],
                "business_model": response.content,
                "validated_data": validated_data,
                "financial_variables": financial_variables,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Fallback: basic prototype structure
            prototype = {
                "template_type": list(self.templates.keys())[list(self.templates.values()).index(template)],
                "business_model": "Basic prototype structure",
                "validated_data": validated_data,
                "financial_variables": financial_variables
            }
        
        return prototype


class HexaclockOrchestrator:
    """
    The Executive Operating System for the Hexaclock.
    Coordinates the 6-stage R&D cycle with the hierarchical agent system and the six-enterprise supply chain supercharger.
    """
    
    def __init__(
        self,
        coordinator_llm: BaseLLMProvider,
        hierarchical_orchestrator: HierarchicalOrchestrator,
        max_recalibrations: int = 5,
        min_viability_score: float = 0.95
    ):
        """
        Initialize the Hexaclock Orchestrator.
        
        Args:
            coordinator_llm: Large model for coordination
            hierarchical_orchestrator: The hierarchical agent system
            max_recalibrations: Maximum recalibration loops before archiving
            min_viability_score: Minimum Viability Confidence Score (VCS) for approval
        """
        self.coordinator_llm = coordinator_llm
        self.hierarchical_orchestrator = hierarchical_orchestrator
        self.max_recalibrations = max_recalibrations
        self.min_viability_score = min_viability_score
        self.template_equatter = TemplateEquatter(coordinator_llm)
        self.logger = logging.getLogger(__name__)
        
        # Active concepts being processed
        self.active_concepts: Dict[str, HexaPacket] = {}
        
        # Completed concepts
        self.completed_concepts: Dict[str, ConceptResult] = {}
        
        # Stage execution handlers
        self.stage_handlers = {
            HexaclockStage.ORACLE: self._execute_oracle,
            HexaclockStage.INTERPRETER: self._execute_interpreter,
            HexaclockStage.AUDITOR_PRIMARY: self._execute_auditor_primary,
            HexaclockStage.ALCHEMIST: self._execute_alchemist,
            HexaclockStage.AUDITOR_SECONDARY: self._execute_auditor_secondary,
            HexaclockStage.GATEKEEPER: self._execute_gatekeeper,
            HexaclockStage.RECALIBRATION: self._execute_recalibration
        }
    
    async def process_concept(
        self,
        initial_query: str,
        concept_id: Optional[str] = None,
        failure_report: Optional[FailureReport] = None
    ) -> ConceptResult:
        """
        Process a concept through the complete Hexaclock cycle.
        
        Args:
            initial_query: Initial market research query or concept
            concept_id: Optional concept ID (generated if not provided)
            failure_report: Optional failure report from previous attempt
            
        Returns:
            ConceptResult with final status
        """
        if not concept_id:
            concept_id = str(uuid.uuid4())
        
        # Create initial Hexa-Packet
        packet = HexaPacket(
            concept_id=concept_id,
            current_stage=HexaclockStage.ORACLE,
            metadata={"initial_query": initial_query}
        )
        
        if failure_report:
            packet.failure_reports.append(failure_report)
            packet.recalibration_count = failure_report.stage_history[-1].metadata.get("recalibration_count", 0) + 1
            packet.metadata["targeted_search"] = failure_report.rejection_reason
        
        self.active_concepts[concept_id] = packet
        start_time = datetime.now(timezone.utc)
        
        try:
            # Execute stages sequentially
            stages = [
                HexaclockStage.ORACLE,
                HexaclockStage.INTERPRETER,
                HexaclockStage.AUDITOR_PRIMARY,
                HexaclockStage.ALCHEMIST,
                HexaclockStage.AUDITOR_SECONDARY,
                HexaclockStage.GATEKEEPER
            ]
            
            for stage in stages:
                packet.current_stage = stage
                self.logger.info(f"🕐 Hexaclock Stage {stage.value} for concept {concept_id}")
                
                # Execute stage
                stage_result = await self.stage_handlers[stage](packet, initial_query)
                
                if not stage_result:
                    # Stage failed, check if we should recalibrate
                    if packet.recalibration_count < self.max_recalibrations:
                        await self._execute_recalibration(packet, initial_query)
                        # Restart from Oracle
                        continue
                    else:
                        # Archive concept
                        return self._archive_concept(packet, "Max recalibrations exceeded")
                
                # Check if Gatekeeper approved
                if stage == HexaclockStage.GATEKEEPER:
                    if stage_result.metadata.get("approved", False):
                        # Success!
                        return self._finalize_concept(packet, start_time, ConceptStatus.APPROVED)
                    else:
                        # Rejected - recalibrate if possible
                        if packet.recalibration_count < self.max_recalibrations:
                            await self._execute_recalibration(packet, initial_query)
                            # Restart cycle
                            continue
                        else:
                            return self._archive_concept(packet, "Budget rejected after max recalibrations")
            
            # Should not reach here, but handle gracefully
            return self._finalize_concept(packet, start_time, ConceptStatus.REJECTED)
            
        except Exception as e:
            self.logger.error(f"Error processing concept {concept_id}: {e}")
            return self._finalize_concept(packet, start_time, ConceptStatus.REJECTED)
        finally:
            if concept_id in self.active_concepts:
                del self.active_concepts[concept_id]
    
    async def _execute_oracle(
        self,
        packet: HexaPacket,
        query: str
    ) -> Optional[StageReport]:
        """Execute Oracle stage (Red Owl - Market Research)"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Use hierarchical orchestrator to route to Red Owl enterprise
            result = await self.hierarchical_orchestrator.process_problem(
                problem_id=packet.concept_id,
                problem_description=query if not packet.metadata.get("targeted_search") else packet.metadata["targeted_search"],
                input_data={
                    "stage": "oracle",
                    "failure_report": packet.failure_reports[-1].__dict__ if packet.failure_reports else None
                }
            )
            
            # Extract Red Owl results
            red_owl_result = result.get("red_owl", {})
            
            # Update packet with research data
            packet.validated_data["market_research"] = red_owl_result
            
            report = StageReport(
                stage=HexaclockStage.ORACLE,
                timestamp=datetime.now(timezone.utc),
                action_taken="Market research and data acquisition",
                resources_consumed={"api_calls": 1, "data_sources": len(red_owl_result.get("sources", []))},
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                confidence_score=red_owl_result.get("confidence", 0.8),
                metadata={"sources": red_owl_result.get("sources", [])}
            )
            
            packet.add_stage_report(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Oracle stage failed: {e}")
            return None
    
    async def _execute_interpreter(
        self,
        packet: HexaPacket,
        query: str
    ) -> Optional[StageReport]:
        """Execute Interpreter stage (Orange Orangutan - Data Translation)"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Route to Orange Orangutan enterprise
            result = await self.hierarchical_orchestrator.process_problem(
                problem_id=packet.concept_id,
                problem_description="Translate market research into structured business formats",
                input_data={
                    "stage": "interpreter",
                    "market_research": packet.validated_data.get("market_research", {})
                }
            )
            
            orange_result = result.get("orange_orangutan", {})
            
            # Update packet with interpreted data
            packet.validated_data["structured_data"] = orange_result
            
            report = StageReport(
                stage=HexaclockStage.INTERPRETER,
                timestamp=datetime.now(timezone.utc),
                action_taken="Data translation and organization",
                resources_consumed={"llm_tokens": orange_result.get("tokens_used", 0)},
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                confidence_score=orange_result.get("confidence", 0.85),
                metadata={"formats_generated": orange_result.get("formats", [])}
            )
            
            packet.add_stage_report(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Interpreter stage failed: {e}")
            return None
    
    async def _execute_auditor_primary(
        self,
        packet: HexaPacket,
        query: str
    ) -> Optional[StageReport]:
        """Execute Primary Auditor stage (Yellow Honeybee - Full Verification)"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Route to Yellow Honeybee for full verification
            result = await self.hierarchical_orchestrator.process_problem(
                problem_id=packet.concept_id,
                problem_description="Perform full cross-consistency verification",
                input_data={
                    "stage": "auditor_primary",
                    "structured_data": packet.validated_data.get("structured_data", {}),
                    "verification_type": "full"
                }
            )
            
            yellow_result = result.get("yellow_honeybee", {})
            
            # Update packet with verified data
            packet.validated_data["verified_data"] = yellow_result
            
            report = StageReport(
                stage=HexaclockStage.AUDITOR_PRIMARY,
                timestamp=datetime.now(timezone.utc),
                action_taken="Full cross-consistency verification",
                resources_consumed={
                    "external_apis": yellow_result.get("external_checks", 0),
                    "verification_sources": yellow_result.get("sources_checked", [])
                },
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                confidence_score=yellow_result.get("verification_confidence", 0.9),
                metadata={"verification_passed": yellow_result.get("passed", True)}
            )
            
            packet.add_stage_report(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Primary Auditor stage failed: {e}")
            return None
    
    async def _execute_alchemist(
        self,
        packet: HexaPacket,
        query: str
    ) -> Optional[StageReport]:
        """Execute Alchemist stage (Green Tortoise - Prototype Generation)"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Generate prototype using Template Equatter
            prototype = await self.template_equatter.generate_prototype(
                validated_data=packet.validated_data.get("verified_data", {}),
                financial_variables=packet.financial_variables
            )
            
            # Also route to Green Tortoise for additional processing
            result = await self.hierarchical_orchestrator.process_problem(
                problem_id=packet.concept_id,
                problem_description="Generate business prototype from verified data",
                input_data={
                    "stage": "alchemist",
                    "verified_data": packet.validated_data.get("verified_data", {}),
                    "prototype_draft": prototype
                }
            )
            
            green_result = result.get("green_tortoise", {})
            
            # Update packet with prototype
            packet.prototype_draft = {
                **prototype,
                **green_result
            }
            
            report = StageReport(
                stage=HexaclockStage.ALCHEMIST,
                timestamp=datetime.now(timezone.utc),
                action_taken="Prototype generation using template equatters",
                resources_consumed={"templates_applied": 1},
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                confidence_score=green_result.get("prototype_confidence", 0.85),
                metadata={"template_type": prototype.get("template_type")}
            )
            
            packet.add_stage_report(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Alchemist stage failed: {e}")
            return None
    
    async def _execute_auditor_secondary(
        self,
        packet: HexaPacket,
        query: str
    ) -> Optional[StageReport]:
        """Execute Secondary Auditor stage (Yellow Honeybee - Light Verification)"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Route to Yellow Honeybee for light semantic check
            result = await self.hierarchical_orchestrator.process_problem(
                problem_id=packet.concept_id,
                problem_description="Perform light semantic verification of prototype",
                input_data={
                    "stage": "auditor_secondary",
                    "prototype": packet.prototype_draft,
                    "verified_data": packet.validated_data.get("verified_data", {}),
                    "verification_type": "light"
                }
            )
            
            yellow_result = result.get("yellow_honeybee", {})
            
            report = StageReport(
                stage=HexaclockStage.AUDITOR_SECONDARY,
                timestamp=datetime.now(timezone.utc),
                action_taken="Light semantic verification",
                resources_consumed={"semantic_checks": 1},
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                confidence_score=yellow_result.get("semantic_confidence", 0.9),
                metadata={"semantic_consistency": yellow_result.get("consistent", True)}
            )
            
            packet.add_stage_report(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Secondary Auditor stage failed: {e}")
            return None
    
    async def _execute_gatekeeper(
        self,
        packet: HexaPacket,
        query: str
    ) -> Optional[StageReport]:
        """Execute Gatekeeper stage (Blue Dolphin - Budget Validation)"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Route to Blue Dolphin for budget validation
            result = await self.hierarchical_orchestrator.process_problem(
                problem_id=packet.concept_id,
                problem_description="Validate budget and financial feasibility",
                input_data={
                    "stage": "gatekeeper",
                    "prototype": packet.prototype_draft,
                    "verified_data": packet.validated_data.get("verified_data", {})
                }
            )
            
            blue_result = result.get("blue_dolphin", {})
            
            # Calculate Viability Confidence Score (VCS)
            auditor_confidence = packet.stage_reports[-2].confidence_score if len(packet.stage_reports) >= 2 else 0.9
            financial_confidence = blue_result.get("financial_confidence", 0.8)
            vcs = (auditor_confidence + financial_confidence) / 2
            
            # Update financial variables
            packet.financial_variables = blue_result.get("budget", {})
            
            approved = (
                blue_result.get("approved", False) and
                vcs >= self.min_viability_score and
                blue_result.get("roi", 0) > 0
            )
            
            report = StageReport(
                stage=HexaclockStage.GATEKEEPER,
                timestamp=datetime.now(timezone.utc),
                action_taken="Budget validation and feasibility analysis",
                resources_consumed={"financial_models": 1},
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                confidence_score=vcs,
                metadata={
                    "approved": approved,
                    "roi": blue_result.get("roi", 0),
                    "budget": blue_result.get("budget", {}),
                    "rejection_reason": None if approved else blue_result.get("rejection_reason", "ROI below threshold")
                }
            )
            
            packet.add_stage_report(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Gatekeeper stage failed: {e}")
            return None
    
    async def _execute_recalibration(
        self,
        packet: HexaPacket,
        query: str
    ) -> Optional[StageReport]:
        """Execute Recalibration stage (Purple Elephant - Loop Optimization)"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get last gatekeeper report
            gatekeeper_report = next(
                (r for r in reversed(packet.stage_reports) if r.stage == HexaclockStage.GATEKEEPER),
                None
            )
            
            if not gatekeeper_report:
                return None
            
            # Create failure report
            failure_report = FailureReport(
                concept_id=packet.concept_id,
                rejection_reason=gatekeeper_report.metadata.get("rejection_reason", "Unknown"),
                failed_budget_variables=packet.financial_variables,
                roi_shortfall=gatekeeper_report.metadata.get("roi", 0),
                viability_confidence_score=gatekeeper_report.confidence_score,
                stage_history=packet.stage_reports.copy()
            )
            
            packet.failure_reports.append(failure_report)
            
            # Route to Purple Elephant for recalibration
            result = await self.hierarchical_orchestrator.process_problem(
                problem_id=packet.concept_id,
                problem_description="Optimize and recalibrate based on failure",
                input_data={
                    "stage": "recalibration",
                    "failure_report": failure_report.__dict__,
                    "recalibration_count": packet.recalibration_count
                }
            )
            
            purple_result = result.get("purple_elephant", {})
            
            # Update metadata for targeted search
            packet.metadata["targeted_search"] = purple_result.get("optimized_query", query)
            
            report = StageReport(
                stage=HexaclockStage.RECALIBRATION,
                timestamp=datetime.now(timezone.utc),
                action_taken="Recalibration and loop optimization",
                resources_consumed={"optimization_cycles": 1},
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                confidence_score=purple_result.get("optimization_confidence", 0.8),
                metadata={
                    "recalibration_count": packet.recalibration_count,
                    "optimized_query": purple_result.get("optimized_query")
                }
            )
            
            packet.add_stage_report(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Recalibration stage failed: {e}")
            return None
    
    def _finalize_concept(
        self,
        packet: HexaPacket,
        start_time: datetime,
        status: ConceptStatus
    ) -> ConceptResult:
        """Finalize a concept and create result"""
        total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Get final VCS from last gatekeeper report if approved
        vcs = 0.0
        if status == ConceptStatus.APPROVED:
            gatekeeper_report = next(
                (r for r in reversed(packet.stage_reports) if r.stage == HexaclockStage.GATEKEEPER),
                None
            )
            if gatekeeper_report:
                vcs = gatekeeper_report.confidence_score
        
        result = ConceptResult(
            concept_id=packet.concept_id,
            status=status,
            viability_confidence_score=vcs,
            final_prototype=packet.prototype_draft if status == ConceptStatus.APPROVED else None,
            approved_budget=packet.financial_variables if status == ConceptStatus.APPROVED else None,
            total_processing_time=total_time,
            total_recalibrations=packet.recalibration_count,
            stage_history=packet.stage_reports.copy()
        )
        
        self.completed_concepts[packet.concept_id] = result
        return result
    
    def _archive_concept(
        self,
        packet: HexaPacket,
        reason: str
    ) -> ConceptResult:
        """Archive a concept that failed after max recalibrations"""
        return ConceptResult(
            concept_id=packet.concept_id,
            status=ConceptStatus.ARCHIVED,
            viability_confidence_score=0.0,
            total_processing_time=0.0,
            total_recalibrations=packet.recalibration_count,
            stage_history=packet.stage_reports.copy(),
            metadata={"archive_reason": reason}
        )
    
    async def process_multiple_concepts(
        self,
        queries: List[str],
        max_parallel: int = 5
    ) -> List[ConceptResult]:
        """
        Process multiple concepts in parallel (limited concurrency at Oracle stage).
        
        Args:
            queries: List of initial queries/concepts
            max_parallel: Maximum parallel Oracle searches
            
        Returns:
            List of ConceptResults
        """
        # Process in batches
        results = []
        for i in range(0, len(queries), max_parallel):
            batch = queries[i:i + max_parallel]
            batch_results = await asyncio.gather(*[
                self.process_concept(query) for query in batch
            ])
            results.extend(batch_results)
        
        return results
    
    def get_concept_status(self, concept_id: str) -> Optional[ConceptResult]:
        """Get status of a concept"""
        if concept_id in self.completed_concepts:
            return self.completed_concepts[concept_id]
        elif concept_id in self.active_concepts:
            packet = self.active_concepts[concept_id]
            return ConceptResult(
                concept_id=concept_id,
                status=ConceptStatus.IN_PROGRESS,
                viability_confidence_score=0.0,
                total_processing_time=0.0,
                total_recalibrations=packet.recalibration_count
            )
        return None

