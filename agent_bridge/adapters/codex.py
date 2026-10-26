import shutil
import subprocess
import os
from typing import Optional
from .base import BaseAgentAdapter
from ..models import AgentMessage, MessageType, AgentInfo

class CodexAdapter(BaseAgentAdapter):
    """Adapter for OpenAI Codex CLI (codex exec)"""

    DEFAULT_PATHS = [
        r"C:\Users\Administrator\AppData\Local\Programs\OpenAI\Codex\bin\codex.EXE",
        os.path.expanduser(r"~\AppData\Local\Programs\OpenAI\Codex\bin\codex.EXE")
    ]

    def __init__(self, name: str = "Codex", executable_path: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name, "OpenAI Codex CLI - Engineering & Algorithm Specialist")
        self.executable_path = executable_path or self._resolve_executable()
        self.model = model

    def _resolve_executable(self) -> Optional[str]:
        # Check explicit paths first
        for p in self.DEFAULT_PATHS:
            if os.path.exists(p):
                return p
        # Check system PATH
        return shutil.which("codex")

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
            adapter_type="codex",
            description=self.description,
            available=self.is_available(),
            executable_path=self.executable_path,
            version=version
        )

    def send(self, prompt: str, context: Optional[str] = None, timeout: int = 120, **kwargs) -> AgentMessage:
        if not self.is_available():
            raise RuntimeError(f"Codex CLI executable not found at '{self.executable_path}'.")

        full_prompt = prompt
        if context:
            full_prompt = f"### 上下文背景\n{context}\n\n### 任务指令\n{prompt}"

        # Use codex exec --skip-git-repo-check
        # Output directly to a temp file or capture stdout
        cmd = [
            self.executable_path,
            "exec",
            "--skip-git-repo-check",
        ]
        target_model = kwargs.get("model") or self.model
        if target_model:
            cmd.extend(["-m", target_model])
        cmd.append("-")

        try:
            res = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=timeout
            )
            output = res.stdout.strip()
            if not output and res.stderr:
                output = f"[Codex Notice]: {res.stderr.strip()}"

            return AgentMessage(
                sender=self.name,
                content=output or "(Codex returned empty response)",
                message_type=MessageType.REPLY,
                raw_payload={"returncode": res.returncode, "stderr": res.stderr}
            )
        except subprocess.TimeoutExpired:
            return AgentMessage(
                sender=self.name,
                content=f"[Timeout] Codex execution exceeded {timeout}s limit.",
                message_type=MessageType.REPLY
            )
        except Exception as e:
            return AgentMessage(
                sender=self.name,
                content=f"[Execution Error]: {str(e)}",
                message_type=MessageType.REPLY
            )
