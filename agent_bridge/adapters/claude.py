import shutil
import subprocess
import os
from typing import Optional
from .base import BaseAgentAdapter
from ..models import AgentMessage, MessageType, AgentInfo

class ClaudeCodeAdapter(BaseAgentAdapter):
    """Adapter for Anthropic Claude Code CLI (claude -p)"""

    DEFAULT_PATHS = [
        r"C:\Users\Administrator\AppData\Roaming\npm\claude.CMD",
        os.path.expanduser(r"~\AppData\Roaming\npm\claude.CMD")
    ]

    def __init__(self, name: str = "ClaudeCode", executable_path: Optional[str] = None):
        super().__init__(name, "Anthropic Claude Code - Architecture & Systematic Engineering Specialist")
        self.executable_path = executable_path or self._resolve_executable()

    def _resolve_executable(self) -> Optional[str]:
        for p in self.DEFAULT_PATHS:
            if os.path.exists(p):
                return p
        return shutil.which("claude")

    def is_available(self) -> bool:
        return self.executable_path is not None and os.path.exists(self.executable_path)

    def get_info(self) -> AgentInfo:
        version = None
        if self.is_available():
            try:
                res = subprocess.run([self.executable_path, "--version"], capture_output=True, text=True, timeout=3)
                version = res.stdout.strip()
            except Exception:
                version = "unknown"

        return AgentInfo(
            name=self.name,
            adapter_type="claude_code",
            description=self.description,
            available=self.is_available(),
            executable_path=self.executable_path,
            version=version
        )

    def send(self, prompt: str, context: Optional[str] = None, timeout: int = 120, **kwargs) -> AgentMessage:
        if not self.is_available():
            raise RuntimeError(f"Claude Code CLI executable not found at '{self.executable_path}'.")

        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nTask:\n{prompt}"

        cmd = [
            self.executable_path,
            "-p",
            full_prompt
        ]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=timeout
            )
            output = res.stdout.strip()
            return AgentMessage(
                sender=self.name,
                content=output or "(Claude Code returned empty response)",
                message_type=MessageType.REPLY
            )
        except subprocess.TimeoutExpired:
            return AgentMessage(
                sender=self.name,
                content=f"[Timeout] Claude Code execution exceeded {timeout}s limit.",
                message_type=MessageType.REPLY
            )
        except Exception as e:
            return AgentMessage(
                sender=self.name,
                content=f"[Execution Error]: {str(e)}",
                message_type=MessageType.REPLY
            )
