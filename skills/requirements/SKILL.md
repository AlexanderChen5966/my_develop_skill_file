---
name: requirements
metadata:
  version: 1.8.0
description: 將模糊需求轉換為標準化任務文件，存入 docs/shared/。先讀既有架構／API 參考文件（含上游 repo）並判斷可信度，再翻原始碼補足；自動分析影響範圍（含跨服務 enum／DTO 契約）、拆解實作任務、確認風險清單，產出可直接交給 AI agent 實作的任務文件。觸發時機：/requirements、討論作法、需求分析、寫任務文件、規劃功能、我想要新增/修改功能時。只要使用者描述想做的功能變更，就應主動使用此 skill。
---

# Requirements Analysis

將使用者的需求描述轉換為標準化任務文件，存入 `docs/shared/`。

## 工作流程

### Step 1：理解需求

先確認以下資訊（若使用者描述不夠完整，逐一詢問）：

1. **功能描述**：要做什麼？改什麼行為？
2. **目標頁面/模組**：影響哪個頁面？路由是什麼？
3. **觸發條件**：什麼情況下觸發這個行為？
4. **預期結果**：使用者操作後應該看到什麼？
5. **邊界條件**：例外情況如何處理？（空值、錯誤狀態等）

若需求已夠清楚，直接進入 Step 2a，不要不必要地多問。

#### 需求模糊時：先叫 `grilling` 追問，不要自己猜

符合任一情況，就先呼叫 Skill tool 叫 `grilling`（Claude Code 透過個人 plugin 安裝時名稱是 `core:grilling`，以可用 skill 清單上的名稱為準），把模糊處問到沒有分歧再往下走：

- 上面 5 項有 2 項以上答不出來，或使用者的回答彼此矛盾
- 有多種合理做法，選哪一種會改變影響範圍或任務拆法（例：改既有頁面 vs. 開新頁面）
- 需求只描述了結果，沒說誰、在什麼情況下觸發

規則：

- **能查的先查，不拿去問人**：後端行為、既有程式怎麼寫、API 欄位——這些走 Step 2a／2b 查證，`grilling` 只問「只有使用者能決定」的事（範圍、優先順序、取捨、例外怎麼處理）
- 追問的結論要寫進任務文件（「需求確認」或對應章節），不能只留在對話裡
- 沒有 Skill tool 的 agent（Codex、Copilot CLI 等）：讀 `~/.agents/skills/grilling/SKILL.md` 照做；讀不到就照它的精神，一輪列出所有能問的問題、每題附建議答案，等回覆再問下一輪

### Step 2a：先讀既有參考文件（讀比寫便宜）

**在翻原始碼之前，先找既有的架構／API 文件。** 讀現成文件比重新推導一次便宜得多——
但**前提是文件可信**，所以必須先做可信度判斷。

#### 找出參考文件

```bash
# ⚠️ 必須下探子目錄——參考文件常放在 docs/api/、docs/claude/ 等子目錄，`ls docs/` 看不到
find docs -maxdepth 2 -name '*.md' 2>/dev/null | grep -iE 'api|architect|arch|update|contract'
ls ARCHITECTURE.md API_DOCUMENTATION.md UPDATE_RECORD.md 2>/dev/null
```

⚠️ **同一份文件可能有多個版本並存**（如 `api_documentation_v13.md` 與 `v14.md`）。
**先看 frontmatter 的 `status`**：`superseded` 的一律跳過，只用最新且未被取代的那份。
版本無從判斷時**問使用者**，不要憑檔名數字猜——舊版可能才是對應當前後端部署的那份。

**若需求涉及後端 API，同時查上游 repo**（`project-documentation` skill 產出者）：

```bash
# 例：b2b-manager 的上游是 b2b-backend
ls ../b2b-backend/docs/ ../b2b-backend/*.md 2>/dev/null
```

#### 🔴 可信度判斷（必做，不可略過）

參考文件是**描述性文件**，會與程式碼漂移，採用前先依 [references/reference-credibility.md](references/reference-credibility.md) 的表逐項判斷。底線（沒讀細節也要守）：
- 標 `⚠️ 推導未驗證`、沒有 `source-commit` 欄位、`source-commit` 與 HEAD 差距大 → 視為未驗證，**翻原始碼確認**；`status: superseded` 直接跳過
- 🔴 **JSON 鍵命名、包裝層數、分頁欄位名預設不採信文件**，一律翻原始碼（曾發生 camelCase／snake_case 全錯、整頁空白）
- 採用文件的結論要在任務文件註明來源文件與章節

