"""
Cosmic Council MVP Core - Real AI-powered implementation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from .enterprises import (
    RedOwl,
    OrangeOrangutan, 
    YellowHoneybee,
    GreenTortoise,
    BlueDolphin,
    PurpleElephant
)
from .config import get_config
from .logging_config import get_logger

config = get_config()
logger = get_logger("cosmic_council.core")


class CosmicCouncilMVP:
    """
    Real AI-powered implementation of the Cosmic Council.
    
    This version uses actual AI services and research capabilities.
    """
    
    def __init__(self):
        """Initialize the Cosmic Council with all six enterprises."""
        self.enterprises = [
            RedOwl(),
            OrangeOrangutan(), 
            YellowHoneybee(),
            GreenTortoise(),
            BlueDolphin(),
            PurpleElephant()
        ]
        
        logger.info("🚀 Cosmic Council MVP initialized with 6 AI-powered enterprises")
    
    async def solve_problem(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Solve a problem using all six enterprises with real AI.
        
        Args:
            problem: The problem statement to solve
            context: Additional context for problem solving
            
        Returns:
            Dictionary with enterprise names as keys and their solutions as values
        """
        logger.info(f"🎯 Solving problem: {problem}")
        
        results = {}
        shared_context = context or {}
        
        # Process enterprises in sequence, passing context between them
        for enterprise in self.enterprises:
            try:
                logger.info(f"  🔄 Processing with {enterprise.name}...")
                
                # Run the enterprise processing
                result = await enterprise.process(problem, shared_context)
                results[enterprise.name] = result
                
                # Update shared context with results for next enterprise
                shared_context[f"{enterprise.name}_result"] = result
                
                logger.info(f"  ✅ {enterprise.name} completed")
                
            except Exception as e:
                error_msg = f"Error: {e}"
                results[enterprise.name] = error_msg
                logger.error(f"  ❌ {enterprise.name} failed: {e}")
        
        logger.info("🎉 Problem solving complete!")
        return results
    
    def solve_problem_sync(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Synchronous wrapper for solve_problem.
        
        Args:
            problem: The problem statement to solve
            context: Additional context for problem solving
            
        Returns:
            Dictionary with enterprise names as keys and their solutions as values
        """
        return asyncio.run(self.solve_problem(problem, context))
    
    def get_enterprise_names(self) -> List[str]:
        """Get list of all enterprise names."""
        return [enterprise.name for enterprise in self.enterprises]
    
    def get_enterprise_count(self) -> int:
        """Get the number of enterprises."""
        return len(self.enterprises)
