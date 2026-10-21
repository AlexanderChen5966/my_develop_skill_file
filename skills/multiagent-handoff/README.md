# multiagent-handoff skill 使用說明

在多個 AI agent（Claude Code、Codex CLI、Copilot CLI、opencode、agy、Cursor CLI）之間**接力同一個專案**：換手接續、分派任務、事後驗收。

> **v0.6.0**（2026-10-21）加「建議記憶」：save 的交接檔與 report 的任務單多一節，其他 agent 不直接寫長期記憶（`~/.agents/memory/`），由 Claude 在 resume／review 時判斷層級、給使用者看過後寫入。
> **v0.5.0**（2026-10-21）由 `handoff` 改名為 `multiagent-handoff`（避免與 Matt Pocock 的 `/handoff` 撞名；`.handoff/`、`refs/handoff/`、`handoff.py` 沿用）。
> **v0.4.0**（2026-10-19）全域安裝：本體在 `~/.agents/skills/multiagent-handoff/`，六個工具共用同一份。
> 規劃與設計理由見 b2b-manager `docs/agent-handoff/agent-handoff-規劃.md`。

---

## 什麼時候用

| 情境 | 用哪個動作 |
|---|---|
| Claude 額度快用完，要換 Codex 繼續做 | 交出方 `save` → 接手方 `resume` |
| 隔天回來接著做，或忘了昨天做到哪 | `resume` |
| 把一個小任務丟給 Copilot／Codex，晚點再回來看 | 主 agent `delegate` → 對方 `report` → 主 agent `review` |

**不適用**：有需求文件、而且 Claude 全程在場協調外部 CLI 實作並多模型 review 的情況，請用 **ai-pair**。
判斷方式：主 agent 會全程在場用 ai-pair，會中途離開用 multiagent-handoff。

---

## 快速開始

每個專案第一次使用時執行一次（把 `.handoff/` 加進 `.git/info/exclude`；b2b-manager 已做過）：

```bash
python3 ~/.agents/skills/multiagent-handoff/scripts/handoff.py init
```

### 在 Claude Code

直接說出動作即可，skill 會自動觸發：

```
multiagent-handoff save
multiagent-handoff resume
multiagent-handoff delegate 修正報表匯出 --to Codex
multiagent-handoff review 20261019-修正報表匯出
```

### 在其他 agent（Codex、Copilot、opencode、agy）

五個工具都已安裝（見下方「安裝位置」），直接用同樣的說法即可：

```
用 multiagent-handoff skill 執行 resume。
```

```
用 multiagent-handoff skill，你是被分派的 agent，
執行 report 流程，任務單是 .handoff/tasks/20261019-修正報表匯出.md。
```

### `--run`：讓主 agent 直接叫起指定的 agent

不想自己開工具時，在 Claude Code 說：

```
multiagent-handoff delegate 修正報表匯出 --to agy --run
multiagent-handoff delegate 修正報表匯出 --to codex --run --model gpt-5.4-mini
```

主 agent 會先建立任務單並填好，**給你看過、你同意後**才用非互動模式啟動對方，等它跑完就直接進 review。
腳本指令是 `run`（手動執行也可以）：

```bash
python3 ~/.agents/skills/multiagent-handoff/scripts/handoff.py run <task-id> --agent agy [--model M] [--timeout 1800]
python3 ~/.agents/skills/multiagent-handoff/scripts/handoff.py run <task-id> --agent codex --dry-run   # 只印出指令
```

