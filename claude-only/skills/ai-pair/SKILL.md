---
name: ai-pair
description: |
  Coordinates a heterogeneous AI team on one coding task: an external CLI
  implements, then reviewers from three different model families verify it.
  Use when a task already has a requirement document under docs/shared/ and
  needs implementation plus multi-model review, when a whole branch needs
  spec-compliance verification before merge, or when the user says /ai-pair,
  ai pair, dev-team, content-team, or team-stop.
  Do NOT use for config changes, i18n key additions, single-line fixes, or any
  task with no requirement document — without a spec baseline the reviewers
  degrade into style checkers. For a plain code review with no spec baseline,
  use stack-review instead.
argument-hint: "dev-team|content-team|team-stop [project] [--quick|--deep] [--dev=copilot|native|auto] [--conserve]"
disable-model-invocation: true
allowed-tools: Bash(copilot:*), Bash(agy:*), Bash(mktemp:*), Bash(git fetch:*), Bash(git diff:*), Bash(git log:*), Bash(git status:*)
metadata:
  version: 5.0.0
---

# AI Pair Collaboration

Coordinate heterogeneous AI teams: one creates, three review from different angles.
Uses Claude Code's native Agent tool, GitHub Copilot CLI, and Antigravity CLI (`agy`).

> **v5.0 核心原則：Claude 額度只花在「協調決策」與「review 驗證」；探索與實作外包給 external CLI。**
> 依據是資源不可替代性——Claude 額度耗盡時 Team Lead 本身停擺，整個流程無法運作；Copilot Credits 耗盡只需降級。
> 完整推導見 `reference/archive/重構建議-v5.0.md`，實測依據見 `reference/archive/phase-v5-cli-probe.md`。

## Why Multiple AI Reviewers?

Different model families have different blind spots. Reviewers from different families maximize coverage:

| Reviewer | Engine | Focus |
|---|---|---|
| copilot-reviewer | copilot CLI | bugs, security, concurrency, performance, edge cases |
| claude-reviewer | **native Agent subagent** | architecture, maintainability, **cross-file / cross-repo 查證** |
| gemini-reviewer | agy CLI | spec compliance, missing scenarios, requirement alignment |

> ⚠️ **多 reviewer 的存在目的就是維護品質，因此 reviewer 不是預算調節閥。**
> 依**任務風險**調整數量（Level 1/2/3）可以；依**預算壓力**削減不行。額度緊張時的調節閥見「Budget Pressure」段。

## When to Run ai-pair

**Prerequisite: a requirement document must exist.**

```
✅ Run ai-pair   → task has docs/shared/{feature}.md
❌ Skip ai-pair  → config change, i18n key, single-line fix, no requirement doc
```

沒有需求文件就沒有 spec 基準，`gemini-reviewer` 的 spec compliance 無從比對。

**一個分支可能由多份需求文件管轄**——Review Context Protocol 支援文件清單，不假設 1 task = 1 doc。

## Commands

```bash
/ai-pair dev-team [project]              # Level 2 review（預設）
/ai-pair dev-team [project] --quick      # Level 1: fast scan
/ai-pair dev-team [project] --deep       # Level 3: all 3 reviewers in parallel

/ai-pair dev-team [project] --dev=copilot   # developer 引擎（預設）
/ai-pair dev-team [project] --dev=native    # 品質優先，走 native subagent
/ai-pair dev-team [project] --dev=auto      # 依任務形狀自動判定
/ai-pair dev-team [project] --conserve      # 節約模式（見下）

/ai-pair content-team [topic]
/ai-pair team-stop
```

---

## Team Architecture

```
User (Commander)
  │
Team Lead ── 當前 Claude session（高階模型）
  │  Role: 協調、判斷、決策。不做大範圍探索、不做實作。
  │
  ├── explorer            → external CLI（常態外包）
  │     找相關檔案、既有 pattern、方法呼叫點、後端 enum 值
  │
  ├── developer           → copilot CLI（預設）／native subagent（品質升級）
  │     依 TASK context file 實作
  │
  ├── copilot-reviewer    → copilot CLI          [Level 2 / 3]
  ├── claude-reviewer     → native subagent      [Level 2 / 3]  ⛔ 不可省略
  └── gemini-reviewer     → agy CLI              [Level 1 / 3]
```

### ⚠️ 前提：Claude 額度歸零時 Team Lead 也停擺

