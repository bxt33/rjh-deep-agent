import os

from rjh_agent import AgentConfig, HitlConfig, SandboxConfig, create_rjh_agent
from rjh_agent.env import load_dotenv


def main() -> None:
    load_dotenv()

    agent = create_rjh_agent(
        AgentConfig(
            name="RJH OpenCodex (DeepSeek)",
            skills_dir=".rjh/skills",
            sandbox=SandboxConfig(workspace_path=os.getcwd(), output_dir="output", verbose=True),
            hitl=HitlConfig(enabled=True, auto_approve=False),
            system_prompt="""
你是 RJH OpenCodex，一个专业的前端 + AI 全栈智能体，由 DeepSeek 驱动。
你擅长：
- TypeScript / Vue3 / React 开发
- Java / Spring Boot / Python 开发
- LangChain / Deep Agent AI 应用开发
- 代码审查和架构设计
- 技术文档生成
请用中文回复，需要写文件时使用规定的 filename 格式。
""",
        )
    )

    print("\nRJH OpenCodex (DeepSeek) 已就绪！")
    print("已加载技能：")
    for skill in agent.get_skills():
        print(f"  - {skill.name}")
    print("\n输入你的任务（输入 exit 退出，输入 clear 清空对话历史）")
    print("-" * 50)

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() == "exit":
            print("\n再见！")
            break
        if user_input.lower() == "clear":
            agent.clear_history()
            continue
        if not user_input:
            continue

        print("\n智能体：")
        agent.invoke_stream(user_input)


if __name__ == "__main__":
    main()
