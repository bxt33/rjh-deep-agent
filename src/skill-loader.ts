/**
 * Skill 加载器
 * 扫描 .rjh/skills 目录，读取所有 .skill.md 文件并解析成结构化数据
 */

import fs from 'fs'
import path from 'path'

export interface Skill {
  name: string
  fileName: string
  description: string
  script: string
  examples?: string
  outputFormat?: string
  references?: string
  raw: string
}

/**
 * 解析单个 .skill.md 文件
 */
function parseSkillFile(filePath: string): Skill {
  const raw = fs.readFileSync(filePath, 'utf-8')
  const lines = raw.split('\n')

  // 提取技能名称（第一个 # 标题）
  const nameMatch = lines.find(l => l.startsWith('# '))
  const name = nameMatch ? nameMatch.replace('# ', '').trim() : path.basename(filePath, '.skill.md')    
  // path.basename  是什么意思 const filePath = '/Users/david/skills/vue.skill.md' console.log(path.basename(filePath)) 输出 vue.skill.md




  // 按 ## 章节分割
  const sections: Record<string, string> = {}
  let currentSection = ''
  let currentContent: string[] = []

  for (const line of lines) {
    if (line.startsWith('## ')) {
      if (currentSection) {
        sections[currentSection] = currentContent.join('\n').trim()
      }
      currentSection = line.replace('## ', '').trim()
      currentContent = []
    } else if (!line.startsWith('# ')) {
      currentContent.push(line)
    }
  }
  // 保存最后一个章节
  if (currentSection) {
    sections[currentSection] = currentContent.join('\n').trim()
  }

  return {
    name,
    fileName: path.basename(filePath),
    description: sections['Description'] || '',
    script: sections['Script'] || '',
    examples: sections['Examples'],
    outputFormat: sections['Output Format'],
    references: sections['References'],
    raw,
  }
}

/**
 * 加载指定目录下所有 .skill.md 文件
 */
export function loadSkills(skillsDir: string): Skill[] {
  const resolvedDir = path.resolve(skillsDir)

  if (!fs.existsSync(resolvedDir)) {
    console.warn(`[SkillLoader] 目录不存在：${resolvedDir}`)
    return []
  }

  const files = fs.readdirSync(resolvedDir)
  const skillFiles = files.filter(f => f.endsWith('.skill.md'))

  if (skillFiles.length === 0) {
    console.warn(`[SkillLoader] 未找到任何 .skill.md 文件：${resolvedDir}`)
    return []
  }

  const skills = skillFiles.map(file => {
    const filePath = path.join(resolvedDir, file)
    const skill = parseSkillFile(filePath)
    console.log(`[SkillLoader] 已加载技能：${skill.name} (${file})`)
    return skill
  })

  return skills
}

/**
 * 将 Skill 列表格式化成 SystemPrompt 中的技能说明
 */
export function buildSkillsPrompt(skills: Skill[]): string {
  if (skills.length === 0) return ''

  const skillDescriptions = skills
    .map((skill, index) => {
      let desc = `${index + 1}. **${skill.name}**\n   触发条件：${skill.description}`
      if (skill.examples) {
        const firstExample = skill.examples.split('\n').slice(0, 2).join('\n')
        desc += `\n   示例：${firstExample}`
      }
      return desc
    })
    .join('\n\n')

  return `
## 你具备以下专项技能（Skill）

${skillDescriptions}

当用户的输入符合某个技能的触发条件时，请主动调用该技能的执行逻辑来处理任务。
`
}
