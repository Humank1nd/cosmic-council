# council/__init__.py
# Core framework modules - import only the essential ones for now
from . import hexagon
from . import cycles
from . import reflection
from . import explain
from . import sahasrara

# Core system modules - import only the working ones
from . import core
from . import types

# Re-export key classes for easy access
from .core import (
    CosmicCouncil,
    ProblemStatement,
    ProblemComplexity,
    EnterpriseType,
    CycleStatus,
    EnhancedEnterpriseResult
)

from .hexagon import (
    CosmicCouncilHexagon,
    CycleResult,
    EnterpriseResult
)

from .sahasrara import (
    SahasraraEngine,
    SahasraraState,
    get_sahasrara_engine,
)

__all__ = [
    # Core modules
    'hexagon', 'cycles', 'reflection', 'explain', 'core', 'types', 'sahasrara',
    
    # Key classes
    'CosmicCouncil', 'ProblemStatement', 'ProblemComplexity', 'EnterpriseType',
    'CycleStatus', 'EnhancedEnterpriseResult', 'CosmicCouncilHexagon',
    'CycleResult', 'EnterpriseResult',
    'SahasraraEngine', 'SahasraraState', 'get_sahasrara_engine'
]
