# Widget 元件文件範本

此範本適用於 Flutter 共用元件/Widget 的技術文件。

## 標準結構

```markdown
---
title: [Widget 名稱] 元件文件
type: widget
created: YYYY-MM-DD
status: completed
related-modules: [使用此元件的模組]
---

# [Widget 名稱]

## 概述

**路徑：** `lib/path/to/widget.dart`
**類型：** `StatelessWidget` / `StatefulWidget` / `HookConsumerWidget`
**用途：** [一句話說明用途]

## 使用方式

\`\`\`dart
WidgetName(
  requiredParam: value,
  optionalParam: value,
)
\`\`\`

## 參數 (Props)

| 參數 | 型別 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `param1` | `String` | ✅ | - | 說明 |
| `param2` | `bool` | ❌ | `false` | 說明 |

## 狀態管理

**使用的 Provider：**
- `providerName` — 說明用途

**內部狀態：**
- `_localState` — 說明用途

## 使用位置

| 頁面/元件 | 路徑 | 用法說明 |
|-----------|------|---------|
| `PageName` | `lib/page/module/page.dart:行號` | 怎麼用 |

## 注意事項

- [已知限制或特殊行為]
- [效能考量]

## 相關元件

- `RelatedWidget` — 關係說明
```

## 撰寫指引

1. **參數表格是核心**：讓使用者快速理解怎麼呼叫
2. **使用範例要可執行**：直接複製貼上就能用
3. **列出所有使用位置**：方便評估修改影響範圍
4. **注意事項寫踩坑經驗**：避免其他人重複犯錯
