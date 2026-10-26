from typing import Dict, Type
from .base import BaseAgentAdapter
from .codex import CodexAdapter
from .workbuddy import WorkBuddyAdapter
from .claude import ClaudeCodeAdapter
from .mock import MockAgentAdapter

ADAPTER_REGISTRY: Dict[str, Type[BaseAgentAdapter]] = {
    "codex": CodexAdapter,
    "workbuddy": WorkBuddyAdapter,
    "claude": ClaudeCodeAdapter,
    "mock": MockAgentAdapter
}

def get_adapter(adapter_type: str, name: str = None, **kwargs) -> BaseAgentAdapter:
    cls = ADAPTER_REGISTRY.get(adapter_type.lower())
    if not cls:
        raise ValueError(f"Unknown adapter type: '{adapter_type}'. Available: {list(ADAPTER_REGISTRY.keys())}")
    if name:
        return cls(name=name, **kwargs)
    return cls(**kwargs)

__all__ = [
    "BaseAgentAdapter",
    "CodexAdapter",
    "WorkBuddyAdapter",
    "ClaudeCodeAdapter",
    "MockAgentAdapter",
    "ADAPTER_REGISTRY",
    "get_adapter"
]
