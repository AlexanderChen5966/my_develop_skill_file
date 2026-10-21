---
name: feedback-aipair-developer
description: ai-pair copilot-developer 適用場景與直接實作的取捨判斷
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bf7caf03-b8c8-4e99-b2fc-53d67e3e69cf
---

對於「同一 pattern 重複套用」的任務（如全站表格排序），Team Lead 直接用 Read/Edit 工具實作比走 copilot-developer 更快、更精確。

copilot-developer 分工適合用在：
- 需求模糊、需要 agent 自行判斷
- 多檔案同時大幅改寫
- 需要外部 CLI 不同視角

**Why:** SSGS-12150 排序任務（Tasks 6-8）直接實作效率遠高於 CLI 進程啟動開銷；Tasks 9-10 改走 copilot-developer 後速度接近，但需要準備詳細的 task context file。

**How to apply:** 同 pattern 連續任務 → 直接實作；第一次接觸的複雜多檔案任務 → copilot-developer。