### Step 2b：探索相關程式碼

補足 Step 2a 沒涵蓋、或判定需要確認的部分：

```bash
# 找到目標頁面
ls lib/page/[模組]/

# 搜尋相關關鍵字
grep -r "關鍵字" lib/page/[模組]/ --include="*.dart" -l
```

重點理解：
- 目前實作方式（State、API、Widget 結構）
- 需要修改的具體檔案與函式
- 現有類似功能的作法（作為新實作的參考）

#### 框架／套件用法：依版本查官方文件

框架與套件（Flutter、Riverpod、GoRouter、Next.js、antd、TanStack Query 等）的用法不要憑記憶寫。**用到新用法時先讀** [references/framework-docs.md](references/framework-docs.md)。重點：先從 lock 檔讀確切版本並寫進任務文件；只查該版本的官方文件並附網址；查不到寫 `未驗證（依訓練資料）`；文件矛盾以 lock 版本實際安裝的套件為準，用編譯器實測。

**收尾時記錄下來**（寫入任務文件）：

- 哪些結論來自**參考文件**（註明文件與章節）
- 哪些結論來自**原始碼**（註明檔案與行號）
- 讀文件時發現的**文件與程式碼不符**之處 → 回報使用者，這是上游文件該修的地方

### Step 3：風險評估

依照 CLAUDE.md（其他 agent 改讀 AGENTS.md）的風險清單，逐一確認：

| 風險項目 | 是否影響 |
|---------|---------|
| OAuth2 / TaskManager | 是否涉及認證流程？ |
| API / build_runner | 是否新增或修改 API 端點？ |
| 路由配置 | 是否新增頁面或修改路由？ |
| 狀態管理結構 | 是否改動 StateNotifier？ |
| DataCell 游標規則 | 是否修改 DataCell.onTap？ |
| DataTable 排序 | 是否修改 sortColumnIndex？ |
| 欄位寬度配置 | 是否修改 fixedWidth / ColumnSize？ |
| **跨服務契約（enum）** | 是否新增／依賴後端 enum？後端之後新增值，前端會怎樣？ |
| **跨服務契約（DTO）** | 回應包裝層數、鍵命名、必填非空欄位是否已從**原始碼**確認？ |
| **權限資源** | 是否需新增 `Authorities` 值？後端 `@PreAuthorize` 的實際字串是什麼？ |
| **共用元件／全站樣式** | 是否修改共用元件（design-system、共用 widget）或全站樣式（`globals.css`、theme、design token）？列出會受影響、已經上線的頁面 |

#### 🔴 碰到風險的任務標「需 doubt-check」

上表任一項是「是」，就在 Step 6 對應的實作任務填 `**需 doubt-check：**`，寫出要複查的**決定**（一句話，例：「http client 只對 logs 的 body 保留原始 key，不影響其他頁」），不是寫風險項目名稱。沒碰到就填「否」。

為什麼不讓實作的 agent 自己判斷：doubt-check 要對付的就是過度自信，而過度自信的 agent 最不會覺得自己需要複查。2026-11-10 操作紀錄 02 實測，agent 沒有在設計時自己觸發，是做完才補審。

已經在寫任務文件時複查過的決定，在 `**需 doubt-check：**` 註明「已複查（<日期>，複查的是哪一版草稿）」；實作偏離那份草稿時要重審。

#### 🔴 跨服務契約風險為何要獨立列一項

這類風險**在前端完全沒有 diff，code review 不可能發現**——後端新增一個 enum 值、前端零改動，
就足以讓整頁解析失敗。它不是「某次改壞了」，而是**上游變動、下游沒跟**。

因此任務文件必須明確寫出：

- 依賴哪些後端 enum，以及**前端的解析方式是否容錯**
  （非 nullable 解析 → 後端新增值會讓**整批資料解析失敗、整頁空白**，不是單列異常）
- 回應包裝的**實際欄位與層數**（含 create/update 是否多一層 `{"data": {...}}`）
- 這些結論的來源（原始碼檔案行號，或已驗證的參考文件章節）

### Step 4：確認 docs/shared/ 存在

```bash
ls docs/shared/ 2>/dev/null || echo "不存在"
```

若目錄不存在，建立它：

```bash
mkdir -p docs/shared
```

並建立 `docs/shared/readme.md`（使用 [references/readme-template.md](references/readme-template.md) 的格式）。

### Step 5：檢查同名文件是否已存在

