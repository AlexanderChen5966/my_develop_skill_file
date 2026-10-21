---
name: doc-update
metadata:
  version: 1.1.0
description: Code review 通過後，自動將 docs/shared/ 任務文件狀態從「待實作」標記為「已完成」，並同步更新 CHANGELOG.md 與 docs/shared/readme.md 索引。觸發時機：/doc-update、code review 通過後、更新任務文件、mark as done、標記完成、功能實作完畢需要收尾文件時。只要使用者提到 code review 完成、功能上線、任務結束等情境，就應主動使用此 skill。
---

# Doc Update

Code review 通過後的文件收尾工作：將 docs/shared/ 的任務文件標記為已完成，並同步更新 CHANGELOG.md。

## 工作流程

### Step 1：確認本次變更範圍

```bash
# 查看本次變更的檔案
git diff HEAD~1 --name-only 2>/dev/null || git diff --cached --name-only
```

若使用者已明確指定任務名稱或文件，直接跳到 Step 3。

### Step 2：找到對應的任務文件

先確認 `docs/shared/` 目錄存在：

```bash
ls docs/shared/ 2>/dev/null
```

若目錄不存在，告知使用者「此專案沒有 docs/shared/ 目錄，無法更新任務文件」並停止。

列出狀態為「待實作」或「進行中」的文件：

```bash
grep -l -E "待實作|進行中" docs/shared/*.md
```

對照 Step 1 的變更檔案路徑，比對文件中提到的「目標檔案」或「影響範圍」，找出對應的任務文件。

若有多份候選文件，向使用者確認後再繼續。

### Step 3：讀取任務文件並確認狀態

閱讀找到的任務文件，**先確認狀態**：

- 若狀態已是 `**✅ 已完成**`：**立即停止**，告知使用者「該文件已標記為完成，無需更新」，不執行任何後續步驟。
- 若狀態為 `**⏳ 待實作**` 或 `**🔄 進行中**`：繼續執行，理解：
  - 原計劃的任務步驟
  - 執行步驟清單
  - 相關檔案清單

### Step 4：更新任務文件狀態

**4a. 更新 `## 狀態` 區塊**

不論原本是「⏳ 待實作」或「🔄 進行中」，統一改為（使用今天實際日期）：
```
## 狀態

**✅ 已完成**（YYYY-MM-DD）
```

**4b. 標記各任務標題**

在 `### 任務 N：` 標題末尾加上 ✅：
```
### 任務 1：新增常數 ✅
```

**4c. 標記執行步驟**

在「## 執行步驟」的每個步驟末尾加上 ✅：
```
步驟 1：修改 order_data_table.dart ✅
步驟 2：執行靜態分析 ✅
```

**4d. 更新驗收清單（如有）**

若文件中有手動驗證的核取方塊 `[ ]`，全部改為 `[x]`：
```
→ [ ] 短品項名稱：正常顯示  改為  → [x] 短品項名稱：正常顯示
```

**4e. 記錄實際與計劃的差異（僅當有差異時）**

若實際實作與計劃不同（例如改用不同 API、調整了邏輯），在文件底部的「## 相關檔案」之後追加：

```markdown
## 實際實作備註

- [說明差異，例如：「Tooltip 改用 waitDuration 參數避免閃爍」]
```

無差異時不需要加此區塊，保持文件簡潔。

### Step 5：更新 CHANGELOG.md

在 `## [Unreleased]` 下加入對應條目，依變更性質分類：

| 類別 | 適用情境 |
|------|---------|
| `Added` | 新功能、新欄位、新頁面 |
| `Changed` | UI 調整、行為變更 |
| `Fixed` | Bug 修正 |

格式：
```markdown
### Added
- [一行功能簡述，用繁體中文]
```

若 `[Unreleased]` 下已有相關項目，合併描述而非重複新增。

### Step 6：更新 docs/shared/readme.md 索引

更新任務文件在索引中的狀態標記，並確認分類正確。

索引格式：
```markdown
### AI Agent 任務佇列

| 文件 | 功能 | 狀態 |
|------|------|------|
| [order_fuel_type_ellipsis_tooltip.md](./order_fuel_type_ellipsis_tooltip.md) | 品項欄截斷 + Hover Tooltip | ✅ 已完成 |
| [invoice_status_update_task.md](./invoice_status_update_task.md) | 發票狀態更新 | ✅ 已完成 |
```

詳見 [references/readme-format.md](references/readme-format.md) 了解完整的 readme.md 目標格式。

---

## 注意事項

- **日期使用今天的實際日期**，不使用文件中的「建立日期」
- **只更新狀態為「⏳ 待實作」或「🔄 進行中」的文件**，已完成的文件不再處理
- **不修改技術內容**（程式碼範例、實作說明等），只更新狀態標記與差異備註
- **若無法確認對應哪份任務文件，先問使用者**，不要猜測