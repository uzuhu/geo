export const TOPIC_IDS = ['intro', 'compare', 'strategy', 'measure', 'technical'] as const;

export type TopicId = (typeof TOPIC_IDS)[number];

export interface Topic {
  id: TopicId;
  label: string;
  question: string;
  hint: string;
}

export const TOPICS: Topic[] = [
  {
    id: 'intro',
    label: '入门',
    question: 'GEO 是什么？',
    hint: '先建立概念，再谈优化',
  },
  {
    id: 'compare',
    label: '对照',
    question: '和 SEO 有什么不同？',
    hint: '两套目标，一条链路',
  },
  {
    id: 'strategy',
    label: '策略',
    question: '怎么写才会被引用？',
    hint: '被验证过的内容战术',
  },
  {
    id: 'measure',
    label: '度量',
    question: '怎么知道有没有效果？',
    hint: 'KPI 与 Prompt Panel',
  },
  {
    id: 'technical',
    label: '技术',
    question: 'AI 爬虫怎么放行？',
    hint: 'robots.txt 与抓取地基',
  },
];

const topicMap = new Map(TOPICS.map((topic) => [topic.id, topic]));

export function getTopic(id: string): Topic {
  return (
    topicMap.get(id as TopicId) ?? {
      id: 'intro',
      label: id,
      question: id,
      hint: '',
    }
  );
}
