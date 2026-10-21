---
name: multiagent-handoff
description: |
  跨 AI agent 的專案接力：存狀態、接手、分派任務、回報、驗收（save / resume / delegate / report / review）。
  適用 Claude Code、Codex、Copilot CLI、opencode、agy、Cursor 等任何能讀檔與執行 shell 的 agent。
  觸發時機：/multiagent-handoff、交接、換手、接手、額度快用完、要交給 Codex/Copilot 繼續、
  把任務分派給其他 agent、其他 agent 做完要驗收、讀 .handoff/、resume。
  不適用：同一 session 內由 Claude 協調外部 CLI 實作＋多模型 review（那是 ai-pair）。
argument-hint: "save | resume | delegate <slug> [--to <agent>] [--run [--model M]] | report <task-id> | review <task-id>"
metadata:
  version: 0.5.0
---

# multiagent-handoff

在多個 AI agent 之間接力同一個專案。**狀態以 git 為準，交接檔只補 git 看不出來的部分**（意圖、決定、下一步）。

> 本體在 `~/.agents/skills/multiagent-handoff/`（Codex／Copilot／opencode 原生讀取）；Claude Code 與 agy 經 `~/.agents/link-skills.sh` 建立的 symlink 讀取。**只改本體**。

## 共通規則

- 所有指令在**專案根目錄**執行。腳本路徑固定為下列絕對路徑，以下簡寫為 `$H`。
  ```bash
  H=~/.agents/skills/multiagent-handoff/scripts/handoff.py
  ```
- `.handoff/` 只存在本機（`.git/info/exclude`），**不 commit、不改 `.gitignore`**。第一次使用先 `python3 $H init`。
- 換手前**不需要 commit**——同一台機器、同一個資料夾，未提交修改下一手看得到。
- ❌ 不要在交接檔裡複述專案規則（`AGENTS.md` 已涵蓋），只寫這個任務特有的事。
- ❌ 不要把檔案內容貼進交接檔，寫 `檔案:行號` 即可。

---

## save — 交出去之前

1. `python3 $H snapshot`，取得分支／HEAD／未提交修改。
2. **覆寫** `.handoff/CURRENT.md`，格式如下。每一節都要有內容，沒有就寫「無」：
   ```markdown
   # 目前任務：<任務名稱>（對應 docs/shared/xxx.md，沒有就寫「無」）
   - 分支：<branch>　HEAD：<short hash>
   - 上一手：<你的工具名稱>，<YYYY-MM-DD HH:MM>

   ## 已完成
   ## 進行中（具體位置：檔案:行號，做到哪一步）
   ## 下一步（依序，第一步要具體到可以直接開工）
   ## 已決定的事與原因（避免下一手推翻）
   ## 已知問題／試過但失敗的做法
   ## 驗證方式（跑什麼指令算通過）
   ```
3. `python3 $H log "<你的工具> → <下一手或「待定」>｜<一句話進度>"`
4. 告訴使用者交接檔已寫好，下一手開工時說「multiagent-handoff resume」即可。

> 額度快用完時，**先做 save 再做別的**。來不及也沒關係，resume 有備援。

## resume — 接手時

1. `python3 $H snapshot`。
2. 讀 `.handoff/CURRENT.md`（若存在）與 `.handoff/log.md` 最後幾行。
3. **比對交接檔與實際狀態**：
   - snapshot 若提示「有檔案在 CURRENT.md 之後才被修改」→ 交接檔可能過期，以 diff 為準。
   - 交接檔寫「已完成」但 diff 看不到對應修改 → 列為疑點。
4. **找不到 CURRENT.md、或已過期時的備援**：
   - `python3 $H sessions`：列出本專案最近的 Claude Code / Codex / agy 對話，取最後幾則使用者訊息與 agent 回覆，推回任務目標與進度（agy 只有使用者訊息）。
   - 再用 `git diff HEAD` 看實際改了什麼。
