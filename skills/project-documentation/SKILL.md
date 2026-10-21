---
name: project-documentation
description: >-
  自動化產出專案技術文件，支援多種技術棧。
  完整支援 Flutter (Riverpod/Bloc) 和 Spring Boot (Spring Data JDBC)。
  提供六種文件類型：(1) 專案架構文件；(2) 功能模組文件；(3) API 總覽文件；
  (4) Bug 修復紀錄；(5) Widget 元件文件；(6) 變更歷程文件。
  觸發關鍵字："產出文件"、"記錄功能"、"建立架構文件"、"整理 API"、
  "bug 紀錄"、"修復紀錄"、"widget 文件"、"元件文件"、"變更歷程"、"更新文件"。
metadata:
  version: 2.2.1
  last-updated: 2026-08-03
---

# Project Documentation

自動化產出專案技術文件，支援多種技術棧的可擴展文件系統。

---

## 🔴 核心原則（優先於本文件其餘所有內容）

本 skill 產出的是**描述性文件**——描述「現況是什麼」，而非「該怎麼做」。描述會與程式碼**漂移**，
且過期而看起來權威的文件**比沒有文件更危險**：下游（`/requirements`、其他 repo 的開發者）
沒有理由懷疑它。以下三條原則就是為此而設。

### 原則 1：不得產出流程未要求的內容

**只產出本 skill 流程明確列出、且有原始碼依據的內容。**

- ❌ 不得自行補充流程未要求的章節、範例、JSON payload、預設值說明
- ❌ 不得為了「文件看起來完整」而填入未經確認的內容
- ✅ 流程要求某項但原始碼找不到依據 → **寫「未找到／未確認」**，不要填空

> 🔴 **這條是最高優先的約束**。曾發生的實際故障中，錯誤的 JSON 範例**根本不在流程要求範圍內**
> ——範本只要求寫回應的**型別名稱**（`Response<XxxDTO>`），AI 為求完整自行補上了整份 JSON 範例，
> 且鍵命名全錯（camelCase 396 處 vs 實際 snake_case）。下游照抄成前端 DTO 後 runtime 解析失敗。
>
> **補齊推導步驟不足以解決問題**——只要「自行發揮」沒被禁止，AI 就會在其他未被規範處重演同一件事。

### 原則 2：標記可信度

每一項內容都必須可判斷可信度：**確定性抽取的不標記；憑慣例推導的一律標 `⚠️ 推導未驗證`**。

詳細規範見 [frontmatter-spec.md](references/frontmatter-spec.md) >「內容可信度標記」。

理由：AI 判斷不出自己哪裡在猜（猜測與抽取在生成當下的主觀確信度相同），
但**可以被要求區分「我從檔案讀到的」與「我依慣例補的」**。

### 原則 3：文件必須帶「可判斷版本的標記」

**每份文件都要能回答：這份描述對應哪個時間點的程式碼？**
沒有這個訊號，就無法判斷該不該重生成，文件會靜默過期。

**兩種實作形式，依專案既有慣例擇一**（⚠️ 不要在同一專案混用）：

| 形式 | 內容 | 適用 |
|------|------|------|
| **A. YAML frontmatter**（預設）| `source-commit`（`git rev-parse --short HEAD`）＋ `updated` | 新建文件、專案無既有慣例時 |
| **B. 專案自有版本／日期慣例** | 版本號 ＋ 最後更新日期，散佈在文件 footer／版本總覽表／changelog 表頭 | 專案**已有**這套慣例時——**沿用它，不要另外硬塞 frontmatter** |

```bash
git rev-parse --short HEAD    # 形式 A 產出前先取得
```

⚠️ **形式 B 的已知弱點**：多數自有慣例只有「版本號＋日期」，**沒有 commit hash**，
所以能回答「文件改過」卻回答不了「對應哪個程式碼狀態」。
若該專案的 changelog 條目有記 commit 範圍（如 `commits abc1234 ~ def5678`），
**務必維持**——那是形式 B 唯一的可追溯來源。

形式 B 的完整規則見 Step 0 >「專案自有版本／日期慣例」與
[frontmatter-spec.md](references/frontmatter-spec.md) >「形式 B」。

