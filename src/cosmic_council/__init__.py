"""
Agent Orchestrator Framework
The Ultimate Problem-Solving Framework

A comprehensive, AI-powered problem-solving system that implements the revolutionary 
Hexagon methodology. Built on the principles of the Agent Orchestrator's six enterprise 
agents, this framework provides a structured, intelligent approach to tackling 
complex problems across business, personal, and global domains.
"""

# Core imports
from .core.core import (
    CosmicCouncil,
    ProblemStatement,
    ProblemComplexity,
    EnterpriseType,
    CycleStatus,
    EnhancedEnterpriseResult
)

from .core.hexagon import (
    CosmicCouncilHexagon,
    CycleResult,
    EnterpriseResult
)

# Version
__version__ = "1.0.0"
__author__ = "Agent Orchestrator Team"

# Main exports
__all__ = [
    # Core classes
    'CosmicCouncil',
    'ProblemStatement', 
    'ProblemComplexity',
    'EnterpriseType',
    'CycleStatus',
    'EnhancedEnterpriseResult',
    
    # Hexagon classes
    'CosmicCouncilHexagon',
    'CycleResult',
    'EnterpriseResult',
    
    # Version info
    '__version__',
    '__author__'
]
