---
name: figma-to-requirements
metadata:
  version: 1.0.0
description: 把 Figma 設計截圖轉成「精確的 UI 任務需求草稿」，存入 docs/shared/。讀取本專案 DESIGN.md，將截圖元素對應到既有設計 token（顏色/文字/間距/元件），產出 token 對應表 + 狀態矩陣 + 待新增 token 清單，再交棒 requirements 補完功能面。通用設計（讀本專案 DESIGN.md，可跨 Flutter 專案使用）。觸發時機：截圖轉需求、Figma 轉需求、設計稿轉任務、把截圖變成需求文件、UI 需求分析、依設計稿寫需求。
---

# Figma → Requirements（UI 需求草稿）

把一組 Figma 設計截圖轉成**精確的 UI 任務需求草稿**，作為 `requirements` 的前處理階段。

## 定位與邊界（重要）

本 skill 只做**視覺 → 設計 token 對應**，產出 UI 規格草稿。明確**不做**以下兩件事：

| 不做 | 由誰做 |
|------|--------|
| ❌ 產生 Flutter / 任何程式碼 | 實作階段（agent 對著 DESIGN.md 實作）|
| ❌ 影響範圍分析 / 風險評估 / 工程任務拆解 | `requirements`（本 skill 交棒給它）|

> 核心原則：**精確度來自「本專案 DESIGN.md 的 token 詞彙」**，把截圖元素對應到真實 token，不 hardcode 顏色/尺寸/文案。

## 工作流程

### Step 1：確認專案與素材

1. **截圖在哪？** 通常是 `docs/assets/<功能名>/*.png` 一整個資料夾。
2. **判斷「本專案」＝截圖所屬 repo，而非當前工作目錄（CWD）。**
   截圖路徑可能不在 CWD 底下（例：skill 安裝在 A 專案，但素材在 B 專案）。
   ⚠️ 切勿盲目對 CWD 跑 `ls DESIGN.md`——不同專案的 token 系統可能完全不同
   （如 Web 用 screenutil、mobile 禁用；色票/字型/元件命名各異），對錯 DESIGN.md 會產出錯誤對應。
   ```bash
   # 從截圖實際路徑往上找所屬 repo 根目錄的 DESIGN.md
   SHOT_DIR="<截圖資料夾的絕對路徑>"
   D="$SHOT_DIR"; while [ "$D" != "/" ] && [ ! -f "$D/DESIGN.md" ]; do D="$(dirname "$D")"; done
   [ -f "$D/DESIGN.md" ] && echo "本專案根目錄＝$D" || echo "缺 DESIGN.md"
   ```
   - 找到 → 該 repo 根目錄即「本專案」：讀它的 `DESIGN.md`、輸出到**它的** `docs/shared/`。
   - 找不到 → 停止，提示使用者「請先在截圖所屬 repo 建立 DESIGN.md（設計系統 SoT），本 skill 依賴它對應 token」。
3. **這是一組功能流程還是單一畫面？** 多張 → 當**一組 flow** 處理（不要拆成 N 份獨立規格）。

### Step 2：載入 DESIGN.md（取得 token 詞彙）

讀 `DESIGN.md`，建立可對應的 token 清單：
- colors（語義色名 → HEX）、typography（title/body/caption…）、spacing/radius、components（既有元件/helper）、anti-patterns（反模式）
- 記住 `source_of_truth`：顏色出處（如 `color.dart` / `SLColor`）、文字（如 `SLText`）、文案（如 easy_localization / S.of(context)）

### Step 3：逐畫面視覺分析

對每張截圖（善用**檔名語意**，如「未選擇站點，洗車方案不能選擇」帶 business rule 線索）：
- **版面結構**：Column / Row / Stack / Grid / List；區塊劃分（Header / 主體 / 底部按鈕…）
- **元件清單**：按鈕、輸入框、卡片、Chip、下拉、表格、Grid item…
- **畫面間關係**：哪些畫面是同一元件的不同狀態？畫面跳轉順序？

### Step 4：Token 對應（本 skill 的靈魂）

每個視覺元素 → 對應到 DESIGN.md 的 token：
- 顏色：這個藍 → `SLColor.primary`；這個底 → `SLColor.bgLite`
- 文字：標題 → `title` 樣式；內文 → `body`
- 元件：優先對應 DESIGN.md `components` 段的既有元件/helper
- **截圖出現 DESIGN.md 沒有的顏色/樣式** → **不要硬湊**，列入「待新增 token 清單」（Step 6）

### Step 5：狀態矩陣（強制產出）

把截圖中出現的**所有狀態**列成矩陣，避免漏掉邊界態：
- 例：洗車方案 →〔未選站點：disabled〕〔已選站點：enabled〕
- 例：配件 →〔有選：顯示規格〕〔無選：顯示提示〕
- 例：預約結果 →〔成功〕〔失敗〕
- 截圖沒涵蓋但邏輯上存在的狀態（如 loading / 空清單 / 錯誤）→ 標「⚠️ 截圖未涵蓋，需確認」

### Step 6：產出 UI 規格草稿

存入 `docs/shared/<功能>_task.md`（檔名全小寫底線、≤5 詞）。
metadata header **與 requirements 完全一致**：

