"""
Example 01: Quickstart with AgentBridge
演示如何使用 AgentBridge 启动两个 Agent 之间的全自动对讲
"""

from agent_bridge import AgentOrchestrator
from agent_bridge.adapters import get_adapter

def main():
    print("🚀 正在初始化 Agent 适配器...")
    # 可以选用实际已安装的 codex, workbuddy, claude，或者使用 mock 进行测试
    agent_a = get_adapter("mock", name="算法架构师-Codex")
    agent_b = get_adapter("mock", name="可视化专家-WorkBuddy")

    orchestrator = AgentOrchestrator(console_output=True)

    topic = "针对本地电商拿货价格表设计一套自动化阶梯返利算法及可视化看板"
    
    print(f"\n📢 开始针对议题《{topic}》进行自主对讲...")
    history = orchestrator.debate(
        agent_a=agent_a,
        agent_b=agent_b,
        topic=topic,
        rounds=2
    )

    print(f"\n🎉 对讲圆满结束，共产生 {len(history)} 轮结构化交接记录！")

if __name__ == "__main__":
    main()
