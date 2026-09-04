---
title: "Google-Extended 和 Googlebot 有什么区别？"
answer: "Googlebot 服务于传统搜索与 AI Overviews；Google-Extended 是 Google 用于训练与生成式 AI 产品的抓取令牌，专门覆盖 Gemini 等生成式场景。两者建议都放行。"
step: foundation
order: 3
publishDate: 2026-09-04
author: "阿虎 / zuwho"
related: [ai-crawlers-blocked, robots-txt-ai]
---

它们是 Google 的两个不同抓取标识，服务的场景不同：

| | Googlebot | Google-Extended |
| --- | --- | --- |
| 服务对象 | 传统 Google 搜索 + AI Overviews | Gemini 等 Google 生成式 AI 产品 |
| 作用 | 索引网页、决定搜索排名 | 为模型训练与 AI 生成提供语料 |
| 屏蔽后果 | 从搜索结果消失（SEO 归零） | 不再进入 Gemini 的引用来源集 |

## 为什么容易混淆

很多站点运维看到陌生 UA 就想屏蔽。`Google-Extended` 名字里没有 "bot"，容易被当成可选的、无关紧要的爬虫。但如果你在做 GEO——希望内容被 Gemini 引用——它恰恰是必须放行的那一个。

## 建议

两者都放行。屏蔽 `Googlebot` 会同时摧毁 SEO 和 AI Overviews 的可见度；屏蔽 `Google-Extended` 则把 Gemini 的引用机会拱手让人。完整的放行配置见 [对 AI 友好的 robots.txt 怎么写？](../robots-txt-ai/)。

## 相关词条

- [AI 爬虫有哪几类？不放行会怎样？](../ai-crawlers-blocked/)
- [对 AI 友好的 robots.txt 怎么写？](../robots-txt-ai/)