```markdown
**優先級：** High / Medium / Low
**建立日期：** YYYY-MM-DD
**完成日期：** —
**分支編號：** SSGS-XXXXX（若已知，否則省略此行）
**狀態：** ⏳ 待實作
**影響路徑：** `[依截圖推測的頁面/模組路徑，待 requirements 探索後確認]`
```

接著填以下 UI 段落（見下方「輸出模板」），工程段落留 stub 給 requirements。

### Step 7：交棒 requirements

草稿產出後，明確提示使用者：

> ✅ UI 規格草稿已建立於 `docs/shared/<功能>_task.md`。
> 下一步請補充功能面需求（觸發條件 / API / 業務規則 / 邊界），
> 接著執行 **requirements** 補完：影響範圍探索、風險評估、工程任務拆解。

**不要**自己做風險評估或寫程式碼——那是 requirements 與實作階段的職責。

---

## 輸出模板（UI 規格段落）

```markdown
# <功能名> UI 任務需求

**優先級：** Medium
**建立日期：** YYYY-MM-DD
**完成日期：** —
**狀態：** ⏳ 待實作
**影響路徑：** `lib/...（待 requirements 確認）`

## 背景
（截圖來源功能、共幾個畫面、整體流程一句話）
素材：`docs/assets/<功能>/`

## 畫面流程
1. 畫面 A（檔名）→ 用途 → 跳轉到 B
2. ...

## UI 規格

### 畫面 A — <名稱>
- 版面：Column [Header / 主體 / 底部按鈕]
- 元件樹：
  - AppBar（標題「...」）
  - <元件>（對應 DESIGN.md component）

#### Token 對應表
| 截圖元素 | 對應 token | 出處 |
|---------|-----------|------|
| 主按鈕底色 | `SLColor.primary` | color.dart |
| 標題文字 | `title`（20/w600）| SLText |
| 卡片底 | `SLColor.bgLite` | color.dart |

## 狀態矩陣
| 元件 | 狀態 | 視覺表現 | 來源截圖 |
|------|------|---------|---------|
| 洗車方案 | 未選站點 | disabled 灰 | 未選擇站點...png |
| 洗車方案 | 已選站點 | enabled | 洗車方案Grid.png |
| 預約結果 | 成功 / 失敗 | 兩種畫面 | 4-1 / 4-2.png |

## 待新增 token 清單
> 截圖出現但 DESIGN.md 沒有的，需先在 token 來源新增，禁止 hardcode
| 截圖顏色/樣式 | 建議 token 名 | 建議加到 |
|-------------|-------------|---------|
| #XXXXXX | `SLColor.xxx` | color.dart |

## 需確認的不確定項
- [ ] （截圖看不出的互動 / 文案 key / 邊界狀態）

---
## 〔以下交棒 requirements 補完〕
## 功能邏輯（觸發條件 / API / 業務規則）— 待補
## 影響範圍 — 待 requirements 探索
## 風險分析 — 待 requirements
## 任務清單（含 code snippet）— 待 requirements
```

---

## 與其他 skill 的分工

| Skill | 輸入 | 職責 | 產出 |
|-------|------|------|------|
| **figma-to-requirements**（本） | 截圖 + DESIGN.md | 視覺→token 對應、狀態矩陣 | UI 規格草稿 |
| `requirements` | 文字 / 本 skill 草稿 | 影響範圍、風險、任務拆解 | 完整任務文件 |
| 實作階段（agent） | 完整任務文件 + DESIGN.md | 產生程式碼 | code |

## 通用性說明

本 skill 讀「**截圖所屬 repo 根目錄的 DESIGN.md**」（見 Step 1，非當前 CWD），因此跨 Flutter 專案通用（b2b-manager / app01-double 各自的 token 不同，由各自 DESIGN.md 提供）。skill 安裝位置與素材所屬專案可以不同。
若要在其他專案使用：複製本資料夾到該專案 `.claude/skills/`，或移到 `~/.agents/skills/` 跨工具全域共用（再執行 `~/.agents/link-skills.sh`）。前提：該專案根目錄需有 DESIGN.md。

## 注意事項

- **多畫面當一組 flow**，不要產出 N 份獨立規格
- **不 hardcode**：對應不到的色/樣式一律進「待新增 token 清單」
- **狀態矩陣是強制產出**，漏狀態是 UI 需求不精確的最大來源
- **不產 code、不做風險分析**，做完交棒 requirements
- 技術術語保留英文，說明用繁體中文台灣用語

## Changelog

### v1.0.1（2026-06-23）
- Step 1 改為「本專案＝截圖所屬 repo（非 CWD）」：新增往上層找 DESIGN.md 的判斷，避免 skill 安裝位置與素材不同專案時對錯 token 系統
- 同步修正「通用性說明」敘述

### v1.0.0（2026-06-23）
- 初版：視覺→token 對應前處理 skill，產 UI 規格草稿（token 對應表 + 狀態矩陣 + 待新增 token 清單），交棒 requirements
- 通用設計（讀本專案 DESIGN.md），輸出對齊 requirements task-doc metadata header
