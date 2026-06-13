from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SandboxConfig:
    workspace_path: str
    output_dir: str = "output"
    verbose: bool = True


class SandboxContext:
    def __init__(self, config: SandboxConfig):
        self.workspace_path = Path(config.workspace_path).resolve()
        self.output_path = (self.workspace_path / config.output_dir).resolve()
        self.verbose = config.verbose
        self.output_path.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print("[Sandbox] 工作区初始化完成")
            print(f"[Sandbox]   真实路径：{self.workspace_path}")
            print(f"[Sandbox]   输出目录：{self.output_path}")

    def is_path_safe(self, target_path: str) -> bool:
        resolved = (self.output_path / target_path).resolve()
        try:
            resolved.relative_to(self.output_path)
            return True
        except ValueError:
            return False

    def write_file(self, filename: str, content: str) -> str:
        if not self.is_path_safe(filename):
            raise ValueError(f"[Sandbox] 安全拦截：路径越界 {filename}")

        target_path = self.output_path / filename
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")

        if self.verbose:
            print(f"[Sandbox] 文件已写入：{target_path.relative_to(self.workspace_path)}")

        return str(target_path)

    def read_file(self, filename: str) -> str | None:
        if not self.is_path_safe(filename):
            print(f"[Sandbox] 安全拦截：路径越界 {filename}")
            return None

        target_path = self.output_path / filename
        if not target_path.exists():
            return None
        return target_path.read_text(encoding="utf-8")

    def list_files(self) -> list[str]:
        if not self.output_path.exists():
            return []
        return [
            str(path.relative_to(self.output_path))
            for path in self.output_path.rglob("*")
            if path.is_file()
        ]


def create_sandbox(config: SandboxConfig) -> SandboxContext:
    return SandboxContext(config)
