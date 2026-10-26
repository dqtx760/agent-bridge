# AgentBridge 🌉

> **告别充当 AI 的“人肉剪贴板”** —— 跨智能体全自动对讲、辩论与任务协同调度中继器。  
> Universal Autonomous Multi-Agent Relay & Orchestration Bridge for **Codex**, **WorkBuddy**, **Claude Code**, and CLI Agents.

---

## 🌟 为什么需要 AgentBridge？

现在的开发者和团队往往同时运行着多个不同厂商的 AI 智能体：
- **OpenAI Codex**：擅长核心算法设计、底层代码编写与语法级重构；
- **Tencent WorkBuddy**：擅长高保真 Office 文档（PPTX/Word/Excel）、多媒体生成与在线网页部署；
- **Claude Code / Gemini**：擅长系统级统筹、终端命令执行与测试排查。

**痛点**：它们各自生活在不同的窗口和沙箱中。每当你想让 A 写代码、B 审查、C 做汇报时，你必须在不同窗口之间**一遍又一遍地复制粘贴**，人工充当低效的“AI 搬运工”。

**AgentBridge 解决的核心问题**：
通过本地 CLI 适配器、ACP 结构化协议与事件调度总线，**让多个独立的 Agent 能够像在会议室开会一样，全自动直连对讲、多轮交锋并形成最终交付物，无需任何人工搬运！**

### 💡 这个工具到底是什么？（本质定义）

**AgentBridge 本质就是一个用纯 Python 编写的轻量级命令行工具（CLI）和“自动化包工头”调度脚本。**

它本身**不是大模型**，也不占用几十 G 的显存。它在 Python 底层具体就干四件事：
1. **呼叫 Codex**：通过本地进程管道调起 `codex exec`，后台秒级取回算法与单测；
2. **呼叫 WorkBuddy**：通过本地 Gateway 接口或客户端快捷键，直接在桌面客户端中开辟真实的独立任务线程（调用 H3 等模型）；
3. **规范交接**：遵循 ACP (Agent Communication Protocol) 标准契约，把前者算出的数据修剪好塞给后者；
4. **画个群聊看板**：自带轻量级 Web 服务，把多智能体的交接全过程渲染为像微信/飞书一样的 3 人实时群聊大屏。

---
## 🏗️ 架构图解

```mermaid
flowchart TD
    User([👤 用户：下达顶层目标]) --> Bridge[🌉 AgentBridge 调度中枢<br/><i>(纯 Python 调度器 / 3人 Web 看板)</i>]

    subgraph Agents [🤖 本地多智能体协同矩阵]
        direction LR
        Codex[⚡ OpenAI Codex<br/>核心代码 & 算法]
        Claude[🧠 终端主控<br/>系统工程 & 架构拆解]
        WorkBuddy[💼 Tencent WorkBuddy<br/>商业文档 & PPTX 交付]
    end

    Bridge -->|1. 无头管道调用| Codex
    Bridge -->|2. 系统级协同| Claude
    Bridge -->|3. 真实桌面线程注入| WorkBuddy

    Codex --> Result[📦 最终成果统一落盘<br/>代码仓库 + 商业 PPTX + 桌面文件]
    Claude --> Result
    WorkBuddy --> Result
```

---

## ✨ 核心特性

- 🚀 **Zero-Clipboard（零剪贴板）**：告别人工复制粘贴，进程级/协议级直连自动运转。
- 🔌 **多适配器架构（Adapters）**：
  - `CodexAdapter`：基于 OpenAI Codex CLI (`codex exec`)
  - `WorkBuddyAdapter`：基于 Tencent WorkBuddy / CodeBuddy（兼容 ACP 规范与真实 FS 共享）
  - `ClaudeCodeAdapter`：基于 Anthropic Claude Code CLI (`claude -p`)
  - `MockAgentAdapter`：用于离线演示与自动化 CI 单测
- 📜 **标准协议保障（ACP Ready）**：严格遵循结构化 Agent 通信协议（Ask、Reply、Introduce、Checkpoint），上下文自动裁剪，防信息过载。
- 🎭 **双重协作模式**：
  - **Debate / Chat 模式**：双 Agent 围绕同一议题自主交锋、互相提问，并在 N 轮内达成共识。
  - **Pipeline 模式**：串行流水线作业（Agent 1 产出中间数据 -> Agent 2 消费生成文档）。