5. 先向使用者**摘要**（任務、已完成、下一步、疑點），**取得確認後才開工**。
6. 開工後在 log 追加一行：`python3 $H log "<上一手> → <你>｜接手，從 <第一步> 開始"`。

## delegate — 主 agent 分派任務

1. `python3 $H new-task <slug> --to "<被分派的 agent>"`。
   - 會記錄**分派基準**（`refs/handoff/<task-id>`）：含當下未提交的修改，所以驗收時不會把分派前就存在的改動算在對方頭上。
2. 填寫任務單 `.handoff/tasks/<task-id>.md` 的各節：
   - **可以動的檔案／不能動的檔案**：每行一個反引號包住的路徑或 glob（例 `` `lib/page/report/**` ``）。review 會依此自動檢查範圍。
   - **禁止事項**：只挑與本任務相關的專案硬規則。
   - **完成標準**：優先寫可執行的指令。
   - 有需求文件就連結 `docs/shared/`，不要重寫需求。
3. 交給對方，二選一：
   - **手動**（預設）：把這句話告訴使用者，由使用者自己開那個工具貼上
     > 用 multiagent-handoff skill（`~/.agents/skills/multiagent-handoff/SKILL.md`），你是被分派的 agent，執行 report 流程，任務單是 `.handoff/tasks/<task-id>.md`
   - **`--run`**（使用者說「直接跑」「幫我叫 Codex」或帶了 `--run`）：**先把任務單內容給使用者看過、取得同意**，再執行
     ```bash
     python3 $H run <task-id> --agent <codex|agy|copilot|opencode|cursor> [--model <名稱>] [--timeout 1800]
     ```
     - 腳本會先檢查任務單已填（目標／可以動的檔案／完成標準），沒填會拒絕
     - 輸出寫到 `.handoff/tasks/<task-id>.run.log`；結束後若任務單狀態**沒有變成「已回報」**，視為失敗（可能是假成功或逾時），讀 log 最後 30 行回報使用者，**不要直接進 review**
     - 不確定指令對不對時先加 `--dry-run` 看組出來的指令
     - 成功後直接進 review
4. ⚠️ 提醒使用者：對方工作期間，主 agent 不要動同一個資料夾（`--run` 時主 agent 會等它跑完，期間不要做別的修改）。

### `--run` 各 agent 的實際指令

| `--agent` | 組出的指令 | 必要旗標的原因 |
|---|---|---|
| `codex` | `codex exec --skip-git-repo-check -s workspace-write [--add-dir <工具鏈目錄>…] [-m M] "<prompt>"` | `-s workspace-write` 才能改檔。sandbox **只能寫 workspace**：Flutter 專案會自動 `--add-dir` Flutter SDK `bin/cache`、`~/.dart-tool`、`~/.pub-cache`（存在才加），否則 `flutter analyze` 會因寫不了 `engine.stamp` 失敗 |
| `agy` | `agy --dangerously-skip-permissions --print-timeout <秒>s --add-dir ~/.agents/skills/multiagent-handoff [--model M] -p "<prompt>"` | 見下方 agy 注意事項；`--add-dir` 讓它讀得到 workspace 外的 skill |
| `copilot` | `copilot --allow-all-tools --add-dir ~/.agents/skills/multiagent-handoff [--model M] -p "<prompt>"` | 非互動模式無人核准工具；`--add-dir` 同上 |
| `opencode` | `opencode run --auto [-m provider/model] "<prompt>"` | `--auto` 自動核准未明確禁止的權限 |
| `cursor` | `cursor-agent -p --trust --force --add-dir ~/.agents/skills/multiagent-handoff [--model M] "<prompt>"` | `--force` 核准指令；`--trust` 跳過信任 workspace 提問（新 workspace 沒加會卡住）。模型用 `cursor-agent --list-models` 列出 |

**opencode 一律指定 `--model`**（例：`github-copilot/gpt-5.4-mini`；`opencode models` 列出可用模型）。
實測預設模型會陷入「重複讀任務單」的迴圈直到逾時。另外 `opencode run` 把工作交給背景 service，
逾時被中止時 service 內的 session **可能仍在跑**——逾時後先 `git status` 確認工作區沒有繼續變動，再決定下一步。

