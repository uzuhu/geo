// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const BASE = '/geo'; // 与 base 配置保持一致

/**
 * rehype 插件：把词条正文里的相对链接改写成带 base 的绝对链接。
 * 背景：词条正文同时在 /wiki/<slug>/ 独立页和首页阅读器（/）两处渲染，
 * `../foo/` 这类相对链接在首页会解析错误。构建期统一改写：
 *   ../foo/      → /geo/wiki/foo/   （词条互链，视为同目录兄弟词条）
 *   ../../tools/ → /geo/tools/      （指向站点根下的路径）
 */
function rehypeBaseLinks() {
  function walk(node) {
    if (node.type === 'element' && node.tagName === 'a' && node.properties) {
      const href = node.properties.href;
      if (typeof href === 'string') {
        const m = href.match(/^((?:\.\.\/)+)([\w-]+)\/$/);
        if (m) {
          const levels = m[1].length / 3; // '../'.length === 3
          const slug = m[2];
          node.properties.href =
            levels === 1 ? `${BASE}/wiki/${slug}/` : `${BASE}/${slug}/`;
        }
      }
    }
    for (const child of node.children ?? []) walk(child);
  }
  return (tree) => walk(tree);
}

export default defineConfig({
  site: 'https://uzuhu.github.io',
  base: '/geo',
  trailingSlash: 'always',
  prefetch: true,
  integrations: [sitemap()],
  markdown: {
    rehypePlugins: [rehypeBaseLinks],
    shikiConfig: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
    },
  },
});
