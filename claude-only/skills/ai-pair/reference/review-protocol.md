---
title: Review Context Protocol & Inter-Agent Protocol
description: MANIFEST 四段結構（含契約面清單）、原始輸出落檔、統一解析配方、agent 間訊息格式
version: 5.0.0
last_updated: 2026-07-30
---

# Review Context Protocol & Inter-Agent Protocol（v5.0）

## 目錄

- [Review Context Protocol](#review-context-protocol)
  - [Step 0 — Cache check](#step-0--cache-check)
  - [Step 1 — 建立 review base（先做這步）](#step-1--建立-review-base先做這步)
  - [Step 2 — 建立 MANIFEST（傳路徑，不傳 payload）](#step-2--建立-manifest傳路徑不傳-payload)
  - [Step 3 — 派發](#step-3--派發)
  - [Step 4 — reviewer 的讀取範圍](#step-4--reviewer-的讀取範圍)
  - [Step 5 — 收集與驗證](#step-5--收集與驗證)
  - [Step 6 — Cache 寫入／清除](#step-6--cache-寫入清除)
- [CLI Invocation Protocols](#cli-invocation-protocols)
- [Inter-Agent Protocol v2](#inter-agent-protocol-v2)
  - [Review Report](#review-report)
  - [🔴 幻覺路徑機械攔阻](#-幻覺路徑機械攔阻)
  - [Error Report](#error-report)
  - [Task Dispatch](#task-dispatch)
- [Team Lead Translation Layer](#team-lead-translation-layer)

---

## Review Context Protocol

### Step 0 — Cache check

```bash
CACHE_DIR=.ai-pair-cache/review-findings     # ⚠️ 須列入 .gitignore
CACHE_FILE="$CACHE_DIR/{task_id}.md"
```

同 task id + 同 workspace + 同 reviewer set + 同 level + age ≤ 48h + 小幅迭代 → `HAS_CACHE=true`。

### Step 1 — 建立 review base（先做這步）

```bash
git fetch origin                            # 🔴 本地 ref 可能過期數週
git log --oneline HEAD..origin/${TARGET}    # 非空 → 警告分支落後，建議先 merge
```

> **真實事故**：本地 `main` 過期 7 週，一個已合併上游的任務在分支上被重複實作，review 卻乾淨放行，重複只在 MR 階段以合併衝突浮現。

### Step 2 — 建立 MANIFEST（傳路徑，不傳 payload）

```bash
MANIFEST=$(mktemp /tmp/manifest-XXXXXX)
# REVIEW_BASE 預設 HEAD~1（單任務）；整分支 review 用 origin/<target>...HEAD
git diff --stat --no-color "${REVIEW_BASE}" -- ${SCOPE} >> "$MANIFEST"
```

MANIFEST 內容**四段**：

1. 🔴 **裁決／決議清單**（從需求文件抽取，**不丟全文**——1400 行的文件會吃掉 context 並稀釋重點）。支援**多份**需求文件
2. **審查範圍**：檔案路徑清單 + `git diff --stat`
3. 🔴 **契約面清單**（v5.0 首跑後新增，見下）
4. **指示**：reviewer 自行讀取範圍內檔案；可讀範圍外檔案以查證 finding，但不得擴張範圍

#### 🔴 第 3 段「契約面清單」為何是必要的

v5.0 首跑實測：**預埋的已知契約缺陷，3 個 reviewer 全數未發現。**

根因是**範圍紀律與跨檔案缺陷之間的張力**——manifest 要求「不要擴張審查範圍」，而該缺陷的宿主檔案不在 diff 內（只有它的**消費端**在範圍內）。reviewer 遵守了紀律，因此沒去看它。

**結論：不能期待 reviewer 自行發現範圍外的相依契約。Team Lead 必須主動列出。**

```markdown
## 2b. 契約面清單（逐項驗證；為此可讀範圍外檔案）

- 非 nullable `$enumDecode(` 的全部位點 → 前端 enum 是否覆蓋後端全部值？
  （清單由 explorer 產出；本分支改動的 N 個 enum 另需與後端逐字比對）
  | .g.dart 位點 | enum 型別 | 宣告檔 | 後端對應 |
  |---|---|---|---|
  | group_setting_event_result.g.dart:12 | GroupUserNotificationSettingsType | ... | NotificationType.java |
  | ...（explorer 回報的全部位點） | | | |

- API DTO wire format → snake_case 欄名、`{"data":...}` 包裝出現在哪些端點
- 權限字串 → 前端 `Authorities` / `Rule` 與後端 `Role.java` 是否逐字一致
```

**產出方式**：由 explorer 先做契約面盤點（見「explorer」段的 Q 範本），Team Lead 把結果整理成表格放進 manifest。

> ⚠️ **這一段不可省略。** 沒有它，等於把「找出範圍外相依缺陷」的責任丟給 reviewer 的自律——實測證明不可靠。

### Step 3 — 派發

```bash
copilot --model "$M" --allow-all-tools \
        --add-dir /tmp --add-dir "$PROJECT_DIR" --add-dir "$BACKEND_REPO" \
        --max-ai-credits "$CAP" -s --effort "$EFFORT" \
        -p "Read the review manifest at $MANIFEST and follow it."
```

> ✅ 已實測：copilot 與 agy 加 `--add-dir` 後均能正確讀取指定路徑的檔案。

> 🔴 **copilot 的輸出格式陷阱（實測 E6）：`--output-format json` 是 JSONL 事件串流**（大量 `assistant.message_delta`），stdout **不是**單一 JSON，直接 `jq` 會失敗。
> - ✅ **建議**：只用 `-s`（不加 `--output-format`）→ stdout 直接是乾淨 JSON，可直接 `jq`
> - 若需要 token/usage 統計才加 `--output-format json`，並用
>   `jq -r 'select(.type=="assistant.message") | .data.content'` 取出內容後再 parse
> - agy 不受影響：`--output-format json` 回單一 JSON 物件，取 `.structured_output`


### Step 4 — reviewer 的讀取範圍

> Reviewers **must** work from the manifest's declared scope — read any file needed to
> verify a finding, but do not expand or re-derive the review scope.

**⚠️ v4.x 的「reviewers must NOT read source files」禁令已廢除。** 該禁令原意是省 token，實際廢掉了跨檔案／跨 repo 查證能力——而那正是 ai-pair 過去輸給 `stack-review` 的主因。

### Step 5 — 收集與驗證

#### 🔴 原始輸出一律落檔留存，包含失敗的那次

```bash
RUN_DIR=".ai-pair-cache/runs/{task_id}"    # ⚠️ 須列入 .gitignore
mkdir -p "$RUN_DIR"
<cli> ... > "$RUN_DIR/{role}.raw"          # 每個 reviewer 一份，不覆寫
```

失敗的輸出**尤其要留**——它同時是：

1. **稽核證據**：事後可查「當時到底審了什麼、有沒有空跑」
2. **回歸測試資料**：修正解析／權限問題後，可**零成本**對真實失敗輸入驗證修正是否有效

> 📌 實效：v5.0 首跑後修正解析邏輯，靠留存的三份原始輸出測出**三個文件層 bug**（zsh 保留字、agy 失敗輸出不乾淨、變數穿透壞掉），全程未呼叫任何模型、未花任何 Credit。若當時沒留檔，這三個 bug 會直接上線。

#### 解析與驗證

- 依「CLI Invocation Protocols」的統一解析配方取 findings（三條鐵則）
- 機械驗證每個 finding 的 `file` 是否在審查範圍內；不在 → 整份 `ERR:MODEL`
- 🔴 **抽驗**：對 W/C 級 finding 至少人工確認一項關鍵主張（路徑存在不等於論述成立）

### Step 6 — Cache 寫入／清除

PASS → 刪除 `CACHE_FILE`；WARN/BLOCK → 寫入正規化 findings（**不存 raw CLI log，絕不 commit**）。

Cache 清除時機：PASS 確認、task id 改變、需求轉向、檔案集擴大、review level 改變，或 Team Lead 不確定時。

---

## CLI Invocation Protocols

**Quick reference**（完整規格由 `../SKILL.md` 索引至 CLI 協定文件）：

| CLI | 必要旗標 | 結構化輸出 | 解析 |
|---|---|---|---|
| copilot | `--allow-all-tools` + `--add-dir` | `-s`（不加 `--output-format`） | 🔴 **須抽取尾端 JSON**，stdout 混有過程敘述 |
| agy | 🔴 `--dangerously-skip-permissions` + `--add-dir` | `--json-schema` + `--output-format json` | 取 `.structured_output` |

🔴 **agy 在 headless 模式必須加 `--dangerously-skip-permissions`。**
`--add-dir` 只授予**檔案讀取**權；grep／glob 等 shell 工具需要 `command` 權限，headless 無法提示 → **自動拒絕**，agy 會回 `status:"SUCCESS"` 但 `response` 為空、無 `structured_output`（實測 E7）。

🔴 **copilot 的 stdout 不保證是乾淨 JSON。** 單輪短任務時是；但配 `--allow-all-tools` 做多步驟工具呼叫時，過程敘述會混入 stdout，JSON 落在**最尾端**。必須抽取：

```bash
# 🔴 三條鐵則（皆經回歸測試，見 archive/phase-v5-cli-probe.md E8）
#   ① 一律先落檔，不讓 CLI 輸出穿過 shell 變數（會被 control char 弄壞）
#   ② 一律抽取 JSON 物件行——兩個 CLI 的 stdout 都可能夾雜非 JSON 文字
#   ③ ❌ 不可用變數名 status —— zsh 的 $status 是唯讀保留字，賦值直接報錯

# --- agy ---
agy --model "$M" --dangerously-skip-permissions --add-dir ... \
    --output-format json --json-schema "$SCHEMA" -p "..." > "$RAW"
grep -o '{"conversation_id".*}' "$RAW" | tail -1 > "$RAW.parsed"
agy_status=$(jq -r '.status // empty' "$RAW.parsed")
so=$(jq -r '.structured_output // empty' "$RAW.parsed")

if [ "$agy_status" = "ERROR" ]; then
  echo "ERR:MODEL|$(jq -r '.error' "$RAW.parsed" | head -1)"
elif [ "$agy_status" = "SUCCESS" ] && [ -z "$so" ]; then
  # 假成功：最常見原因是漏了 --dangerously-skip-permissions
  echo "ERR:MODEL|SUCCESS with no structured_output"
else
  jq '.structured_output' "$RAW.parsed"      # ✅ findings 在此
fi

# --- copilot ---
copilot --model "$M" --allow-all-tools --add-dir ... -s -p "..." > "$RAW"
grep -o '{"findings".*}' "$RAW" | tail -1 > "$RAW.parsed"
[ -s "$RAW.parsed" ] || echo "ERR:MODEL|no findings JSON in output"
```

- 🔴 **一律傳路徑，不嵌 payload**（避免捏造路徑、避免傳遞失敗、避免踩 long-context 費率）
- copilot 加 `--max-ai-credits`（**最小值 30**）作為成本上限


---

## Inter-Agent Protocol v2

> Agent-to-agent 訊息用結構化格式；只有呈現給使用者的最終輸出是人類可讀的。

### Review Report

優先用**結構化輸出**（agy `--json-schema`；copilot 以 `-s` + prompt 約束 JSON），不再靠模型自律遵守文字格式：

```json
{ "findings": [ { "file": "...", "line": 142, "severity": "C|W|S",
                  "issue": "...", "fix": "..." } ],
  "verdict": "PASS|WARN|BLOCK" }
```

⚠️ **agy 的解析必須取 `structured_output` 欄位，不可取 `response`**——後者混入 agent 的過程敘述。

文字降級格式（CLI 不支援 schema 時）：

```
SRC:{model_id}
{severity}|{file:line_or_NA}|{issue}|{fix}
VERDICT:{PASS|WARN|BLOCK}
```

### 🔴 幻覺路徑機械攔阻

**findings 的 `file` 不在審查範圍內 → 整份標 `ERR:MODEL` 棄用**，不逐項人工判斷。

> 實測證明捏造路徑主要是**傳遞方式**造成的，不是模型缺陷：同一個模型，把程式碼貼進 prompt 會在自己的 sandbox 建檔並回報假路徑；改傳路徑 + `--add-dir` 就正確讀到真實檔案。因此 manifest 設計（見下）本身就大幅降低此問題，本機制是第二道防線。

### Error Report

```
SRC:{model_id}
ERR:{code}|{raw_message}
```

Error codes: `QUOTA` | `AUTH` | `MODEL` | `TIMEOUT` | `CLI_MISSING`

### Task Dispatch

```
TASK:{file_path}          # Team Lead → developer
ACK                       # developer → Team Lead
DONE:{file1,file2,...}    # developer → Team Lead（⚠️ 須機械驗證）
FAIL:{reason}
CONFLICT:{rules}|{fix}    # developer → Team Lead（Constraints 與 Verification 衝突）
```

---


---

## Team Lead Translation Layer

```
C → ❌ CRITICAL          VERDICT:PASS  → ✅
W → ⚠️ WARNING           VERDICT:WARN  → ⚠️
S → 💡 SUGGESTION        VERDICT:BLOCK → ❌ BLOCK

ERR:QUOTA       → ⏭️ 已跳過 — {model} 額度耗盡
ERR:AUTH        → ⏭️ 已跳過 — {model} 認證失敗，請重新登入
ERR:MODEL       → ⏭️ 已跳過 — {model} 無法使用或 findings 不可採信
ERR:TIMEOUT     → ⏭️ 已跳過 — {model} 執行逾時，已重試一次
ERR:CLI_MISSING → ⏭️ 已跳過 — 對應 CLI 未安裝
```

---

