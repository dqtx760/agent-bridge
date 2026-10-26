import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from .adapters import get_adapter, ADAPTER_REGISTRY
from .orchestrator import AgentOrchestrator

app = typer.Typer(
    name="agent-bridge",
    help="AgentBridge: 跨智能体全自动对讲与协同调度中继器 (Universal Multi-Agent Relay)"
)
console = Console()

@app.command("list")
def list_agents():
    """扫描并列出本机所有可用的 Agent 客户端与适配器"""
    table = Table(title="🤖 本地智能体 (Agents) 探测与适配列表", header_style="bold magenta")
    table.add_column("Agent 标识", style="cyan", width=15)
    table.add_column("适配器类型", style="green", width=15)
    table.add_column("可用状态", justify="center", width=10)
    table.add_column("检测到路径 / 详情", style="white")

    for key in ADAPTER_REGISTRY.keys():
        try:
            adapter = get_adapter(key)
            info = adapter.get_info()
            status = "[bold green]已就绪[/bold green]" if info.available else "[bold red]未发现[/bold red]"
            details = info.executable_path or info.description
            table.add_row(info.name, info.adapter_type, status, details)
        except Exception as e:
            table.add_row(key, key, "[red]异常[/red]", str(e))

    console.print(table)
    console.print("\n[dim]提示：使用 `agent-bridge chat --agent1 codex --agent2 workbuddy` 可开启两机自动对讲。[/dim]")

@app.command("chat")
def chat(
    agent1: str = typer.Option("mock", "--agent1", "-a1", help="发起方 Agent 类型 (codex, workbuddy, claude, mock)"),
    agent2: str = typer.Option("mock", "--agent2", "-a2", help="对谈方 Agent 类型 (codex, workbuddy, claude, mock)"),
    topic: str = typer.Option("评估一份电商拿货价格表的优化空间", "--topic", "-t", help="讨论的核心议题"),
    rounds: int = typer.Option(2, "--rounds", "-r", help="对谈轮数")
):
    """启动两个 Agent 之间的全自动多轮对讲/辩论"""
    try:
        a1 = get_adapter(agent1)
        a2 = get_adapter(agent2)
    except Exception as e:
        console.print(f"[bold red]初始化 Agent 失败:[/bold red] {e}")
        raise typer.Exit(1)

    orchestrator = AgentOrchestrator(console_output=True)
    orchestrator.debate(a1, a2, topic=topic, rounds=rounds)

@app.command("test")
def smoke_test():
    """快速自检：使用 Mock Agent 演示全自动双机对讲流程"""
    from .adapters.mock import MockAgentAdapter
    a1 = MockAgentAdapter("架构师-Codex", "核心算法与系统架构")
    a2 = MockAgentAdapter("交付官-WorkBuddy", "方案汇报与可视化排版")

    orchestrator = AgentOrchestrator(console_output=True)
    orchestrator.debate(
        a1, a2,
        topic="为本地拿货价格表建立一个自动化每日报表系统",
        rounds=2
    )
@app.command("ui")
def launch_ui(port: int = typer.Option(8765, "--port", "-p", help="工作台服务端口")):
    """启动浏览器图形化工作台看板 (Visual Workbench)"""
    import webbrowser
    from .web import start_workbench
    console.print(f"[bold green][AgentBridge] 正在启动多智能体可视化工作台: http://127.0.0.1:{port}[/bold green]")
    console.print("[dim]浏览器将自动打开看板，按 Ctrl+C 可停止服务。[/dim]")
    webbrowser.open(f"http://127.0.0.1:{port}")
    start_workbench(port=port)

def main():
    app()

if __name__ == "__main__":
    main()
