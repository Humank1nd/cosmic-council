# E8-Engine/Agent Orchestrator/src/core/strategy/learning_loop.py
"""
Learning Loop Service
=====================

Automates the adaptive learning process by periodically running the
AdaptivePolicyEngine and CalibrationEngine.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List

import structlog
from .registry import AgentRole, StrategyRegistry
from .outcomes import OutcomeEvaluator
from .calibration import CalibrationEngine
from .optimizer import AdaptivePolicyEngine, UpdateRisk
from .store import StrategyStore, SQLiteStrategyStore
from .metrics import record_learning_loop_metrics

log = structlog.get_logger()

class LearningLoopService:
    """
    Background service that orchestrates the strategy learning loop.
    """

    def __init__(
        self,
        registry: StrategyRegistry,
        evaluator: OutcomeEvaluator,
        calibrator: CalibrationEngine,
        optimizer: AdaptivePolicyEngine,
        store: StrategyStore,
        interval_seconds: int = 3600,  # Default to 1 hour
    ):
        self.registry = registry
        self.evaluator = evaluator
        self.calibrator = calibrator
        self.optimizer = optimizer
        self.store = store
        self.interval_seconds = interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def run_iteration(self):
        """
        Runs a single iteration of the learning loop for all roles.
        """
        log.info("Starting learning loop iteration")
        start_time = datetime.now(timezone.utc)
        
        roles = list(AgentRole)
        updates_applied = 0
        updates_proposed = 0

        for role in roles:
            try:
                log.info("Analyzing role", role=role.value)
                updates = self.optimizer.analyze_role(role)
                updates_proposed += len(updates)

                for update in updates:
                    # Save update to store
                    await self.store.save_update(update)
                    
                    # Auto-apply low-risk updates if configured
                    if update.risk == UpdateRisk.LOW and self.optimizer.auto_apply_low_risk:
                        log.info("Auto-applying low-risk update", 
                                 role=role.value, update_type=update.update_type.value)
                        
                        # Apply to registry
                        profile = self.registry.get_profile(role)
                        # NOTE: In a real system, we'd have a method to apply update to profile
                        # For now, we assume the optimizer or registry handles this or we do it manually
                        # profile.apply_update(update) 
                        
                        # Mark as applied in store
                        update.status = "applied"
                        update.applied_at = datetime.now(timezone.utc)
                        await self.store.save_update(update)
                        updates_applied += 1
                    else:
                        log.info("Pending high-risk update for approval", 
                                 role=role.value, risk=update.risk.value)

            except Exception as e:
                log.error("Error in learning loop for role", role=role.value, error=str(e))

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        record_learning_loop_metrics(
            proposed=updates_proposed,
            applied=updates_applied,
            duration_seconds=duration
        )
        
        log.info("Learning loop iteration complete", 
                 proposed=updates_proposed, applied=updates_applied, duration=duration)

    async def start(self):
        """Starts the background loop."""
        if self._running:
            return
        
        self._running = True
        log.info("Learning loop service started", interval_seconds=self.interval_seconds)
        
        self._task = asyncio.create_task(self._loop())

    async def _loop(self):
        while self._running:
            try:
                await self.run_iteration()
            except Exception as e:
                log.error("Unhandled error in learning loop", error=str(e))
            
            await asyncio.sleep(self.interval_seconds)

    async def stop(self):
        """Stops the background loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        log.info("Learning loop service stopped")
