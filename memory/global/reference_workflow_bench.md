---
name: reference-workflow-bench
description: 開發流程版本比對工具在 ~/.agents/experiments/workflow-bench；回放已完成 Jira 卡比較 v1/v2/v3…，受測環境用獨立 CLAUDE_CONFIG_DIR
metadata:
  node_type: memory
  type: reference
  modified: 2026-11-09
permalink: agents-memory/global/reference-workflow-bench
---

開發流程（主流程＋skill）版本比對工具：`~/.agents/experiments/workflow-bench/`，用法看該目錄 `README.md`。

- 做法：用已完成卡片的 merge 前 commit 回放，給原始需求（不給任務文件），跑完用隱藏驗收 `tickets/<卡>/check.py` 比對標準答案；`scripts/analyze.py` 算準確度、token、費用、開發模組叫用
- 版本凍結在 `versions/<v>/skills/`；新版本要先在這裡新增快照再跑，舊版不要改。個人層記憶的規則 bench 讀不到，放 `versions/<v>/CLAUDE.local.md` 帶入（v3 起）
- 已有結果：v1 $4.18、v2 $4.94、v3 $4.79，三版都 14/14（報告第 6 節）
- 受測 agent 用獨立設定目錄 `claude-home/`（已登入；沒有全域 skill、plugin、MCP、記憶），權限走 `settings.json` 白名單——自動模式不允許 `--dangerously-skip-permissions`
- `tickets/`、`runs/`、`claude-home/` 含公司程式碼與卡片內容，已 gitignore，不可推到個人 GitHub
- 結果報告：`~/Desktop/開發流程升級_2026-11-09/workflow-bench試跑報告_SSGS-13687.md`（2026-11-09，v1、v2 都 14/14，v2 費用 +18%）

- **比對標準（使用者 2026-11-09 決定，成本考量）**：每個版本只跑 SSGS-13687 一次；v1、v2 試跑即正式基準；不放寬白名單、不加卡、不重複跑，除非使用者另外要求

**How to apply:** 使用者要比較流程版本或驗證 skill 改動效果時，沿用這套工具，不要另起爐灶；改白名單或 prompt 屬於改變控制變因，改了就要重跑所有要比較的版本。