Team Lead **就是**當前 session。額度真的歸零時整個協調層停止，沒有 fallback 能救——因為沒有人能派工。這正是「實作與探索優先外包」的根本理由：**盡可能延後那個時刻**。

### Claude 額度的邊際價值排序

1. **Team Lead**（協調、決策）— 不可替代
2. **claude-reviewer**（跨檔案／跨 repo 查證）— native 工具權限最完整，且是 developer 外包後唯一的獨立驗證環節
3. **explorer** — 可外包
4. **developer** — **最該外包**，唯一有成熟替代品的角色

---

## developer 引擎切換

| 優先序 | 引擎 | 觸發 |
|---|---|---|
| **預設** | copilot CLI | 常態 |
| 升級 | native Agent subagent | 見下方三條件 |

**切回 native 的條件（任一成立）：**

1. Copilot Credits 耗盡
2. 🔴 **同一任務連續 2 輪被 reviewer BLOCK** ← 兩次出局，封住 rework 稅
3. Team Lead 判定任務屬「同 pattern 重複套用」或「小範圍精確修改」

**引擎切換一律明確通知使用者，不得靜默切換。**

### 🔴 rework 稅

copilot-first 只有在「產出能一輪過 review」時才真的省。產出品質不足時，Team Lead 要讀、要驗、要判斷，reviewer 多輪往返——**這些成本全落在 Claude 額度上**。一輪爛的 copilot round 可能比直接 native 做掉更貴。條件 2 就是為此設的上限。

---

## explorer：探索常態外包

Team Lead 的探索工作是 Claude 額度的第二大消耗源，常態外包。風險是**決策者拿到有損摘要**，因此以下護欄為**強制**：

### 護欄一：結構化輸出 + 原文片段（最重要）

探索結果必須是結構化資料，**附關鍵程式碼原文片段與 `file:line`**，不是散文摘要。以 `--json-schema`（agy）強制。

> **摘要可以錯，引用的原文不會。** Team Lead 依原文片段判斷，而非依 explorer 的結論判斷。

### 護欄二：可稽核的搜尋軌跡

必須回報執行過的 grep／glob 指令與命中數。Team Lead 據此判斷**覆蓋面是否足夠**。

> 「沒找到」與「沒找對地方」在摘要裡長得一模一樣，只有搜尋軌跡能區分。

#### 🔴 explorer 輸出一律 `tee` 落檔，禁止截斷

```bash
copilot ... -p "..." | tee "$EXPLORE_OUT"      # ✅
copilot ... -p "..." | tail -60                # ❌ 破壞搜尋軌跡
```

**v5.0 首跑時執行者本人違反了這條**：用 `tail -60` 截取 explorer 輸出，把搜尋軌跡整段丟掉。後果是**無法區分「explorer 漏了某個位點」與「我截掉了」**——護欄二的稽核能力歸零，該輪的覆蓋面分析只能存疑。

搜尋軌跡在輸出**前段**（工具呼叫記錄），findings 在後段。`tail` 正好砍掉軌跡，`head` 正好砍掉結論——**兩者都不能用**。

### 護欄三：關鍵點抽驗

高風險檔案與契約邊界（權限判定、API DTO、路由、狀態結構），Team Lead **仍自行讀取確認**。預設外包，關鍵點抽驗。

### 護欄四：不可外包白名單

| 不可外包（Team Lead 自行讀取） | 為什麼 |
|---|---|
| 需求文件（`docs/shared/*.md`）與其裁決清單 | 這是所有判斷的基準；基準錯則全盤錯 |
| 專案規則（CLAUDE.md／AGENTS.md／`.claude/rules/`） | 規則理解錯會**系統性**違規，且 reviewer 也抓不到（依同一份錯誤理解） |
| 最終決策所依據的關鍵檔案原文 | 決策品質直接相依 |

**可外包的範圍**：哪些檔案相關、既有 pattern 長什麼樣、某方法有沒有被呼叫、某 enum 後端有哪些值——**發現性、廣度性**工作。
**不外包**：上表白名單，以及對探索結果的**解讀與取捨**。

---

## Review Levels（二維）

| | 決定 |
|---|---|
| **Level**（1/2/3） | 派幾個 reviewer |
| **Effort**（low/medium/high/…） | 每個 reviewer 想多深 |

```
Level 1 — Quick scan (--quick)   : gemini-reviewer only        ~30s
Level 2 — Standard (default)     : copilot + claude (parallel) ~2 min
Level 3 — Deep (--deep)          : all 3 in parallel           ~3 min
```

