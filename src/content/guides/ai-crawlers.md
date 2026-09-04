---
title: "AI 爬虫与 robots.txt 配置"
kicker: "技术配置"
topic: technical
order: 5
description: "生成式引擎要引用你的内容，第一步是能抓到它。本文列出主流 AI 爬虫（GPTBot、ClaudeBot、PerplexityBot、Google-Extended 等），给出对 AI 友好的 robots.txt 范例，以及验证爬虫可访问性的方法。"
publishDate: 2026-09-03
updatedDate: 2026-09-03
author: "阿虎 / zuwho"
takeaways:
  - "生成式引擎要引用你的内容，前提是它的爬虫能抓到页面——放行 AI 爬虫是 GEO 的技术地基。"
  - "主流 AI 爬虫包括：Googlebot、Bingbot、GPTBot（OpenAI）、ClaudeBot（Anthropic）、PerplexityBot、Google-Extended、Applebot。"
  - "在 robots.txt 中放行这些 UA，并在底部带上 Sitemap 链接，可显著提升被 AI 检索与引用的机会。"
  - "本站 robots.txt 已默认放行上述爬虫，并指向 https://uzuhu.github.io/geo/sitemap-index.xml。"
faq:
  - question: "不放行 AI 爬虫会怎样？"
    answer: "如果 robots.txt 禁止了 GPTBot、ClaudeBot 等，对应的生成式引擎将无法抓取你的页面，自然也不会在答案中引用你。放行它们是 GEO 的技术前提。"
  - question: "Google-Extended 和 Googlebot 有什么区别？"
    answer: "Googlebot 服务于传统搜索与 AI Overviews；Google-Extended 是 Google 用于训练与生成式 AI 产品的抓取令牌（token），专门覆盖 Gemini 等生成式场景。两者建议都放行。"
  - question: "怎么验证 AI 爬虫能访问我的页面？"
    answer: "先用各大平台官方提供的验证方式（如 Google 的 robots.txt 测试工具）确认未被屏蔽；再用 curl 模拟对应 UA 抓取关键页面，确认返回 200 且正文可读。"
---

## 为什么放行 AI 爬虫是 GEO 的地基

GEO 的「生成阶段」依赖「检索阶段」：生成式引擎先用爬虫抓取网页，再综合成答案。如果你的 `robots.txt` 把 AI 爬虫挡在门外，对应的引擎**根本读不到你的内容**，更不可能引用你。

> 这和密码学里「先能通信，再谈安全」同理：先让 AI 抓得到，才有资格谈「被引用」。

## 主流 AI 爬虫清单

| 爬虫 UA | 所属方 | 用途 |
| --- | --- | --- |
| `Googlebot` | Google | 传统搜索 + AI Overviews |
| `Bingbot` | Microsoft | Bing 搜索 + Copilot |
| `GPTBot` | OpenAI | ChatGPT 网页检索与引用 |
| `ClaudeBot` | Anthropic | Claude 网页检索与引用 |
| `PerplexityBot` | Perplexity | Perplexity 答案引擎 |
| `Google-Extended` | Google | Gemini 等生成式 AI 产品 |
| `Applebot` / `Applebot-Extended` | Apple | Apple 智能（Apple Intelligence） |
| `CCBot` | Common Crawl | 许多模型训练数据来源 |

> **📝 建议全部放行**：上述爬虫代表了当前主流的生成式检索与训练来源。对以「被引用」为目标的 GEO 站点，全部放行通常不会带来负面效果，反而扩大被纳入答案来源集的机会。

## 对 AI 友好的 robots.txt 范例

将以下内容放到站点根目录的 `public/robots.txt`：

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

# 站点地图（务必指向含 base 前缀的绝对地址）
Sitemap: https://uzuhu.github.io/geo/sitemap-index.xml
```

要点：

- 每个 `User-agent` 单独成段，`Allow: /` 表示全站放行；
- 底部 `Sitemap:` 必须是**绝对地址**，且含部署子路径（本项目为 `/geo/`）；
- 若只想对部分目录限制，可改用 `Disallow: /private/`。

## 本站的 robots.txt

本知识库已在 `public/robots.txt` 中默认放行上述爬虫，并指向 `https://uzuhu.github.io/geo/sitemap-index.xml`。你可以直接查看仓库中的 `public/robots.txt` 作为模板。

## 验证爬虫可访问性

1. **用官方工具确认未被屏蔽**：例如 Google 的 robots.txt 测试工具，输入页面 URL 与 UA，确认返回「允许」。
2. **用 curl 模拟对应 UA 抓取**：例如 `curl -A "GPTBot" https://uzuhu.github.io/geo/guides/what-is-geo/`，确认返回 HTTP 200 且正文可读。
3. **确认 Sitemap 可达**：浏览器或 curl 打开 `https://uzuhu.github.io/geo/sitemap-index.xml`，确认能正常返回 XML。
4. **定期复检**：部署流程或 CDN 规则变更后，重新跑一遍上述检查，避免无意中屏蔽了 AI 爬虫。

## 小结

技术可达性是 GEO 的「第一公里」。把 `robots.txt` 配好、把 `sitemap-index.xml` 指对，你的内容才有机会进入生成式引擎的候选来源集。

相关阅读：[GEO 优化策略](/geo/guides/geo-strategies/) · [GEO 与 SEO 的差异](/geo/guides/geo-vs-seo/)
