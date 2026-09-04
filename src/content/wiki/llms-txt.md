---
title: "llms.txt 是什么，必须做吗？"
answer: "llms.txt 是放在网站根目录的纯文本说明文件，列出核心页面与一句话描述，帮助 AI 快速理解站点结构。多份实战指南称其为「当前性价比最高的 GEO 手段」，强烈建议做。"
step: foundation
order: 5
publishDate: 2026-09-04
author: "阿虎 / zuwho"
related: [robots-txt-ai, structured-data-useful, geo-ready-checklist]
---

`llms.txt` 是一个约定俗成的标准：放在网站根目录（`https://your-domain.com/llms.txt`）的纯文本文件，用极简格式向 AI 爬虫说明「这个站有什么、核心内容在哪」。

## 长什么样

```text
# GEO 知识库

> 面向 ChatGPT、Claude、Perplexity 与 Google AI Overviews 的 GEO 实战知识库。

- /wiki/what-is-geo/：GEO 的定义、由来与三大支柱
- /wiki/best-geo-strategy/：9 项被验证的内容战术
- /wiki/geo-ready-checklist/：单页 GEO-ready 检查清单
- /wiki/measure-no-budget/：零成本度量方法

Sitemap: https://your-domain.com/sitemap-index.xml
```

## 为什么性价比高

- **成本几乎为零**：一个静态文本文件，十分钟写完；
- **直击痛点**：AI 爬虫不总是善于在复杂站点里找重点，llms.txt 直接把「重点清单」递到它手里；
- **2025–2026 年的多份实战指南**（Victory Digital 90 天 Playbook、ClickForest 策略清单等）都把它列为优先级最高的技术地基动作之一。

## 必须做吗

严格说不是标准强制，但对内容型站点几乎是「无脑应该做」。它与技术地基的另外几件事（robots.txt 放行、JSON-LD Schema、静态渲染）互为补充，见相关词条。

## 相关词条

- [对 AI 友好的 robots.txt 怎么写？](../robots-txt-ai/)
- [结构化数据对 GEO 真的有用吗？](../structured-data-useful/)
- [单篇内容要怎么改才算 GEO-ready？](../geo-ready-checklist/)
