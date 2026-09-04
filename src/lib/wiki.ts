import { getCollection, type CollectionEntry } from 'astro:content';
import { WORKFLOW, getStep, type WorkflowStep } from './workflow';

export type WikiEntry = CollectionEntry<'wiki'>;

export function withBase(path: string): string {
  const base = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${base}${normalized}`;
}

export function entryHref(id: string): string {
  return withBase(`/wiki/${id}/`);
}

export function wikiIndexHref(): string {
  return withBase('/wiki/');
}

export async function getWikiEntries(): Promise<WikiEntry[]> {
  const entries = await getCollection('wiki', ({ data }) => data.draft !== true);
  const stepOrder = (step: string) => {
    const index = WORKFLOW.findIndex((s) => s.id === step);
    return index === -1 ? 99 : index;
  };
  return entries.sort((a, b) => {
    const stepDelta = stepOrder(a.data.step) - stepOrder(b.data.step);
    if (stepDelta !== 0) return stepDelta;
    return (a.data.order ?? 999) - (b.data.order ?? 999);
  });
}

/** 按流程步骤把词条分组，只保留有词条的步骤。 */
export function groupByStep(entries: WikiEntry[]) {
  return WORKFLOW.map((step) => ({
    step,
    entries: entries.filter((e) => e.data.step === step.id),
  })).filter((g) => g.entries.length > 0);
}

export function entryStep(entry: WikiEntry): WorkflowStep | undefined {
  return getStep(entry.data.step);
}

/** 词条的「参见」：related slugs 解析成可渲染对象，容错无效 slug。 */
export function relatedEntries(entries: WikiEntry[], slugs: string[]) {
  return slugs
    .map((slug) => entries.find((e) => e.id === slug))
    .filter((e): e is WikiEntry => Boolean(e))
    .map((e) => ({ href: entryHref(e.id), title: e.data.title, answer: e.data.answer }));
}

export interface SearchItem {
  type: 'entry';
  href: string;
  title: string;
  hint: string;
  topic: string;
  haystack: string;
}

export function buildSearchIndex(entries: WikiEntry[]): SearchItem[] {
  return entries.map((entry) => {
    const step = getStep(entry.data.step);
    return {
      type: 'entry' as const,
      href: entryHref(entry.id),
      title: entry.data.title,
      hint: entry.data.answer,
      topic: step ? step.title : '',
      haystack: `${entry.data.title} ${entry.data.answer} ${step?.title ?? ''}`.toLowerCase(),
    };
  });
}

export function toEntryCard(entry: WikiEntry) {
  const step = getStep(entry.data.step);
  return {
    id: entry.id,
    href: entryHref(entry.id),
    title: entry.data.title,
    answer: entry.data.answer,
    stepTitle: step?.title ?? '',
  };
}