| `--agent` | 實際執行的指令 | 指定模型 | 實測 |
|---|---|---|---|
| `codex` | `codex exec --skip-git-repo-check -s workspace-write [--add-dir …] …` | `-m <model>` | ✅ 完整 delegate → report → review；SSGS-14167 實戰 35 秒 |
| `agy`（1.4.2） | `agy --dangerously-skip-permissions --print-timeout <秒>s --add-dir <skill 本體> -p …` | `--model <slug>`（`agy models \| cat` 列出） | ✅ `run` 完整一輪，72 秒；全域版 71 秒 |
| `copilot` | `copilot --allow-all-tools --add-dir <skill 本體> -p …` | `--model <model>` | ✅ `run` 完整一輪，23 秒（預設模型） |
| `opencode` | `opencode run --auto …` | `-m provider/model`（`opencode models` 列出） | ✅ `run` 完整一輪：Copilot 模型 12 秒、免費 `glm-5.3-flash-free` 74 秒（**需指定模型**，見下方） |
| `cursor` | `cursor-agent -p --trust --force --add-dir <skill 本體> …` | `--model <model>`（`cursor-agent --list-models` 列出） | ✅ `run` 完整一輪，27 秒（預設 `auto`） |

`run` 的保護機制：

- 任務單的「目標／可以動的檔案／完成標準」沒填會**拒絕派工**，避免對方只拿到空白任務單
- 狀態不是「待執行」會拒絕，避免重複派工；確定要重跑請加 `--force`
- 對方的輸出寫進 `.handoff/tasks/<task-id>.run.log`，不經 shell 變數
- **不看 exit code，看任務單有沒有變成「已回報」**：exit 0 但沒回報的情況，會判定為假成功或失敗（已用模擬測試確認）
- 自動更新任務單的「指派給」欄位，並寫進 log
- **Codex 跑 Flutter 專案**：sandbox 只能寫 workspace，`run` 會自動 `--add-dir` Flutter SDK 的 `bin/cache`、`~/.dart-tool`、`~/.pub-cache`。2026-10-20 實戰時漏了這個，Codex 跑不了 `flutter analyze`（它如實回報未完成）；實測只開 cache 會改卡在 `~/.dart-tool`，兩者都開才完整跑完

**opencode 一定要加 `--model`**。2026-10-19 實測：

| 嘗試 | 模型 | 結果 |
|---|---|---|
| 1 | 預設（`deepseek-v4.1-flash` → `elorian/glimpse`） | ❌ 重複讀任務單 55 次，460 秒逾時、沒有回報（`run` 正確判定為失敗） |
| 2 | `github-copilot/gpt-5.4-mini` | ✅ 12 秒完成，任務單只讀 1 次 |
| 3 | 同上，加 `--standalone`（想讓逾時時確實中止） | ❌ 卡住超過 5 分鐘、零進度，已放棄這個做法 |
| 4 | `opencode/glm-5.3-flash-free`（免費，不耗 Copilot Credits） | ✅ 74 秒完成，任務單只讀 1 次，回報附 `檔案:行號` 與驗證輸出 |

沒帶 `--model` 時，`run` 會先印出警告。另外 `opencode run` 是把工作交給背景 service 執行，逾時中止後 service 裡的 session 可能還在跑，逾時後先 `git status` 確認工作區沒有繼續被改動。

agy 的注意事項（來源：ai-pair `reference/cli-invocation-ref.md` 實測紀錄＋官方 issue）：

- **必須加 `--dangerously-skip-permissions`**：沒加的話，非互動模式碰到工具權限請求時沒有人能核准，會出現「假成功」（exit 0，但事情沒做）
- **輸出先導向檔案**，不要經過 shell 變數（控制字元會破壞內容）
- 1.0.x 版有「非 TTY 時 stdout 為空」和「`-p` 卡住」的 issue；1.4.2 實測已經正常。若版本退回或升級後異常，先查這兩個 issue
- `--print-timeout` 預設是 0（不限時）。macOS 沒有 `timeout` 指令，建議一律加上（`run` 已自動帶）
- 只看得到 workspace 內的檔案。`run` 已自動 `--add-dir` skill 本體；任務若還需要讀其他 repo，改用手動派工自行加 `--add-dir`
- 對話紀錄：`sessions --tool agy` 讀 `~/.gemini/antigravity-cli/history.jsonl`，**只有使用者輸入**（agent 回覆存在 `conversations/*.db`，未解析）

