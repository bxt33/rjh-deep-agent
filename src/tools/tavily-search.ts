/**
 * Tavily 搜索工具
 * 专为 AI 智能体优化的搜索引擎，适合在 Agent 中使用
 * 获取 Key：https://app.tavily.com/ （免费额度每月 1000 次）
 */

export interface SearchResult {
  title: string
  url: string
  content: string
  score: number
}

export class TavilySearch {
  private apiKey: string
  private baseUrl = 'https://api.tavily.com/search'

  constructor(apiKey: string) {
    this.apiKey = apiKey
  }

  /**
   * 执行搜索
   * @param query 搜索关键词
   * @param maxResults 最大返回数量，默认 5
   */
  async search(query: string, maxResults = 5): Promise<SearchResult[]> {
    console.log(`[TavilySearch] 搜索：${query}`)

    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify({
          query,
          max_results: maxResults,
          search_depth: 'basic',
          include_answer: false,
          include_raw_content: false,
        }),
      })

      if (!response.ok) {
        throw new Error(`Tavily API 错误：${response.status} ${response.statusText}`)
      }

      const data = (await response.json()) as {
        results: Array<{
          title: string
          url: string
          content: string
          score: number
        }>
      }

      console.log(`[TavilySearch] 获取到 ${data.results.length} 条结果`)

      return data.results.map(r => ({
        title: r.title,
        url: r.url,
        content: r.content.slice(0, 800), // 截取前 800 字符，控制 Token 用量
        score: r.score,
      }))
    } catch (err) {
      console.error('[TavilySearch] 搜索失败：', err)
      return []
    }
  }
}