預設 effort：Level 1 → `low`；Level 2 → `medium`；Level 3 → `high`（copilot 可上探 `xhigh`/`max`）。

**Auto-escalation**：Level 1 找到 CRITICAL → 升 Level 2（通知使用者）。Level 2 在核心模組找到 CRITICAL → 建議 Level 3（詢問使用者）。

### Budget Pressure：額度緊張時調什麼

**⛔ 不可削減 reviewer 組成。** 調節閥依序是：

1. 降 `--effort`（同一組 reviewer，深度略減）
2. 縮小 explorer 的探索範圍
3. 把任務切更細（單輪範圍小 → 成本低，且 review 更精準）
4. developer 維持 copilot（本來就是預設）

### 節約模式（`--conserve`）

Team Lead 自身也要收斂，否則只省了實作、額度照樣燒完：

- ❌ 不自己做大範圍 Read/Grep 探索 → 連探索一起委派
- ✅ TASK context file 寫得**更完整**（減少往返輪次）
- ⚠️ **review 強度與角色組成不變**——換了 developer 引擎意味著產出更需要驗證

---

## Model Selection（摘要）

**Tier 是意圖宣告，不是模型清單。** Team Lead 只宣告角色需要的 tier，由 `resolve_model(cli, tier)` 從**當下實際可用清單**挑選（pattern 比對，不寫死 slug）。

```
developer 預設：gpt-5.4-mini  ⇄ claude-sonnet-5 → gpt-5.3-codex → gpt-5.6-terra
⛔ 永不進入 developer：mai-code-1-flash-picker、gpt-5.6-luna、claude-sonnet-4.6、任何未過 A/B 者
🟡 kimi-k2.7-code：僅手動指定（品質佳但成本 2.37×），需 --allow-all-paths
```

| 項目 | developer | reviewer |
|---|---|---|
| 模型資格 | 🔴 **必須在 A/B 已驗證白名單內**（⚠️ **不是 tier**——tier 是成本分級，非品質分級） | 任何可用模型 |
| `--effort` 下限 | **medium 以上** | low 可接受（Level 1） |

🔴 **派工前必須實際執行 `assert_dev_model` / `assert_dev_effort` 兩個 gate。** 「宣告但無機制」的規則不會報錯，只會靜默被違反——v5.0 上線前這條下限正是此狀態，且與預設模型 `gpt-5.4-mini`（LOW tier）互相矛盾而無人察覺。

**准入條件（淘汰制）**：①遵守 Constraints ②不產出空殼實作 ③🔴**回報必須誠實（淘汰項）**④效率不劣化。
新模型**必須**過 A/B 才能進偏好序；**成本一律用實測 credits，不可用 list price 推算**。

⚠️ **agy 同時接受 slug（`gemini-3.1-pro-high`）與顯示名（`Gemini 3.1 Pro (High)`）**，兩者皆有效。
⚠️ **兩個 CLI 命名慣例相反**：copilot 用點（`claude-haiku-4.5`），agy slug 用連字號（`claude-sonnet-4-6`）。

> 📖 完整 tier pattern 表、准入程序、已驗證/黑名單清單、費率快照 → `reference/model-selection.md`

## Prerequisites

- **Claude Code** — Team Lead + native subagent runtime
- **Copilot CLI** (`copilot`) — explorer / developer / copilot-reviewer
- **Antigravity CLI** (`agy`) — gemini-reviewer

```bash
copilot --version && agy --version
```

### Permissions Setup

```json
"Write(//tmp/**)",
"Bash(mktemp:*)",
"Bash(copilot:*)",
"Bash(agy:*)"
```

⚠️ **必須用萬用字元。** 逐模型列舉與動態選模互斥——每出一個新模型就要加一條。

---

## Quota Fallback

| ERR code | Action |
|---|---|
| QUOTA | Mark SKIPPED, continue with remaining |
| AUTH | Prompt user to re-login, continue |
| MODEL | Try fallback chain; if all fail → SKIP |
| TIMEOUT | Retry once; if still fails → SKIP |
| CLI_MISSING | Mark SKIPPED, show install command |

**Minimum viable threshold**：2+ reviewers → continue with note；1 → continue with warning；0 → abort。

⛔ **但 claude-reviewer 不列入可跳過的範圍**（native subagent 幾乎不會失敗；若它失敗代表 Claude 額度問題，此時 Team Lead 本身也已受影響）。

