# 技术文档生成器

## Description
当用户需要生成技术文档、README、API 文档、使用说明时触发此技能。
根据代码或需求描述，自动生成结构清晰、内容完整的 Markdown 文档。

## Script
1. 理解用户提供的代码结构或功能描述
2. 确定文档类型：README / API 文档 / 使用说明 / 架构文档
3. 生成标准 Markdown 格式文档，包含：
   - 项目概述和背景
   - 安装和运行步骤
   - 核心功能说明
   - 代码示例
   - 注意事项
4. 将文档写入指定文件（默认 README.md 或 docs/ 目录）

## Output Format
标准 Markdown 格式，包含：
- # 项目标题
- ## 功能特性
- ## 快速开始
- ## 使用示例
- ## 注意事项

## References
- GitHub README 最佳实践
- 中文技术文档写作规范
