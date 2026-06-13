import os

from rjh_agent import AgentConfig, HitlConfig, RJHAgent, SandboxConfig, create_rjh_agent
from rjh_agent.env import load_dotenv
from rjh_agent.tools import TavilySearch


def researcher_agent(topic: str, search: TavilySearch) -> str:
    print(f"\n[Researcher] 开始搜索：{topic}")
    results = search.search(topic, 3)
    summary = "\n\n".join(f"[{index}] {item.title}\n{item.content}" for index, item in enumerate(results, 1))
    print(f"[Researcher] 搜索完成，获取 {len(results)} 条结果")
    return summary


def analyst_agent(agent: RJHAgent, raw_data: str, aspect: str) -> str:
    print(f"\n[Analyst] 开始分析：{aspect}")
    result = agent.invoke(
        f"""
请分析以下资料，提取关于「{aspect}」的核心观点，用简洁的要点形式输出（3-5点）：

{raw_data}

输出格式：
## {aspect}
- 要点1
- 要点2
- 要点3
"""
    )
    print(f"[Analyst] 分析完成：{aspect}")
    return result.content


def writer_agent(agent: RJHAgent, sections: dict[str, str], title: str) -> str:
    print(f"\n[Writer] 开始整合文档：{title}")
    sections_text = "\n\n".join(f"### {key}\n{value}" for key, value in sections.items())

    result = agent.invoke(
        f"""
请将以下各部分内容整合成一份完整、专业的技术调研报告。

报告标题：{title}

各部分内容：
{sections_text}

要求：
1. 输出完整 Markdown 格式
2. 包含摘要、正文、结论三部分
3. 语言专业简洁
4. 将完整报告写入文件：
```filename:tech-research-report.md
（完整报告内容）
```
"""
    )
    print("[Writer] 文档整合完成")
    return result.content


def main() -> None:
    load_dotenv()

    if not os.getenv("TAVILY_API_KEY"):
        print("未配置 TAVILY_API_KEY，将使用内置知识运行（跳过网络搜索）")

    main_agent = create_rjh_agent(
        AgentConfig(
            name="RJH OpenCodex (DeepSeek) - 多智能体协作版",
            skills_dir=".rjh/skills",
            sandbox=SandboxConfig(workspace_path=os.getcwd(), output_dir="output", verbose=True),
            hitl=HitlConfig(enabled=False),
        )
    )

    search = TavilySearch(os.getenv("TAVILY_API_KEY")) if os.getenv("TAVILY_API_KEY") else None

    report_title = "2026年前端 AI 智能体开发技术调研报告"
    print(f"\n主智能体开始 Planning：{report_title}")
    print("任务拆解：")
    print("  -> 子智能体 A (Researcher)：并行搜索各技术方向资料")
    print("  -> 子智能体 B (Analyst)：分析各维度核心观点")
    print("  -> 子智能体 C (Writer)：整合输出完整报告")

    framework_data = "LangChain 是基础框架，LangGraph 做状态编排，Deep Agent 做通用智能体开箱即用"
    scenario_data = "前端工程师做 AI 应用有天然优势：TypeScript 支持好，UI 能力强，工程化熟练"

    if search:
        framework_data = researcher_agent("LangChain LangGraph Deep Agent 框架对比 2026", search)
        scenario_data = researcher_agent("前端工程师 AI 应用开发 TypeScript 智能体 2026", search)

    analyst_agent_instance = create_rjh_agent(
        AgentConfig(
            name="分析师智能体 (DeepSeek)",
            skills_dir=".rjh/skills",
            sandbox=SandboxConfig(workspace_path=os.getcwd(), output_dir="output", verbose=False),
            hitl=HitlConfig(enabled=False),
        )
    )

    framework_analysis = analyst_agent(main_agent, framework_data, "框架选型与对比")
    scenario_analysis = analyst_agent(analyst_agent_instance, scenario_data, "前端工程师的 AI 发展机遇")

    writer_agent(
        main_agent,
        {
            "框架选型与对比": framework_analysis,
            "前端工程师的 AI 发展机遇": scenario_analysis,
        },
        report_title,
    )

    sandbox = main_agent.get_sandbox()
    if sandbox:
        files = sandbox.list_files()
        print("\n" + "=" * 50)
        print("多智能体协作完成！")
        print("=" * 50)
        print("\n生成的文件：")
        for file_name in files:
            print(f"  output/{file_name}")

        report = sandbox.read_file("tech-research-report.md")
        if report:
            print("\n报告预览（前 600 字）：")
            print("-" * 50)
            print(report[:600] + ("\n..." if len(report) > 600 else ""))


if __name__ == "__main__":
    main()
