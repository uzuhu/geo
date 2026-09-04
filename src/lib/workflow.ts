/**
 * 做 GEO 的流程模型：站点主入口按「流程步骤」组织。
 * 每一步回答三件事：用户会遇到什么问题（FAQ 内联展开）、我们的建议（文章）、可用工具（外链）。
 */

export interface WorkflowTool {
  name: string;
  desc: string;
  url: string;
  badge?: string; // 免费 / 试用 / 付费
}

export interface WorkflowStep {
  id: string;
  title: string;
  goal: string; // 这一步要达成什么（一句话）
  when: string; // 用户在这一步的处境
  guideIds: string[]; // 建议阅读的文章（slug）
  /** 可选：按问题关键词挑 FAQ 子串，避免同一条问题在多步重复出现 */
  faqPicks?: string[];
  tools: WorkflowTool[];
}

export const WORKFLOW: WorkflowStep[] = [
  {
    id: 'understand',
    title: '建立认知',
    goal: '搞清 GEO 是什么、和 SEO 什么关系、值不值得投入。',
    when: '刚听说 GEO，不确定它是不是又一个营销概念。',
    guideIds: ['what-is-geo', 'geo-vs-seo'],
    tools: [],
  },
  {
    id: 'assess',
    title: '摸清现状',
    goal: '先知道你的内容现在有没有被 AI 引用、被怎么说。',
    when: '想动手，但不知道自己起点在哪。',
    guideIds: ['measure-geo'],
    faqPicks: ['没有预算'],
    tools: [
      {
        name: 'ChatGPT / Perplexity 直接问',
        desc: '最便宜的检测：拿 10 个客户会问的提示词，直接问 AI，看有没有引用你。零成本，适合起步。',
        url: 'https://chatgpt.com/',
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
        desc: '多模型引用追踪，覆盖 ChatGPT、Perplexity、Gemini、Claude，适合中小团队持续监测。',
        url: 'https://www.peec.ai/',
        badge: '试用',
      },
    ],
  },
  {
    id: 'foundation',
    title: '配好地基',
    goal: '让 AI 爬虫能来、能抓、能看懂你的页面结构。',
    when: '内容不错，但 AI 可能根本读不到。',
    guideIds: ['ai-crawlers'],
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
    title: '改造内容',
    goal: '把页面改成 AI 愿意直接引用的「答案」，而不是需要再总结的长文。',
    when: '地基没问题，但 AI 就是不引用你。',
    guideIds: ['geo-strategies', 'geo-playbook'],
    faqPicks: ['哪一项', '关键词堆砌', '信息增益', '单篇内容', 'llms.txt'],
    tools: [],
  },
  {
    id: 'measure',
    title: '衡量效果',
    goal: '用数据回答「有没有效」，而不是凭感觉。',
    when: '改了一阵子，不知道该向老板/自己证明什么。',
    guideIds: ['measure-geo'],
    faqPicks: ['Search Console', '最重要的指标'],
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
    guideIds: ['geo-playbook'],
    faqPicks: ['多久', '优先级'],
    tools: [],
  },
];

const stepMap = new Map(WORKFLOW.map((s) => [s.id, s]));

export function getStep(id: string): WorkflowStep | undefined {
  return stepMap.get(id);
}