## 支援狀態

| 技術棧 | 狀態 | 檢測方式 |
|-------|-----|---------|
| **Flutter (Riverpod/Bloc)** | ✅ 完整支援 | `pubspec.yaml` |
| **Spring Boot (Data JDBC)** | ✅ 完整支援 | `pom.xml` + `@SpringBootApplication` |
| **Android** | 🔧 框架就緒 | `app/build.gradle` |

✅ = 完整支援 | 🔧 = 框架就緒（待擴展）

## 文件規範

所有產出的文件必須遵守統一規範，詳見 [frontmatter-spec.md](references/frontmatter-spec.md)：

- **版本標記**（原則 3，二擇一）：**形式 A** YAML frontmatter——必填 `title`、`type`、`created`、`updated`、**`source-commit`**、`status`、`related-modules`；**形式 B** 沿用專案自有的版本號／日期慣例（見 Step 0）
- **可信度標記**：推導而未從原始碼確認的內容一律標 `⚠️ 推導未驗證`
- **命名規則**：**以專案既有慣例為準**；目錄為空／新建時才用 kebab-case
- **存放位置**：產出前先 `ls docs/` 確認實際目錄，不要新建重複文件
- **語言**：繁體中文（zh-TW），技術術語保留英文

## 六種文件類型

### 1. 專案架構文件
**產出**: `docs/project-architecture.md`（**先確認專案實際路徑**，如 `ARCHITECTURE.md`）
**內容**: 技術棧、架構模式、目錄結構、環境配置、開發工作流程
**觸發**: "project"、"專案架構"

### 2. 功能模組文件
**產出**: `docs/page_architecture/[模組]-documentation.md`
**內容**: API 端點、數據模型、狀態管理/業務邏輯、UI 組件/Controller、權限控制
**觸發**: "feature"、特定模組名稱

### 3. API 總覽文件
**產出**: `docs/api-reference.md`（**先確認專案實際路徑**，如 `API_DOCUMENTATION.md`）
**內容**: 所有 REST API endpoints（分組、HTTP方法、Request/Response）＋ **wire 契約**（見下）
**觸發**: "api"、"API 清單"

> 🔴 **本類型是跨 repo 消費者（前端 `/requirements`）最主要的依據**，錯誤代價最高。
> **必須包含「wire 契約」章節**（序列化命名策略、包裝類實際欄位、錯誤格式、enum 值），
> 且全部從原始碼抽取——見下方各技術棧的「API 總覽文件」流程。

### 4. Bug 修復紀錄
**產出**: `docs/bug_record/[問題名稱].md`
**內容**: 問題描述、錯誤現象、根因分析、修復方式、驗證方式
**觸發**: "bug"、"修復紀錄"、"bug record"
**範本**: [templates/bug-record.md](references/templates/bug-record.md)

### 5. Widget 元件文件
**產出**: `docs/widget/[元件名稱].md`
**內容**: 元件概述、使用方式、參數表格、狀態管理、使用位置、注意事項
**觸發**: "widget"、"元件文件"、"component"
**範本**: [templates/widget-doc.md](references/templates/widget-doc.md)

### 6. 變更歷程文件

**產出**: `UPDATE_RECORD.md`（專案根目錄或 `docs/`，依既有慣例）
**內容**: 依時間倒序的變更條目，每條含 **commit hash**、日期、影響章節、⚠️ 行為變更標記
**觸發**: "變更歷程"、"更新紀錄"、"update record"

**步驟**:
1. `git log --oneline` 取得自文件 `source-commit` 之後的 commit
2. 逐條判斷是否影響已產出的文件（API 契約／架構／權限）
3. **行為變更**（非新增而是改動既有行為）必須標 `⚠️`——下游最需要知道的就是這種
4. 標註影響到的文件章節編號，讓下游能直接定位
5. 更新 frontmatter 的 `updated` 與 `source-commit`

> 🔴 **這是跨 repo 協作效用最高的一份文件**。下游 repo 判斷「上游改了什麼、我要不要跟」時，
> 逐一 diff 原始碼成本過高，此文件是唯一可靠且低成本的來源。
> 因此 commit hash、`⚠️` 行為變更標記、章節編號**三者缺一不可**。

