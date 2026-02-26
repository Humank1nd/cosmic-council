"""
Cosmic Council Integrations Module.

Provides external service integrations for:
- Firebase/Firestore data management
- Automation pipelines
- Real-time synchronization
- Cross-totem workflow execution
- Research & Inquiry Hub (Muladhara Knowledge Repository)
"""

from .firebase_automation import (
    # Enums
    TotemDatabase,
    AutomationType,
    PipelineStatus,
    SyncMode,

    # Data Records
    TotemRecord,
    ResearchRecord,
    StrategyRecord,
    InnovationRecord,
    ResourceRecord,
    CommunicationRecord,
    EthicsRecord,

    # Pipeline Components
    PipelineStep,
    AutomationPipeline,
    WorkflowExecution,

    # Firebase Client
    FirebaseClient,
    MockFirebaseClient,

    # Managers
    TotemDatabaseManager,
    AutomationEngine,
    RealTimeSyncManager,

    # Integration Facade
    CosmicCouncilIntegration,
    get_integration,
    create_integration,
)

from .research_hub import (
    # Enums
    ResearchDomain,
    QuantumPrinciple,
    SourceType,
    InquiryStatus,

    # Data Models
    QuantumConcept,
    GuidingQuestion,
    ResearchIteration,
    LiteratureReference,
    KnowledgeNode,
    ResearchTopic,

    # Collections
    ResearchCollections,

    # Research Hub
    ResearchInquiryHub,
    get_research_hub,
    create_research_hub,
)

__all__ = [
    # Enums - Firebase Automation
    'TotemDatabase',
    'AutomationType',
    'PipelineStatus',
    'SyncMode',

    # Enums - Research Hub
    'ResearchDomain',
    'QuantumPrinciple',
    'SourceType',
    'InquiryStatus',

    # Data Records - Firebase Automation
    'TotemRecord',
    'ResearchRecord',
    'StrategyRecord',
    'InnovationRecord',
    'ResourceRecord',
    'CommunicationRecord',
    'EthicsRecord',

    # Data Models - Research Hub
    'QuantumConcept',
    'GuidingQuestion',
    'ResearchIteration',
    'LiteratureReference',
    'KnowledgeNode',
    'ResearchTopic',

    # Pipeline Components
    'PipelineStep',
    'AutomationPipeline',
    'WorkflowExecution',

    # Firebase Client
    'FirebaseClient',
    'MockFirebaseClient',

    # Managers
    'TotemDatabaseManager',
    'AutomationEngine',
    'RealTimeSyncManager',

    # Collections
    'ResearchCollections',

    # Integration Facade
    'CosmicCouncilIntegration',
    'get_integration',
    'create_integration',

    # Research Hub
    'ResearchInquiryHub',
    'get_research_hub',
    'create_research_hub',
]
