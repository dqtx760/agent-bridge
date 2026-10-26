"""
AgentBridge - Universal Multi-Agent Relay & Orchestration Framework
跨智能体全自动对讲与协同调度中继器
"""

from .models import AgentMessage, MessageType, CollaborationSession
from .orchestrator import AgentOrchestrator
from .adapters import get_adapter, ADAPTER_REGISTRY
from .protocols import ACPProtocol

__version__ = "0.1.0"
__all__ = [
    "AgentMessage",
    "MessageType",
    "CollaborationSession",
    "AgentOrchestrator",
    "get_adapter",
    "ADAPTER_REGISTRY",
    "ACPProtocol"
]