## 工作流程

### Step 0: 判斷「新建」或「更新」（必做）

```bash
ls docs/                              # 確認實際目錄結構與命名慣例
git rev-parse --short HEAD            # 取得 source-commit
```

找出目標文件是否已存在：

| 情況 | 動作 |
|------|------|
| **不存在** | 走新建流程（Step 1 起） |
| **存在，且 `source-commit` == 目前 HEAD** | ⏹ **停止**，回報「文件已是最新，無需重生成」 |
| **存在，`source-commit` 較舊** | 走**更新流程**（見下），❌ **不可直接覆蓋** |
| **存在但無 `source-commit`**（舊版產出） | 視為不可信基線：重新產出，但**先列出將被移除的內容給使用者確認** |

#### ⚠️ 先判斷這個專案用哪種版本標記形式

```bash
grep -rn '^source-commit:' docs/ | head            # 形式 A 的訊號
grep -rn '文件版本\|最後更新\|^## 🆕' docs/ | head   # 形式 B 的訊號
```

| 命中 | 用哪種 |
|------|--------|
| 有 `source-commit:` | **形式 A**（YAML frontmatter）|
| 有「文件版本／最後更新／`## 🆕`」但無 frontmatter | **形式 B**（專案自有慣例）——**沿用它，不要另外硬塞 frontmatter** |
| 都沒有 | 新建文件 → 用**形式 A** |

🔴 **不可在同一專案混用**，否則會出現兩套版本訊號互相矛盾。

完整規則見 [frontmatter-spec.md](references/frontmatter-spec.md)（形式 A ／ 形式 B 各一節）。
⚠️ 形式 B 的關鍵易錯點：**出現位置通常不只一處**（footer／彙總表／changelog 表頭），
漏改任一處就會自相矛盾。

#### 🔴 更新流程（不可直接覆蓋）

既有文件可能含**人工修正過的內容**——那些往往正是修掉 AI 猜錯之處，直接覆蓋會把正確資訊換回錯的。

1. `git log --oneline <source-commit>..HEAD` 取得期間變更
2. 判斷哪些**章節**受影響，**只重生成受影響章節**
3. 未受影響的章節**原封不動保留**
4. 遇到「既有內容與重新抽取結果不符」→ ⏹ **停止並回報差異**，由使用者裁決
   （可能是程式碼改了，也可能是人工修正過而抽取又錯了一次）
5. 更新 frontmatter 的 `updated` 與 `source-commit`

### Step 1: 檢測專案類型

```bash
# Flutter
ls pubspec.yaml
grep "flutter_riverpod\|flutter_bloc" pubspec.yaml

# Spring Boot
ls pom.xml
grep "@SpringBootApplication" -r src/ ssgs-b2b-app/src/ 2>/dev/null

# Android (TODO)
ls app/build.gradle
```

### Step 2: 載入上下文與範本

- **Flutter**: [stack-context/flutter.md](references/stack-context/flutter.md) + [templates/flutter-feature.md](references/templates/flutter-feature.md)
- **Spring Boot**: [stack-context/springboot.md](references/stack-context/springboot.md) + [templates/springboot-feature.md](references/templates/springboot-feature.md)
- **Android**: [stack-context/android.md](references/stack-context/android.md) 🔧
- **通用**（bug/widget/變更歷程）: [templates/bug-record.md](references/templates/bug-record.md) / [templates/widget-doc.md](references/templates/widget-doc.md) / [templates/change-log.md](references/templates/change-log.md)

### Step 3: 載入文件規範

讀取 [frontmatter-spec.md](references/frontmatter-spec.md) 確保產出符合統一規範。

### Step 4: 執行文件產出

依技術棧和文件類型執行對應流程（見下方）。

**規模控制**：單一文件超過 **1500 行**時分檔，並保留一份索引文件。
API 總覽依 Controller／資源分檔（如 `api/car.md`、`api/order.md` + `api-reference.md` 索引）。
超大單檔對下游是負擔——`/requirements` 只需要其中一小段，卻得整份載入。

### Step 5: 產出自檢（必做，不可略過）

產出後**逐條檢查**，任一項不通過就修正後重檢：

