# rjh-deep-agent

## 项目介绍

 OpenCodex 是一个基于 DeepSeek + TypeScript 的本地通用型 AI 代码智能体，
对标 OpenAI Codex / Claude Code 产品形态。

实现了通用型智能体标准六层架构，包含：
- Skill 技能文件体系（.skill.md 热插拔，重启自动加载）
- VFS 沙箱（文件写操作路径隔离，防越界访问）
- HITL 人为参与机制（高风险操作终端确认，同 Codex 设计原理）
- 多子智能体并行协作（Promise.all，Researcher / Analyst / Writer 角色分工）
- 模型可替换架构（DeepSeek / Ollama / 通义 / 豆包，改两行切换）

技术栈：TypeScript /python/ Node.js / openai SDK / DeepSeek API / Tavily Search / tsup
