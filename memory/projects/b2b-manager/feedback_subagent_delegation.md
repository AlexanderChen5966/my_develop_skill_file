---
name: feedback-subagent-delegation
description: b2b-manager 不採用自動 subagent 分工，維持主 session 直接實作
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 083a402c-9474-4b39-ab8c-f8aeedfcf22e
  modified: 2026-08-14T05:42:40.954Z
---

2026-08-14 討論「Opus 當管理者指揮其他 model 的 subagent」後結論：**不導入自動分工**，維持主 session 直接實作為預設。

**Why:**
- 專案規模不足以攤平派工開銷——每個 subagent 要 cold read 一次 CLAUDE.md + AGENTS.md + `.claude/rules/`，不共用主 session 的 prompt cache，多數情況比直接做更貴
- 專案規則大量是**負面約束**（`sortColumnIndex` 不可 +1、權限 gating 不可用 disable、VirtualDataTable 邊框位置、`external_libs/` 不可 pub upgrade），subagent 讀不到對話累積的判斷，也讀不到 memory，容易「不知道自己不知道」而踩雷
- 與 [[feedback-aipair-developer]]、[[feedback-copilot-reviewer]] 的實測結論一致

**How to apply:**
預設自己做。僅這三種情境值得派工：
1. 跨檔案盤點／找全站慣例 → Explore + haiku（只回結論，省 context）
2. 跨 repo 調查（如 b2b-backend 契約比對） → general-purpose + sonnet
3. 3 個以上**獨立**的重複樣板頁面 → sonnet 平行（省時間不省錢；1~2 個直接做更快）

❌ 動到 DataTable、權限 gating、API 契約、`page_route.dart` 一律不派工。
