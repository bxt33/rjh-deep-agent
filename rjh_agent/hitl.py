from __future__ import annotations

from dataclasses import dataclass, field


HIGH_RISK_KEYWORDS = [
    "rm -rf",
    "drop table",
    "delete from",
    "format",
    "sudo",
    "chmod 777",
    "删除所有",
    "清空数据库",
    "格式化",
]


@dataclass
class HitlConfig:
    enabled: bool = True
    extra_keywords: list[str] = field(default_factory=list)
    auto_approve: bool = False


def is_high_risk_operation(content: str, extra_keywords: list[str] | None = None) -> bool:
    keywords = [*HIGH_RISK_KEYWORDS, *(extra_keywords or [])]
    lower = content.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def hitl_checkpoint(operation_desc: str, config: HitlConfig | None = None) -> bool:
    config = config or HitlConfig()
    if not config.enabled:
        return True

    if not is_high_risk_operation(operation_desc, config.extra_keywords):
        return True

    print("\n" + "=" * 50)
    print("[HITL] 检测到高风险操作，需要人工确认")
    print("=" * 50)
    print(f"操作描述：{operation_desc}")
    print("=" * 50)

    if config.auto_approve:
        print("[HITL] 自动同意模式，继续执行...\n")
        return True

    answer = input("\n请确认是否继续执行？(y/n): ").strip().lower()
    approved = answer in {"y", "yes"}
    print("[HITL] 已确认，继续执行...\n" if approved else "[HITL] 已拒绝，操作中止。\n")
    return approved