- [ ] **每一項「已驗證」內容都能指出來源檔案與行號**——指不出來的改標 `⚠️ 推導未驗證` 或刪除
- [ ] **沒有流程未要求的章節／範例／JSON payload**（原則 1）
- [ ] **所有 JSON 範例的鍵命名都經序列化配置確認**——未確認就標記或刪除
- [ ] **版本標記**（依 Step 0 判定的形式）：
      **形式 A** → frontmatter 七個欄位齊全、`source-commit` 為實際 HEAD；
      **形式 B** → 所有出現位置（footer／彙總表／changelog 表頭）都已同步、版本號的增減與「內容是否實質變更」一致、日期是**撰寫當下**而非 commit 日期、新 changelog 條目帶 commit 範圍
- [ ] 檔名與存放位置符合該專案**既有慣例**（非 skill 預設）
- [ ] 未改動 `docs/shared/*`、`AGENTS.md`、`CLAUDE.md`、`DESIGN.md`
- [ ] 更新流程：未受影響章節確實原封不動

最後向使用者回報：**已驗證項數 / 標記為推導未驗證的項數 / 找不到依據而留空的項目**。

> ⚠️ 不要回報「文件已完成」而不附上這三個數字。下游需要知道這份文件有多少比例是可信的。

## Flutter 文件產出（完整支援）

### 專案架構文件

1. 讀取 [stack-context/flutter.md](references/stack-context/flutter.md) 和 `CLAUDE.md`（其他 agent 改讀 `AGENTS.md`）
2. 探索關鍵檔案：
   - `lib/api/connector/task_manager.dart`
   - `lib/page/page_route.dart`
   - `lib/api/connector/auth_service.dart`
3. 產出專案架構文件（**確認實際路徑**，如 `docs/claude/claude-architecture.md`）
4. 執行 Step 5 自檢

### 功能模組文件

**輸入**: 模組名稱（order、driver、car等）

**步驟**:
1. 定位主頁面：`lib/page/[模組]/[模組]_page.dart`
2. 提取 API：從 `rest_client.dart` Grep `@(GET|POST|PATCH|DELETE)\(.*/[模組]`
3. 分析狀態：讀取 `lib/api/notifier/[模組]/[模組]_state_notifier.dart`
4. 提取模型：搜索 `lib/api/request/[模組]/` 和 `lib/api/response/[模組]/`
5. 列舉組件：探索 `lib/page/[模組]/widgets/`
6. 搜索權限：Grep `Authorities.[Resource]`
7. **確認該模組 DTO 的 wire 形式**：依「API 總覽文件 > 階段 B」的 B1／B2／B3 逐項確認
   （命名策略、手寫 `toJson` 覆寫、enum 解析容錯性）。⚠️ 即使只產出單一模組文件，階段 B 仍必做
8. 使用範本：[templates/flutter-feature.md](references/templates/flutter-feature.md)
9. 產出：`docs/page_architecture/[模組]-documentation.md`（確認實際目錄與命名慣例）
10. 執行 Step 5 自檢

### API 總覽文件

#### 階段 A：端點清單

1. 讀取 `lib/api/restclient/rest_client.dart`
2. Grep `@(GET|POST|PUT|PATCH|DELETE)` 提取所有端點
3. 解析方法簽名（參數、回傳類型、行號）
4. 依路徑前綴分組

#### 🔴 階段 B：wire 契約（**必做**）

同樣**不可依 `json_serializable` 預設慣例填空**——本專案的實際配置才算。

```bash
# 全域 fieldRename 配置
cat build.yaml 2>/dev/null | grep -A5 "json_serializable"
grep -rn "fieldRename" lib/ build.yaml
# 逐欄覆寫
grep -rn "@JsonKey" lib/api/
# enum wire 值
grep -rn "@JsonValue\|@JsonEnum" lib/models/enums/
```

**B1. 命名策略**：`build.yaml` 的全域 `field_rename` 與各類別 `@JsonSerializable(fieldRename:)`
何者生效、有無 `@JsonKey(name:)` 逐欄覆寫。

**B2. ⚠️ 手寫 `toJson()` / `fromJson()` 覆寫**——最容易被漏掉的一類

