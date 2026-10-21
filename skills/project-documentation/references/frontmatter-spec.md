# 文件版本標記與命名規範

所有 `docs/` 下產出的文件都必須帶**可判斷版本的標記**（SKILL.md 原則 3），
形式二擇一、**同一專案不可混用**：

| 形式 | 何時用 |
|------|--------|
| **A. YAML frontmatter**（本文件主要規範）| 新建文件；專案沒有既有版本慣例 |
| **B. 專案自有版本／日期慣例** | 專案**已有**這套慣例 → 沿用它，見文末「形式 B」 |

🔴 **先 `ls docs/` 並打開既有文件確認用哪一種**，不要預設 A。
在已有慣例的專案硬塞 frontmatter，會造成兩套版本訊號並存而互相矛盾。

---

## 形式 A：必要欄位

```yaml
---
title: 文件標題
type: feature | bug-record | widget | project | api | change-log
created: YYYY-MM-DD
updated: YYYY-MM-DD
source-commit: <生成時 HEAD 的 commit hash（短碼即可）>
status: draft | in-progress | completed
related-modules: [模組名稱]
---
```

## 欄位說明

| 欄位 | 必填 | 說明 |
|------|------|------|
| `title` | ✅ | 文件標題（繁體中文） |
| `type` | ✅ | `feature`（功能模組）、`bug-record`（修復紀錄）、`widget`（元件文件）、`project`（專案架構）、`api`（API 總覽）、`change-log`（變更歷程） |
| `created` | ✅ | 建立日期（ISO 8601） |
| `updated` | ✅ | 最後更新日期。**每次重生成必須更新** |
| `source-commit` | ✅ | **生成時的 commit hash**（`git rev-parse --short HEAD`） |
| `status` | ✅ | 文件狀態 |
| `related-modules` | ✅ | 相關模組（陣列），如 `[car, order]` |
| `jira-id` | ❌ | 對應的 Jira/GitLab issue 編號 |

### 🔴 為什麼 `source-commit` 是必填（形式 A）

本 skill 產出的是**描述性文件**（描述「現況是什麼」），與人工維護的**規範性文件**（`AGENTS.md`、`DESIGN.md`，定義「該怎麼做」）性質不同：

| | 規範性文件 | 本 skill 的產出 |
|---|---|---|
| 來源 | 人工維護 | **從程式碼衍生** |
| 會不會失真 | ❌ 不會（它定義規則，規則即真相）| ⚠️ **會漂移**（程式碼變了、文件沒跟上）|

沒有 `source-commit`，就**無法判斷文件對應哪個版本的程式碼**，也就無法判斷該不該重生成。過期而看起來權威的文件**比沒有文件更危險**——下游沒有理由懷疑它。

`updated` 同理由選填改為必填。

---

## 🔴 內容可信度標記（必要規範）

**每一項從原始碼抽取或推導的內容，都必須可判斷其可信度。**

| 標記 | 適用內容 | 下游行為 |
|------|---------|---------|
| （不標記）＝**已驗證** | 從原始碼**確定性抽取**：端點路徑、`@PreAuthorize` 權限字串、DTO 欄位名與型別、enum 常數、包裝類結構、序列化命名策略、`@Query` SQL | 可直接採用 |
| ⚠️ **推導未驗證** | 憑框架慣例或經驗撰寫、**未從原始碼確認**的內容 | **必須翻原始碼確認後才可依賴** |

寫法：在該項目後方或區塊開頭加註。

```markdown
**回應：** `Response<CarDTO>`

⚠️ **推導未驗證**：以下 JSON 範例依框架預設慣例撰寫，未從序列化配置確認鍵命名。
```

### 為什麼採「標記不確定性」而非「要求不要猜」

AI **判斷不出自己哪裡在猜**——猜測與抽取在生成當下的主觀確信度相同。但它**可以被要求區分「我從檔案讀到的」與「我依慣例補的」**。

> 實例：某次產出的 API 文件，JSON 範例鍵命名全錯（camelCase 396 處 vs 實際 snake_case），下游照抄成前端 DTO 後 runtime 解析失敗、整頁無法顯示。**若範例旁有一行「⚠️ 推導未驗證」，就會去讀序列化配置，整條故障鏈不會發生。**

---

## 命名規則

**以專案既有慣例為準**——本 skill 不改寫既有專案的命名體系。

### 判斷順序

1. **該目錄已有同類文件** → 沿用其命名風格（不論 kebab-case、snake_case 或全大寫）
2. **該目錄為空／新建** → 用 **kebab-case**（如 `car-list-documentation.md`）
3. ❌ 禁止在同一目錄內混用兩種風格

