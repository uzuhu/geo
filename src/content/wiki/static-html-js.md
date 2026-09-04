---
title: "为什么内容写进 JavaScript 是 GEO 大忌？"
answer: "很多 AI 爬虫不会可靠执行 JavaScript，关键内容必须能在「查看网页源代码」时直接看到。用静态生成（SSG）或服务端渲染（SSR），并把首屏加载压到 2 秒内。"
step: foundation
order: 7
publishDate: 2026-09-04
author: "阿虎 / zuwho"
related: [structured-data-useful, verify-ai-crawler-access, geo-common-mistakes]
---

爬虫抓到你的页面 ≠ 看到你的内容。如果正文、标题、FAQ 全靠客户端 JavaScript 渲染，AI 爬虫抓到的只是一个空壳 `<div id="app"></div>`——前面所有的 GEO 优化都白做。

## 三件事要做

### 1. 内容出现在静态 HTML 里

- 用**静态生成（SSG）或服务端渲染（SSR）**输出内容；
- 测试方法：右键「查看页面源代码」，确认正文、标题、FAQ 都在原始 HTML 中，而不是靠 JS 注入。

### 2. 速度也是门槛

Perplexity 这类依赖实时检索（RAG）的引擎，抓取窗口很窄，页面超过 **1.5–2 秒**就可能被放弃。把首屏加载压到 2 秒以内、修掉 LCP/CLS 问题，AI 才「来得及」引你。

### 3. 语义化 HTML5

用 `header / nav / main / article / section / footer` 明确内容边界。语义越清晰，模型抽取越准。

## 一个正面例子

本站基于 **Astro**，构建产物是纯静态 HTML，天然符合这条——正文、标题、FAQ 在源代码里直接可见，无需执行任何 JS。

## 相关词条

- [结构化数据对 GEO 真的有用吗？](../structured-data-useful/)
- [怎么验证 AI 爬虫能访问我的页面？](../verify-ai-crawler-access/)
- [GEO 常见误区有哪些？](../geo-common-mistakes/)
