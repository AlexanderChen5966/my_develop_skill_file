---
name: feedback_aipair_trigger
description: 只有產生過需求文件的任務才會用 ai-pair 執行；小改動直接手動
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b5f6d874-0cd8-4a4b-a4d1-48e9bc4eff24
---

只有**已有需求文件（docs/shared/*.md）的任務**才啟動 ai-pair 流程執行。

**Why:** ai-pair 的價值在於多 reviewer 驗證需求落實度；沒有需求文件就沒有 spec 基準，reviewer 無法做 spec compliance check。

**How to apply:**
- 有需求文件 → 可走 ai-pair（依複雜度選 Tier + Level）
- 無需求文件的小改動（設定檔、i18n key、單行 bugfix）→ 直接手動修改，不啟動 ai-pair
- 需求文件路徑慣例：各專案的 `docs/shared/{feature}.md`（例：b2b-manager、app01-double）
