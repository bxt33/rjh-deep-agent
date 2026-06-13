/**
 * Demo 3：多子智能体协作
 * 场景：生成一份完整的前端技术调研报告
 * 运行命令：npm run demo:multi
 */

import 'dotenv/config'
import { createRJHAgent, type RJHAgent } from './agent.js'
import { TavilySearch } from './tools/tavily-search.js'

// ── 子智能体 A：技术研究员 ──────────────────────────────────
async function researcherAgent(topic: string, search: TavilySearch): Promise<string> {
  console.log(`\n[Researcher] 开始搜索：${topic}`)
  const results = await search.search(topic, 3)
  const summary = results.map((r, i) => `[${i + 1}] ${r.title}\n${r.content}`).join('\n\n')
  console.log(`[Researcher] 搜索完成，获取 ${results.length} 条结果`)
  return summary
}

// ── 子智能体 B：内容分析师 ──────────────────────────────────
async function analystAgent(agent: RJHAgent, rawData: string, aspect: string): Promise<string> {
  console.log(`\n[Analyst] 开始分析：${aspect}`)
  const result = await agent.invoke(`
请分析以下资料，提取关于「${aspect}」的核心观点，用简洁的要点形式输出（3-5点）：

${rawData}

输出格式：
## ${aspect}
- 要点1
- 要点2
- 要点3
`)
  console.log(`[Analyst] 分析完成：${aspect}`)
  return result.content
}

// ── 子智能体 C：文档写手 ────────────────────────────────────
async function writerAgent(
  agent: RJHAgent,
  sections: Record<string, string>,
  title: string
): Promise<string> {
  console.log(`\n[Writer] 开始整合文档：${title}`)
  const sectionsText = Object.entries(sections)
    .map(([key, value]) => `### ${key}\n${value}`)
    .join('\n\n')

  const result = await agent.invoke(`
请将以下各部分内容整合成一份完整、专业的技术调研报告。

报告标题：${title}

各部分内容：
${sectionsText}

要求：
1. 输出完整 Markdown 格式
2. 包含摘要、正文、结论三部分
3. 语言专业简洁
4. 将完整报告写入文件：
\`\`\`filename:tech-research-report.md
（完整报告内容）
\`\`\`
`)
  console.log('[Writer] 文档整合完成')
  return result.content
}

// ── 主智能体编排 ────────────────────────────────────────────
async function main() {
  if (!process.env.TAVILY_API_KEY) {
    console.warn('⚠️  未配置 TAVILY_API_KEY，将使用内置知识运行（跳过网络搜索）')
  }

  const mainAgent = await createRJHAgent({
    name: '智能体 OpenCodex (DeepSeek) - 多智能体协作版',
    skillsDir: '.rjh/skills',
    sandbox: { workspacePath: process.cwd(), outputDir: 'output', verbose: true },
    hitl: { enabled: false },
  })

  const search = process.env.TAVILY_API_KEY
    ? new TavilySearch(process.env.TAVILY_API_KEY)
    : null

  const reportTitle = '2026年前端 AI 智能体开发技术调研报告'
  console.log(`\n 主智能体开始 Planning：${reportTitle}`)
  console.log(' 任务拆解：')
  console.log('  → 子智能体 A (Researcher)：并行搜索各技术方向资料')
  console.log('  → 子智能体 B (Analyst)：并行分析各维度核心观点')
  console.log('  → 子智能体 C (Writer)：整合输出完整报告')

  // ── Step 1：并行搜索 ──
  console.log('\n' + '='.repeat(50))
  console.log(' Step 1：并行搜索阶段')
  console.log('='.repeat(50))

  let frameworkData = 'LangChain 是基础框架，LangGraph 做状态编排，Deep Agent 做通用智能体开箱即用'
  let scenarioData = '前端工程师做 AI 应用有天然优势：TypeScript 支持好，UI 能力强，工程化熟练'

  if (search) {
    ;[frameworkData, scenarioData] = await Promise.all([
      researcherAgent('LangChain LangGraph Deep Agent 框架对比 2025', search),
      researcherAgent('前端工程师 AI 应用开发 TypeScript 智能体 2025', search),
    ])
  }

  // ── Step 2：并行分析 ──
  console.log('\n' + '='.repeat(50))
  console.log(' Step 2：并行分析阶段')
  console.log('='.repeat(50))

  const analystAgentInstance = await createRJHAgent({
    name: '分析师智能体 (DeepSeek)',
    skillsDir: '.rjh/skills',
    sandbox: { workspacePath: process.cwd(), outputDir: 'output', verbose: false },
    hitl: { enabled: false },
  })

  const [frameworkAnalysis, scenarioAnalysis] = await Promise.all([
    analystAgent(mainAgent, frameworkData, '框架选型与对比'),
    analystAgent(analystAgentInstance, scenarioData, '前端工程师的 AI 发展机遇'),
  ])

  // ── Step 3：整合报告 ──
  console.log('\n' + '='.repeat(50))
  console.log('  Step 3：整合输出报告')
  console.log('='.repeat(50))

  await writerAgent(mainAgent, {
    '框架选型与对比': frameworkAnalysis,
    '前端工程师的 AI 发展机遇': scenarioAnalysis,
  }, reportTitle)

  // ── 汇总 ──
  const sandbox = mainAgent.getSandbox()
  if (sandbox) {
    const files = sandbox.listFiles()
    console.log('\n' + '='.repeat(50))
    console.log(' 多智能体协作完成！')
    console.log('='.repeat(50))
    console.log('\n 生成的文件：')
    files.forEach(f => console.log(`  ✅ output/${f}`))

    const report = sandbox.readFile('tech-research-report.md')
    if (report) {
      console.log('\n 报告预览（前 600 字）：')
      console.log('─'.repeat(50))
      console.log(report.slice(0, 600) + (report.length > 600 ? '\n...' : ''))
    }
  }
}

main().catch(console.error)
