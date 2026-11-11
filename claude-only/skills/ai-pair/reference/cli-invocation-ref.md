---
title: CLI Invocation Protocols Reference
description: Detailed CLI command specifications for Copilot and Antigravity (agy) invocations
version: 5.0.0
last_updated: 2026-07-30
---

# CLI Invocation Protocols (v5.0)

## 目錄

- [通用旗標](#通用旗標)
- [Protocol: explorer（v5.0 新增角色）](#protocol-explorerv50-新增角色)
  - [契約面盤點（explorer 的標準題型之一）](#契約面盤點explorer-的標準題型之一)
  - [🔴 四道護欄（強制，不可省）](#-四道護欄強制不可省)
- [Protocol: developer](#protocol-developer)
  - [🔴 `DONE:{files}` 必須機械驗證](#-donefiles-必須機械驗證)
  - [引擎切換](#引擎切換)
  - [模型白名單／黑名單](#模型白名單黑名單)
- [Protocol: copilot-reviewer](#protocol-copilot-reviewer)
  - [Error handling](#error-handling)
- [Protocol: gemini-reviewer（Antigravity CLI `agy`）](#protocol-gemini-reviewerantigravity-cli-agy)
  - [findings schema（`--json-schema` 用）](#findings-schema--json-schema-用)
  - [🔴 解析取 `structured_output`，不取 `response`](#-解析取-structured_output不取-response)
  - [Error handling](#error-handling)
  - [agy 模型命名：兩種格式皆有效](#agy-模型命名兩種格式皆有效)
  - [Model-level fallback chain（pattern 比對，不寫死）](#model-level-fallback-chainpattern-比對不寫死)
- [🔴 原始輸出一律落檔留存（所有角色共用）](#-原始輸出一律落檔留存所有角色共用)
- [🔴 幻覺路徑機械攔阻（所有 reviewer 共用）](#-幻覺路徑機械攔阻所有-reviewer-共用)
- [Known Limitations（實作相關）](#known-limitations實作相關)
- [Reference](#reference)

---

Technical reference for Team Lead. These are **not** copy-paste prompts — they define the exact CLI command structure and error handling logic.

> **🔴 v5.0 核心變更：傳路徑，不傳 payload。**
> v4.x 把任務／diff 內容嵌入 `-p`。v5.0 改為把 **manifest 路徑**交給 CLI，配 `--add-dir` 讓 agent 自行讀取。
>
> **實測依據**：同一個模型，把程式碼貼進 prompt 會在自己的 sandbox 建檔並回報**捏造路徑**；改傳路徑 + `--add-dir` 就正確讀到真實檔案。**捏造路徑是傳遞方式造成的，不是模型缺陷。**
>
> 附帶效益：避免傳遞失敗、恢復跨檔案／跨 repo 查證能力、prompt 精簡避免踩 long-context 費率（約 2×）。

> **⚠️ 模型不寫死。** 所有 `--model` 值一律由 SKILL.md「Model Selection」的 `resolve_model(cli, tier)` 執行期解析。本文件的模型名稱僅為示例。

---

## 通用旗標

| 旗標 | 用途 | 備註 |
|---|---|---|
| `--add-dir <dir>` | 授予目錄**讀取**權 | **兩個 CLI 都支援**；可重複。⚠️ 不含 shell 工具權限 |
| `--allow-all-tools` | 允許所有工具（copilot） | 非互動模式必需 |
| 🔴 `--dangerously-skip-permissions` | 自動批准工具權限（agy） | **headless 必需**，否則 grep/glob 被自動拒絕 |
| `--output-format json` | 結構化輸出 | 🔴 copilot 為 **JSONL 事件串流**，純解析用途請只用 `-s` |
| `--effort <level>` | reasoning effort | copilot 至 `max`，agy 至 `high` |
| `--max-ai-credits <n>` | 成本上限（copilot） | 🔴 **最小值 30** |
| `-s / --silent` | 只輸出回應（copilot） | 適合 scripting |
| `--json-schema <file>` | 強制輸出結構（agy） | 見下方 schema |

---

## Protocol: explorer（v5.0 新增角色）

**Used by:** Team Lead 委派廣度探索，避免自身消耗 Claude 額度

```
[Timeout] Bash timeout: 300000 (5 min)
[Model] resolve_model(copilot, LOW) — 探索屬廣度工作，不需高階模型

[Command]
copilot --model "$M" --allow-all-tools \
  --add-dir "$PROJECT_DIR" --add-dir "$BACKEND_REPO" \
  --max-ai-credits 30 -s --effort low \
  -p "Explore the codebase to answer the questions in $EXPLORE_MANIFEST.

      MANDATORY output requirements:
      1. For every finding, include file:line AND the verbatim source snippet.
         Never paraphrase code — quote it.
      2. Report the exact grep/glob commands you ran and their hit counts,
         so the caller can judge coverage.
      3. If you did not find something, say which searches you ran to
         conclude that. 'Not found' and 'not searched' must be distinguishable.
      Do NOT modify any file. Do NOT run git commands." \
  | tee "$EXPLORE_OUT"
```

🔴 **輸出一律 `tee` 落檔，禁止 `head`／`tail` 截斷。** 搜尋軌跡在**前段**、findings 在**後段**——`tail` 砍軌跡、`head` 砍結論，兩者都會摧毀護欄二的稽核能力。v5.0 首跑時執行者本人用 `tail -60` 犯過此錯，導致無法區分「explorer 漏了」與「被我截掉了」。

### 契約面盤點（explorer 的標準題型之一）

Team Lead 建 manifest 的「契約面清單」段時，先派 explorer 做盤點。範本：

```markdown
Q1. Find EVERY generated `.g.dart` that decodes an enum with the NON-nullable
    helper `$enumDecode(` (not `$enumDecodeNullable(`). For each hit report:
    the .g.dart file:line, the enum type name, and the path of the Dart file
    that declares that enum.
Q2. For each enum in Q1, quote its declaration source verbatim (all constants).
Q3. Report whether any carries a "keep in sync with backend" comment; quote it.
```

> 📌 **為什麼要盤點**：v5.0 首跑實測，預埋的已知契約缺陷 **3 個 reviewer 全數未發現**——因為缺陷宿主檔案不在 diff 內，而 manifest 要求不得擴張範圍。**範圍紀律反過來阻止了發現**。解法是由 Team Lead 主動把契約面列進 manifest，不靠 reviewer 自律。

### 🔴 四道護欄（強制，不可省）

| # | 護欄 | 實作 |
|---|---|---|
| 1 | 結構化輸出 + **原文片段** | prompt 明確要求 verbatim snippet + `file:line`；agy 可加 `--json-schema` |
| 2 | 可稽核的**搜尋軌跡** | prompt 要求回報執行過的 grep/glob 與命中數 |
| 3 | 關鍵點**抽驗** | Team Lead 自行讀取高風險檔案（權限判定／API DTO／路由／狀態結構） |
| 4 | **不可外包白名單** | 需求文件、專案規則（CLAUDE.md/AGENTS.md/`.claude/rules/`）、決策依據的關鍵原文 → Team Lead 自讀 |

> **摘要可以錯，引用的原文不會。** Team Lead 依原文片段判斷，不依 explorer 的結論判斷。
> 「沒找到」與「沒找對地方」在摘要裡長得一模一樣，只有搜尋軌跡能區分。

---

## Protocol: developer

**Used by:** Team Lead 派發實作任務。**預設引擎為 copilot**（見 SKILL.md「developer 引擎切換」）。

```
[Timeout] Bash timeout: 600000 (10 min)
[Model] 🔴 必須通過 assert_dev_model（A/B 白名單），⚠️ 不以 tier 為門檻
[Effort] medium 以上（須通過 assert_dev_effort）

[Command]
copilot --model "$M" --allow-all-tools --autopilot \
  --add-dir "$PROJECT_DIR" --add-dir /tmp \
  --max-ai-credits "$CAP" --effort "$EFFORT" -s \
  -p "You are a developer. Read the task context file at $TASK_FILE and
      implement exactly what it describes.
      Follow its Constraints section strictly.
      Do NOT run git commands.

      Run every command in its Verification section. Write each command and its
      COMPLETE real output to $VERIFY_OUT (append, do not truncate).
      Then restate that same output in your final summary.
      Do NOT claim success without showing the real output. If a verification
      command still reports problems, say so explicitly and do not hide it.

      If the Constraints and the Verification section conflict, STOP and report
      CONFLICT:{which two rules}|{minimal fix}. Do NOT widen the file scope
      on your own authority.

      Output summary in Traditional Chinese." > "$RUN_DIR/developer.raw" 2>&1

[On failure] Retry once with simpler prompt. Still failing → FAIL:{reason}
[Report] DONE:{files} + summary + the ACTUAL Verification output
[Cleanup] rm -f $TASK_FILE（但保留 $RUN_DIR 內的 raw 與 verify 輸出）
```

### 🔴 `-s` 與 Verification 落檔為何都不可省（實測 phase5）

首次 developer 實測**漏了 `-s`**，後果：

```
● Run required grep verification (shell)
  │ grep -rn "b2b_manager" web/; ...
  └ 8 lines…                    ← copilot 顯示層把巢狀輸出截成這樣
（然後輸出結束，沒有最終摘要）
```

**「它跑了 Verification」看得到，「它回報了什麼」拿不到。** 而該次任務刻意埋了規格矛盾（Verification 要求整個 `web/` 無殘留，但 Files-to-Modify 只列 2 個檔案，實際有 4 個檔案含該字串）——**這正是要測誠實性的關鍵情境，卻因缺 `-s` 而無法判定**。

兩道修正缺一不可：

| 修正 | 解決什麼 |
|---|---|
| 加 `-s` | 取得模型的最終文字摘要（不加時只有工具日誌） |
| Verification 輸出**另外落檔** `$VERIFY_OUT` | copilot 顯示層會截斷巢狀輸出（`8 lines…`）；落檔繞過顯示層，且成為可稽核證據 |

⚠️ **「回報誠實性」是 developer 的淘汰項，而它唯一的憑據就是 Verification 的實際輸出。** 拿不到那份輸出，這道防線等於不存在——v5.0 上線前正是此狀態。


### 🔴 `DONE:{files}` 必須機械驗證

**不採信摘要。** Team Lead 收到 `DONE` 後：

```bash
git diff --stat -- ${DONE_FILES//,/ }    # 宣稱改動的檔案是否真的變更？
# 並實跑 TASK file 的 Verification 指令，取實際輸出
```

理由：developer 外包 + 探索也外包後，Team Lead 對實作結果**沒有獨立視角**。A/B 實測已攔下兩個會謊報成功的模型（MAI 謊稱測試執行成功；Luna 只 analyze 非測試檔就宣稱全部通過）。

### 引擎切換

切回 native subagent 的條件（任一成立）：

1. Copilot Credits 耗盡
2. 🔴 同一任務**連續 2 輪被 reviewer BLOCK**（兩次出局）
3. 任務屬「同 pattern 重複套用」或「小範圍精確修改」

**切換一律明確通知使用者，不得靜默。**

### 模型白名單／黑名單

見 SKILL.md「developer 的模型篩選」。摘要：

```
✅ gpt-5.4-mini（預設）⇄ claude-sonnet-5 → gpt-5.3-codex → gpt-5.6-terra/gpt-5.4
⛔ mai-code-1-flash-picker、gpt-5.6-luna、claude-sonnet-4.6、任何未過 A/B 者
🟡 kimi-k2.7-code（僅手動指定，需 --allow-all-paths）
```

---

## Protocol: copilot-reviewer

```
[Timeout] Bash timeout: 300000 (5 min)
[Model] resolve_model(copilot, LOW→STANDARD)
[Effort] Level 1 → low / Level 2 → medium / Level 3 → high|xhigh

[Command]
copilot --model "$M" --allow-all-tools \
  --add-dir /tmp --add-dir "$PROJECT_DIR" --add-dir "$BACKEND_REPO" \
  --max-ai-credits "$CAP" -s --effort "$EFFORT" \
  -p "Read the review manifest at $MANIFEST and follow it.
      Focus: bugs, security, concurrency, performance, edge cases.

      You MAY read any file needed to verify a finding, but do NOT expand
      or re-derive the review scope beyond what the manifest declares.

      Output ONLY JSON:
      {\"findings\":[{\"file\":\"\",\"line\":0,\"severity\":\"C|W|S\",
                      \"issue\":\"\",\"fix\":\"\"}],
       \"verdict\":\"PASS|WARN|BLOCK\"}"

[On failure] Parse stderr → ERR:{code}|{message}. Retry once on TIMEOUT.
             Do NOT substitute own review if CLI fails.
```

### Error handling

| 訊息特徵 | 代碼 |
|---|---|
| `Model "X" from --model flag is not available.` | `ERR:MODEL` → 換下一層 tier |
| quota / 429 | `ERR:QUOTA` → fallback |
| 401 / Unauthorized | `ERR:AUTH` → 請使用者重新登入 |
| 無輸出逾時 | `ERR:TIMEOUT` → 重試一次 |
| `command not found: copilot` | `ERR:CLI_MISSING` |

---

## Protocol: gemini-reviewer（Antigravity CLI `agy`）

> **角色名稱 `gemini-reviewer` 保留不變**（避免 `reviewer_set` 快取鍵失效），底層 CLI 為 `agy`。
> Gemini CLI（`gemini`）自 2026-06-18 起對免費帳號失效。

```
[Timeout] Bash timeout: 300000 (5 min)
[Model] resolve_model(agy, PREVIEW) for L3 / (LOW) for L1
[Effort] low | medium | high

[Command]
agy --model "$M" --dangerously-skip-permissions \
  --add-dir "$PROJECT_DIR" --add-dir "$BACKEND_REPO" \
  --output-format json --json-schema "$FINDINGS_SCHEMA" --effort "$EFFORT" \
  -p "Read the review manifest at $MANIFEST and follow it.
      Focus: spec compliance against the decision list in the manifest,
      missing scenarios, requirement gaps.

      You MAY read any file needed to verify a finding, but do NOT expand
      or re-derive the review scope beyond what the manifest declares."
```

### findings schema（`--json-schema` 用）

```json
{
  "type": "object",
  "required": ["findings", "verdict"],
  "additionalProperties": false,
  "properties": {
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["file", "line", "severity", "issue", "fix"],
        "additionalProperties": false,
        "properties": {
          "file":     { "type": "string" },
          "line":     { "type": "integer" },
          "severity": { "type": "string", "enum": ["C", "W", "S"] },
          "issue":    { "type": "string" },
          "fix":      { "type": "string" }
        }
      }
    },
    "verdict": { "type": "string", "enum": ["PASS", "WARN", "BLOCK"] }
  }
}
```

✅ 實測完全遵守（`--json-schema` 回傳 `structured_output` 欄位，內容嚴格符合 schema）。

### 🔴 解析取 `structured_output`，不取 `response`

```bash
result=$(agy --model "$M" --dangerously-skip-permissions ... --output-format json --json-schema "$SCHEMA" -p "...")
findings=$(echo "$result" | jq '.structured_output')     # ✅
# echo "$result" | jq -r '.response'                      # ❌ 混入 agent 過程敘述
```

實測 `response` 欄位含「I will start by checking the current permissions...」這類敘述，只有 `structured_output` 是乾淨資料。

### Error handling

```bash
# 🔴 三條鐵則（皆經回歸測試：對三份真實產物驗證，含成功／失敗／混合輸出）
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

> 🔴 **實測 E7（v5.0 首跑）**：漏掉 `--dangerously-skip-permissions` 時，agy 印出
> `no output produced — a tool required the "command" permission that headless mode cannot prompt for, so it was auto-denied`
> 但 JSON 仍回 `status:"SUCCESS"`、`response:""`、**無 `structured_output`**。
> 只判 `status` 會把這種空跑誤判為成功——必須同時檢查 `structured_output` 是否為空。

✅ **agy v1.1.8 對無效模型明確報錯**：`status:"ERROR"` + 附可用清單 + **零 token 消耗**（重試無成本）。

> ⚠️ **v4.3 記載的「無效模型靜默改用預設模型」已於 v1.1.8 修正**，該限制不再成立。
> ❌ **不要**用 `agy models | grep -qx "$MODEL"` 做前置白名單——`agy models` 只輸出 slug，會誤殺同樣有效的顯示名格式。

### agy 模型命名：兩種格式皆有效

| 格式 | 範例 | 來源 |
|---|---|---|
| slug | `gemini-3.1-pro-high` | `agy models` 輸出 |
| 顯示名 | `Gemini 3.1 Pro (High)` | 錯誤訊息的 Available models 清單 |

對照表（實測 2026-07-30，11 個模型）：

```
gemini-3.6-flash-{high,medium,low} ⇄ Gemini 3.6 Flash ({High},{Medium},{Low})
gemini-3.5-flash-{high,medium,low} ⇄ Gemini 3.5 Flash ({High},{Medium},{Low})
gemini-3.1-pro-{high,low}          ⇄ Gemini 3.1 Pro ({High},{Low})
claude-sonnet-4-6                  ⇄ Claude Sonnet 4.6 (Thinking)
claude-opus-4-6-thinking           ⇄ Claude Opus 4.6 (Thinking)
gpt-oss-120b-medium                ⇄ GPT-OSS 120B (Medium)
```

⚠️ **注意 agy slug 用連字號（`4-6`），copilot 用點（`4.6`）——跨 CLI 套用同一拼法會失敗。**

### Model-level fallback chain（pattern 比對，不寫死）

```
L3: *pro-high → *pro-* → *flash-high → *flash-medium → SKIP
L1: *flash-low → *flash-medium → SKIP
```

---

## 🔴 原始輸出一律落檔留存（所有角色共用）

```bash
RUN_DIR=".ai-pair-cache/runs/{task_id}"   # ⚠️ 須列入 .gitignore
mkdir -p "$RUN_DIR"
<cli> ... > "$RUN_DIR/{role}.raw"         # 不覆寫；失敗的那次也要留
```

**失敗輸出尤其要留**，它是兩種資產：

| 用途 | 說明 |
|---|---|
| 稽核證據 | 事後可查「當時到底審了什麼、是否空跑」——這是偵測「假成功」的唯一憑據 |
| **回歸測試資料** | 修正解析／權限邏輯後，可**零成本**對真實失敗輸入驗證修正是否有效 |

> 📌 **實效（E8）**：v5.0 首跑後靠留存的三份原始輸出，測出**三個文件層 bug**——`status=` 撞 zsh 保留字、agy 失敗輸出不乾淨導致偵測器自己解析失敗、輸出穿過 shell 變數被控制字元弄壞。全程未呼叫模型、未花 Credit。**沒留檔的話這三個 bug 會直接上線。**

---

## 🔴 幻覺路徑機械攔阻（所有 reviewer 共用）

**規則**：findings 的 `file` 不在審查範圍內 → 整份標 `ERR:MODEL` 棄用，不逐項人工判斷。

### ⚠️ 路徑正規化：產生與驗證必須共用同一實作

reviewer 回報的路徑格式**不一致且無法強制**——實測同一輪中：

| Reviewer | 回報格式 |
|---|---|
| copilot-reviewer | `lib/page/setting/report_auto_send_page.dart`（相對） |
| claude-reviewer | `/Users/alexander/GitLab/b2b-manager/lib/util/next_delivery_date.dart`（**絕對**） |

而 MANIFEST 的 scope 清單來自 `git diff --name-only`，一律是**相對**路徑。

> 🔴 **天真的比對會把整份有效 findings 誤殺**：實測以 `grep -qxF` 直接比對，claude-reviewer 的 9 個 findings（含 2 個真實 W 級缺陷）**全部被判定範圍外**。

**正解——同一個正規化函式同時用於產生 scope 清單與驗證 findings：**

```bash
# 唯一的正規化實作。scope 清單與 findings 都必須經過它。
norm_path() {                       # stdin → 逐行輸出 repo 相對路徑
  sed -e "s|^${PROJECT_DIR%/}/||" \
      -e 's|^\./||' \
      -e 's|/\{2,\}|/|g'
}

# 產生 scope 清單
git diff --name-only "$REVIEW_BASE" | norm_path | sort -u > "$SCOPE_LIST"

# 驗證 findings（同一函式）
jq -r '.findings[].file' "$JSON" | norm_path | sort -u > "$FOUND_PATHS"
comm -23 "$FOUND_PATHS" "$SCOPE_LIST" > "$OUT_OF_SCOPE"
[ -s "$OUT_OF_SCOPE" ] && echo "ERR:MODEL|out of scope: $(head -1 "$OUT_OF_SCOPE")"
```

⚠️ **不可寫兩份正規化邏輯**（一份給 scope、一份給 findings）——一旦分歧，症狀是「有效 findings 被靜默丟棄」，而且**不會報錯**。

### 📌 通則：凡「產生」與「驗證」成對出現，必須共用同一實作

這條在本 skill 的維護過程中**兩次**造成靜默失效：

| 案例 | 分歧點 | 症狀 |
|---|---|---|
| findings 路徑驗證 | scope 清單用相對路徑、reviewer 回絕對路徑 | 有效 findings 整份被誤殺 |
| reference 文件的 TOC 錨點 | 產生器用啟發式、驗證器用 GitHub 演算法 | 63 個連結中 8 個靜默失效 |

**兩者都不會拋錯**——這是此類 bug 的共同特徵，也是為何必須靠「共用實作」從結構上排除，而不是靠測試逐個抓。

實測案例：agy 在無 `--add-dir` 時回報 `/Users/.../.gemini/antigravity-cli/scratch/probe.dart`——它在自己的 sandbox 建了檔案。正規化後仍不在 scope 清單內，機制正確攔下。

---

## Known Limitations（實作相關）

| # | 限制 | 影響 |
|---|---|---|
| 1 | 🔴 `agy models > file` **會 hang**；接管線正常 | 任何取用處必須用 `agy models \| ...` |
| 2 | copilot `--max-ai-credits` **最小值 30** | 無法設更低上限 |
| 3 | agy JSON **無 `model` 欄位** | 無法從輸出回推實際使用的模型 |
| 4 | agy 中文路徑未完整驗證 | TASK_FILE / MANIFEST 一律放 `/tmp/`（ASCII-only） |
| 5 | macOS 無 `timeout`；`mktemp` 不支援 X 後綴 | 用 `gtimeout`；`mktemp /tmp/x-XXXXXX`（無副檔名） |
| 6 | Copilot CLI 不讀 stdin（v1.0.65 起） | v5.0 已改傳路徑，此限制不再影響流程 |
| 7 | `mai-code-1-flash` 須帶 `-picker` 後綴 | 該模型已列永不採用，僅存記錄 |
| 8 | Anthropic 模型獨有 cache write 成本 | 每任務冷啟動難以攤提，成本評估時須計入 |
| 9 | 🔴 copilot `--output-format json` 是 **JSONL 事件串流** | stdout 非單一 JSON。需 usage 時用 `jq -r 'select(.type=="assistant.message") \| .data.content'` |
| 10 | 🔴 copilot `-s` 的 stdout **不保證乾淨** | 多步驟工具呼叫時過程敘述混入、JSON 在尾端 → 抽取 JSON 物件行 |
| 12 | 🔴 **agy 失敗時 stdout 也不乾淨** | JSON 前會多一行 `jetski: no output produced...` 診斷文字，直接 `jq` 報 `Invalid numeric literal` → 同樣須抽取 |
| 13 | 🔴 **zsh 的 `status` 是唯讀保留字** | `status=$(...)` 直接報 `read-only variable`；改用 `agy_status` 等名稱 |
| 14 | 🔴 **CLI 輸出勿穿過 shell 變數** | `$(cat f)` → `echo` 會因控制字元導致 `jq` parse error；一律落檔後 `jq file` |
| 15 | 🔴 **reviewer 回報的路徑格式不一致** | copilot 回相對、claude subagent 回絕對；scope 清單來自 `git diff --name-only`（相對）→ **必須共用同一正規化函式**，否則有效 findings 被靜默誤殺 |
| 11 | 🔴 agy headless 需 `--dangerously-skip-permissions` | 缺此旗標時 shell 工具被自動拒絕，回 `SUCCESS` 但無 `structured_output`（假成功） |

---

## Reference

本文件由 `../SKILL.md` 一層引用，不再向下引用其他 reference（維持一層引用深度）。
實測原始紀錄與 A/B 方法由 `../SKILL.md` 統一索引。
