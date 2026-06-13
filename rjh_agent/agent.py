from __future__ import annotations

import os
import re
import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from .hitl import HitlConfig, hitl_checkpoint
from .sandbox import SandboxConfig, SandboxContext, create_sandbox
from .skill_loader import Skill, build_skills_prompt, load_skills


@dataclass
class AgentConfig:
    name: str
    model: str | None = None
    api_key: str | None = None
    temperature: float | None = None
    skills_dir: str = ".rjh/skills"
    sandbox: SandboxConfig | None = None
    hitl: HitlConfig = field(default_factory=HitlConfig)
    system_prompt: str = ""
    max_tokens: int = 4096


@dataclass
class AgentMessage:
    role: str
    content: str


@dataclass
class AgentResult:
    content: str
    messages: list[AgentMessage]
    files_written: list[str]


class RJHAgent:
    def __init__(self, config: AgentConfig):
        api_key = config.api_key or os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            raise RuntimeError("缺少 DEEPSEEK_API_KEY，请在 .env 文件中配置")

        self.config = AgentConfig(
            name=config.name,
            model=config.model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            api_key=api_key,
            temperature=config.temperature
            if config.temperature is not None
            else float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
            skills_dir=config.skills_dir,
            sandbox=config.sandbox
            or SandboxConfig(workspace_path=os.getcwd(), output_dir="output", verbose=True),
            hitl=config.hitl,
            system_prompt=config.system_prompt,
            max_tokens=config.max_tokens,
        )

        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.skills: list[Skill] = []
        self.sandbox: SandboxContext | None = None
        self.conversation_history: list[AgentMessage] = []

    def _chat_completion(self, messages: list[dict[str, str]], stream: bool = False):
        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": stream,
            "messages": messages,
        }

        request = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )

        try:
            return urllib.request.urlopen(request, timeout=120)
        except urllib.error.HTTPError as err:
            body = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 错误：{err.code} {body}") from err

    def init(self) -> None:
        print("\n" + "=" * 50)
        print(f" {self.config.name} 启动中...")
        print("=" * 50)

        print("\n[Agent] 正在加载 Skill 文件...")
        self.skills = load_skills(self.config.skills_dir)
        print(f"[Agent] 共加载 {len(self.skills)} 个 Skill")

        print("\n[Agent] 正在初始化沙箱...")
        self.sandbox = create_sandbox(self.config.sandbox)

        print(f"\n[Agent] 初始化完成，模型：{self.config.model}")
        print("=" * 50 + "\n")

    def build_system_prompt(self) -> str:
        skills_section = build_skills_prompt(self.skills)
        sandbox_section = (
            f"\n## 工作区信息\n当前工作区路径：{self.sandbox.output_path}\n所有文件操作都写入此目录。"
            if self.sandbox
            else ""
        )

        return f"""你是 {self.config.name}，一个基于 DeepSeek 的通用型 AI 智能体。

## 核心能力
- 理解用户的自然语言目标，自动规划执行步骤
- 调用相应的 Skill 技能处理专项任务
- 将结果写入本地文件系统
- 对高风险操作会提示用户确认
{skills_section}
{sandbox_section}

## 行为准则
- 每次回复都要说明你正在做什么（Planning -> 执行 -> 输出）
- 需要写文件时，使用以下格式：
```filename:文件名.md
文件内容
```
- 如果任务超出能力范围，直接说明
- 使用中文回复

{self.config.system_prompt}"""

    def invoke(self, user_message: str) -> AgentResult:
        if not hitl_checkpoint(user_message, self.config.hitl):
            return AgentResult("操作已被用户取消。", self.conversation_history, [])

        self.conversation_history.append(AgentMessage(role="user", content=user_message))

        print(f"\n[Agent] 收到任务：{user_message[:80]}{'...' if len(user_message) > 80 else ''}")
        print("[Agent] 正在思考...\n")

        messages = [
                {"role": "system", "content": self.build_system_prompt()},
                *[
                    {"role": message.role, "content": message.content}
                    for message in self.conversation_history
                ],
        ]

        with self._chat_completion(messages, stream=False) as response:
            data = json.loads(response.read().decode("utf-8"))

        assistant_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        self.conversation_history.append(AgentMessage(role="assistant", content=assistant_content))

        files_written = self.process_file_operations(assistant_content)

        print("\n" + "-" * 50)
        print("[Agent] 执行完成")
        if files_written:
            print(f"[Agent] 写入文件：{', '.join(files_written)}")

        return AgentResult(assistant_content, self.conversation_history, files_written)

    def invoke_stream(self, user_message: str) -> AgentResult:
        if not hitl_checkpoint(user_message, self.config.hitl):
            return AgentResult("操作已被用户取消。", self.conversation_history, [])

        self.conversation_history.append(AgentMessage(role="user", content=user_message))

        print(f"\n[Agent] 收到任务：{user_message[:80]}{'...' if len(user_message) > 80 else ''}")
        print("[Agent] 开始流式输出：\n")
        print("-" * 50)

        messages = [
                {"role": "system", "content": self.build_system_prompt()},
                *[
                    {"role": message.role, "content": message.content}
                    for message in self.conversation_history
                ],
        ]

        chunks: list[str] = []
        with self._chat_completion(messages, stream=True) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data: "):
                    continue

                data_line = line[len("data: "):].strip()
                if data_line == "[DONE]":
                    break

                data = json.loads(data_line)
                delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta:
                    print(delta, end="", flush=True)
                    chunks.append(delta)

        print("\n" + "-" * 50)
        full_content = "".join(chunks)
        self.conversation_history.append(AgentMessage(role="assistant", content=full_content))

        files_written = self.process_file_operations(full_content)

        print("\n[Agent] 流式执行完成")
        if files_written:
            print(f"[Agent] 写入文件：{', '.join(files_written)}")

        return AgentResult(full_content, self.conversation_history, files_written)

    def process_file_operations(self, content: str) -> list[str]:
        if not self.sandbox:
            return []

        files_written: list[str] = []
        file_block_regex = re.compile(r"```(?:filename:|file:)([^\n]+)\n([\s\S]*?)```")

        for match in file_block_regex.finditer(content):
            filename = match.group(1).strip()
            file_content = match.group(2).strip()

            try:
                if hitl_checkpoint(f"写入文件：{filename}", self.config.hitl):
                    written_path = self.sandbox.write_file(filename, file_content)
                    files_written.append(filename)
                    print(f"[Agent] 已写入：{written_path}")
            except Exception as err:
                print(f"[Agent] 写入失败 {filename}: {err}")

        return files_written

    def write_file(self, filename: str, content: str) -> str:
        if not self.sandbox:
            raise RuntimeError("沙箱未初始化")
        return self.sandbox.write_file(filename, content)

    def get_sandbox(self) -> SandboxContext | None:
        return self.sandbox

    def clear_history(self) -> None:
        self.conversation_history = []
        print("[Agent] 对话历史已清空")

    def get_skills(self) -> list[Skill]:
        return self.skills


def create_rjh_agent(config: AgentConfig) -> RJHAgent:
    agent = RJHAgent(config)
    agent.init()
    return agent
