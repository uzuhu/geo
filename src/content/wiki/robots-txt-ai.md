---
title: "对 AI 友好的 robots.txt 怎么写？"
answer: "每个主流 AI 爬虫（GPTBot、ClaudeBot、PerplexityBot、Google-Extended 等）单独成段并 Allow: /，底部带上指向绝对地址的 Sitemap。可直接抄下面的模板。"
step: foundation
order: 2
publishDate: 2026-09-04
author: "阿虎 / zuwho"
related: [ai-crawlers-blocked, verify-ai-crawler-access, llms-txt]
---

将以下内容放到站点根目录的 `robots.txt`：

```txt
# 放行主流搜索引擎
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

# 放行主流 AI / 生成式引擎爬虫
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot
Allow: /

User-agent: CCBot
Allow: /

# 站点地图（务必指向含部署子路径的绝对地址）
Sitemap: https://your-domain.com/sitemap-index.xml
```

## 要点

- 每个 `User-agent` 单独成段，`Allow: /` 表示全站放行；
- 底部 `Sitemap:` 必须是**绝对地址**，且含部署子路径（若站点部署在子目录下，如 `/geo/`，地址里要带上）；
- 若只想对部分目录限制，可改用 `Disallow: /private/`；
- **建议全部放行**：上述爬虫代表了当前主流的生成式检索与训练来源，对以「被引用」为目标的 GEO 站点，全部放行通常不会带来负面效果，反而扩大被纳入答案来源集的机会。

配好后记得验证生效，见 [怎么验证 AI 爬虫能访问我的页面？](../verify-ai-crawler-access/)。

## 相关词条

- [AI 爬虫有哪几类？不放行会怎样？](../ai-crawlers-blocked/)
- [怎么验证 AI 爬虫能访问我的页面？](../verify-ai-crawler-access/)
- [llms.txt 是什么，必须做吗？](../llms-txt/)