---

## 五個動作

### 換手：`save` / `resume`

**`save`**（交出方，額度警告一出現就先做）

1. 拍 git 快照：分支、HEAD、未提交的修改
2. 覆寫 `.handoff/CURRENT.md`：已完成、進行中（`檔案:行號`）、下一步、已決定的事、試過但失敗的做法、驗證方式
3. 在 `.handoff/log.md` 追加一行

換手前**不用 commit**。同一台機器、同一個資料夾，未提交的修改下一手看得到。

**`resume`**（接手方）

1. 讀 `CURRENT.md`，和實際的 `git diff` 比對
2. 如果有檔案比 `CURRENT.md` 還晚修改，會提示「交接檔可能過期」，此時以 diff 為準
3. **找不到交接檔**（上一手來不及 save）時，改讀本專案最近的 Claude Code／Codex 對話紀錄，推回任務和進度
4. 先摘要給你確認，**你同意後才開工**

### 分派：`delegate` / `report` / `review`

**`delegate`**（主 agent）

1. 建立任務單 `.handoff/tasks/<日期>-<名稱>.md`
2. 記錄**分派基準**（`refs/handoff/<task-id>`），**當下還沒 commit 的修改也算在基準裡**，所以分派前就存在的修改不會被算成對方改的
3. 填寫任務單：目標、**可以動的檔案**、**不能動的檔案**、禁止事項、完成標準

可以動和不能動的檔案，每行寫一個用反引號包住的路徑或 glob：