```bash
grep -rn "Map<String, dynamic> toJson()" lib/api/request/ lib/api/response/
```

有些 DTO **手寫覆寫**而非使用產生的版本（例如需精確控制送出哪些欄位）。
這類 DTO 的 wire 形式**與 annotation 完全脫鉤**，只讀 annotation 會得到錯的結論。
文件必須標明「此 DTO 為手寫序列化」並列出實際輸出欄位。

**B3. enum 解析的容錯性**——關係到穩定性而非只是格式

```bash
grep -rn '\$enumDecode(' lib/api/         # 非 nullable：未知值直接拋錯
grep -rn '\$enumDecodeNullable(' lib/api/ # nullable：未知值回傳 null
grep -rn "unknownEnumValue" lib/api/      # 有 fallback
```

**逐 enum 標註採用哪一種**。用非 nullable `$enumDecode` 者，
後端新增一個值就會讓**整批資料解析失敗、整頁無法顯示**——這是必須寫進文件的風險資訊。
⚠️ 同一 enum 可能在不同 DTO 採用不同解析方式，需逐處確認，不可只看一處就下結論。

#### 階段 C：產出

5. 產出 API 總覽文件（確認實際路徑），wire 契約章節置於端點清單之前
6. 執行 Step 5 自檢

## Spring Boot 文件產出（完整支援）

### 專案架構文件

1. 讀取 [stack-context/springboot.md](references/stack-context/springboot.md)
2. 分析 `pom.xml` 依賴和模組結構
3. 搜索 `@Configuration`、`@Bean` 配置類別
4. 分析 `SecurityConfig.java` 安全配置
5. 產出專案架構文件（**確認實際路徑**，如 `ARCHITECTURE.md`）
6. 執行 Step 5 自檢

### 功能模組文件

**輸入**: 模組名稱（car、order、driver、invoice 等）

**步驟**:
1. 定位 Controller：Grep `@RestController` + `@RequestMapping("/[模組]")` in `ssgs-b2b-app/.../controllers/`
2. 提取 API：Grep `@(Get|Post|Patch|Put|Delete)Mapping` 提取所有端點
3. 提取權限：Grep `@PreAuthorize` 取得權限要求
4. 提取 Swagger 標註：`@Operation(summary = "...")` 取得 API 摘要
5. 定位 Entity：讀取 `ssgs-b2b-dao/.../domain/[Name]Entity.java`
6. 定位 Repository：讀取 `ssgs-b2b-dao/.../repositories/[Name]Repository.java`
7. 提取自訂 SQL：Grep `@Query` 取得自訂查詢
8. 定位 Service：搜索 `ssgs-b2b-lib/.../services/` 相關服務
9. 定位 DTO：搜索 `ssgs-b2b-app/.../dto/` 和 `ssgs-b2b-lib/.../domain/requests/`
10. 提取驗證：Grep `@Valid` 相關自訂約束
11. **確認該模組 DTO 的 wire 形式**：依「API 總覽文件 > 階段 B」的 B1／B2／B4／B5 逐項確認
    （命名策略、包裝層數、enum 值、`@JsonProperty` 等逐欄例外）。
    ⚠️ 若本次僅產出單一模組文件而未產出 API 總覽，**階段 B 仍必做**——不可假設命名策略
12. 使用範本：[templates/springboot-feature.md](references/templates/springboot-feature.md)
13. 產出：`docs/page_architecture/[模組]-documentation.md`（確認實際目錄與命名慣例）
14. 執行 Step 5 自檢

### API 總覽文件

#### 階段 A：端點清單（annotation 抽取）

1. 搜索所有 Controller：`find ssgs-b2b-app -name "*Controller.java"`
2. Grep `@(Get|Post|Patch|Put|Delete)Mapping` 提取所有端點
3. 提取 `@RequestMapping` 前綴
4. 提取 `@Operation(summary = "...")` 摘要
5. 提取 `@PreAuthorize` 權限
6. 依 Controller（`@Tag`）分組

#### 🔴 階段 B：wire 契約（**必做，不可略過**）

階段 A 只得到「有哪些端點」，**得不到「JSON 長什麼樣」**。以下四項全部從原始碼抽取；
**任一項找不到就明確寫「未確認」，絕不可依框架預設慣例填空**（原則 1）。

