---
name: cross-platform-archive-agent
description: >
  Generate optimal compression commands based on target extraction platform.
  Automatically excludes OS-specific metadata and system junk files.
  Supports macOS, Windows, and Linux as both build and target platforms.
  Use when the user asks to compress/archive files or folders (e.g., "壓縮", "打包", "archive", "zip", "tar").
metadata:
  version: 1.0.0
  last-updated: 2026-03-03
---

# Cross-Platform Archive Agent

根據 **target extraction platform** 自動產生最佳壓縮指令，並排除跨平台垃圾檔。

## 工作流程

### Step 1：解析輸入

從使用者的自然語言中提取：

| 欄位 | 說明 | 範例 |
|------|------|------|
| `path` | 要壓縮的檔案或資料夾路徑 | `./project`、`src/` |
| `target_platform` | 解壓縮的目標平台（使用者指定） | `windows`、`macos`、`linux` |
| `dry_run` | 是否為模擬模式 | 偵測到「模擬」、「dry-run」、「不要真的壓縮」 |

**支援的自然語言指令格式：**
```
壓縮 <路徑>
壓縮 <路徑> 成 zip
壓縮 <路徑> 成 tar.gz
壓縮 <路徑>，解壓平台是 windows
壓縮 <路徑>，給 linux 用
模擬壓縮 <路徑>
```

---

### Step 2：確認 Build Platform

偵測優先順序：
1. 使用者在請求中明確指定（如「我在 Windows 上」）
2. 從對話上下文推斷（如先前提到的作業系統）
3. 若無法確定，主動詢問使用者

> Build platform 影響指令可用性（如 `tar` 在 Windows 原生環境可能需要 WSL），但**不影響排除規則**，排除規則只依 `target_platform` 決定。

---

### Step 3：決定壓縮格式與輸出檔名

**格式對照表：**

| Target Platform | 格式 | 工具 |
|----------------|------|------|
| `windows` | `.zip` | `zip` |
| `macos` | `.tar.gz` | `tar` |
| `linux` | `.tar.gz` | `tar` |

**輸出檔名規則：**
```
輸出檔名 = basename(path) + 對應副檔名
```
範例：`./project` → `project.zip`，`./src/` → `src.tar.gz`

---

### Step 4：建立排除清單

**Ignore Rules：**
```
macos:   .DS_Store, __MACOSX, ._*
windows: Thumbs.db, Desktop.ini
linux:   .directory, .Trash-*
common:  .git, .gitignore, .env
```

**組合邏輯：**
```
excludes = common + 所有「非 target_platform」的 OS 規則
```

**各 target 的排除組合：**

| Target | 排除項目 |
|--------|---------|
| `windows` | common + macos 規則 + linux 規則 |
| `macos` | common + windows 規則 + linux 規則 |
| `linux` | common + macos 規則 + windows 規則 |

---

### Step 5：套用 Pattern 語法產生指令

**Pattern 語法差異：**

| 工具 | 寫法 | 說明 |
|------|------|------|
| `zip` | `-x "**/pattern"` | 需加 `**/` 前綴以遞迴比對子目錄 |
| `tar` | `--exclude='pattern'` | 預設比對任意深度的檔名，無需路徑前綴 |

目錄排除：`zip` 用 `**/.git/**`（含內容），`tar` 用 `--exclude='.git'`（整個目錄）

#### zip 指令範本（target: windows）

```bash
zip -r <output>.zip <path> \
  -x "**/.DS_Store" \
  -x "**/__MACOSX/**" \
  -x "**/._*" \
  -x "**/.directory" \
  -x "**/.Trash-*" \
  -x "**/.git/**" \
  -x "**/.gitignore" \
  -x "**/.env"
```

#### tar 指令範本（target: linux 或 macos）

```bash
tar \
  --exclude='.DS_Store' \
  --exclude='__MACOSX' \
  --exclude='._*' \
  --exclude='Thumbs.db' \
  --exclude='Desktop.ini' \
  --exclude='.git' \
  --exclude='.gitignore' \
  --exclude='.env' \
  -czf <output>.tar.gz <path>
```

> 依照 target_platform 從範本中移除對應的平台排除項目（target 平台的垃圾檔**不排除**）。

---

### Step 6：輸出

#### 一般模式

直接輸出可執行的 CLI 壓縮指令（bash code block），附上簡短說明：
- 目標平台
- 使用格式
- 排除的平台垃圾檔類型

#### Dry-run 模式

若偵測到以下關鍵字：`模擬`、`dry-run`、`不要真的壓縮`

僅輸出排除清單，不產生壓縮指令。格式如下：
```
[Dry Run] 排除清單（target: <platform>）
- <item 1>
- <item 2>
...
```

---

## 完整範例

### 範例 1：壓縮給 Windows 用

**輸入：** `壓縮 ./project，解壓平台是 windows`

**輸出：**
```bash
zip -r project.zip project \
  -x "**/.DS_Store" \
  -x "**/__MACOSX/**" \
  -x "**/._*" \
  -x "**/.directory" \
  -x "**/.Trash-*" \
  -x "**/.git/**" \
  -x "**/.gitignore" \
  -x "**/.env"
```

---

### 範例 2：壓縮給 Linux 用

**輸入：** `壓縮 ./src，給 linux 用`

**輸出：**
```bash
tar \
  --exclude='.DS_Store' \
  --exclude='__MACOSX' \
  --exclude='._*' \
  --exclude='Thumbs.db' \
  --exclude='Desktop.ini' \
  --exclude='.git' \
  --exclude='.gitignore' \
  --exclude='.env' \
  -czf src.tar.gz src
```
