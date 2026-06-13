/**
 * HITL（Human-in-the-Loop）人为参与机制
 * 当智能体执行到高风险操作时，主动中断并等待人工确认
 * 对应第一讲介绍的 HITL 概念
 */

import readline from 'readline'

/** 高风险操作关键词 */
const HIGH_RISK_KEYWORDS = [
  'rm -rf',
  'drop table',
  'delete from',
  'format',
  'sudo',
  'chmod 777',
  '删除所有',
  '清空数据库',
  '格式化',
]

export interface HitlConfig {
  /** 是否开启 HITL（默认 true） */
  enabled?: boolean
  /** 自定义高风险关键词 */
  extraKeywords?: string[]
  /** 自动同意（用于自动化测试，生产环境不要开） */
  autoApprove?: boolean
}

/**
 * 检测操作内容是否包含高风险关键词
 */
export function isHighRiskOperation(content: string, extraKeywords: string[] = []): boolean {
  const keywords = [...HIGH_RISK_KEYWORDS, ...extraKeywords]
  const lower = content.toLowerCase()
  return keywords.some(kw => lower.includes(kw.toLowerCase()))
}

/**
 * 等待用户在终端输入确认
 */
async function waitForConfirmation(prompt: string): Promise<boolean> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  })

  return new Promise(resolve => {
    rl.question(prompt, answer => {
      rl.close()
      resolve(answer.trim().toLowerCase() === 'y' || answer.trim().toLowerCase() === 'yes')
    })
  })
}

/**
 * HITL 检查点
 * 在执行高风险操作前调用，返回是否允许继续执行
 */
export async function hitlCheckpoint(
  operationDesc: string,
  config: HitlConfig = {}
): Promise<boolean> {
  const { enabled = true, extraKeywords = [], autoApprove = false } = config

  if (!enabled) return true

  if (!isHighRiskOperation(operationDesc, extraKeywords)) return true

  // 高风险操作，触发人工审核
  console.log('\n' + '='.repeat(50))
  console.log('⚠️  [HITL] 检测到高风险操作，需要人工确认')
  console.log('='.repeat(50))
  console.log(`操作描述：${operationDesc}`)
  console.log('='.repeat(50))

  if (autoApprove) {
    console.log('[HITL] 自动同意模式，继续执行...\n')
    return true
  }

  const approved = await waitForConfirmation('\n请确认是否继续执行？(y/n): ')

  if (approved) {
    console.log('[HITL] 已确认，继续执行...\n')
  } else {
    console.log('[HITL] 已拒绝，操作中止。\n')
  }

  return approved
}
