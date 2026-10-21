---
name: feedback-copilot-reviewer
description: copilot-reviewer（GPT）無法讀取 stdin diff，回報虛構檔案路徑
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bf7caf03-b8c8-4e99-b2fc-53d67e3e69cf
---

copilot-reviewer 透過 `cat file | copilot --model gpt-4.1 -p "..."` 方式執行時，GPT 未能實際讀取 diff 內容，回報了不存在於專案中的檔案路徑（如 `lib/widget/table/user_table.dart`），結果完全不可採信。

**Why:** SSGS-12150 review 時 copilot-reviewer 回報了虛構路徑，claude-reviewer（subagent）則正確讀取 diff 並提出有效 findings。

**How to apply:** copilot-reviewer 結果出現不存在的檔案路徑時，直接標記 ERR:MODEL 跳過，不採用其 findings。claude-reviewer subagent 是更可靠的 reviewer。
