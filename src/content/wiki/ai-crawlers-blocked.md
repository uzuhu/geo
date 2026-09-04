---
title: "AI 爬虫有哪几类？不放行会怎样？"
answer: "如果 robots.txt 禁止了 GPTBot、ClaudeBot 等爬虫，对应的生成式引擎将无法抓取你的页面，自然也不会在答案中引用你。放行它们是 GEO 的技术前提。"
step: foundation
order: 1
publishDate: 2026-09-04
author: "阿虎 / zuwho"
related: [robots-txt-ai, google-extended-vs-googlebot, verify-ai-crawler-access]
---

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

## 常见的误伤

不少站点为防恶意抓取，用 `User-agent: *` + `Disallow: /` 一刀切屏蔽了「所有爬虫」，等于把 AI 爬虫也挡在门外，**GEO 直接归零**。正确的做法是按 UA 白名单放行，配置模板见 [对 AI 友好的 robots.txt 怎么写？](../robots-txt-ai/)。

## 相关词条

- [对 AI 友好的 robots.txt 怎么写？](../robots-txt-ai/)
- [Google-Extended 和 Googlebot 有什么区别？](../google-extended-vs-googlebot/)
- [怎么验证 AI 爬虫能访问我的页面？](../verify-ai-crawler-access/)
