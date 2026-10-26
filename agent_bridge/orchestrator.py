import time
from typing import List, Tuple, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .models import AgentMessage, MessageType, CollaborationSession
from .adapters.base import BaseAgentAdapter
from .protocols.acp import ACPProtocol

console = Console()

class AgentOrchestrator:
    """Core Orchestrator for Multi-Agent Dialogues, Debates, and Pipelines"""

    def __init__(self, console_output: bool = True):
        self.console_output = console_output
        self.session_history: List[AgentMessage] = []

    def _render_message(self, msg: AgentMessage, round_num: Optional[int] = None):
        if not self.console_output:
            return

        header = f"[bold cyan]{msg.sender}[/bold cyan] -> [bold magenta]{msg.recipient}[/bold magenta]"
        if round_num is not None:
            header += f" [yellow](Round {round_num})[/yellow]"

        panel_color = "green" if "codex" in msg.sender.lower() else "blue" if "workbuddy" in msg.sender.lower() else "white"

        console.print(Panel(
            msg.content,
            title=header,
            subtitle=f"[dim]{msg.timestamp.strftime('%H:%M:%S')} | {msg.message_type.value}[/dim]",
            border_style=panel_color
        ))
        console.print()

    def debate(
        self,
        agent_a: BaseAgentAdapter,
        agent_b: BaseAgentAdapter,
        topic: str,
        rounds: int = 2,
        on_turn: Optional[Callable[[AgentMessage], None]] = None
    ) -> List[AgentMessage]:
        """
        Runs an autonomous multi-turn dialogue/debate between two agents.
        No human copy-pasting required.
        """
        if self.console_output:
            console.rule(f"[bold yellow]🚀 启动双智能体自主对讲: {agent_a.name} ⚔️ {agent_b.name}[/bold yellow]")
            console.print(f"[bold]议题/目标:[/bold] {topic}\n")

        history: List[AgentMessage] = []
        current_context = f"协作核心议题: {topic}"

        # Initial prompt for Agent A
        prompt_a = (
            f"你好 {agent_a.name}！请针对议题《{topic}》给出你的第一轮分析与方案初稿。\n"
            f"请直入主题，明确技术方案与关键论据，结尾抛出你希望对方考虑的关注点。"
        )

        for r in range(1, rounds + 1):
            # Turn 1: Agent A speaks
            with console.status(f"[bold green]{agent_a.name} 正在思考并作答...[/bold green]"):
                resp_a = agent_a.send(prompt_a, context=current_context)
                resp_a.recipient = agent_b.name
                resp_a.thread_id = f"debate-{topic[:10]}-{int(time.time())}"

            history.append(resp_a)
            self._render_message(resp_a, round_num=r)
            if on_turn:
                on_turn(resp_a)

            # Turn 2: Agent B replies
            prompt_b = (
                f"这是来自 {agent_a.name} 的分析输出：\n\n"
                f"{resp_a.content}\n\n"
                f"请以你的专业视角对其进行 Review、补充优化或提出不同见解，推进共识达成。"
            )

            with console.status(f"[bold blue]{agent_b.name} 正在审阅并回应...[/bold blue]"):
                resp_b = agent_b.send(prompt_b, context=current_context)
                resp_b.recipient = agent_a.name
                resp_b.thread_id = resp_a.thread_id

            history.append(resp_b)
            self._render_message(resp_b, round_num=r)
            if on_turn:
                on_turn(resp_b)

            # Update context for next round
            current_context = (
                f"上轮 {agent_a.name} 观点摘要: {resp_a.content[:150]}...\n"
                f"上轮 {agent_b.name} 观点摘要: {resp_b.content[:150]}..."
            )
            prompt_a = (
                f"这是来自 {agent_b.name} 的反馈：\n\n"
                f"{resp_b.content}\n\n"
                f"请针对其建议进行迭代完善，形成进一步的实施结论。"
            )

        if self.console_output:
            console.rule("[bold green]✅ 对讲完成，共识已达成[/bold green]")

        return history

    def pipeline(
        self,
        stages: List[Tuple[BaseAgentAdapter, str]]
    ) -> List[AgentMessage]:
        """
        Executes a sequential multi-agent pipeline.
        Output of Agent 1 feeds into Agent 2 as context, etc.
        """
        if self.console_output:
            console.rule("[bold cyan]⛓️ 启动多智能体串行流水线 (Pipeline)[/bold cyan]")

        history: List[AgentMessage] = []
        accumulated_context = ""

        for idx, (agent, task_prompt) in enumerate(stages, 1):
            if self.console_output:
                console.print(f"[bold yellow]阶段 {idx}/{len(stages)}:[/bold yellow] 由 [bold]{agent.name}[/bold] 执行: {task_prompt}")

            with console.status(f"[bold]{agent.name}[/bold] 正在执行任务..."):
                resp = agent.send(task_prompt, context=accumulated_context)

            history.append(resp)
            self._render_message(resp)

            # Accumulate output
            accumulated_context += f"\n\n### 阶段 {idx} ({agent.name}) 产出:\n{resp.content}"

        if self.console_output:
            console.rule("[bold green]🎉 流水线全链路执行成功[/bold green]")

        return history