**B1. 序列化命名策略**——決定所有 JSON 鍵的大小寫形式，錯了整份文件全錯

```bash
# ⚠️ --include 的 glob 必須加引號，否則 zsh 會嘗試展開並報 "no matches found"
# ⚠️ Maven 專案一律排除 target/（build 產物會造成重複與誤判）
# 全域配置
grep -rn "property-naming-strategy\|propertyNamingStrategy" \
  --include='*.yml' --include='*.yaml' --include='*.properties' . | grep -v target
# 程式化配置的 ObjectMapper bean
grep -rn "PropertyNamingStrategies\|PropertyNamingStrategy" --include='*.java' . | grep -v target
grep -rn "ObjectMapper" --include='*.java' . | grep -v target | grep -i "@Bean\|@Primary"
# 類別層級覆寫
grep -rn "@JsonNaming" --include='*.java' . | grep -v target
```

⚠️ **`@Primary` 必須從檔案內容確認，不可只看 grep 命中行**——`@Primary` 通常獨立一行，
與 `setPropertyNamingStrategy(...)` 不在同一行，grep 抓不到兩者的對應關係。**必須 Read 該 config 類別。**

⚠️ **順帶確認 `FAIL_ON_UNKNOWN_PROPERTIES`**：若 `@Primary` mapper **未** disable 它，
則請求送出後端不存在的欄位會回 400。這是下游組請求時必須知道的資訊。

⚠️ **可能存在多個 ObjectMapper，策略各不相同**。務必確認：
- 哪一個標 `@Primary`（Spring MVC 預設用它序列化 REST 回應）
- 其餘 ObjectMapper 各自服務哪些對外介接（可能是 `LOWER_CAMEL_CASE`）
- **文件必須逐一列出「哪些 API 用哪個策略」**，不可只寫一個結論

> 📌 實例：某後端有 **3 個** ObjectMapper——`@Primary` 的是 `SNAKE_CASE`，
> 另兩個對外介接是 `LOWER_CAMEL_CASE`。只看其中一個就會讓整份文件的鍵命名全錯。

**B2. 回應包裝類的實際欄位**——逐一 Read，不可憑類別名推測

```bash
find . \( -name "Response.java" -o -name "SearchResult.java" -o -name "*PageResult*.java" \) | grep -v target
```

⚠️ **同時確認包裝是否套用**：Read Controller 的方法簽名，看回傳型別是
`SearchResult<T>`（**直接回傳、無外層**）還是 `Response<SearchResult<T>>`（多一層 `data`）。
**同一專案的不同端點可能不一致**——例如搜尋端點直接回 `SearchResult<T>`，
而 create/update 回 `Response<T>`。只看包裝類原始碼得不到這個資訊。

對每個包裝類**逐一 Read 並列出實際欄位名**。分頁包裝類特別容易猜錯
（`page`/`pages`/`total` vs `currentPage`/`totalPages`/`totalElements` 是完全不同的命名體系）。

> 📌 實例：文件把分頁包裝寫成 `{results, totalElements, totalPages, currentPage, pageSize}`，
> 實際是 `{data, page, pages, total}`——**五個欄名全錯**。且該錯誤寫在「通用資料模型」章節，
> 再被複製到每個分頁端點，**一個錯誤模板擴散全文**。

⚠️ 也要確認**是否有多層包裝**（如 create 回應多一層 `{"data": {...}}`）——
少一層就會讓下游的必填非空欄位收到 null 而拋錯。

**B3. 錯誤回應格式**

```bash
grep -rn "@ControllerAdvice\|@RestControllerAdvice\|@ExceptionHandler" --include='*.java' . | grep -v target
find . \( -name "ErrorResponse.java" -o -name "*ErrorDto*.java" \) | grep -v target
```

Read 該類別，確認**實際巢狀層數**（`{"message": ...}` 與 `{"error": {"message": ...}}` 對下游是不同的解析路徑）。

**B4. enum 值清單**

```bash
find . -path '*/enums/*.java' | grep -v target
grep -rn "@JsonValue" --include='*.java' . | grep -v target
```

