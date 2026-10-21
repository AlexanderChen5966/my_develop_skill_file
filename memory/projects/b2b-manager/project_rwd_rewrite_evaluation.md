---
name: project-rwd-rewrite-evaluation
description: 2026-10-21 RWD／Vue-React 重寫／Next-Nuxt 評估結論，記錄於 docs/shared/rwd_and_web_rewrite_evaluation.md，未立案
metadata:
  node_type: memory
  type: project
  originSessionId: 78118b82-1bcd-4b42-b546-f5c73458555e
  modified: 2026-10-21T02:39:21.680Z
---

2026-10-21 評估：Flutter Web 改 RWD（全站 3–5 人月、分階段只做高頻查詢頁 1–1.5 人月）；Vue/React 重寫成本約 RWD 的 3–5 倍；若重寫不需 Next/Nuxt，Vite SPA 即可（SSR 會迫使 OAuth2 改 BFF、部署改 Node）。詳見 `docs/shared/rwd_and_web_rewrite_evaluation.md`。

**Why:** 使用者在評估是否做 RWD 或換技術棧，尚未決策。
**How to apply:** 再談 RWD／重寫時先讀該文件接續，不重新盤點；若決定執行，需重新定義 list-page-header 與 datatable-safety 規則。相關：[[project-docs-concurrent-write-hazard]]
