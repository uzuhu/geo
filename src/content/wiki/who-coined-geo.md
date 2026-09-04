---
title: "GEO 是谁提出的？有依据吗？"
answer: "GEO 由普林斯顿等机构的研究者在 2024 年 KDD 论文《GEO: Generative Engine Optimization》（arXiv:2311.09735）中正式提出，并给出了可复现的评测基准 GEO-bench，不是营销造词。"
step: understand
order: 2
publishDate: 2026-09-04
author: "阿虎 / zuwho"
related: [what-is-geo, best-geo-strategy]
---

GEO 不是营销造词，而是有学术定义的范式。2024 年，普林斯顿等机构的研究团队（Aggarwal、Murahari、Rajpurohit、Kalyan、Narasimhan、Deshpande）在 ACM KDD 会议上发表了论文 **《GEO: Generative Engine Optimization》**（[arXiv:2311.09735](https://arxiv.org/abs/2311.09735)），首次系统化地定义了 GEO 并给出了评测方法。

## 论文的三个关键贡献

1. **定义了生成式引擎与 GEO**：把「让内容在 AI 合成答案中被选中、引用、归因」这一过程正式命名为 GEO。
2. **构建了 GEO-bench 基准**：包含 10,000 条跨领域查询，用于评测不同内容策略在生成式引擎中的可见度。
3. **验证了有效性**：通过严谨实验证明，GEO 最多可将内容在生成答案中的可见度提升 **约 40%**，且效果因领域而异。

## 这意味着什么

有基准、有对照实验、可复现——GEO 是一门可度量的内容工程，而不是玄学。论文在 GEO-bench 上测试出的 9 项内容策略及各自效果，见 [哪一项 GEO 策略效果最好？](../best-geo-strategy/)。

## 相关词条

- [GEO 是什么？](../what-is-geo/)
- [哪一项 GEO 策略效果最好？](../best-geo-strategy/)
