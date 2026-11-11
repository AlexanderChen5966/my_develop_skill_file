# AI-Pair：異構 AI 團隊協作 | Heterogeneous AI Team Collaboration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Experimental](https://img.shields.io/badge/Status-Experimental-orange.svg)](#狀態)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills)

> 版本：5.0.0 | 授權：MIT | 作者：Axton Liu

讓不同 AI 模型組成團隊協作：一個創作，三個從不同角度審查同一份工作 — 不是為了冗餘，而是因為不同模型家族天然關注不同維度。

Coordinate multiple AI models as a team: one creates, three review the same work from different angles — not for redundancy, but because different model families naturally focus on different dimensions.

> **🔴 v5.0 重大變更（2026-07-30）：**
> 1. **Claude 額度只花在「協調決策」與「review 驗證」**——探索與實作外包給 external CLI。依據是資源不可替代性：Claude 額度耗盡時 Team Lead 本身停擺。
> 2. **傳路徑，不傳 payload**——給 CLI 的是 manifest 路徑 + `--add-dir`，不再把內容嵌入 `-p`。實測證明捏造路徑是傳遞方式造成的。
> 3. **廢除「reviewer 不得讀 source」禁令**——該禁令廢掉了跨檔案／跨 repo 查證能力。
> 4. **新增 `explorer` 角色**（探索常態外包，附四道護欄）。
> 5. **模型改執行期發現**，不再查死表；developer 模型建立 A/B 准入制。
>
> ⚠️ **v4.3 遷移備註（2026-06-22）：** Gemini CLI（`gemini`）自 2026-06-18 起停止為 Google One / 免費帳號服務，gemini-reviewer 底層已遷移至 **Antigravity CLI（`agy`）**。角色名稱 `gemini-reviewer` 保留不變。

> **本文件為合併版：** 原 `說明文件.md` 已併入本 README（v4.3 起只維護單一說明文件，避免雙份文件版本落差）。

---

## 目錄