---

## Workflow

1. **User assigns task** → Team Lead 讀需求文件與專案規則（**不外包**），委派 explorer 做廣度探索
2. **Team Lead** 依 explorer 的結構化結果 + 關鍵點抽驗，寫 TASK context file
3. **Team Lead dispatches** `TASK:{path}` → developer（預設 copilot）
4. **developer implements** → `DONE:{files}` + summary
5. **Team Lead 機械驗證** `DONE` 宣稱的檔案是否真的變更（`git diff --stat`），並**實跑** Verification 指令
6. **Team Lead 呈現結果**，詢問是否 review
7. **User approves** → Team Lead 建 manifest，並行派發給 reviewers
8. **Reviewers report** → Team Lead 收集、處理 ERR、機械驗證 findings 路徑
9. **Team Lead translates** 為人類可讀並呈現
10. **User decides** → Revise（回步驟 2，帶 feedback）或 Pass
11. **Team Lead 處理 review cache**：PASS → 刪除；WARN/BLOCK → 寫入，下輪作為 `Previous findings`

**Auto PASS/BLOCK**：全 PASS → auto PASS；任一 BLOCK → BLOCK，使用者裁決；全 WARN → 列出警告。

---

## Team Lead Execution Steps

### Step 1: Create Team

```
TeamCreate: team_name = "{project}-dev" or "{topic}-content"
```

> ⚠️ **環境相容性**：部分環境沒有 `TeamCreate` / `TeamDelete`（native Agent Teams 未啟用）。**不要中止**——Team Lead = 當前 session，其餘角色用 Bash 直呼 CLI 或 Agent 工具啟動 subagent。偵測方式：`TeamCreate` 不在工具清單或呼叫失敗 → 跳過 Step 1。`team-stop` 同理跳過 `TeamDelete`。

### Step 2: Pre-flight

```bash
copilot --version || echo "COPILOT_MISSING"
agy --version || echo "AGY_MISSING"
```

缺少任一 CLI 時警告使用者，詢問降級執行或中止。

### Step 3: Launch Agents

native subagent 用 Agent 工具（`subagent_type: "general-purpose"`）；external CLI 用 Bash 直呼。

### Step 4: Confirm to User

```
Team ready.

Team: {team_name}
  Team Lead:         當前 session
  explorer:          copilot CLI（常態外包）
  developer:         copilot CLI ({resolved_model})  ← --dev=native 可改
  copilot-reviewer:  copilot CLI ({resolved_model})
  claude-reviewer:   native subagent
  gemini-reviewer:   agy ({resolved_model})

Review level: Level 2 (default)  Effort: medium
Awaiting your first task.
```

---

## Team Lead Planning Protocol

### 🔴 Bias Mitigation

**統籌者為高階模型時，此風險更高。** 模型能力越強，「我自己判斷就好、reviewer 共識不重要」的誘惑越大。

Team Lead 不應對以下情況自信：

- **Self-review**：一律送至少 2 個 reviewer，絕不跳過
- **「小」改動**：即使 typo 也走 Level 1，不得未經 review 自行接受
- **熟悉程度**：高風險模組（auth、payment、核心邏輯）一律 Level 3
- 🔴 **駁回共識**：**若 3 個 reviewer 全報 BLOCK，接受它，不得以統籌者判斷駁回**

**Auto-escalation**：Team Lead 在 5 個任務內駁回 2 次以上 BLOCK → 停下來稽核偏誤。

### 派工前

1. **自行讀取**需求文件與專案規則（不可外包，見 explorer 護欄四）
2. 委派 explorer 做廣度探索，取結構化結果 + 原文片段
3. 對關鍵點抽驗
4. 有歧義時最多問一個問題
5. **一次只派一個任務**，不批次打包
6. 寫 TASK context file

```bash
TASK_FILE=$(mktemp /tmp/task-context-XXXXXX)   # macOS 不支援 X 之後的後綴
```

### TASK context file 格式（三個引擎共用同一份）