> 📌 原規範硬性禁止 snake_case 與全大寫，與實際不符（前端 `docs/` 用 snake_case、後端根目錄用 `API_DOCUMENTATION.md`），且自身矛盾（目錄名 `page_architecture`／`bug_record` 本身就是 snake_case）。**規範脫離實際只會被忽略**，故改為配合既有慣例。

---

## 存放位置

**同樣以專案既有結構為準**，產出前先 `ls docs/` 確認實際目錄。

### 預設位置（新建專案時採用）

| 類型 | 目錄 | 範例 |
|------|------|------|
| 功能模組文件 | `docs/page_architecture/` | `car-list-documentation.md` |
| Bug 修復紀錄 | `docs/bug_record/` | `company-switch-bug-fix.md` |
| Widget 元件文件 | `docs/widget/` | `station-dropdown-chip.md` |
| 專案架構文件 | `docs/` | `project-architecture.md` |
| API 總覽文件 | `docs/` | `api-reference.md` |
| 變更歷程文件 | 專案根目錄或 `docs/` | `UPDATE_RECORD.md` |

### ⚠️ 已知的實際差異（不要「修正」它們）

| 類型 | 預設 | b2b-manager 實際 | b2b-backend 實際 |
|---|---|---|---|
| 專案架構 | `docs/project-architecture.md` | `docs/claude/claude-architecture.md` | `ARCHITECTURE.md` |
| API 總覽 | `docs/api-reference.md` | `docs/api/` | `API_DOCUMENTATION.md` |
| 變更歷程 | — | — | `UPDATE_RECORD.md` |

**產出時寫入實際路徑，不要新建一份預設路徑的重複文件。**

---

## 形式 B：專案自有版本／日期慣例

部分專案不用 YAML frontmatter，而是自己一套版本追蹤慣例。
**這是該專案的 frontmatter 等價物，沿用它、不要改造它。**

### 典型出現位置（通常不只一處）

| 位置 | 樣子 |
|------|------|
| 各文件 footer | `**文件版本**: 1.16` ＋ `**最後更新**: 2026-08-03` |
| 彙總表（常在 changelog 檔）| `\| API_DOCUMENTATION.md \| v1.16 \| 2026-08-03 \|` |
| changelog 條目表頭 | `## 🆕 v1.13 / v1.16 更新內容 (2026-08-03，commits abc1234 ~ def5678)` |

🔴 **每次更新都要把所有出現位置同步改掉**——實測某專案同時有上述三種，
漏改任一處就會出現「footer 說 v1.16、總覽表說 v1.15」的矛盾。

### 規則

1. **先窮舉所有出現位置**再動手（`grep -n '文件版本\|最後更新\|^## 🆕'`）
2. **版本號**依專案既有遞增規則；**內容實質未變時不要 bump**
   （下游用「版本號有無變」判斷是否為實質變更——亂 bump 會製造假警報）
3. **日期**填**文件實際撰寫／更新當下**的日期
   🔴 **不可誤用「最後一個 commit 的日期」**——事後補文件、分批處理多個 commit 時兩者必然不同
4. **changelog 條目若有 commit 範圍，務必維持**（見下）

### ⚠️ 形式 B 的結構性弱點

多數自有慣例只有「版本號＋日期」，**沒有 commit hash**。
結果是能回答「文件改過」，卻回答不了「**對應哪個程式碼狀態**」——
而後者才是判斷「該不該重生成」的依據。

補救：**changelog 條目的 commit 範圍是形式 B 唯一的可追溯來源**，
寫條目時務必帶上（`commits <起> ~ <迄>`）。若專案原本沒有這個習慣，
在不改造既有慣例的前提下**主動補上**——這是形式 B 唯一值得增補的欄位。

### 自檢（Step 5 對應項）

- [ ] 所有出現位置都已同步更新（不只改了 footer 忘了總覽表）
- [ ] 版本號的增減與「內容是否實質變更」一致
- [ ] 日期是撰寫當下，不是 commit 日期
- [ ] changelog 新條目帶有 commit 範圍

---

## 不屬於本 skill 的文件

以下由其他流程維護，**本 skill 不產出、不改動**：

| 路徑 | 負責 |
|------|-----|
| `docs/shared/*`（任務需求文件） | `/requirements` |
| `AGENTS.md`／`CLAUDE.md`／`.claude/rules/` | 人工維護（規範性文件） |
| `DESIGN.md` | 人工維護 |
