import { withBase } from './guides';
import type { TopicId } from './topics';

export const SCENARIO_IDS = ['cite', 'config', 'measure', 'explain', 'rewrite'] as const;

export type ScenarioId = (typeof SCENARIO_IDS)[number];

export interface Scenario {
  id: ScenarioId;
  label: string;
  question: string;
  blurb: string;
  topics: TopicId[];
}

/**
 * 任务场景：按"用户正在做的事"组织，而不是按目录主题。
 * topics 决定该场景聚合哪些主题的问答与文章。
 */
export const SCENARIOS: Scenario[] = [
  {
    id: 'cite',
    label: '被引用',
    question: '让 AI 引用我的内容',
    blurb: '我的博客 / 文章想被 ChatGPT、Claude、Perplexity 提到',
    topics: ['strategy'],
  },
  {
    id: 'config',
    label: '配地基',
    question: '把技术地基配好',
    blurb: 'robots.txt、爬虫放行、JSON-LD、sitemap 怎么搞',
    topics: ['technical'],
  },
  {
    id: 'measure',
    label: '看效果',
    question: '知道有没有效果',
    blurb: '怎么衡量 GEO，怎么跟老板汇报',
    topics: ['measure'],
  },
  {
    id: 'explain',
    label: '讲清楚',
    question: '跟人讲清 GEO',
    blurb: '是什么、跟 SEO 有啥区别、值不值得做',
    topics: ['intro', 'compare'],
  },
  {
    id: 'rewrite',
    label: '照着改',
    question: '照着改我的页面',
    blurb: '给我可照做的步骤和复制即用的模板',
    topics: ['strategy', 'technical'],
  },
];

const scenarioMap = new Map(SCENARIOS.map((s) => [s.id, s]));

export function getScenario(id: string): Scenario {
  return scenarioMap.get(id as ScenarioId) ?? SCENARIOS[0];
}

export function scenarioHref(id: string): string {
  return withBase(`/scenarios/${id}/`);
}
