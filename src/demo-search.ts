/**
 * Demo 2：搜索 + 写文件完整链路
 * 需要：TAVILY_API_KEY 环境变量
 * 运行命令：npm run demo:search
 */

import 'dotenv/config'
import { createRJHAgent } from './agent.js'
import { TavilySearch } from './tools/tavily-search.js'

async function main() {
  if (!process.env.TAVILY_API_KEY) {
    console.error('❌ 缺少 TAVILY_API_KEY，请在 .env 中配置')
    console.log('   获取地址：https://app.tavily.com/ (免费额度每月 1000 次)')
    process.exit(1)
  }

  const search = new TavilySearch(process.env.TAVILY_API_KEY)

  const agent = await createRJHAgent({
    name: '智能体 OpenCodex (DeepSeek) - 搜索版',
    skillsDir: '.rjh/skills',
    sandbox: { workspacePath: process.cwd(), outputDir: 'output', verbose: true },
    hitl: { enabled: false },
    systemPrompt: `
你是一个具备网络搜索能力的 AI 助手，由 DeepSeek 驱动。
需要写文件时请用：
\`\`\`filename:文件名.md
内容
\`\`\`
`,
  })

  const query = 'LangChain Deep Agent 快速入门教程 2026'
  console.log(`\n 搜索关键词：${query}`)

  const searchResults = await search.search(query)
  console.log(`[Search] 获取到 ${searchResults.length} 条结果`)

  const userMessage = `
请根据以下搜索结果，总结 LangChain Deep Agent 的核心概念和快速入门步骤，
输出一份清晰的中文学习笔记，并保存到文件 deep-agent-notes.md。

搜索结果：
${searchResults.map((r, i) => `[${i + 1}] ${r.title}\n来源：${r.url}\n摘要：${r.content}`).join('\n---\n')}

要求：
1. 用简洁的中文总结
2. 包含核心概念解释
3. 包含快速入门步骤
4. 写入文件 deep-agent-notes.md
`

  const result = await agent.invokeStream(userMessage)

  if (result.filesWritten.length === 0) {
    const sandbox = agent.getSandbox()
    if (sandbox) {
      sandbox.writeFile('deep-agent-notes.md', result.content)
      console.log('\n✅ 已手动保存结果到 output/deep-agent-notes.md')
    }
  }
}

main().catch(console.error)
