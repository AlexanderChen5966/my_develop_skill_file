---
title: Model Selection & developer 模型篩選
description: 執行期模型解析、兩個 CLI 的命名慣例、developer 模型准入制與已驗證清單
version: 5.0.0
last_updated: 2026-07-30
---

# Model Selection & developer 模型篩選（v5.0）

## 目錄

- [硬性下限](#硬性下限)
- [已驗證的 developer 模型（2026-07-30）](#已驗證的-developer-模型2026-07-30)
- [🔴 准入條件（淘汰制）](#-准入條件淘汰制)
- [為什麼「回報誠實性」是淘汰項](#為什麼回報誠實性是淘汰項)
- [新模型准入程序](#新模型准入程序)
- [費率參考（2026-07-30 查證）](#費率參考2026-07-30-查證)

---

## developer 的模型篩選（比 reviewer 嚴格）

developer 的錯誤會**直接進入程式碼**，且修正成本落在不可替代的 Claude 額度上。

## 🔴 developer 的門檻：A/B 准入，不是 tier

⚠️ **初稿寫「developer 禁用 LOW/FREE tier」，該規則已作廢。** 它與「developer 預設 `gpt-5.4-mini`」自相矛盾——`gpt-5.4-mini` 在既有 Tier 表屬 **LOW**，卻有**三次 A/B 勝出**（vs MAI／Luna／Kimi）加一次實作實測通過。

**根因：tier 是成本分級，不是品質分級。** 拿它當品質門檻是選錯代理指標。

**正確門檻——白名單制：**

| 判準 | developer | reviewer（對照） |
|---|---|---|
| 模型資格 | 🔴 **必須在 A/B 已驗證白名單內** | 任何可用模型皆可 |
| `--effort` 下限 | **medium 以上** | low 可接受（Level 1） |
| `--model auto` | 僅最後手段（路由結果不可預測） | 可接受 |

理由：reviewer 的錯誤會被其他 reviewer 與 Team Lead 攔下；**developer 的錯誤直接進入程式碼**，修正成本落在不可替代的 Claude 額度上。所以 developer 要的是**「這個模型實測過」**，不是「這個模型很貴」。

### 可執行的 gate（派工前必跑）

```bash
# 唯一的 developer 白名單。新增項目必須先通過「新模型准入程序」。
DEV_ALLOWED="gpt-5.4-mini claude-sonnet-5 gpt-5.3-codex gpt-5.6-terra gpt-5.4"
DEV_MANUAL_ONLY="kimi-k2.7-code"                    # 僅 --dev 明確指定時可用
DEV_BLOCKED="mai-code-1-flash-picker gpt-5.6-luna claude-sonnet-4.6"

assert_dev_model() {                                # $1=model  $2=manual|auto
  case " $DEV_BLOCKED " in *" $1 "*)
    echo "ERR:MODEL|$1 is blocked for developer (failed A/B admission)"; return 1;; esac
  case " $DEV_ALLOWED " in *" $1 "*) return 0;; esac
  if [ "$2" = "manual" ]; then
    case " $DEV_MANUAL_ONLY " in *" $1 "*) return 0;; esac
  fi
  echo "ERR:MODEL|$1 has not passed A/B admission for the developer role"; return 1
}

assert_dev_effort() {                               # $1=effort
  case "$1" in medium|high|xhigh|max) return 0;; esac
  echo "ERR:EFFORT|developer requires effort >= medium (got '$1')"; return 1
}
```

✅ **已驗證**（8/8 案例）：`gpt-5.4-mini`／`claude-sonnet-5` 通過；`gpt-5.6-luna`／`mai-code-1-flash-picker` 因黑名單被拒；`kimi-k2.7-code` 在 auto 模式被拒、manual 模式通過；未准入的 `gpt-5-mini` 被拒；`effort=low` 被拒、`medium` 通過。

⚠️ **這個 gate 必須實際執行**，不可只寫在文件裡當宣告——**「宣告但無機制」的規則不會報錯，只會靜默被違反**。本條下限在 v5.0 上線前正是此狀態（表格有規定、無任何檢查），且與預設模型互相矛盾而無人察覺。

## 已驗證的 developer 模型（2026-07-30）

```
偏好序：
  gpt-5.4-mini                     ← 預設（A/B 三度勝出：vs MAI／Luna／Kimi）
  ⇄ claude-sonnet-5                ← Claude 族系首選
  → gpt-5.3-codex                  （程式取向任務）
  → gpt-5.6-terra / gpt-5.4        （需要 400K context）
  → --model auto                   （最後手段）

⛔ 永不進入 developer：
   mai-code-1-flash-picker   （A/B 四項全敗：違反約束、空殼測試、謊報通過、成本更高）
   gpt-5.6-luna              （A/B 淘汰：測試無法編譯，卻選擇性 analyze 後宣稱通過）
   claude-sonnet-4.6         （停用；Sonnet 5 效果更好，促銷到期亦不回退）
   任何未過 A/B 的模型、任何 LOW/FREE tier 模型

🟡 kimi-k2.7-code：僅供手動指定。品質優於基準（14 測試案例全過）但成本 2.37×；
   適合高風險、需可驗證正確性的任務，不入自動偏好序。需 --allow-all-paths。
```

## 🔴 准入條件（淘汰制）

| # | 條件 |
|---|---|
| 1 | 遵守 TASK file 的 Constraints |
| 2 | 不產出空殼實作 |
| 3 | 🔴 **回報必須誠實** ← **淘汰項** |
| 4 | token／時間效率不劣化 |

## 為什麼「回報誠實性」是淘汰項

developer 外包 + 探索也外包後，**Team Lead 對實作結果沒有獨立視角**。一個會謊報成功的模型能讓錯誤直接穿透協調層。

實際攔下過兩個模型：MAI 謊稱「測試流程成功執行」；Luna 只 analyze 非測試檔就宣稱「已通過、符合全部驗收項目」（實際 42 個 analyzer error、測試無法編譯）。**兩者都是以選擇性驗證製造通過的表象。**

**對應防護（三者缺一不可）：**

1. **claude-reviewer 強制保留** — 唯一獨立驗證環節
2. **`DONE:{files}` 必須機械驗證** — 用 `git status` / `git diff --stat` 比對宣稱改動的檔案是否真的變更，**不採信摘要**
3. **Verification 段須可執行** — TASK file 的 Verification 必須是實際可跑的指令，由 Team Lead 或 reviewer **實跑**，不接受「已驗證」的文字聲明

## 新模型准入程序

- ❌ 不得因第三方評測數據亮眼而直接升為預設
- ✅ A/B：**相同 TASK file、相同 flags、只換 `--model`、隔離目錄各跑一次**（方法見 `reference/archive/phase3-luna-kimi/`）
- 🔴 **重跑必須用全新空目錄**——殘留產物會讓後續 run 變成「review 既有程式碼」而非「從零實作」，扭曲 token 與品質評分
- 🔴 **成本一律用 A/B 實測 credits，不可用 list price 推算**

> 📌 **list price 無法預測 agentic 成本。** Kimi 的 output 費率比預設便宜 11%，實際成本卻貴 137%——因為 agentic loop 的成本由 **input token** 主導。Phase 2 學到「第三方 benchmark 不可信」，Phase 3 學到「連官方 list price 也不能推算」。唯一可信的是本地 A/B。

---


---

## 費率參考（2026-07-30 查證）

⚠️ **費率會變動，本表僅為查證當時的快照。** 判定成本一律用 A/B 實測 credits，**不可用 list price 推算**——實測證明 output 費率與實際成本可差 2 倍以上（agentic loop 的成本由 input token 主導）。

官方頁面：`docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing`

| 模型 | Input | Output | 備註 |
|---|---|---|---|
| `gpt-5.4-mini` | 0.75 | 4.50 | developer 預設 |
| `claude-sonnet-5` | 2.00 | 10.00 | 促銷至 2026-08-31；到期後仍優先於 4.6（品質更好） |
| `gpt-5.3-codex` | 1.75 | 14.00 | 程式取向 |
| `gpt-5.6-terra` / `gpt-5.4` | 2.50 | 15.00 | context 400K |
| `claude-sonnet-4.6` | 3.00 | 15.00 | ⛔ 停用 |
| `gpt-5.6-luna` | 1.00 | 6.00 | ⛔ A/B 淘汰（誠實性） |
| `kimi-k2.7-code` | 0.95 | 4.00 | 🟡 僅手動指定 |
| `mai-code-1-flash-picker` | 0.75 | 4.50 | ⛔ 永不採用；與 mini 同價但多用 49% token |

📌 **Anthropic 模型獨有 cache write 成本**（Sonnet 5 為 $2.50/M）。ai-pair 每任務冷啟動，cache write 難以攤提 → 跨任務模式下 GPT 系列成本占優。

📌 **long context 費率約 2×**（Terra $2.50/$15 → $5.00/$22.50）。這是「傳 manifest 不傳 payload」的直接成本理由。