```markdown
## 可以動的檔案
- `lib/page/report/**`
- `lib/l10n/intl_zh_TW.arb`

## 不能動的檔案
- `pubspec.yaml`
- `external_libs/**`
```

⚠️ 對方工作期間，主 agent **不要動同一個資料夾**，不然 review 分不出是誰改的。

**`report`**（被分派的 agent）

- 只改「可以動的檔案」。需要改範圍外的檔案時，停下來寫進「疑問」
- 填回報：每個檔案改了什麼、**實際跑過的**驗證指令和結果、沒處理完的事項
- 把狀態改為 `已回報`

**`review`**（主 agent）

列出分派後**實際**變動的檔案，並自動標記：

```
- ✅ `lib/a/x.dart`
- 🟡 範圍外 `notes.txt`（untracked）
- 🔴 禁止範圍 `pubspec.yaml`
```

接著主 agent 會逐檔看 diff，**自己重跑完成標準的驗證指令**，最後填寫驗收結果（`已驗收` 或 `退回`）。
**以 diff 為準，不以回報為準。**

---

## 檔案結構

```
~/.agents/skills/multiagent-handoff/   ← 本體（只改這裡）
├── README.md            ← 本文件（給人看）
├── SKILL.md             ← 給 agent 執行的流程
└── scripts/handoff.py   ← git 快照、分派基準、範圍檢查、對話紀錄讀取

<專案>/.handoff/          ← 只在本機（.git/info/exclude），不 commit
├── CURRENT.md           ← 最新交接狀態（每次 save 覆寫）
├── log.md               ← 換手紀錄（只追加）
└── tasks/
    ├── <task-id>.md         ← 任務單＋回報＋驗收
    ├── <task-id>.base.json  ← 分派基準（基準 commit、untracked 檔案雜湊）
    └── <task-id>.run.log    ← `--run` 時對方的完整輸出
```

另外每個分派任務會在 git 留一個 ref：`refs/handoff/<task-id>`。
它不會出現在分支列表，也不會被 push。驗收完可以刪除：

```bash
git update-ref -d refs/handoff/<task-id>
```

---

## 腳本指令（手動除錯用）

平常由 agent 呼叫，手動執行可以確認狀態：

```bash
H=~/.agents/skills/multiagent-handoff/scripts/handoff.py

python3 $H snapshot                       # 目前分支／HEAD／未提交修改／交接檔是否過期
python3 $H sessions                       # 本專案最近的 Claude Code／Codex／agy 對話摘要
python3 $H sessions --tool codex -n 3     # 只看 Codex，取最近 3 個
python3 $H new-task <名稱> --to Codex     # 開任務單並記錄基準
python3 $H run <task-id> --agent agy       # 叫起指定 agent 執行 report（--dry-run 只印指令）
python3 $H review <task-id>               # 驗收：實際變動＋範圍檢查（task-id 可只打部分）
python3 $H log "Claude → Codex｜完成 API，剩 UI"
```

所有指令都**只讀 git、只寫 `.handoff/`**，不會修改工作區檔案，也不會 commit。

---

## 已知限制

- `sessions`：Claude Code、Codex 完整；agy 只有使用者輸入；Copilot CLI、opencode 還不支援
- `run`：不重試、不做多模型 review（那是 ai-pair）；opencode 逾時中止時，背景 service 裡的 session 可能還在跑
- `review` 的 glob 用 Python `fnmatch`，`*` 會跨目錄比對（`lib/*.dart` 也會命中子目錄的檔案）
- 分派期間主 agent 如果也改了檔案，`review` 會一起列出，分不出是誰改的
- skill 是「被提到才觸發」：你沒說 handoff，agent 不會主動去讀 `.handoff/`（`AGENTS.md` 還沒加交接規則）

---

## 安裝位置

本體 `~/.agents/skills/multiagent-handoff/`，各工具讀取方式（2026-10-19 逐一實測，六個工具都看到**恰好 1 份**）：

| 工具 | 讀取位置 | 方式 | 實測方法 |
|---|---|---|---|
| Codex CLI | `~/.agents/skills/` | 原生 | 詢問 `codex exec` |
| Copilot CLI | `~/.agents/skills/` | 原生 | `copilot skill list` |
| opencode | `~/.agents/skills/` | 原生 | 詢問 `opencode run` |
| Claude Code | `~/.claude/skills/multiagent-handoff` | symlink | 詢問 `claude -p` |
| agy 1.4.2 | `~/.gemini/config/skills/multiagent-handoff` | symlink | 詢問 `agy -p`＋對照組 |
| Cursor CLI | `~/.agents/skills/`＋`~/.claude/skills/`（自動去重，實測 1 份） | 原生 | 詢問 `cursor-agent -p --mode ask` |

symlink 由 `~/.agents/link-skills.sh` 管理：

```bash
~/.agents/link-skills.sh          # 建立缺少的連結（新增跨工具 skill 後跑一次）
~/.agents/link-skills.sh check    # 只檢查：缺少／失效／被實體資料夾佔用（工具升版後跑一次）
~/.agents/link-skills.sh unlink   # 移除連結（只刪 symlink，不碰實體檔案）
```

⚠️ **agy 的路徑以實測為準，不要照官方網頁**。官方網頁寫 CLI 讀 `~/.gemini/antigravity-cli/skills/`，
但 agy 1.4.2 實際只讀 `~/.gemini/config/skills/`（放在前者連實體資料夾都讀不到）；
`~/.gemini/config/skills.json` 指向共用資料夾的寫法也實測無效。agy 升版後先跑 `check` 並重測一次。

### 換電腦重建

1. 把 `~/.agents/` 整個複製過去（本體＋`link-skills.sh`）
2. 執行 `~/.agents/link-skills.sh`
3. 各工具確認看得到 multiagent-handoff（方法見上表）

## 待辦

- [ ] 拿一個真實的小任務完整跑一次 `delegate → report → review`（候選：SSGS-14167）
- [ ] 在 Claude 額度快用完時實測一次 `save → resume`（換 Codex 接手）
- [ ] `AGENTS.md` 加一段交接規則（需要使用者確認，會影響所有 agent）
- [ ] 決定 `~/.agents/` 的備份方式（目前沒有 git、沒有備份；`~/.claude/skills/` 已另存 `~/.claude/backups/skills-20261019.tar.gz`）
