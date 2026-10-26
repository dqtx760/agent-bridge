import os
import subprocess
from typing import Optional
from .base import BaseAgentAdapter
from ..models import AgentMessage, MessageType, AgentInfo
from ..protocols.acp import ACPProtocol

class WorkBuddyAdapter(BaseAgentAdapter):
    """Adapter for Tencent WorkBuddy AI (Office & Ecology Specialist)"""

    DEFAULT_WORKSPACE = r"C:\Users\Administrator\Desktop\agent_collab"
    DEFAULT_EXE = r"D:\software\WorkBuddy\WorkBuddy.exe"

    def __init__(self, name: str = "WorkBuddy", workspace_dir: Optional[str] = None):
        super().__init__(name, "Tencent WorkBuddy - Office Documents, PPTX & Online Deployment Specialist")
        self.workspace_dir = workspace_dir or self.DEFAULT_WORKSPACE
        os.makedirs(self.workspace_dir, exist_ok=True)

    def is_available(self) -> bool:
        # Check if WorkBuddy is installed or running
        return os.path.exists(self.DEFAULT_EXE) or os.path.exists(r"C:\Users\Administrator\.workbuddy")

    def get_info(self) -> AgentInfo:
        return AgentInfo(
            name=self.name,
            adapter_type="workbuddy",
            description=self.description,
            available=self.is_available(),
            executable_path=self.DEFAULT_EXE if os.path.exists(self.DEFAULT_EXE) else None,
            version="5.8.x"
        )

    def send(self, prompt: str, context: Optional[str] = None, **kwargs) -> AgentMessage:
        """
        Formats prompt as an ACP message and writes to the shared collaboration workspace.
        If WorkBuddy daemon is responsive, it can process directly; otherwise stores for pickup.
        """
        msg = AgentMessage(
            sender="Orchestrator",
            recipient=self.name,
            content=prompt,
            message_type=MessageType.ASK
        )
        acp_formatted = ACPProtocol.format_message(msg, context=context, expect=kwargs.get("expect"))

        # Save to shared mailbox
        inbox_file = os.path.join(self.workspace_dir, "workbuddy_inbox.md")
        with open(inbox_file, "w", encoding="utf-8") as f:
            f.write(acp_formatted)

        # Check if outbox exists or if we should return immediate representation
        return AgentMessage(
            sender=self.name,
            content=f"[WorkBuddy Dispatch] 任务已写入共享工作区: {inbox_file}\n"
                    f"内容已同步为标准 ACP 格式。若有生成产物将保存在 {self.workspace_dir}。",
            message_type=MessageType.REPLY,
            artifacts=[inbox_file]
        )
