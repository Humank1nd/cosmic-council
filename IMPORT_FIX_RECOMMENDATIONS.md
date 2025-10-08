
# Import Fix Recommendations

## Common Issues and Solutions

### 1. Old cosmic_council imports
**Problem:** `from cosmic_council.core.core import ProblemStatement`
**Solution:** `from src.core.types import ProblemStatement`

### 2. Database manager imports
**Problem:** `from shared.utils.database import get_database_manager`
**Solution:** `from src.database.connection import get_database_connection`

### 3. Logger imports
**Problem:** `from shared.logging.logger import get_enterprise_logger`
**Solution:** `from src.utils.logging import get_logger`

### 4. Core service imports
**Problem:** `from src.cosmic_council.core.hexagon import CosmicCouncilHexagon`
**Solution:** `from src.core.services import CosmicCouncilHexagon`

### 5. Agent imports
**Problem:** `from src.cosmic_council.agents.unified_ai_agent_system import UnifiedAIAgentSystem`
**Solution:** `from src.agents.orchestration.coordinator import AgentCoordinator`

## Quick Fix Script
Run this in your Python environment to fix common import issues:

```python
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Now you can import from the new structure
from src.core.types import ProblemStatement, EnterpriseType
from src.database.connection import get_database_connection
from src.utils.logging import get_logger
```

## Testing Imports
To test if your imports work:

```python
try:
    from src.core.types import ProblemStatement
    print("✅ Core types import successful")
except ImportError as e:
    print(f"❌ Core types import failed: {e}")

try:
    from src.database.connection import get_database_connection
    print("✅ Database connection import successful")
except ImportError as e:
    print(f"❌ Database connection import failed: {e}")
```
