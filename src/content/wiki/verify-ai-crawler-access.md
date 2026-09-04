---
title: "怎么验证 AI 爬虫能访问我的页面？"
answer: "三步：官方 robots.txt 测试工具确认未屏蔽；用 curl 模拟对应 UA 抓取关键页面确认返回 200 且正文可读；确认 sitemap XML 可达。部署变更后定期复检。"
step: foundation
order: 4
publishDate: 2026-09-04
author: "阿虎 / zuwho"
related: [robots-txt-ai, static-html-js, gsc-for-geo]
---

配好 `robots.txt` 不等于万事大吉，按下面四步验证一遍：

## 1. 用官方工具确认未被屏蔽

例如 Google 的 robots.txt 测试工具，输入页面 URL 与 UA（如 `Googlebot`、`Google-Extended`），确认返回「允许」。

## 2. 用 curl 模拟对应 UA 抓取

```bash
curl -A "GPTBot" https://your-domain.com/your-key-page/
```

确认返回 HTTP **200**，且输出的 HTML 里正文可读（不是空壳或报错页）。

## 3. 确认 Sitemap 可达

浏览器或 curl 打开 `https://your-domain.com/sitemap-index.xml`，确认能正常返回 XML。

## 4. 定期复检

部署流程或 CDN 规则变更后，重新跑一遍上述检查——很多站点是在改版或换 CDN 时**无意中**屏蔽了 AI 爬虫的。

另外，抓取可达 ≠ 内容可读。如果正文全靠 JavaScript 渲染，爬虫抓到的只是空壳，见 [为什么内容写进 JavaScript 是 GEO 大忌？](../static-html-js/)。Googlebot 侧的抓取问题可以在 Search Console 里排查，见 [Google Search Console 能看 GEO 效果吗？](../gsc-for-geo/)。

## 相关词条

- [对 AI 友好的 robots.txt 怎么写？](../robots-txt-ai/)
- [为什么内容写进 JavaScript 是 GEO 大忌？](../static-html-js/)
- [Google Search Console 能看 GEO 效果吗？](../gsc-for-geo/)