1. [狀態](#狀態)
2. [核心理念](#核心理念)
3. [系統架構](#系統架構)
4. [前置條件](#前置條件)
5. [Tier 系統與可用模型](#tier-系統與可用模型)
6. [安裝方式](#安裝方式)
7. [使用方式](#使用方式)
8. [Review Levels](#review-levels)
9. [工作流程詳解](#工作流程詳解)
10. [CLI 呼叫協定](#cli-呼叫協定)
11. [使用範例](#使用範例)
12. [常見問題排查](#常見問題排查)
13. [未包含的功能](#未包含的功能)
14. [專案演變](#專案演變)
15. [檔案結構](#檔案結構)

---

## 狀態

> **實驗性 | Experimental**
>
> - 公開原型，可用於實際工作流程，但尚未涵蓋所有邊界情況。
> - 需要 Claude Code + Copilot CLI；gemini-reviewer 另需 Antigravity CLI（`agy`）。
> - 重點是展示工具與系統如何協作，而非長期維護此程式庫。
> - 如遇問題，請提交可重現的案例（輸入 + 輸出 + 重現步驟 + 環境資訊）。

---

## 核心理念

### 為什麼需要多個 AI 審查者？

大多數人使用多個 AI 的方式是：把同一個問題分別問一遍，然後對比答案。這只用到了不同模型能力的一個維度 — 你得到的是同一個問題的多個回答，而不是同一份工作的多個視角。

AI-Pair 把模型差異變成結構化工作流程：給每個模型分配匹配其特長的角色，讓它們從不同角度審查同一份工作。

| 傳統做法 | AI-Pair 做法 |
|---------|-------------|
| 同一問題 → 多個答案 | 同一份工作 → 多個視角 |
| 各自獨立回答 | 結構化角色分工 |
| 人工對比結果 | 自動彙總報告 |

### 三個 reviewer 的正交視角

| Reviewer | 模型 | 關注面向 |
|---|---|---|
| copilot-reviewer | GPT-5.4 mini（via Copilot CLI） | bugs、安全性、並發、效能、邊界條件 |
| claude-reviewer | Claude subagent | 架構、設計模式、可維護性、替代方案 |
| gemini-reviewer | agy「Gemini 3.1 Pro (High)」 | spec compliance、遺漏情境、需求對齊 |

三者幾乎零重疊，這正是這套設計的價值所在。

---

## 系統架構

### 開發團隊（`/ai-pair dev-team [project]`）

```
使用者（Commander）
  │
團隊領導（當前 Claude Code 工作階段）
  │  職責：規劃任務、分析程式碼、產出任務文件、協調
  │
  ├── copilot-developer（Claude Code Agent）
  │     └── 呼叫 → copilot --model claude-sonnet-4.6 --allow-all-tools --autopilot
  │           職責：依任務文件自主執行開發
  │
  ├── copilot-reviewer（Claude Code Agent）      [Level 2 / Level 3]
  │     └── 呼叫 → copilot --model gpt-5.4-mini -p "..."
  │           職責：bugs、安全性、並發、效能、邊界條件
  │
  ├── claude-reviewer（Claude Code Agent）        [Level 2 / Level 3]
  │           職責：架構、設計模式、可維護性
  │
  └── gemini-reviewer（Claude Code Agent）        [Level 1 / Level 3]
        └── 呼叫 → agy --model $M --dangerously-skip-permissions --add-dir ... -p "..."
              職責：spec compliance、遺漏情境、需求對齊
```

### 內容團隊（`/ai-pair content-team [topic]`）

```
使用者（Commander）
  │
團隊領導（當前 Claude Code 工作階段）
  ├── author（Claude Code Agent）— 撰寫文章 / 腳本 / Newsletter
  ├── copilot-reviewer — copilot CLI：邏輯、準確性、結構、事實查核
  ├── claude-reviewer — Claude 視角：可讀性、吸引力、風格、受眾適配
  └── gemini-reviewer — agy：完整性、遺漏重點、主題對齊
```

⚠️ **必須用萬用字元**——逐模型列舉與動態選模互斥。

> 💡 亦可在 `SKILL.md` frontmatter 加 `allowed-tools` 做**單輪**預先批准（免權限提示），但授權在下一則使用者訊息即清除，多輪流程仍須上方的 `settings.json` allow-rules。

---

## 前置條件

皆為**命令列工具**，在終端機中執行（Terminal、iTerm2 等），不是桌面應用程式。

| 工具 | 用途 | 安裝 / 驗證 |
|------|------|------|
| [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) | Team Lead + agent runtime | `npm install -g @anthropic-ai/claude-code` → `claude --version` |
| [Copilot CLI](https://github.com/github/copilot-cli) | explorer / developer / copilot-reviewer | `npm install -g @github/copilot-cli` → `copilot --version` |
| Antigravity CLI（`agy`） | gemini-reviewer（取代停服的 Gemini CLI） | 依官方指引安裝 → `agy --version` |

所有 CLI 使用前都需完成認證設定。

### 權限設定（必要）

加入 `.claude/settings.local.json`：

```json
"Write(//tmp/**)",
"Bash(mktemp:*)",
"Bash(copilot:*)",
"Bash(agy:*)"
```

⚠️ **必須用萬用字元**——逐模型列舉與動態選模互斥（每出一個新模型就要加一條）。

> 💡 亦可在 `SKILL.md` frontmatter 加 `allowed-tools` 做**單輪**預先批准（免權限提示）。但依官方文件，該授權在下一則使用者訊息即清除，且它**只預先批准、不限制**工具；ai-pair 是多輪流程，仍須上方的 `settings.json` allow-rules。

---

## Tier 系統與可用模型

模型選擇由 **Tier**（成本 + 能力）引導：

| Tier | Output Credits/M | 模型 | 適用情境 |
|---|---|---|---|
| **FREE** | 200 | `gpt-5-mini` | Fallback、額度耗盡 |
| **LOW** | 450~500 | `gpt-5.4-mini`、`claude-haiku-4.5`、agy `"Gemini 3.5 Flash (Low)"` | Level 1 快速掃描、成本敏感 |
| **STANDARD** | 1,400~1,500 | `claude-sonnet-4.6`、`gpt-5.2/5.3/5.4`、agy `"Gemini 3.5 Flash (Medium)"` | Level 2/3 預設 |
| **PREVIEW** | — | agy `"Gemini 3.1 Pro (High)"` | gemini-reviewer Level 3 深度 review 主力 |
| **COMPLEX** | 1,400+ | `gpt-5.3-codex`（保留） | 企業級任務 |

### agy 可用模型清單（實測確認 2026-06-22）

| 模型名稱 | tier 對應 | 備註 |
|---|---|---|
| `Gemini 3.5 Flash (Low)` | LITE | 速度最快，Level 1 |
| `Gemini 3.5 Flash (Medium)` | STANDARD | 預設模型，fallback 層 |
| `Gemini 3.1 Pro (High)` | PREVIEW | 最強，Level 3 主力 |
| `Claude Sonnet 4.6 (Thinking)` / `Claude Opus 4.6 (Thinking)` | — | Anthropic |
| `GPT-OSS 120B (Medium)` | — | OpenAI |

> ⚠️ `--model` 必須帶引號完整名稱（含括號）。傳入無效名稱時 agy **不報錯**，會靜默改用預設模型 — 請確認字串完全符合上表。

---

## 安裝方式

### 方式 A：直接安裝（推薦）

```bash
# 全域安裝（所有專案都可使用）
git clone https://github.com/axtonliu/ai-pair.git ~/.claude/skills/ai-pair

# 專案層級安裝
git clone https://github.com/axtonliu/ai-pair.git .claude/skills/ai-pair
```

### 方式 B：手動安裝

1. 下載本儲存庫的 `SKILL.md`
2. 放到 `~/.claude/skills/ai-pair/SKILL.md`
3. 重新啟動 Claude Code

---

## 使用方式

```bash
/ai-pair dev-team [project]          # 啟動開發團隊（預設 Level 2）
/ai-pair dev-team [project] --quick  # Level 1：快速掃描（agy only）
/ai-pair dev-team [project] --deep   # Level 3：三 reviewer 並行
/ai-pair content-team [topic]        # 啟動內容團隊
/ai-pair team-stop                   # 關閉團隊，清理資源
```

範例：

```bash
/ai-pair dev-team b2b-manager
/ai-pair dev-team SSGS-11275 --deep
/ai-pair content-team AI-Newsletter
/ai-pair team-stop
```

> **何時啟動 ai-pair？** 前提是任務已有需求文件（`docs/shared/{feature}.md`）。config 改動、單一 i18n key、單行修正、無需求文件者，跳過 ai-pair。

---

## Review Levels

| Level | 指令 | Reviewer 組合 | 適用情境 | 估時 |
|-------|------|-------------|---------|------|
| 1 | `--quick` | gemini-reviewer only（agy「Gemini 3.5 Flash (Low)」） | typo、i18n、小 UI 調整 | ~30s |
| 2 | 預設 | copilot-reviewer + claude-reviewer（並行） | 一般功能、bug fix | ~2min |
| 3 | `--deep` | 三 reviewer 並行 | 架構變更、高風險模組、核心邏輯 | ~3min |

**自動升級：** Level 1 發現 CRITICAL → 自動升 Level 2（通知使用者）；Level 2 在核心模組發現 CRITICAL → 建議升 Level 3（詢問使用者）。

---

## 工作流程詳解

AI-Pair 採用**半自動工作流程** — 每一步你都保持完整控制權，不會有自動執行的迴圈。

```
步驟 1：你下達任務
        ↓
步驟 2：Team Lead 分析程式碼，產出任務文件（/tmp/task-context-XXXX）
        ↓
步驟 3：developer 收到任務文件路徑，呼叫 Copilot CLI（模型執行期解析）自主開發
        ↓
步驟 4：Team Lead 回報開發結果（修改了哪些檔案），你決定是否送審
        ↓ （你批准）
步驟 5：Team Lead 產生一份共用 MANIFEST（路徑清單 + 裁決清單），依 Level 並行 dispatch
        ↓
步驟 6：reviewer 以壓縮格式回報，Team Lead 彙總並處理任何 ERR
        ↓
步驟 7：Team Lead 翻譯成人類可讀報告呈現給你
        ↓
步驟 8：你決定
    ├── 「修改」→ 回到步驟 1（帶著審查意見）
    └── 「通過」→ 下一個任務或結束
```

### 核心設計

- **Inter-Agent Protocol v2**：agent 間優先使用**結構化輸出**（agy `--json-schema`；copilot 以 `-s` + prompt 約束 JSON），不再靠模型自律遵守文字格式；只有最終報告轉成人類可讀。
- **manifest-based review**：Team Lead 產生一份共用 `MANIFEST`（審查範圍路徑清單 + 需求文件的裁決清單），透過 `REVIEW:{path}` 傳給各 reviewer；**reviewer 可讀任何驗證 finding 所需的檔案**（含跨 repo），但不得擴張審查範圍。
- **機械驗證**：`DONE:{files}` 用 `git diff --stat` 比對，findings 的 `file` 須在審查範圍內，否則整份棄用——不採信摘要。
- **單任務 dispatch**：每次只 dispatch 一個小型任務文件，不批次多任務。
- **Review 結果快取**：WARN/BLOCK 時寫入 `.ai-pair-cache/review-findings/{task_id}.md`，48h 內 re-review 自動附加 `Previous findings`。
- **Quota Fallback**：見下方 CLI 協定的 fallback chain；Claude subagent 永遠可用。

---

## CLI 呼叫協定

> 🔴 **v5.0：一律傳路徑，不嵌 payload。** 模型名稱由執行期 `resolve_model(cli, tier)` 解析，以下 `$M` 代表解析結果。
> 完整規格見 `reference/cli-invocation-ref.md`。

### 探索者模式（explorer，v5.0 新增）

```bash
copilot --model $M --allow-all-tools \
  --add-dir "$PROJECT_DIR" --add-dir "$BACKEND_REPO" \
  --max-ai-credits 30 -s --effort low \
  -p "Explore the codebase to answer the questions in $EXPLORE_MANIFEST.
      For every finding include file:line AND the verbatim source snippet.
      Report the grep/glob commands you ran and their hit counts.
      Do NOT modify any file. Do NOT run git commands."
```

- **逾時**：300000ms。**Tier**：LOW。
- **四道護欄**：結構化輸出+原文片段／可稽核搜尋軌跡／關鍵點抽驗／不可外包白名單（需求文件與專案規則由 Team Lead 自讀）。

### 開發者模式（developer）

```bash
copilot --model $M --allow-all-tools --autopilot \
  --add-dir "$PROJECT_DIR" --add-dir /tmp \
  --max-ai-credits $CAP --effort $EFFORT \
  -p "Read the task context file at $TASK_FILE and implement exactly what it
      describes. Follow its Constraints strictly. Do NOT run git commands.
      Run the Verification commands and report the ACTUAL output."
```

- **逾時**：600000ms（`--autopilot` 可能多輪）。**Tier**：STANDARD 以上（禁用 LOW/FREE）。
- 🔴 **Team Lead 須機械驗證 `DONE`**：`git diff --stat` 比對宣稱改動的檔案，並實跑 Verification。
- **引擎切換**：Credits 耗盡／同任務連續 2 輪 BLOCK／同 pattern 重複任務 → 改 native subagent，並明確通知。

### 審查者模式（copilot-reviewer）

```bash
copilot --model $M --allow-all-tools \
  --add-dir /tmp --add-dir "$PROJECT_DIR" --add-dir "$BACKEND_REPO" \
  --max-ai-credits $CAP -s --effort $EFFORT \
  -p "Read the review manifest at $MANIFEST and follow it.
      Focus: bugs, security, concurrency, performance, edge cases.
      You MAY read any file needed to verify a finding, but do NOT expand
      the review scope beyond what the manifest declares.
      Output ONLY JSON: {findings:[{file,line,severity,issue,fix}], verdict}"
```

- **逾時**：300000ms。**Fallback**：依 tier pattern 偏好序，最終 `--model auto`。
- 🔴 **只用 `-s`，不加 `--output-format json`**——後者是 JSONL 事件串流。
- 🔴 **`-s` 的 stdout 也不保證乾淨**：多步驟工具呼叫時過程敘述會混入，JSON 在尾端 → `grep -o '{"findings".*}' | tail -1`。

### 規格審查者模式（gemini-reviewer → agy）

```bash
agy --model $M --dangerously-skip-permissions \
  --add-dir "$PROJECT_DIR" --add-dir "$BACKEND_REPO" \
  --output-format json --json-schema "$FINDINGS_SCHEMA" --effort $EFFORT \
  -p "Read the review manifest at $MANIFEST and follow it.
      Focus: spec compliance against the decision list, missing scenarios."
```

- **逾時**：300000ms。
- 🔴 **必須加 `--dangerously-skip-permissions`**——`--add-dir` 只給檔案讀取權，grep/glob 在 headless 會被自動拒絕，導致回 `SUCCESS` 卻空手而回（**假成功**）。
- 🔴 **解析取 `.structured_output`，不取 `.response`**（後者混入 agent 過程敘述）；`SUCCESS` 但 `structured_output` 為空 → 判為 `ERR:MODEL`。
- **錯誤判定**：`.status == "ERROR"` → `ERR:MODEL`（附可用清單，**零 token 消耗**，重試無成本）。
- **模型命名**：agy **同時接受** slug（`gemini-3.1-pro-high`）與顯示名（`Gemini 3.1 Pro (High)`）。
  ⚠️ 兩個 CLI 慣例相反——copilot 用點（`claude-haiku-4.5`），agy slug 用連字號（`claude-sonnet-4-6`）。
  ❌ 不要用 `agy models | grep -qx` 做前置白名單，會誤殺有效的顯示名格式。
- **Fallback chain**（pattern 比對，不寫死）：
  - L3：`*pro-high` → `*pro-*` → `*flash-high` → `*flash-medium` → SKIP
  - L1：`*flash-low` → `*flash-medium` → SKIP

### 錯誤處理規則

| ERR code | 處理方式 |
|---|---|
| `QUOTA` | 標記 SKIPPED 或依 fallback chain 降級 |
| `AUTH` | 提示使用者重新登入後重試 |
| `MODEL` | 換下一層 tier（注意：agy 對無效模型多半靜默改用預設，不一定觸發） |
| `TIMEOUT` | 重試一次，仍失敗則 SKIP |
| `CLI_MISSING` | 標記 SKIPPED，顯示安裝指令 |

**核心原則：絕對不可靜默跳過 CLI 呼叫，也不得由 Claude 自行替代外部 reviewer。**

可用 reviewer 門檻：2+ → 正常續行；1 → 加註警告續行；0 → 中止並請使用者修復。

---

## 使用範例

### 範例一：開發團隊 — 為 /api/login 實作速率限制

```bash
/ai-pair dev-team my-web-app
# 任務：為 /api/login 端點實作速率限制，每個 IP 每 15 分鐘最多 5 次嘗試。
```

**copilot-reviewer 發現（安全 / 邊界條件）：**
- 速率限制鍵只用 IP 位址，代理伺服器後所有使用者共享同一 IP，建議結合 IP + User-Agent 或 X-Forwarded-For
- 儲存器沒有清理過期記錄的機制
- 建議新增 `X-RateLimit-Remaining` 標頭

**claude-reviewer 發現（架構）：**
- 記憶體內儲存器在多實例下無法運作，建議 Redis 或共享儲存
- 速率限制器與路由處理器緊耦合，應抽取為中介軟體以便複用

兩者完全不重疊 — 一個發現安全邊界，一個發現架構限制。

### 範例二：內容團隊 — 審查 Newsletter 文章

```bash
/ai-pair content-team AI-Newsletter
```

**copilot-reviewer 發現（邏輯 / 準確性）：**
- 「LLMs 在工作階段之間沒有持久狀態」技術上正確但過於簡化，建議加上「預設情況下」限定詞
- 「200K tokens 上下文視窗」應說明這是 Claude 的限制

**gemini-reviewer 發現（完整性 / 受眾適配）：**
- 開頭段落在鉤子出現前用了三個專業術語，建議先帶情境
- 語氣在輕鬆與學術之間切換，目標受眾更適合輕鬆語氣

---

## 常見問題排查

### 問題：審查者沒有真正呼叫 Copilot / agy CLI

**症狀：** 審查完成但只有 Claude Code 用量在增加；Copilot / agy CLI 用量沒有變化。子代理人在角色扮演而非真正呼叫外部 CLI。

**如何驗證：** 檢查輸出是否有 `SRC:gpt-5.4-mini` / `SRC:agy/...` 標籤與 CLI 原始輸出；缺失即代表 CLI 未被呼叫。

**解決方式：**
1. 確認 reviewer agent 確實用 Bash 工具呼叫外部 CLI，未自行替代。
2. 確認 CLI 已安裝：`copilot --version`、`agy --version`。
3. 確認 CLI 已完成認證設定。

### 問題：CLI 呼叫逾時

- developer 確認 Bash 逾時設為 600000ms（10 分鐘）；reviewer 為 300000ms（5 分鐘）。
- 逾時依錯誤處理規則重試一次，仍失敗則 SKIP。

### 問題：中文路徑解析失敗

- 一律把 `TASK_FILE` / `REVIEW_FILE` 放在 `/tmp/`（ASCII-only，如 `/tmp/review-XXXXXX`）— 已內建。

### 問題：macOS `mktemp` 後綴限制

- BSD `mktemp` 不支援 X 之後的後綴，請用 `mktemp /tmp/task-XXXXXX`（不加副檔名）。

---

## 未包含的功能

開源版僅包含 **Agent Teams 模式**。完整私有版另有：

- **手動模式** — 兩個 CLI 實例透過共享檔案通訊
- **iTerm2 編排** — 帶檔案監控的自動化創作 / 審查中繼

這些需要特定本機設定，單獨維護。

---

## 專案演變

AI-Pair 從 [AI Roundtable](https://github.com/axtonliu/ai-roundtable)（Chrome 擴充功能）演變而來，把多 AI 互評概念搬到命令列並加入結構化角色分工。

| 版本 | 日期 | 重點 |
|------|------|------|
| v2.0.0 | — | 改用 GitHub Copilot CLI（GPT）取代 Codex |
| v2.3.0 | 2026-03-31 | Team Lead Planning Protocol、Copilot developer timeout 600s |
| v3.0.0 | 2026-04-29 | 三 reviewer 架構、Inter-Agent Protocol v1、分層 review、fallback chain |
| v3.1.0 | 2026-04-30 | reviewer 改接收 `REVIEW:{path}`（不讀 source files）、Review 快取 |
| v4.0.0 | 2026-05-08 | Pilot Suite 模型分配，developer/reviewer 動態 tier 選擇 |
| v4.2.0 | 2026-05-25 | Content Team 動態模型分配、Level 定義更新 |
| v4.2.5 | 2026-06-01 | Copilot Credit 適應：gpt-4.1→gpt-5.4-mini、Tier 加 Credit 成本欄、claude-haiku-4.5 加入 LOW |
| v4.3.0 | 2026-06-22 | Gemini CLI → Antigravity CLI（`agy`）遷移；角色名稱保留；`說明文件.md` 併入 README |
| v4.3.5 | 2026-06-25 | 修正 Copilot CLI 不讀 stdin（改 `-p` 嵌入）；MAI-Code-1-Flash 經 A/B 判定不採用 |
| **v5.0.0** | **2026-07-30** | **Claude 額度只花在協調決策與 review 驗證；新增 `explorer` 角色（四道護欄）；developer 預設 copilot／native 為品質升級（兩次出局護欄）；claude-reviewer 強制保留且解除讀 source 禁令；傳遞層改 manifest 路徑；模型層改執行期發現；結構化輸出與幻覺路徑機械攔阻；developer 模型 A/B 准入制（回報誠實性為淘汰項）** |

---

## 檔案結構

```
ai-pair/
├── SKILL.md          # Claude Code Skill 定義檔（核心，真正載入的來源）
├── README.md         # 完整說明文件（本檔，雙語標頭 + 繁中詳述）
├── LICENSE           # MIT
├── examples/         # 使用範例（⚠️ 不隨 live skill 安裝，僅存於完整快照）
│   ├── dev-team.md
│   └── content-team.md
└── reference/        # 技術參考
    ├── agents-prompts.md       # 各 agent 初始化 prompt
    ├── cli-invocation-ref.md   # CLI 呼叫協定細節
    └── 重構建議-v4.*.md         # 各版本重構規劃紀錄
```

---

## 貢獻 / 授權 / 作者

歡迎貢獻（低維護專案）：可重現的 bug 報告、文件改進、小型 PR。功能需求可能因維護資源有限而無法回應。

[MIT](LICENSE) — **Axton Liu**（AI Educator & Creator）

- Website: [axtonliu.ai](https://www.axtonliu.ai) ｜ YouTube: [@AxtonLiu](https://youtube.com/@AxtonLiu) ｜ X: [@axtonliu](https://x.com/axtonliu)

---

© AXTONLIU™ & AI 精英學院™ 版權所有
