from typing import Optional
from .base import BaseAgentAdapter
from ..models import AgentMessage, MessageType, AgentInfo

class MockAgentAdapter(BaseAgentAdapter):
    """Mock Agent for local testing, CI pipelines, and demonstration"""

    def __init__(self, name: str = "MockAgent", role: str = "Assistant"):
        super().__init__(name, f"Mock Agent playing role: {role}")
        self.role = role

    def is_available(self) -> bool:
        return True

    def get_info(self) -> AgentInfo:
        return AgentInfo(
            name=self.name,
            adapter_type="mock",
            description=self.description,
            available=True,
            version="1.0.0"
        )

    def send(self, prompt: str, context: Optional[str] = None, **kwargs) -> AgentMessage:
        reply_content = (
            f"[{self.name} - {self.role}]\n"
            f"已收到输入：'{prompt[:60]}...'\n"
            f"执行结果：模拟分析完成，技术指标正常，交付物符合契约要求。"
        )
        return AgentMessage(
            sender=self.name,
            content=reply_content,
            message_type=MessageType.REPLY
        )