根據 Step 1-3 的分析結果決定檔名後，先檢查是否已有同名文件：

```bash
ls docs/shared/[預定檔名].md 2>/dev/null
```

**若文件已存在，讀取其狀態欄位：**

| 現有狀態 | 行為 |
|---------|------|
| ⏳ 待實作 | 直接覆寫更新，狀態維持「待實作」 |
| 🔄 進行中 | 直接覆寫更新，狀態維持「進行中」 |
| ✅ 已完成 | **⚠️ 必須先提示使用者確認**（見下方） |

**已完成文件的處理流程：**

```
偵測到 docs/shared/[檔名].md 狀態為「✅ 已完成」
    ↓
提示使用者：
  「⚠️ 此任務文件已標記為 ✅ 已完成。
   重新修改將把狀態改為 🔄 進行中。
   是否繼續？」
    ↓
使用者拒絕 → 停止，不修改任何檔案
使用者確認 → 繼續 Step 6，狀態設為「🔄 進行中」
```

**若文件不存在：** 直接進入 Step 6（新建文件）。

### Step 6：產出任務文件

使用 [references/task-doc-template.md](references/task-doc-template.md) 為模板，依照探索結果填寫所有欄位。

**狀態設定規則：**
- 新建文件 → `**⏳ 待實作**`
- 覆寫「待實作」文件 → `**⏳ 待實作**`
- 覆寫「進行中」文件 → `**🔄 進行中**`
- 重新開啟「已完成」文件（經使用者確認）→ `**🔄 進行中**`

**檔案命名規則：**
- 全小寫，以底線連接
- 描述功能，不超過 5 個詞
- 範例：`order_fuel_type_ellipsis_tooltip.md`、`invoice_status_update_task.md`

**文件頂部 metadata header 格式（必須遵守，與 sort_data_tables.md 等既有文件統一）：**

```markdown
**優先級：** High / Medium / Low
**建立日期：** YYYY-MM-DD
**完成日期：** —
**分支編號：** SSGS-XXXXX（若已知）
**狀態：** ⏳ 待實作
**影響路徑：** `[主要影響的檔案或模組路徑]`
**後端依賴：** `API_DOCUMENTATION.md §4.18`、`ReportScheduleFrequency.java`、`EntityType`（無則填「無」）
**參考文件基準：** `API_DOCUMENTATION.md @ a1b2c3d`（引用時該文件的 `source-commit`；未引用則填「—」）
```

- 狀態與 metadata 集中在頂部 header block，**不在文件底部重複**
- `**完成日期：**` 新建時填 `—`，由 `/doc-update` 填入實際日期
- `**分支編號：**` 若尚未建立分支可省略該行

#### 🔴 為什麼要有「後端依賴」與「參考文件基準」

**「後端依賴」**：後端變動時，要能反查「哪些任務文件受影響」。
沒有這個宣告，只能靠人記得，無法自動化——這是目前把上游變動接到下游任務的**唯一缺口**。

宣告粒度要能定位：**章節編號**（`§4.18`）、**類別檔名**（`ReportScheduleFrequency.java`）、
**enum 名稱**（`EntityType`）。只寫「後端報表排程 API」太粗，反查不到。

**「參考文件基準」**：記下引用時參考文件的 `source-commit`。
之後上游文件更新，才能判斷「我當初依據的版本」與「現在」之間是否有影響本任務的變更。

⚠️ 若 Step 2a 判定參考文件不可信而改讀原始碼，此欄填 `—`，並在任務文件內註明結論來自原始碼行號。

**寫作原則：**
- 實作任務要具體到「貼近可執行的程式碼」，包含修改前後的 code snippet
- **每個任務都要有「驗證：」**：寫成可以檢查的結果（哪個測試要過、哪個指令、哪個畫面操作看到什麼），不寫「確認功能正常」
- 修改範圍只到需求要求的地方（見個人層記憶〈外科式修改〉）；發現無關的問題寫進「實作注意事項」當回報，不排進任務
- 步驟要有手動驗證清單（`[ ]` checkboxes）
- 若需要 build_runner，在 metadata header 的影響路徑後補充說明

### Step 7：更新 docs/shared/readme.md

**新建文件時：** 在狀態索引表格新增一行：

```markdown
| [filename.md](./filename.md) | 功能一句話說明 | ⏳ 待實作 |
```

**重新開啟已完成文件時：** 修改既有行的狀態：

```markdown
| [filename.md](./filename.md) | 功能一句話說明 | 🔄 進行中 |
```

