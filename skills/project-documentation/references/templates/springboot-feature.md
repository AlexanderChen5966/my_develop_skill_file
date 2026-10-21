# Spring Boot 功能文件範本

此範本適用於 B2B Backend 的功能模組文件。

## 標準結構

### 1. 標題與目錄

```markdown
---
title: [功能名稱]功能文件
type: feature
created: YYYY-MM-DD
updated: YYYY-MM-DD
source-commit: <git rev-parse --short HEAD>
status: completed
related-modules: [模組名稱]
---

# [功能名稱]功能文件

## 目錄
1. [功能概述](#功能概述)
2. [API 端點](#api-端點)
3. [數據模型](#數據模型)
4. [業務邏輯](#業務邏輯)
5. [資料存取](#資料存取)
6. [權限控制](#權限控制)
```

### 2. 功能概述

```markdown
## 功能概述

[功能名稱]功能提供以下能力：
- 搜尋和查看列表
- 新增 / 編輯 / 刪除
- 批量操作
- 匯出

**Controller：** `ssgs-b2b-app/.../controllers/[Name]Controller.java`
**Service：** `ssgs-b2b-lib/.../services/[Name]Service.java`
**Repository：** `ssgs-b2b-dao/.../repositories/[Name]Repository.java`
**Entity：** `ssgs-b2b-dao/.../domain/[Name]Entity.java`
```

### 3. API 端點

```markdown
## API 端點

### 1. [操作名稱]
\`\`\`
[HTTP_METHOD] /[resource]/path
\`\`\`

**摘要：** `@Operation(summary = "...")`
**權限：** `@PreAuthorize("hasAuthority('[resource]:[action]')")`

**請求參數：**
| 參數 | 型別 | 來源 | 必填 | 說明 |
|------|------|------|------|------|
| `id` | `Long` | `@PathVariable` | ✅ | 資源 ID |
| `request` | `CreateXxxRequest` | `@RequestBody` | ✅ | 建立請求 |

**回應型別：** `Response<XxxDTO>` — `Response.java:行號`
**回應實際欄位：** `{data}`（← **從 `Response.java` 讀出的實際欄位，不可憑類別名推測**）
**鍵命名策略：** `SNAKE_CASE`（← 來源：`XxxConfig.java:行號` 的 `@Primary` ObjectMapper）

**Controller 方法：** `XxxController.methodName()` — `XxxController.java:行號`
**Service 方法：** `XxxService.methodName()` — `XxxService.java:行號`

---
```

#### 🔴 關於 JSON 範例

**預設不產出 JSON 範例。** 上表的「回應型別 + 實際欄位 + 鍵命名策略」已足夠讓下游自行組出正確形狀，
且三者都有明確來源可查核。

若確實需要 JSON 範例，**三個條件全部滿足才可寫**：

1. 鍵命名已從序列化配置確認（非依框架預設慣例推測）
2. 每個欄位都對得上 DTO 原始碼的實際欄位
3. 包裝層數已從包裝類原始碼確認（含是否有多層 `{"data": {...}}`）

任一條不滿足 → **不要寫範例**，或標 `⚠️ 推導未驗證`。

> 🔴 **這是本 skill 曾造成實際故障的位置**。原範本此處只要求寫型別名稱（`Response<XxxDTO>`），
> AI 為求文件完整**自行補上了整份 JSON 範例**，鍵命名全用框架預設的 camelCase，
> 而該專案實際是 snake_case（396 : 1）。下游前端照抄成 DTO 後 runtime 解析失敗、整頁空白。
>
> **錯的不是推導能力，是「產出了流程沒要求的東西」。** 見 SKILL.md >「核心原則」原則 1。

### 4. 數據模型

