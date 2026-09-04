import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const STEP_IDS = ['understand', 'assess', 'foundation', 'rewrite', 'measure', 'iterate'] as const;

/**
 * 纯 Wiki 结构：一问一词条。
 *
 * 新增词条：在 src/content/wiki/ 下新建 Markdown 文件即可。
 * 文件名即网址：foo.md → /wiki/foo/
 *
 * 必填：title（问题本身）、answer（一句话结论，页面 TL;DR 与摘要）、step（所属流程步骤）
 * 常用：order、related（参见词条 slug 列表）、tools（工具外链）、publishDate、author
 * step 取值：understand | assess | foundation | rewrite | measure | iterate
 * 步骤定义见 src/lib/workflow.ts
 */
const wiki = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/wiki' }),
  schema: z.object({
    title: z.string(),
    answer: z.string(),
    step: z.enum(STEP_IDS),
    order: z.number().optional(),
    draft: z.boolean().optional().default(false),
    publishDate: z.coerce.date().optional(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().optional(),
    related: z.array(z.string()).optional(),
    tools: z
      .array(
        z.object({
          name: z.string(),
          desc: z.string().optional(),
          url: z.string(),
          badge: z.string().optional(),
        })
      )
      .optional(),
  }),
});

export const collections = { wiki };
