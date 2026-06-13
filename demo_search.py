import os

from rjh_agent import AgentConfig, HitlConfig, SandboxConfig, create_rjh_agent
from rjh_agent.env import load_dotenv
from rjh_agent.tools import TavilySearch


def main() -> None:
    load_dotenv()

    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        raise RuntimeError("缺少 TAVILY_API_KEY，请在 .env 中配置")

    search = TavilySearch(tavily_key)
    agent = create_rjh_agent(
        AgentConfig(
            name="RJH OpenCodex (DeepSeek) - 搜索版",
            skills_dir=".rjh/skills",
            sandbox=SandboxConfig(workspace_path=os.getcwd(), output_dir="output", verbose=True),
            hitl=HitlConfig(enabled=False),
            system_prompt="""
你是一个具备网络搜索能力的 AI 助手，由 DeepSeek 驱动。
需要写文件时请用：
```filename:文件名.md
内容
```
""",
        )
    )

    query = "LangChain Deep Agent 快速入门教程 2026"
    print(f"\n搜索关键词：{query}")

    search_results = search.search(query)
    print(f"[Search] 获取到 {len(search_results)} 条结果")

    joined_results = "\n---\n".join(
        f"[{index}] {item.title}\n来源：{item.url}\n摘要：{item.content}"
        for index, item in enumerate(search_results, start=1)
    )

    user_message = f"""
请根据以下搜索结果，总结 LangChain Deep Agent 的核心概念和快速入门步骤，
输出一份清晰的中文学习笔记，并保存到文件 deep-agent-notes.md。

搜索结果：
{joined_results}

要求：
1. 用简洁的中文总结
2. 包含核心概念解释
3. 包含快速入门步骤
4. 写入文件 deep-agent-notes.md
"""

    result = agent.invoke_stream(user_message)

    if not result.files_written:
        sandbox = agent.get_sandbox()
        if sandbox:
            sandbox.write_file("deep-agent-notes.md", result.content)
            print("\n已手动保存结果到 output/deep-agent-notes.md")


if __name__ == "__main__":
    main()
