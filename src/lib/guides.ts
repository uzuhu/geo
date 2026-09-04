import { getCollection, type CollectionEntry } from 'astro:content';
import { getTopic, type TopicId } from './topics';

export type GuideEntry = CollectionEntry<'guides'>;

export function withBase(path: string): string {
  const base = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${base}${normalized}`;
}

export function guideHref(id: string): string {
  return withBase(`/guides/${id}/`);
}

export function topicHref(id: string): string {
  return withBase(`/topics/${id}/`);
}

export async function getPublishedGuides(): Promise<GuideEntry[]> {
  const guides = await getCollection('guides', ({ data }) => data.draft !== true);
  return guides.sort((a, b) => {
    const orderA = a.data.order ?? 999;
    const orderB = b.data.order ?? 999;
    if (orderA !== orderB) return orderA - orderB;
    const dateA = a.data.publishDate?.getTime() ?? 0;
    const dateB = b.data.publishDate?.getTime() ?? 0;
    return dateB - dateA;
  });
}

export function neighbors(guides: GuideEntry[], id: string) {
  const index = guides.findIndex((guide) => guide.id === id);
  return {
    prev: index > 0 ? guides[index - 1] : undefined,
    next: index >= 0 && index < guides.length - 1 ? guides[index + 1] : undefined,
  };
}

export function relatedGuides(guides: GuideEntry[], current: GuideEntry, limit = 3) {
  const others = guides.filter((guide) => guide.id !== current.id);
  const sameTopic = others.filter((guide) => guide.data.topic === current.data.topic);
  const rest = others.filter((guide) => guide.data.topic !== current.data.topic);
  return [...sameTopic, ...rest].slice(0, limit);
}

export interface SearchItem {
  type: 'guide' | 'faq';
  href: string;
  title: string;
  hint: string;
  topic: string;
  haystack: string;
}

export function buildSearchIndex(guides: GuideEntry[]): SearchItem[] {
  const items: SearchItem[] = [];
  for (const guide of guides) {
    const topic = getTopic(guide.data.topic as TopicId);
    const href = guideHref(guide.id);
    const takeaways = (guide.data.takeaways ?? []).join(' ');
    items.push({
      type: 'guide',
      href,
      title: guide.data.title,
      hint: guide.data.description,
      topic: topic.label,
      haystack: [
        guide.data.title,
        guide.data.description,
        guide.data.kicker ?? '',
        topic.label,
        topic.question,
        takeaways,
      ]
        .join(' ')
        .toLowerCase(),
    });
    for (const faq of guide.data.faq ?? []) {
      items.push({
        type: 'faq',
        href: `${href}#${faqId(faq.question)}`,
        title: faq.question,
        hint: `${guide.data.title} · ${faq.answer}`,
        topic: topic.label,
        haystack: `${faq.question} ${faq.answer} ${guide.data.title}`.toLowerCase(),
      });
    }
  }
  return items;
}

export function faqId(question: string): string {
  const slug = question
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 48);
  return `faq-${slug || 'q'}`;
}

export function toCard(guide: GuideEntry) {
  const topic = getTopic(guide.data.topic as TopicId);
  return {
    id: guide.id,
    href: guideHref(guide.id),
    title: guide.data.title,
    description: guide.data.description,
    kicker: guide.data.kicker ?? topic.label,
    topic: topic.label,
    topicId: topic.id,
    featured: Boolean(guide.data.featured),
    order: guide.data.order,
  };
}