- 💻 **优雅可视化终端**：基于 Rich 构建，实时彩色流式渲染每位 Agent 的头像、身份、思考过程与交付物。

---

## 🕹️ 如何触发与使用？（3种开箱即用的方式）

安装完成后，你可以根据自己的使用习惯，选择以下任意一种方式触发多智能体协同：

```
┌────────────────────────────────────────────────────────────────────────┐
│ 方式 1：浏览器看板触发 ──► 适合视觉党，像微信群聊一样打字与围观         │
│ 方式 2：终端命令行触发 ──► 适合极客与脚本，一行命令驱动后台对讲         │
│ 方式 3：AI 助手自调用  ──► 适合作为 Claude Code / 主终端的外包工具箱    │
└────────────────────────────────────────────────────────────────────────┘
```

### 方式一：最直观 —— 启动 3 人协同群聊工作台（推荐 🌟）

如果你不想记任何复杂参数，直接启动可视化 Web 驾驶舱：

```bash
python -m agent_bridge.cli ui --port 8765
```

1. **自动弹窗**：浏览器会自动打开 `http://127.0.0.1:8765`，展示一个类似微信/飞书的 **3 人项目群聊界面**（大强同学、Gemini、WorkBuddy）；
2. **发号施令**：在底部的输入框里打字（例如：*“把桌面的价格表分析一下，算好返利并做成 3 页招商 PPT”*），点击发送；
3. **实时围观**：
   - 界面上立刻展示主控向 WorkBuddy 派发了什么任务；
   - WorkBuddy 正在处理（带打字动画）并回传大纲；
   - 主控继续跟进补充合规与结算细节；
   - 右侧群文件抽屉自动刷新，点击即可直接预览生成的 `PRICE_STRATEGY_COLLECTION.md` 等落地成果！

---

### 方式二：最极客 —— 终端一行命令直接对讲

如果你平时习惯在黑框命令行里工作，想让两个 Agent 围绕某个特定问题开会并达成共识：

```bash
# 1. 扫描本机已安装的 Agent (Codex / WorkBuddy / Claude)
python -m agent_bridge.cli list

# 2. 一行命令让 Codex 和 WorkBuddy 展开 2 轮自主对讲与交接
python -m agent_bridge.cli chat --agent1 codex --agent2 workbuddy --topic "设计一套本地商品阶梯返利结算系统" --rounds 2
```

- **运行效果**：当前终端实时以彩色流式面板滚动双方的发言；
- **自动化成果**：讨论达成共识后，最终成果会自动落盘至桌面的 `Desktop/agent_collab/` 共享工作区。

---

### 方式三：最优雅 —— 作为你主 AI 的“外包工具箱”（在对话中直接唤起）

如果你日常主要使用 **Claude Code、WezTerm (omp)、Cursor 或终端主助手**：

你不需要退出对话，在主对话中对你的 AI 直接说：
> **“帮我调用 agent-bridge，把这个子任务转交给 WorkBuddy 的 H3 模型去跑一个独立线程。”**

- **底层触发逻辑**：
  1. 主 AI 后台调用 `agent-bridge` 的适配器；
  2. 调度器自动唤醒本地 WorkBuddy 客户端（底层触发 `Ctrl+N` 会话注入）；
  3. **当你切到桌面的 WorkBuddy 客户端时，左侧任务栏会自动生成一个全新的任务线程，正在调用免费的 H3 (hy3) 引擎为你运算！**
  4. 既保全了终端主控的高效，又发挥了本地客户端免额度的优势！

---

## 🎯 智能体底层模型调用机制（具体调用的是哪个模型？）

很多开发者最关心的问题：**“当我触发调用时，它们背后到底是在跑哪一个具体模型？能不能指定？如果 WorkBuddy 默认是 DeepSeek 该怎么办？”**

AgentBridge 采用了一套清晰的**分层模型解析机制**：

| 目标智能体 | 默认调用的具体模型 | 如何修改 / 指定其他模型 |
| :--- | :--- | :--- |
| **OpenAI Codex** | **自动读取 `~/.codex/config.toml`** 中的 `model` 字段（如 `gpt-6-luna`） | 1. 命令行传参：`--codex-model gpt-6.1-sol`<br>2. 配置文件：修改 `config.yaml` 的 `default_model`<br>3. 直接修改本机的 `~/.codex/config.toml` |
| **腾讯 WorkBuddy** | **自动跟随客户端当前激活的默认模型**（当前选 H3 则跑 H3，选 DeepSeek 则跑 DeepSeek） | 1. 在 WorkBuddy 桌面端直接切换默认模型<br>2. 在派发 Prompt 时显式声明（如“让 WorkBuddy 用 DeepSeek 跑...”） |
| **远程 API / 豆包** | **读取 `config.yaml`** 中配置的 `model`（如 `doubao-pro-32k`） | 在 `config.yaml` 的 `agents.doubao_api.model` 中自由修改为任意模型 ID |