同時將「實作記錄」表格中對應的已完成記錄移回「任務文件狀態索引」表格。

若 readme.md 不存在，根據 [references/readme-template.md](references/readme-template.md) 建立。

### Step 8：更新 CHANGELOG.md（僅限重新開啟時）

**僅在「已完成 → 進行中」狀態變更時執行此步驟。新建文件時跳過。**

在 `[Unreleased]` 區塊的 `Changed` 分類下新增：

```markdown
### Changed
- 重新開啟任務文件 `[檔名]`：[簡述需求變更原因]
```

若 CHANGELOG.md 不存在或無 `[Unreleased]` 區塊，跳過此步驟。

---

## 後端契約同步模式（非互動・供 hook 呼叫）

prompt 明確指定「後端契約同步模式」並附漂移報告（`claude -p` headless）時，**不走 Step 1-8**，改讀並照做 [references/backend-contract-sync.md](references/backend-contract-sync.md)。
硬邊界：無人模式只能在任務文件末尾新增／更新 `## ⚠️ 後端契約變更（自動同步・待確認）` 區塊與 `_backend_sync_log.md`，其餘一律不動、不新建任務文件、不 commit、不 build；缺 `後端依賴` 宣告的文件不要猜。

## 注意事項

- **先讀參考文件、再翻原始碼**（Step 2a → 2b）。讀比寫便宜，但**前提是文件可信**——
  參考文件是描述性文件，會與程式碼漂移，必須先做可信度判斷
- **先探索再寫文件**，不要根據假設寫任務，確認過目前程式碼後才描述修改方式
- **每個技術結論都要能指出來源**（原始碼行號，或已驗證的參考文件章節）。
  指不出來源的結論寫「未確認」，**不要憑框架慣例填空**
- **JSON 鍵命名、包裝層數、分頁欄位名預設不採信文件**，除非該處明確標示已從序列化配置確認
- **任務文件要夠具體**，讓另一個 AI agent 讀完後不需要再問問題就能實作
- **不要過度設計**，只描述必要的最小變更
- **技術術語保留英文**（Flutter、Riverpod、DataCell 等），說明文字用繁體中文

## 常見藉口

想跳過某一步時，先對照這張表：

| 藉口 | 為什麼不成立 |
|------|-------------|
| 「API 文件寫得很清楚，不用翻原始碼」 | 曾發生：後端 API 文件的 JSON 鍵全寫 camelCase，實際是 snake_case，前端照抄後整頁空白。文件語氣再肯定也一樣 |
| 「需求大概懂了，先寫再說」 | 猜錯的需求，後面實作、review 全部白做。只有使用者能決定的事，用 `grilling` 問 |
| 「這是使用者沒講清楚，我挑一個合理的就好」 | 會改變影響範圍或任務拆法的選擇，就是要問的事；不影響的才自己決定，並寫進任務文件 |
| 「這個框架 API 我很熟」 | 熟的是訓練資料裡的版本。先看 lock 檔版本、查官方文件；查不到就標未驗證 |
| 「上游文件應該是最新的」 | 先看 `source-commit` 跟 HEAD 差多少；沒有這個欄位就全部視為未驗證 |
| 「順便把旁邊的問題也排進任務」 | 範圍外的問題只回報，另開任務；任務文件只放需求要求的修改 |
| 「驗證就寫『確認功能正常』」 | 沒辦法檢查的驗證等於沒寫。寫出哪個測試、哪個指令、哪個畫面操作看到什麼 |

## 與其他 skill 的關係

| skill | 關係 |
|-------|------|
| `project-documentation` | **上游**。產出本 skill Step 2a 讀取的架構／API／變更歷程文件（含上游 repo 的）。⚠️ 其產出為**描述性**文件，須依 Step 2a 判斷可信度後才可採用 |
| `figma-to-requirements` | **上游**（UI 需求）。產出 UI 任務草稿後交棒本 skill |
| `grilling` | **Step 1 內呼叫**。需求模糊時追問使用者，只問查不到、只有人能決定的事 |
| `/stack-review`、`/ai-pair dev` | **下游**。實作完成後的品質保證 |
| `doubt-check` | **下游（開發中途）**。Step 3 標了「需 doubt-check」的任務，實作到那個決定、寫程式之前用它做對抗式複查 |
| `/doc-update` | **下游**。填入完成日期、更新 readme 狀態 |

> ⚠️ **`docs/shared/` 由本 skill 專屬維護**，`project-documentation` 不產出、不改動此目錄。
