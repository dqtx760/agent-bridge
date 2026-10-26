import re
from typing import Optional, Dict, Any
from ..models import AgentMessage, MessageType

ACP_START = "--- ACP START ---"
ACP_END = "--- ACP END ---"

class ACPProtocol:
    """Agent Communication Protocol (ACP) Serializer & Parser"""

    @staticmethod
    def format_message(msg: AgentMessage, context: Optional[str] = None, expect: Optional[str] = None) -> str:
        lines = [
            ACP_START,
            f"## Type\n{msg.message_type.value}\n",
            f"## From\n{msg.sender}\n",
            f"## To\n{msg.recipient or 'Partner Agent'}\n"
        ]

        if msg.thread_id:
            lines.append(f"## Thread\n{msg.thread_id}\n")

        if context:
            lines.append(f"## Context\n{context}\n")

        if msg.message_type == MessageType.ASK:
            lines.append(f"## Ask\n{msg.content}\n")
            if expect:
                lines.append(f"## Expect\n{expect}\n")
        elif msg.message_type == MessageType.REPLY:
            lines.append(f"## Reply\n{msg.content}\n")
            if msg.artifacts:
                lines.append(f"## Output\n" + "\n".join(f"- {a}" for a in msg.artifacts) + "\n")
        else:
            lines.append(f"## Content\n{msg.content}\n")

        lines.append(ACP_END)
        return "\n".join(lines)

    @staticmethod
    def parse_message(raw_text: str) -> Optional[AgentMessage]:
        if ACP_START not in raw_text:
            # Fallback if text doesn't have ACP markers
            return None

        # Extract content between ACP_START and ACP_END
        pattern = re.compile(rf"{re.escape(ACP_START)}(.*?)(?:{re.escape(ACP_END)}|\Z)", re.DOTALL)
        match = pattern.search(raw_text)
        if not match:
            return None

        body = match.group(1).strip()
        sections: Dict[str, str] = {}
        current_header = None
        current_lines = []

        for line in body.splitlines():
            h_match = re.match(r"^##\s+([A-Za-z0-9_\-\s]+)", line)
            if h_match:
                if current_header:
                    sections[current_header.strip().lower()] = "\n".join(current_lines).strip()
                current_header = h_match.group(1).strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_header:
            sections[current_header.strip().lower()] = "\n".join(current_lines).strip()

        sender = sections.get("from", "Unknown Agent")
        recipient = sections.get("to", "all")
        msg_type_str = sections.get("type", "General")
        thread_id = sections.get("thread", None)

        try:
            msg_type = MessageType(msg_type_str.capitalize())
        except ValueError:
            msg_type = MessageType.GENERAL

        content = sections.get("ask") or sections.get("reply") or sections.get("content") or body

        return AgentMessage(
            sender=sender,
            recipient=recipient,
            content=content,
            message_type=msg_type,
            thread_id=thread_id,
            raw_payload=sections
        )
