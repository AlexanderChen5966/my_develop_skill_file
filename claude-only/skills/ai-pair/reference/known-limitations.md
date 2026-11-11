---
title: Known Limitations
description: v5.0 現行成立的限制、已修正/已過期的歷史紀錄
version: 5.0.0
last_updated: 2026-07-30
---

# Known Limitations（v5.0）

## 目錄

- [現行成立](#現行成立)
- [已修正／已過期（版本沿革）](#已修正已過期保留為版本沿革)

### 現行成立

- 🔴 **`agy models > file` 會 hang**；接管線（`agy models | ...`）正常。任何取用處必須用管線。
- **agy JSON 無 `model` 欄位**——無法從輸出回推實際使用的模型。
- **agy 解析須取 `structured_output`**，`response` 欄位混入 agent 過程敘述。
- 🔴 **copilot `--output-format json` 是 JSONL 事件串流**，不是單一 JSON。需 usage 統計時才加，並以 `jq -r 'select(.type=="assistant.message") | .data.content'` 取出。
- 🔴 **兩個 CLI 的 stdout 都不保證是乾淨 JSON**：agy 失敗時會在 JSON 前多一行診斷文字；copilot `-s` 在多步驟工具呼叫時會混入過程敘述。一律抽取 JSON 物件行。
- 🔴 **不可用變數名 `status`**——zsh 的 `$status` 是唯讀保留字，`status=$(...)` 直接報 `read-only variable`。
- 🔴 **不要讓 CLI 輸出穿過 shell 變數**（`$(cat f)` → `echo`）——會因控制字元導致 `jq` parse error；一律落檔後直接 `jq file`。
- （原 E6-bis 敘述）copilot `-s` 的 stdout 不保證乾淨：單輪短任務時是純結果；多步驟工具呼叫時過程敘述會混入，JSON 在尾端 → 用 `grep -o '{"findings".*}' | tail -1` 抽取（實測 E6 修正）。
- 🔴 **agy headless 需 `--dangerously-skip-permissions`**：`--add-dir` 只給檔案讀取權，shell 工具（grep/glob）的 `command` 權限在 headless 無法提示而被自動拒絕。症狀是 `status:"SUCCESS"` 但 `response` 空、無 `structured_output`（實測 E7）。
- **copilot `--max-ai-credits` 最小值為 30**（傳更小值會被拒）。
- **兩個 CLI 命名慣例相反**（copilot 用點、agy slug 用連字號）。
- **agy 中文路徑行為未完整驗證**——TASK_FILE / MANIFEST 一律放 `/tmp/`（ASCII-only）。
- **macOS 無 `timeout` 指令**（需 `gtimeout`）；`mktemp` 不支援 X 之後的後綴。
- **Copilot 已於 2026-06-01 改 usage-based billing**，multiplier 制廢除。**費率不可寫死在本文件**，須引用官方頁面並標註查證日期。
- **Anthropic 模型獨有 cache write 成本**；ai-pair 每任務冷啟動，難以攤提。
- **成本無統一計價單位**（Claude 訂閱／Copilot Credits／agy 免費額度三池），跨池比較無法計算。
- **無整體評測機制**（benchmark／成本追蹤／品質分數）；唯一的例外是 developer 模型的 A/B 准入程序。

## 已修正／已過期（保留為版本沿革）

- ~~agy 對無效模型名稱不報錯、靜默改用預設模型，`ERR:MODEL` 偵測不可靠~~
  → **已於 agy v1.1.8 修正**。實測明確回 `status:"ERROR"` + 可用清單 + 零 token 消耗。
- ~~Copilot CLI 不讀 stdin，任務內容必須嵌入 `-p`~~
  → 限制仍在，但**解法已改為傳 manifest 路徑**（v5.0），不再嵌 payload。
- ~~`"Gemini 3.1 Pro (High)"` 這類顯示名已失效~~
  → **從未失效**。agy 同時接受 slug 與顯示名。
- `mai-code-1-flash` slug 須帶 `-picker` 後綴（仍成立，但該模型已列永不採用）。
- Gemini CLI 自 2026-06-18 起對免費帳號失效，已改用 `agy`。

---

---

## 未驗清單（v5.0 上線時）

以下路徑在 v5.0 上線時**尚未驗證**。皆為「失敗會明確報錯」或使用頻率低的類型，第一次真的用到就是測試。列出來的目的是：**用到時知道它沒被驗過**。

| 項目 | 為何未阻擋上線 |
|---|---|
| 兩次 BLOCK 出局（連續 2 輪 BLOCK → 切 native） | 編排邏輯，失敗明確；難以人工製造連續 BLOCK 情境 |
| `--conserve` 節約模式 | 行為模式，失敗明確 |
| `--dev=auto`（依任務形狀自動選引擎） | 同上 |
| content-team 全流程 | 獨立流程，不用於程式碼；prompt 已隨 v5.0 改寫但未跑過 |
| 跨模型測試（Haiku／Sonnet／Opus） | `disable-model-invocation: true` 後，description 觸發率不再是關鍵指標 |
| skill-creator eval／觸發率量測 | 同上，且需另建 `evals.json` |
| **copilot + `Conflict Handling` 指示** | native 引擎已驗證會正確回報 `CONFLICT:`；copilot 在**無**該指示時會自行擴張範圍。加了指示後的 copilot 行為未測——但若它仍擴張，`DONE` 的機械驗證會攔下（上一輪即如此），屬**明確失敗**而非靜默 |

> ⚠️ 最後一項是已知的歸因缺口：native 那輪同時換了引擎與指示兩個變數，**無法歸因是哪一個造成行為差異**。要分離需補跑「copilot + 指示」那一格。
