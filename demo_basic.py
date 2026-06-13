import os

from rjh_agent import AgentConfig, HitlConfig, SandboxConfig, create_rjh_agent
from rjh_agent.env import load_dotenv


def main() -> None:
    load_dotenv()

    agent = create_rjh_agent(
        AgentConfig(
            name="RJH OpenCodex (DeepSeek) - 基础版",
            skills_dir=".rjh/skills",
            sandbox=SandboxConfig(workspace_path=os.getcwd(), output_dir="output", verbose=True),
            hitl=HitlConfig(enabled=False),
            system_prompt="你是一个有趣的 AI 助手，擅长处理古诗词和技术问题。",
        )
    )

    print("已加载的 Skill：")
    for skill in agent.get_skills():
        print(f"  - {skill.name}")

    print("\n测试一：诗词笑话生成\n")
    result1 = agent.invoke("飞流直下三千尺，疑是银河落九天")
    print("\nAI 回复：")
    print(result1.content)

    print("\n测试二：另一首诗\n")
    result2 = agent.invoke("举头望明月，低头思故乡")
    print("\nAI 回复：")
    print(result2.content)


if __name__ == "__main__":
    main()