### agy（Antigravity CLI）注意事項

- **`--dangerously-skip-permissions` 不可省**：缺它時非互動模式遇到權限請求無人核准，會 exit 0 但什麼都沒做（假成功）。腳本已固定帶上，並以「任務單狀態是否變成已回報」判斷成敗，不信 exit code
- **模型名稱**：slug（`gemini-3.1-pro-high`、`claude-sonnet-4-6`，連字號）與顯示名（`Gemini 3.1 Pro (High)`）皆可。列出可用模型用 `agy models | cat`——❌ 直接 `agy models > file` 會卡住
- **輸出一律落檔**：1.0.x 版在非 TTY（pipe／redirect／subprocess）時 stdout 可能為空或 `-p` 卡住（官方 issue #76 等）；1.4.2 實測正常。若升級後 run.log 是空的，先查這個
- **工作目錄外的檔案**：agy 只看得到 workspace（cwd）內的檔案。`run` 已自動 `--add-dir` skill 本體；任務若還需要讀其他 repo，請在任務單「背景資訊」說明，並改用手動派工自行加 `--add-dir`
- **對話紀錄**：`~/.gemini/antigravity-cli/history.jsonl` 只有使用者輸入（依 `workspace` 欄位篩專案），agent 回覆在 `conversations/*.db`；`sessions --tool agy` 只能還原「上一手被要求做什麼」，做到哪要看 `git diff`

## report — 被分派的 agent

1. 讀 `.handoff/tasks/<task-id>.md`，**只在「可以動的檔案」範圍內修改**。需要動範圍外的檔案 → 停下來寫進「未處理事項／疑問」，不要自行決定。
2. 做完後填「回報」區塊：
   - 修改內容：每檔一行。
   - 驗證方式與結果：貼**實際執行**的指令與輸出摘要。沒跑就寫沒跑，不要寫「應該可以」。
   - 未處理事項／疑問。
3. 把任務單的「狀態」改為 `已回報`。
4. `python3 $H log "<你> → 主 agent｜<task-id> 已回報"`。

## review — 主 agent 驗收

1. `python3 $H review <task-id>`：列出分派後**實際**變動的檔案（含新增的 untracked 檔），標出 🟡 範圍外／🔴 禁止範圍。
2. **以 diff 為準，不以回報為準**，逐項檢查：
   - [ ] 有沒有超出允許範圍的修改？（腳本已標出，逐一確認是否合理）
   - [ ] 回報列的修改與實際 diff 一致嗎？（有改沒報、有報沒改都要列出）
   - [ ] **自己重跑**「完成標準」的驗證指令，不採信回報的結果。
   - [ ] 是否違反「禁止事項」或專案硬規則？（逐檔 `git diff refs/handoff/<task-id> -- <檔案>`）
3. 填「驗收結果」，狀態改為 `已驗收` 或 `退回`（退回時寫明原因，對方用 report 再做一次）。
4. `python3 $H log "主 agent｜<task-id> 已驗收／退回：<原因>"`。
5. 驗收通過且不再需要基準時，可刪除 ref：`git update-ref -d refs/handoff/<task-id>`。

---

## 已知限制

- `sessions` 支援 Claude Code、Codex（完整）與 agy（僅使用者輸入）；Copilot CLI / opencode 待補。
- `--run` 五個 agent（codex／agy／copilot／opencode／cursor）皆已實測通過（2026-10-19）；opencode 需指定 `--model`。
- `--run` 是「叫起一次、等它結束」，不重試、不做多模型 review——那些是 ai-pair 的範圍。
- `review` 的 glob 用 Python `fnmatch`：`*` 會跨目錄比對（`lib/*.dart` 也會命中子目錄）。
- 分派期間主 agent 若也改了檔案，`review` 會一併列出，無法區分是誰改的。