**逐字列出所有常數名**（有 `@JsonValue` 則以其值為準）。

⚠️ **enum 數量可能很多**（實測某後端有 39 個）。**優先處理對外暴露於 API 的**——
即出現在 DTO／request／response 欄位型別中的。與 API 無關的內部 enum 可略過，
但**必須在文件中說明「本次涵蓋哪些、未涵蓋哪些」**，不可讓下游誤以為已列全。

🔴 **既有文件的 enum 清單一律重新逐一比對，不可沿用**。實測既有 AI 生成文件出現三種錯誤：
- **幽靈值**：文件有、程式碼沒有（`DriverStatus.PENDING`、`TicketStatus.IN_PROGRESS`／`CLOSED`）
- **缺漏值**：程式碼有、文件沒有（`DriverStatus` 缺 `INVITED`／`REJECTED`／`DELETED`）
- **整個 enum 不存在**（文件記載 `AccountType`，39 個 enum 中查無此檔）

下游若採非容錯解析，**缺漏值會直接造成整頁解析失敗**；幽靈值則會讓下游寫出永不執行的分支。

> 🔴 **這項對下游最關鍵**：前端若用非 nullable 的 enum 解析，後端新增一個值就會讓**整頁解析失敗**
> ——不是那一列顯示異常，而是整批資料解析中斷。此類漂移在前端**沒有任何 diff，code review 無法發現**，
> 所以文件必須列全，且新增值時要進變更歷程文件並標 `⚠️`。

**B5. 其他影響 wire 的標註**

```bash
grep -rn "@JsonProperty\|@JsonInclude\|@JsonIgnore\|@JsonFormat" --include='*.java' . | grep -v target
```

**日期時間格式也要從原始碼確認**，不可寫「ISO 8601」了事：

```bash
grep -rn "DateTimeFormatter.ofPattern\|DEFAULT_DATE.*FORMAT\s*=" --include='*.java' . | grep -v target
```

實測某後端的實際格式是 `yyyy-MM-dd HH:mm:ss`（**空格分隔、無 `T`、無時區後綴**），
而既有文件寫成 `YYYY-MM-DDTHH:mm:ssZ (ISO 8601)`——下游照此解析會直接失敗。

`@JsonProperty` 會覆寫命名策略、`@JsonIgnore` 的欄位不會出現在 JSON、
`@JsonFormat` 決定日期時間格式——這些逐欄例外必須標註在對應欄位上。

#### 階段 C：產出

7. 產出 API 總覽文件（**先確認專案實際檔名**）。必須包含獨立的「wire 契約」章節，
   置於端點清單**之前**（下游會先讀它建立解析基礎）
8. 執行 Step 5 自檢

## Bug 修復紀錄產出（通用）

適用於所有技術棧，不需要檢測專案類型。

**步驟**:
1. 讀取 [templates/bug-record.md](references/templates/bug-record.md)
2. 讀取 [frontmatter-spec.md](references/frontmatter-spec.md)
3. 向使用者收集以下資訊（互動式）：
   - 問題描述和錯誤現象
   - 重現步驟
   - 根因分析
   - 修復方式
4. 使用 `git diff` 或 `git log` 提取相關變更
5. 產出：`docs/bug_record/[問題名稱].md`（**依該目錄既有命名慣例**）
6. 執行 Step 5 自檢

## Widget 元件文件產出（Flutter）

**步驟**:
1. 讀取 [templates/widget-doc.md](references/templates/widget-doc.md)
2. 讀取 [frontmatter-spec.md](references/frontmatter-spec.md)
3. 定位 Widget 原始碼：`find lib -name "[widget_name]*.dart"`
4. 分析建構子參數（required/optional、型別、預設值）
5. 搜索使用位置：Grep `[WidgetName](` 全專案
6. 分析 Provider 依賴：Grep `ref.watch\|ref.read` in widget file
7. 產出：`docs/widget/[元件名稱].md`（**依該目錄既有命名慣例**）
8. 執行 Step 5 自檢

## Android 文件產出（框架就緒）

> **TODO**: 以下為預期流程，待實作。

