from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    ASK = "Ask"
    REPLY = "Reply"
    INTRODUCE = "Introduce"
    CHECKPOINT = "Checkpoint"
    FEEDBACK = "Feedback"
    BRIEFING = "Briefing"
    GENERAL = "General"

class AgentMessage(BaseModel):
    sender: str
    recipient: Optional[str] = "all"
    content: str
    message_type: MessageType = MessageType.GENERAL
    thread_id: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    raw_payload: Optional[Dict[str, Any]] = None

    def display_str(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M:%S')}] [{self.sender} -> {self.recipient}] ({self.message_type.value}):\n{self.content}"

class AgentInfo(BaseModel):
    name: str
    adapter_type: str
    description: str
    available: bool = True
    executable_path: Optional[str] = None
    version: Optional[str] = None

class CollaborationSession(BaseModel):
    session_id: str
    topic: str
    participants: List[str]
    messages: List[AgentMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "active"
