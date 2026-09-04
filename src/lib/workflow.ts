/**
 * 做 GEO 的科学流程模型：站点主入口按「流程步骤」组织。
 * 流程依据 2025-2026 主流 GEO 实操框架归纳：
 * 现状诊断（含竞品）→ 问询词规划 → 技术基建 → 官网内容改造 →
 * 站外多平台发布（含视频等多模态）→ 监测 → 迭代。
 * 每一步聚合属于该步骤的 wiki 词条（一问一页的完整答案）与工具外链。
 */

export interface WorkflowTool {
  name: string;
  desc: string;
  url: string;
  badge?: string; // 免费 / 试用 / 付费
}

export interface WorkflowStep {
  id: 'understand' | 'assess' | 'foundation' | 'rewrite' | 'distribute' | 'measure' | 'iterate';
  title: string;
  goal: string; // 这一步要达成什么（一句话）
  when: string; // 用户在这一步的处境
  tools: WorkflowTool[];
}

export const WORKFLOW: WorkflowStep[] = [
  {
    id: 'understand',
    title: '看懂 GEO',
    goal: '搞清 GEO 是什么、和 SEO 什么关系、值不值得投入。',
    when: '刚听说 GEO，不确定它是不是又一个营销概念。',
    tools: [],
  },
  {
    id: 'assess',
    title: '分析现状',
    goal: '用统一提示词测自己和竞品在各大 AI 里的出现率、顺位与被引来源，找到差距。',
    when: '想知道：我在 AI 眼里什么样？竞品为什么被引用而我不是？',
    tools: [
      {
        name: 'ChatGPT / Perplexity 直接问',
        desc: '最便宜的检测：拿 10 个客户会问的提示词，直接问 AI，看有没有引用你、怎么描述你。零成本，适合起步。',
        url: 'https://chatgpt.com/',
        badge: '免费',
      },
      {
        name: 'HubSpot AI Search Grader',
        desc: '输入品牌与产品描述，免费生成一份 AI 搜索表现评分：品牌知名度、情感倾向、推荐意愿。',
        url: 'https://www.hubspot.com/ai-search-grader',
        badge: '免费',
      },
      {
        name: 'Otterly.AI',
        desc: '品牌在 ChatGPT、Perplexity、AI Overviews 中的引用监测，带品牌可见度指数与竞品对比。',
        url: 'https://otterly.ai/',
        badge: '试用',
      },
      {
        name: 'Peec AI',
        desc: '多模型引用追踪，覆盖 ChatGPT、Perplexity、Gemini、Claude，适合中小团队持续监测竞品差距。',
        url: 'https://www.peec.ai/',
        badge: '试用',
      },
      {
        name: 'Profound',
        desc: '企业级 AI 可见度分析平台：提示词级监测、竞品份额、消费者洞察，适合有预算的成熟团队。',
        url: 'https://www.profound.com/',
        badge: '付费',
      },
    ],
  },
  {
    id: 'foundation',
    title: '打好技术地基',
    goal: '让 AI 爬虫能来、能抓、能看懂你的页面结构。',
    when: '内容不错，但 AI 可能根本读不到。',
    tools: [
      {
        name: 'Google Search Console',
        desc: '确认 Googlebot 抓取正常、提交 sitemap。SEO 地基，也是 GEO 地基。',
        url: 'https://search.google.com/search-console',
        badge: '免费',
      },
      {
        name: 'Bing Webmaster Tools',
        desc: 'ChatGPT 的检索底座是 Bing，在这里提交站点对被 ChatGPT 引用有直接帮助。',
        url: 'https://www.bing.com/webmasters',
        badge: '免费',
      },
      {
        name: 'Rich Results Test',
        desc: '验证页面 JSON-LD 结构化数据能否被正确解析。',
        url: 'https://search.google.com/test/rich-results',
        badge: '免费',
      },
      {
        name: 'Schema Markup Validator',
        desc: '官方 Schema.org 校验器，检查 TechArticle、FAQPage 等 markup 的正确性。',
        url: 'https://validator.schema.org/',
        badge: '免费',
      },
    ],
  },
  {
    id: 'rewrite',
    title: '改造官网内容',
    goal: '把页面改成 AI 愿意直接引用的「答案」，而不是需要再总结的长文。',
    when: '地基没问题，但 AI 就是不引用你。',
    tools: [],
  },
  {
    id: 'distribute',
    title: '外部发布造声量',
    goal: '在站外平台发布内容、建设实体权威——AI 只信「多处都说」的信息。',
    when: '官网改好了，但全网只有我自己在说自己好。',
    tools: [
      {
        name: 'Wikipedia / Wikidata',
        desc: '最高权重的实体信源，AI 检索与训练都常用。需要有可靠第三方来源才可建条目。',
        url: 'https://www.wikidata.org/',
        badge: '免费',
      },
      {
        name: 'Google Business Profile',
        desc: '完善品牌实体信息，Google 知识图谱与 AI Overviews 都会读取。',
        url: 'https://business.google.com/',
        badge: '免费',
      },
      {
        name: 'YouTube',
        desc: '视频是 GEO 的多模态资产：ChatGPT 已引用 YouTube 内容。记得上传字幕、章节与文字说明。',
        url: 'https://www.youtube.com/',
        badge: '免费',
      },
    ],
  },
  {
    id: 'measure',
    title: '衡量效果',
    goal: '用数据回答「有没有效」，而不是凭感觉。',
    when: '改了一阵子，不知道该向老板/自己证明什么。',
    tools: [
      {
        name: 'Semrush AI Visibility Toolkit',
        desc: '跟踪品牌在 ChatGPT、AI Overviews、Perplexity 等平台的可见度与情感，附 AI 抓取问题站点审计。',
        url: 'https://www.semrush.com/',
        badge: '试用',
      },
      {
        name: 'Ahrefs Brand Radar',
        desc: '监测各 AI 引擎里品牌被提及与被引用的页面，Ahrefs 用户可一站式对照传统 SEO 数据。',
        url: 'https://ahrefs.com/',
        badge: '付费',
      },
    ],
  },
  {
    id: 'iterate',
    title: '持续迭代',
    goal: '把 GEO 变成每周的常规动作，而不是一次性项目。',
    when: '有了初步效果，怕做完就停滞。',
    tools: [],
  },
];

const stepMap = new Map(WORKFLOW.map((s) => [s.id, s]));

export function getStep(id: string): WorkflowStep | undefined {
  return stepMap.get(id as WorkflowStep['id']);
}
