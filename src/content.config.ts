import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const TOPIC_IDS = ['intro', 'compare', 'strategy', 'measure', 'technical'] as const;

/**
 * 新增文章：在 src/content/guides/ 下新建 Markdown 文件即可。
 * 文件名即网址：foo.md → /guides/foo/
 *
 * 必填：title、description、topic
 * 常用：kicker、order、takeaways、faq、publishDate、author
 * topic 取值：intro | compare | strategy | measure | technical
 * kind 取值：concept | recipe | template | tool | example | qa（内容类型，用于按"应用"组织）
 * 若要新增主题，先改 src/lib/topics.ts
 */
const guides = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    topic: z.enum(TOPIC_IDS),
    kind: z.enum(['concept', 'recipe', 'template', 'tool', 'example', 'qa']).optional(),
    kicker: z.string().optional(),
    order: z.number().optional(),
    featured: z.boolean().optional(),
    draft: z.boolean().optional().default(false),
    publishDate: z.coerce.date().optional(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().optional(),
    takeaways: z.array(z.string()).optional(),
    faq: z
      .array(
        z.object({
          question: z.string(),
          answer: z.string(),
        })
      )
      .optional(),
  }),
});

export const collections = { guides };
