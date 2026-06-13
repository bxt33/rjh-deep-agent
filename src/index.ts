/**
 * 主入口：交互式对话模式
 * 运行命令：npm run dev
 */

import 'dotenv/config'
import readline from 'readline'
import { createRJHAgent } from './agent.js'

async function main() {
  const agent = await createRJHAgent({
    name: '大伟 OpenCodex (DeepSeek)',
    skillsDir: '.rjh/skills',
    sandbox: {
      workspacePath: process.cwd(),
      outputDir: 'output',
      verbose: true,
    },
    hitl: { enabled: true, autoApprove: false },
    systemPrompt: `
你是大伟 OpenCodex，一个专业的前端 + AI 全栈智能体，由 DeepSeek 驱动。
你擅长：
- TypeScript / Vue3 / React 开发
- Java / Spring Boot / Python 开发
- LangChain / Deep Agent AI 应用开发
- 代码审查和架构设计
- 技术文档生成
请用中文回复，需要写文件时使用规定的 filename 格式。
`,
  })

  console.log('\n 大伟 OpenCodex (DeepSeek) 已就绪！')
  console.log(' 已加载技能：')
  agent.getSkills().forEach(s => console.log(`   - ${s.name}`))
  console.log('\n 输入你的任务（输入 exit 退出，输入 clear 清空对话历史）')
  console.log('─'.repeat(50))

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  const askQuestion = (prompt: string): Promise<string> =>
    new Promise(resolve => rl.question(prompt, resolve))

  while (true) {
    const userInput = await askQuestion('\n你：')

    if (userInput.trim().toLowerCase() === 'exit') {
      console.log('\n 再见！')
      rl.close()
      break
    }
    if (userInput.trim().toLowerCase() === 'clear') {
      agent.clearHistory()
      continue
    }
    if (!userInput.trim()) continue

    process.stdout.write('\n 智能体：\n')
    await agent.invokeStream(userInput)
  }
}

main().catch(console.error)
