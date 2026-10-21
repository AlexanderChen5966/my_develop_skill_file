---
name: feedback-no-auto-commit
description: ai-pair 和所有 agent 任務中禁止自動 git commit，由使用者人工處理
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6c55bfa6-d58c-40af-a765-ef1e708aacd6
---

不要在 ai-pair 或任何 agent 任務中執行 git commit。

**Why:** 使用者明確表示 commit 由人工處理，不希望 agent 自動 commit。

**How to apply:** 每次寫 task context file 給 copilot-developer 時，在 Constraints 區塊明確加入「**絕對禁止執行任何 git 指令（git add、git commit、git push 等）**」。若 copilot 已 commit，需提醒使用者此行為不符規定。