### 1. Codex 的模型绑定逻辑
Codex 客户端本质上是由本机的 `~/.codex/config.toml` 统一配置的：
- **默认无感模式**：AgentBridge 会直接尊重你在 Codex 里配置的系统偏好（例如 `model = "gpt-6-luna"`、`model_reasoning_effort = "high"`），无需重复配 key；
- **动态覆盖模式**：如果你想临时换模型（如 `gpt-6.1-sol`、`o3-mini`），直接在命令行或配置中指定：
  ```bash
  python -m agent_bridge.cli chat --agent1 codex --codex-model gpt-6.1-sol --topic "重构算法"
  ```

### 2. WorkBuddy 的模型绑定逻辑（如果默认是 DeepSeek？）
WorkBuddy 客户端支持腾讯混元 `hy3`、`hy4`，也支持通过插件连接的 `DeepSeek` 等模型：
- **默认继承规则**：当 AgentBridge 注入新工单线程时，WorkBuddy 客户端会**自动继承你当前界面正在生效的默认模型**：
  - 如果你当前界面选的是免费的 **H3 (hy3)**，新工单线程就自动以 **H3** 运行；
  - 如果你在 WorkBuddy 里切换成了 **DeepSeek**，新工单线程就会**立刻自动使用 DeepSeek 引擎进行运算**！
- **无需手动重配**：你不需要在代码里为 WorkBuddy 重新配置复杂的 API Key，客户端当前选谁，新派发的工单就由谁来接手，既灵活又直观！

---

## 🚀 极速安装与部署

```bash
git clone https://github.com/dqtx760/agent-bridge.git
cd agent-bridge
pip install -r requirements.txt
```
---

## 🐍 Python 代码调用示例

```python
from agent_bridge import AgentOrchestrator, get_adapter

# 1. 初始化适配器
codex = get_adapter("codex")
workbuddy = get_adapter("workbuddy")

# 2. 启动编排器
orchestrator = AgentOrchestrator(console_output=True)

# 3. 运行多轮辩论与对讲
history = orchestrator.debate(
    agent_a=codex,
    agent_b=workbuddy,
    topic="如何把一个静态 HTML 价格表自动化转化为带利润测算的 PPTX 招商演示？",
    rounds=2
)
```

---

## 📁 项目目录结构

```
agent-bridge/
├── agent_bridge/           # 核心代码包
│   ├── adapters/           # 智能体客户端适配器
│   │   ├── base.py         # 抽象基类
│   │   ├── codex.py        # OpenAI Codex 适配
│   │   ├── workbuddy.py    # Tencent WorkBuddy 适配
│   │   ├── claude.py       # Claude Code 适配
│   │   └── mock.py         # 离线自检模拟器
│   ├── protocols/          # 协议解析层
│   │   └── acp.py          # ACP 协议序列化与解析器
│   ├── models.py           # Pydantic 消息模型
│   ├── orchestrator.py     # 对讲编排与流水线引擎
│   └── cli.py              # 命令行交互入口
├── examples/               # 快速入门示例
├── pyproject.toml          # 打包配置文件
├── requirements.txt        # 轻量依赖清单
├── LICENSE                 # MIT 开源协议
└── README.md               # 项目使用文档
```

---

## 🛣️ 路线图 (Roadmap)

- [x] 原生支持 OpenAI Codex、Tencent WorkBuddy 与 Claude Code
- [x] 支持 ACP (Agent Communication Protocol) 标准消息格式
- [x] 多轮双机对讲 (Debate) 与串行流水线 (Pipeline)
- [ ] 支持基于 A2A (Agent2Agent) HTTP 规范的原生网关服务
- [ ] 增加 Web UI 看板，可视化观察 Agent 之间的通信拓扑与气泡流
- [ ] 支持更多主流 Agent 接入（如 Cursor CLI、Windsurf 等）

---

## 📄 开源许可证

本项目采用 [MIT 许可证](LICENSE)。欢迎提交 Issue 与 Pull Request！
