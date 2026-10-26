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

    def dispatch_gui_thread(self, text: str) -> bool:
        """
        Automatically triggers WorkBuddy to create a brand-new task thread in its UI,
        pastes the task prompt, and presses Enter to run with H3/default model.
        """
        try:
            import win32gui, win32con, win32clipboard, time, ctypes

            # Find WorkBuddy window
            target_hwnd = None
            def enum_cb(h, _):
                nonlocal target_hwnd
                if win32gui.IsWindowVisible(h):
                    title = win32gui.GetWindowText(h)
                    if title and title.strip() == "WorkBuddy":
                        target_hwnd = h
            win32gui.EnumWindows(enum_cb, None)

            if not target_hwnd:
                return False

            # 1. Bring window to foreground and restore
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(target_hwnd)
            time.sleep(0.4)

            # 2. Trigger native shortcut: Ctrl+N (New Task)
            VK_CONTROL = 0x11
            VK_N = 0x4E
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_N, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_N, 0, 2, 0)
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0)
            time.sleep(0.8)  # Wait for new conversation to initialize

            # 3. Put text into clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            win32clipboard.CloseClipboard()

            # 4. Paste via Ctrl+V
            VK_V = 0x56
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_V, 0, 2, 0)
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0)
            time.sleep(0.4)

            # 5. Press Enter to submit
            VK_RETURN = 0x0D
            ctypes.windll.user32.keybd_event(VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(VK_RETURN, 0, 2, 0)
            return True
        except Exception as e:
            return False

    def send(self, prompt: str, context: Optional[str] = None, **kwargs) -> AgentMessage:
        """
        Formats prompt as an ACP message, writes to shared mailbox, and automatically
        spawns a visible thread in WorkBuddy's UI.
        """
        full_prompt = prompt
        if context:
            full_prompt = f"### 上下文背景\n{context}\n\n### 任务要求\n{prompt}"

        # Dual dispatch: 1. Spawn real thread in GUI
        gui_success = self.dispatch_gui_thread(full_prompt)

        # 2. Persist to shared inbox
        msg = AgentMessage(
            sender="Orchestrator",
            recipient=self.name,
            content=full_prompt,
            message_type=MessageType.ASK
        )
        acp_formatted = ACPProtocol.format_message(msg, context=context, expect=kwargs.get("expect"))
        inbox_file = os.path.join(self.workspace_dir, "workbuddy_inbox.md")
        with open(inbox_file, "w", encoding="utf-8") as f:
            f.write(acp_formatted)

        status_note = "已成功在 WorkBuddy 客户端开辟独立线程并启动 H3 模型执行" if gui_success else "已写入共享信箱"
        return AgentMessage(
            sender=self.name,
            content=f"[WorkBuddy 子代理已派发]: {status_note}。\n任务详情已同步至: {inbox_file}",
            message_type=MessageType.REPLY,
            artifacts=[inbox_file]
        )
