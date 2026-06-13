from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    name: str
    file_name: str
    description: str
    script: str
    raw: str
    examples: str | None = None
    output_format: str | None = None
    references: str | None = None


def parse_skill_file(file_path: str | Path) -> Skill:
    path = Path(file_path)
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    name_line = next((line for line in lines if line.startswith("# ")), None)
    name = name_line.replace("# ", "", 1).strip() if name_line else path.name[: -len(".skill.md")]

    sections: dict[str, str] = {}
    current_section = ""
    current_content: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line.replace("## ", "", 1).strip()
            current_content = []
        elif not line.startswith("# "):
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return Skill(
        name=name,
        file_name=path.name,
        description=sections.get("Description", ""),
        script=sections.get("Script", ""),
        examples=sections.get("Examples"),
        output_format=sections.get("Output Format"),
        references=sections.get("References"),
        raw=raw,
    )


def load_skills(skills_dir: str) -> list[Skill]:
    resolved_dir = Path(skills_dir).resolve()

    if not resolved_dir.exists():
        print(f"[SkillLoader] 目录不存在：{resolved_dir}")
        return []

    skill_files = sorted(resolved_dir.glob("*.skill.md"))
    if not skill_files:
        print(f"[SkillLoader] 未找到任何 .skill.md 文件：{resolved_dir}")
        return []

    skills: list[Skill] = []
    for file_path in skill_files:
        skill = parse_skill_file(file_path)
        print(f"[SkillLoader] 已加载技能：{skill.name} ({file_path.name})")
        skills.append(skill)

    return skills


def build_skills_prompt(skills: list[Skill]) -> str:
    if not skills:
        return ""

    descriptions: list[str] = []
    for index, skill in enumerate(skills, start=1):
        desc = f"{index}. **{skill.name}**\n   触发条件：{skill.description}"
        if skill.examples:
            first_example = "\n".join(skill.examples.splitlines()[:2])
            desc += f"\n   示例：{first_example}"
        descriptions.append(desc)

    return f"""
## 你具备以下专项技能（Skill）

{chr(10).join(descriptions)}

当用户的输入符合某个技能的触发条件时，请主动调用该技能的执行逻辑来处理任务。
"""
