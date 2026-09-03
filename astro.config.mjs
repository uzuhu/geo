// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // 站点根域名（GitHub Pages 项目页：https://uzuhu.github.io/geo/）
  site: 'https://uzuhu.github.io',
  // GitHub Pages 子路径前缀
  base: '/geo',

  integrations: [
    starlight({
      title: 'GEO 知识库',
      description: '生成式引擎优化（GEO）与 SEO 实战知识库 —— 面向 AI 爬虫与搜索引擎的结构化内容。',
      // 默认语言
      defaultLocale: 'root',
      locales: {
        root: { label: '简体中文', lang: 'zh-CN' },
      },
      // 右上角社交链接
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/uzuhu/geo' },
      ],
      // 自定义样式（Key Takeaways 卡片等）
      customCss: ['./src/styles/custom.css'],
      // GEO / SEO 二次开发：覆盖 Head 注入 JSON-LD、覆盖 PageTitle 注入核心要点卡片、
      // 覆盖 MarkdownContent 输出语义化 <article>/<section>
      components: {
        Head: './src/components/Head.astro',
        PageTitle: './src/components/PageTitle.astro',
        MarkdownContent: './src/components/MarkdownContent.astro',
      },
    }),
    // 编译时自动生成 sitemap-index.xml
    sitemap(),
  ],
});
