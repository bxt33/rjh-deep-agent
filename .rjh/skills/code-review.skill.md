# 代码审查助手

## Description
当用户请求审查代码、分析代码质量、找 Bug、提出优化建议时触发此技能。
适用于 TypeScript、JavaScript、Python、Vue、React 等前端及全栈技术栈。

## Script
1. 读取用户提供的代码内容或文件路径
2. 分析代码结构、命名规范、逻辑正确性
3. 检查常见问题：内存泄漏、类型错误、性能瓶颈、安全漏洞
4. 给出具体的改进建议，附带修改后的代码示例
5. 按优先级排序：严重问题 > 性能问题 > 代码规范 > 风格建议

## Output Format
- 问题列表（按优先级排序）
- 每个问题附带：问题描述、影响、修复代码示例
- 整体评分（1-10分）和总结

## References
- TypeScript 最佳实践
- ESLint 规范
- Vue3 Composition API 规范
- React Hooks 使用规范
