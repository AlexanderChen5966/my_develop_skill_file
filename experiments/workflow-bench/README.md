# workflow-bench：開發流程版本比對

用已完成的 Jira 卡回放，比較不同版本開發流程（v1、v2、之後的 v3、v4）的穩定度、準確度、token 使用量、開發角色模組的使用狀況。
只比對**軟體開發角色**的模組：requirements、figma-to-requirements、grilling／grill-me、diagnosing-bugs、tdd、stack-review（含 code-reviewer、spec subagent）、doc-update、pr。

## 結構

| 路徑 | 內容 | 進 git？ |
|---|---|---|
| `versions/<v>/skills/` | 凍結的版本 skill（v1＝`~/.agents` 2026-11-09 修改前的 HEAD；v2＝當天修改後；v4＝2026-11-11 plugin 切換、補測後的本體，多了 dev-web 的 flutter-ui-compare）。⚠️ bench 把 skill 放在 `repo/.claude/skills/`，測的是 skill 內容，不是 plugin 包裝（名稱沒有 `dev:` 前綴） | ✅ |
| `prompt.md` | 所有版本共用的指令（固定，不隨版本改） | ✅ |
| `settings.json` | 受測 agent 的權限白名單（不用 bypass） | ✅ |
| `claude-home/` | 受測 agent 專用的 `CLAUDE_CONFIG_DIR`：共同規則 `CLAUDE.md`、`agents/code-reviewer.md`、登入狀態、對話紀錄 | ❌ |
| `tickets/<卡號>/` | 題目、回放設定、**隱藏驗收** `check.py`（公司內容） | ❌ |
| `runs/<卡號>-<v>-r<n>/` | 每次回放：`origin.git`（只有到 base 的歷史）、`repo`、`rounds/`、`report.*` | ❌ |

## 用法

```bash
# 一次性：受測環境登入（獨立設定目錄，不共用主帳號的 session 與記憶）
CLAUDE_CONFIG_DIR=~/.agents/experiments/workflow-bench/claude-home claude auth login

scripts/setup_run.sh SSGS-13687 v2 1          # 建環境
scripts/run.sh runs/SSGS-13687-v2-r1          # 第一輪
# 若最後回覆是在問問題：把回答寫成檔案再接續
scripts/run.sh runs/SSGS-13687-v2-r1 answer.md
python3 scripts/analyze.py runs/SSGS-13687-v2-r1
```

## 比對標準（2026-11-09 使用者決定，成本考量）

- 每個版本只跑 **SSGS-13687 一次**（`setup_run.sh SSGS-13687 <v> 1` → `run.sh` → `analyze.py`）
- 基準：v1、v2 的 `runs/SSGS-13687-v{1,2}-r1/report.json`（試跑即正式基準）
- `prompt.md`、`settings.json`、`claude-home/CLAUDE.md`、模型**都不要改**；改了就要重跑所有要比較的版本
- 已知限制：這張卡簡單，準確度大概都會滿分，比較重點放在費用、token、回合數、開發模組有沒有正確觸發、審查找到什麼、權限拒絕次數

## 控制變因

- 同一個模型（`claude-opus-5-5`）、同一份 `prompt.md`、同一份共同規則與權限白名單
- 版本差異只在 `repo/.claude/skills/`（專案層 skill）
- `claude-home` 沒有全域 skill、plugin、MCP、記憶 → 不會混入主環境的 Matt skill 或專案記憶
- 防洩漏：不帶 `docs/shared/`、`docs/issue/`、`docs/agent-handoff/`；`CHANGELOG.md` 換成空的；`origin.git` 只留到 base 的歷史（答案 commit 會被檢查不存在）

## 已知限制

- 上游 `../b2b-backend` 不存在（SSGS-13687 後端依賴＝無，不影響）
- 題目用任務文件的「使用者回報」段，不是 Jira 原文（當時 Jira MCP 連不上）
- `docs/` 其他文件是現在的版本，可能描述 base 之後的程式碼