```markdown
## 數據模型

### Entity: [Name]Entity

**位置：** `ssgs-b2b-dao/.../domain/[Name]Entity.java`
**資料表：** `@Table("table_name")`

| 欄位 | 型別 | 說明 |
|------|------|------|
| `id` | `Long` | 主鍵（`@Id`） |
| `field1` | `String` | 說明 |
| `createdAt` | `LocalDateTime` | 建立時間（`@CreatedDate`） |

### DTO: [Name]DTO

**位置：** `ssgs-b2b-app/.../dto/responses/[Name]DTO.java`

| 欄位 | 型別 | 說明 |
|------|------|------|
| `id` | `Long` | 資源 ID |

### Request: Create[Name]Request

**位置：** `ssgs-b2b-lib/.../domain/requests/Create[Name]Request.java`

| 欄位 | 型別 | 驗證 | 說明 |
|------|------|------|------|
| `field1` | `String` | `@NotBlank` | 說明 |
```

### 5. 業務邏輯

```markdown
## 業務邏輯

### [Name]Service

**位置：** `ssgs-b2b-lib/.../services/[Name]Service.java`

| 方法 | 說明 | 代碼位置 |
|------|------|---------|
| `search(request)` | 搜尋列表 | 行號範圍 |
| `create(request)` | 新增 | 行號範圍 |
| `update(id, request)` | 更新 | 行號範圍 |
| `delete(id)` | 刪除 | 行號範圍 |

### 匯出服務

**位置：** `ssgs-b2b-lib/.../services/[Name]SearchExportService.java`
**繼承：** `BaseSearchExportService`

### 自訂驗證

| 驗證器 | 位置 | 驗證內容 |
|--------|------|---------|
| `@ValidXxx` | `ssgs-b2b-lib/.../constraints/ValidXxx.java` | 說明 |
```

### 6. 資料存取

```markdown
## 資料存取

### [Name]Repository

**位置：** `ssgs-b2b-dao/.../repositories/[Name]Repository.java`
**繼承：** `CrudRepository<[Name]Entity, Long>`, `CustomRepository`

| 方法 | 查詢類型 | 說明 |
|------|---------|------|
| `findByIdAndGroupIdIn()` | 方法名推導 | 依 ID 和群組查詢 |
| `customQuery()` | `@Query` (SQL) | 自訂查詢 |

### 自訂 SQL 查詢

\`\`\`sql
-- 查詢名稱：[用途說明]
SELECT ... FROM ... WHERE ...
\`\`\`
```

### 7. 權限控制

```markdown
## 權限控制

| API | 權限 | 說明 |
|-----|------|------|
| `POST /[resource]/search` | `[resource]:read` | 搜尋 |
| `POST /[resource]` | `[resource]:create` | 新增 |
| `PATCH /[resource]/{id}` | `[resource]:update` | 更新 |
| `DELETE /[resource]/{id}` | `[resource]:delete` | 刪除 |
```

### 8. 頁尾

```markdown
---

**文件版本：** 1.0
**最後更新：** YYYY-MM-DD
```

## 撰寫指引

1. **三層對照**：每個 API 都要標出 Controller → Service → Repository 的對應關係
2. **SQL 查詢要列出**：`@Query` 中的自訂 SQL 是重要的業務邏輯
3. **驗證規則要列出**：自訂的 `@Valid` 約束對理解業務規則很重要
4. **權限表格化**：一眼看出哪些角色能存取什麼
5. 🔴 **每一項都要能指出來源檔案與行號**——指不出來的改標 `⚠️ 推導未驗證` 或刪除，不要填空
6. 🔴 **不得新增本範本未列出的章節**（見 SKILL.md >「核心原則」原則 1）。
   有原始碼支持但無處可放的資訊 → 回報使用者，由其決定是否擴充範本，**不要自行加章節**
7. **enum 欄位列出完整常數值**——下游若用非容錯解析，缺一個值就會整批解析失敗
8. **手寫序列化要標明**：DTO 若有手寫 `toJson`/`fromJson` 覆寫，其 wire 形式與 annotation 脫鉤，必須註記
