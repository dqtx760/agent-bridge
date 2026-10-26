from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..models import AgentMessage, MessageType, AgentInfo

class BaseAgentAdapter(ABC):
    """Abstract base class for all Agent adapters (Codex, WorkBuddy, Claude Code, etc.)"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the agent CLI / executable / API is available locally."""
        pass

    @abstractmethod
    def get_info(self) -> AgentInfo:
        """Return information about the agent."""
        pass

    @abstractmethod
    def send(self, prompt: str, context: Optional[str] = None, **kwargs) -> AgentMessage:
        """Send a prompt/message to the agent and return its response."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} available={self.is_available()}>"