```markdown
# Task: {task name}

## Project Context
- Project path / Tech stack / Tier
- Relevant files（附 explorer 回報的 file:line 與原文片段）

## Requirement
{Clear description}

## Implementation Guide
{Specific instructions, before/after snippets, edge cases}

## Files to Modify
- {filepath}: {what to change}

## Constraints
- ❌ 絕對禁止執行任何 git 指令（commit 由使用者人工處理）
- {project-specific rules from CLAUDE.md / AGENTS.md}

## Verification
- {必須是可實際執行的指令，例如 flutter analyze / flutter test <path>}

## Conflict Handling
- 若 Constraints 與 Verification 互相衝突（例如 Files to Modify 的範圍不足以讓
  Verification 的成功條件成立）→ 🔴 **停下來回報衝突，不可自行擴張範圍**。
  回報格式：`CONFLICT:{哪兩條衝突}|{你認為的最小解法}`，然後結束。
- 需求本身有歧義且無法從 Constraints 推斷 → 同樣回報 `CONFLICT:`，不要猜。
```

> ⚠️ Verification **不接受**「已驗證」的文字聲明——Team Lead 或 reviewer 必須實跑。

> 🔴 **Conflict Handling 段不可省。** phase5 實測：TASK 的 Files-to-Modify 只列 2 個檔案，而 Verification 的成功條件需要改 4 個檔案。developer **誠實回報了殘留**（誠實性通關），但**自行擴張範圍**去滿足 Verification，違反了 Files-to-Modify。
> 這是**協定缺口而非模型缺陷**——當時 TASK 格式沒有「衝突時該怎麼辦」的指示，模型只能二選一。
> 機械驗證（`git diff --name-only` 比對）正確攔下了超範圍改動，但事前指示能讓它根本不發生。

---

## Review Context Protocol（骨架）

| Step | 動作 | 不可省的理由 |
|---|---|---|
| 0 | Cache check（`.ai-pair-cache/review-findings/{task_id}.md`） | 48h 內小幅迭代可帶 `Previous findings` |
| 1 | 🔴 `git fetch origin` + 檢查是否落後 target | 本地 ref 可能過期數週；實測曾攔到「分支已被合併」使原定範圍變空 |
| 2 | 建 MANIFEST（**四段**，見下） | 傳路徑不傳 payload |
| 3 | 派發（`--add-dir` 專案 + 後端 repo） | reviewer 才能跨檔案／跨 repo 查證 |
| 4 | reviewer 讀取範圍：**可讀任何驗證所需檔案，但不得擴張範圍** | v4.x 的「不得讀 source」禁令已廢除 |
| 5 | 收集：🔴**原始輸出落檔留存（含失敗）** → 抽取 JSON → 機械驗證路徑（🔴**須經共用正規化函式**）→ 抽驗 W/C 級 | 失敗輸出是稽核證據＋零成本回歸測試資料 |
| 6 | Cache 寫入／清除（PASS 則刪） | — |

### MANIFEST 四段

1. **裁決／決議清單**（從需求文件抽取，**不丟全文**；支援多份文件）
2. **審查範圍**：檔案路徑清單 + `git diff --stat`
3. 🔴 **契約面清單**（非 nullable `$enumDecode` 位點、DTO wire format、權限字串 ↔ 後端）
4. **指示**：自行讀取；可讀範圍外檔案以查證，但不得擴張範圍

> 🔴 **第 3 段不可省略。** v5.0 首跑實測：預埋的已知契約缺陷 **3 個 reviewer 全數未發現**——缺陷宿主檔案不在 diff 內，而 manifest 要求不得擴張範圍，**範圍紀律反過來阻止了發現**。不能期待 reviewer 自行發現範圍外的相依契約，**Team Lead 必須主動列出**。

> 📖 完整六步規格、契約面清單範本、統一解析配方（三條鐵則）、Inter-Agent Protocol v2、Translation Layer → `reference/review-protocol.md`

## Agent Prompt Templates

詳見 `reference/agents-prompts.md`。

---

## Known Limitations（摘要）

- 🔴 **兩個 CLI 的 stdout 都不保證是乾淨 JSON** → 一律落檔 + 抽取 JSON 物件行
- 🔴 **agy headless 需 `--dangerously-skip-permissions`**；缺它會「假成功」（`SUCCESS` 但無 `structured_output`）
- 🔴 **不可用變數名 `status`**（zsh 唯讀保留字）；**輸出勿穿過 shell 變數**（控制字元壞 `jq`）
- 🔴 **`agy models > file` 會 hang**，須接管線
- 🔴 **developer 必須加 `-s` 且 Verification 輸出另外落檔**——不加 `-s` 只會拿到工具日誌、最終摘要丟失，且巢狀輸出被截成 `8 lines…`，「回報誠實性」淘汰項就失去唯一憑據
- 🔴 **凡「產生」與「驗證」成對出現，必須共用同一實作**。已兩次造成靜默失效：findings 路徑驗證（scope 用相對／reviewer 回絕對 → 有效 findings 整份誤殺）、reference 的 TOC 錨點（產生器啟發式／驗證器 GitHub 演算法 → 8/63 連結失效）。**兩者都不拋錯**，只能靠結構排除
- copilot `--max-ai-credits` **最小值 30**；macOS 無 `timeout`；`mktemp` 不支援 X 後綴
- **成本無統一計價單位**（Claude 訂閱／Copilot Credits／agy 免費額度三池），跨池比較無法計算
- **無整體評測機制**；唯一例外是 developer 模型的 A/B 准入程序

