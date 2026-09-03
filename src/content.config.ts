import { defineCollection } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';
import { z } from 'astro/zod';

// 知识库文档集合：在 Starlight 默认 frontmatter 之上扩展 GEO/SEO 字段
export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        // 发布日期（用于 TechArticle.datePublished）
        publishDate: z.coerce.date().optional(),
        // 更新日期（用于 TechArticle.dateModified）
        updatedDate: z.coerce.date().optional(),
        // 作者（用于 TechArticle.author）
        author: z.string().optional(),
        // 核心要点（Key Takeaways 高亮卡片）
        takeaways: z.array(z.string()).optional(),
        // 常见问题（自动生成 FAQPage 结构化数据）
        faq: z
          .array(
            z.object({
              question: z.string(),
              answer: z.string(),
            })
          )
          .optional(),
      }),
    }),
  }),
};
