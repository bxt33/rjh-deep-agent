/**
 * Demo 1：基础 Skill 调用
 * 运行命令：npm run demo:basic
 */

import 'dotenv/config'
import { createRJHAgent } from './agent.js'

async function main() {
  const agent = await createRJHAgent({
    name: '大伟 OpenCodex (DeepSeek) - 基础版',
    skillsDir: '.rjh/skills',
    sandbox: { workspacePath: process.cwd(), outputDir: 'output', verbose: true },
    hitl: { enabled: false },
    systemPrompt: '你是一个有趣的 AI 助手，擅长处理古诗词和技术问题。',
  })

  console.log(' 已加载的 Skill：')
  agent.getSkills().forEach(skill => console.log(`  - ${skill.name}`))

  console.log('\n 测试一：诗词笑话生成\n')
  const result1 = await agent.invoke('飞流直下三千尺，疑是银河落九天')
  console.log('\n AI 回复：')
  console.log(result1.content)

  console.log('\n 测试二：另一首诗\n')
  const result2 = await agent.invoke('举头望明月，低头思故乡')
  console.log('\n AI 回复：')
  console.log(result2.content)
}

main().catch(console.error)
