---
name: feedback-handoff-cleanup
description: 任務結案時把 .handoff 內容整合成一份正式文件，然後清掉 .handoff 與 refs/handoff，工作過程不保留
metadata:
  type: feedback
  modified: 2026-11-09
permalink: agents-memory/global/feedback-handoff-cleanup
---

`.handoff/` 只在工作進行中使用。任務結案時，把規則、決策、驗證結果整合成一份正式文件（例如 `docs/shared/<任務>.md`），再清掉該任務的交接檔與 `refs/handoff/*`。

**Why:** 使用者不想讓文件越積越多；只要保留最終紀錄，工作過程不用留，程式碼本來就在 git 上（2026-11-09 SSGS-14167 結案時確認）。

**How to apply:** 收尾時先確認程式已上 git、正式文件已涵蓋要留的內容，再刪除。`.handoff/` 不在版控，刪了救不回來，有其他進行中任務的檔案就不要動。正式文件不要引用已刪除的交接檔。