> 📖 完整清單、已修正/已過期項目的版本沿革 → `reference/known-limitations.md`

## team-stop Flow

1. Send `shutdown_request` to all agents
2. Wait for confirmation
3. `TeamDelete`（環境無此工具則跳過；清掉 `/tmp` 暫存與背景 agent）
4. Output:
   ```
   Team shut down.
   Closed: explorer, developer, copilot-reviewer, claude-reviewer, gemini-reviewer
   Resources cleaned up.
   ```

---

## Reference 索引（一層引用）

### 操作型（執行流程時載入）

| 檔案 | 內容 | 何時載入 |
|---|---|---|
| `reference/review-protocol.md` | Review Context Protocol 六步、MANIFEST 契約面清單範本、統一解析配方、Inter-Agent Protocol v2、Translation Layer | 要派 review 時 |
| `reference/cli-invocation-ref.md` | 各角色的 CLI 指令規格、findings schema、錯誤處理、原始輸出落檔、幻覺路徑攔阻 | 要呼叫 CLI 時 |
| `reference/agents-prompts.md` | 各角色的 agent 初始化 prompt（可直接複製） | 要啟動 agent 時 |
| `reference/model-selection.md` | tier pattern、兩 CLI 命名慣例、developer gate 與黑白名單、費率快照 | 要解析模型時 |
| `reference/ab-admission-method.md` | A/B 准入程序、四條淘汰制條件、六個方法論規則 | **要納入新模型或換 CLI 時** |
| `reference/known-limitations.md` | 現行限制、已修正項目的版本沿革、未驗清單 | 遇到異常行為時 |

⚠️ **操作型 reference 彼此不互相引用**，全部由本檔索引——載入任一份就能執行，不必再追下一層。

### 紀錄型（`reference/archive/`，只在查依據時載入）

| 內容 | 說明 |
|---|---|
| `archive/重構建議-v5.0.md` | v5.0 完整推導、被實測推翻的初稿主張、修訂紀錄 |
| `archive/phase-v5-cli-probe.md` | E1–E8 實測原始紀錄（CLI 能力、費率、輸出格式、回歸測試） |
| `archive/phase6-golive-acceptance.md` | 上線驗收：四項阻擋的修正與證據、契約面清單有效性 A/B |
| `archive/phase2-*` … `archive/phase5-*` | 各輪 A/B 與實測的原始產物 |
| `archive/重構建議-v3` ~ `v4.5.1` | 歷史提案（含未採納者） |

### 提案型

| 檔案 | 狀態 |
|---|---|
| `reference/重構建議-v5.1.md` | **提案中，未採納**——CLI adapter 抽象層與引擎抽換評估（加減 codex／opencode、退訂 copilot 的影響） |

📚 紀錄型文件**不隨 live skill 安裝**，僅存於 repo 工作副本與完整快照。它們之間允許互相標註出處（那是來源引用，不是取得指令的導航）。

---

*v5.0 — 2026-07-30 | Claude 額度只花在協調決策與 review 驗證／developer 預設 copilot（native 為品質升級，含兩次出局護欄）／新增 explorer 角色與四道護欄／claude-reviewer 強制保留，reviewer 不作預算調節閥／developer 模型篩選與 A/B 准入制度化（回報誠實性為淘汰項）／傳遞層改 manifest，廢除「reviewer 不得讀 source」禁令／模型層改執行期發現／結構化輸出與幻覺路徑機械攔阻*

*實測依據：`reference/archive/phase-v5-cli-probe.md`（E1–E5）、`reference/phase3-luna-kimi/`（developer 候選 A/B）*
*完整推導與被推翻的初稿主張：`reference/archive/重構建議-v5.0.md`*