### 專案架構文件
1. 讀取 [stack-context/android.md](references/stack-context/android.md)
2. 分析 `build.gradle`
3. 識別架構模式（MVVM/MVI）
4. 產出文件

### 功能模組文件
1. 定位 Activity/Fragment
2. 分析 ViewModel
3. 提取 Repository 和 Data Source
4. 使用範本：[templates/android-feature.md](references/templates/android-feature.md)

## 文件格式標準

- **語言**: 繁體中文（zh-TW）
- **格式**: Markdown + YAML frontmatter（必填含 `source-commit`、`updated`）
- **命名**: **以專案既有慣例為準**；目錄為空／新建時才用 kebab-case
- **代碼標註**: 完整路徑 + 行號（**每一項「已驗證」內容都必須附得出來**）
- **可信度**: 推導而未確認的內容標 `⚠️ 推導未驗證`
- **範圍**: 不產出流程未要求的章節／範例
- **規模**: 單檔 > 1500 行則分檔 + 索引
- **風格**: 技術性且簡潔

詳見 [frontmatter-spec.md](references/frontmatter-spec.md)。

## 探索策略

- **Glob**: 搜索檔案模式（`lib/page/order/**/*.dart`、`*Controller.java`）
- **Grep**: 搜索代碼模式（`@POST.*orders`、`@PreAuthorize`）
- **Read**: 讀取特定檔案內容

**優先順序**: Glob → Grep → Read

## 擴展到新技術棧

1. 創建 `references/stack-context/[stack].md`（專案概述、技術棧、目錄結構）
2. 創建 `references/templates/[stack]-feature.md`（章節結構）
3. 更新 SKILL.md Step 1 添加檢測邏輯
4. 實作工作流程
5. 測試驗證

## 使用範例

**Flutter - 產出訂單功能文件**:
```
用戶: "產出訂單功能的文件"

1. 檢測 Flutter (pubspec.yaml)
2. 載入 flutter.md 上下文
3. 探索 lib/page/order/
4. 提取 API、StateNotifier、DTO、UI
5. 使用 flutter-feature.md 範本
6. 產出 docs/page_architecture/order-documentation.md
```

**Spring Boot - 產出車輛功能文件**:
```
用戶: "產出車輛 API 的文件"

1. 檢測 Spring Boot (pom.xml)
2. 載入 springboot.md 上下文
3. 讀取 CarController.java
4. 提取 API、@PreAuthorize、@Operation
5. 讀取 CarEntity.java、CarRepository.java
6. 搜索相關 Service 和 DTO
7. 使用 springboot-feature.md 範本
8. 產出 docs/page_architecture/car-documentation.md
```

**Bug 修復紀錄**:
```
用戶: "記錄這次的 bug 修復"

1. 載入 bug-record.md 範本
2. 互動式收集問題資訊
3. 從 git diff 提取變更
4. 產出 docs/bug_record/[問題名稱].md
```

**Widget 元件文件**:
```
用戶: "產出 StationDropdown 的元件文件"

1. 載入 widget-doc.md 範本
2. 定位 Widget 原始碼
3. 分析參數、Provider、使用位置
4. 產出 docs/widget/station-dropdown.md
```

## Resources

### Stack Context Files
專案上下文資訊（技術棧、目錄結構、架構模式）

- [flutter.md](references/stack-context/flutter.md) ✅
- [springboot.md](references/stack-context/springboot.md) ✅
- [android.md](references/stack-context/android.md) 🔧

### Template Files
文件的標準格式範本

- [flutter-feature.md](references/templates/flutter-feature.md) ✅ 功能模組（Flutter）
- [springboot-feature.md](references/templates/springboot-feature.md) ✅ 功能模組（Spring Boot）
- [android-feature.md](references/templates/android-feature.md) 🔧 功能模組（Android）
- [bug-record.md](references/templates/bug-record.md) ✅ Bug 修復紀錄（通用）
- [widget-doc.md](references/templates/widget-doc.md) ✅ Widget 元件（Flutter）
- [change-log.md](references/templates/change-log.md) ✅ 變更歷程（通用，跨 repo 消費者最依賴）

### Specification Files
文件規範

- [frontmatter-spec.md](references/frontmatter-spec.md) ✅ Frontmatter 與命名規範
