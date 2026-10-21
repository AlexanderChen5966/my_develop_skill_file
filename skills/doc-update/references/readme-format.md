# docs/shared/readme.md 目標格式

doc-update skill 執行 Step 6 時，請參照此格式更新 docs/shared/readme.md。

---

## 目標格式

```markdown
# 共用文件模組

**最後更新：** YYYY-MM-DD
**用途：** 存放跨模組共用的任務文件、開發模板

---

## 任務文件狀態索引

| 文件 | 功能說明 | 狀態 |
|------|---------|------|
| [xxx.md](./xxx.md) | 功能一句話說明 | ✅ 已完成（YYYY-MM-DD）|
| [yyy.md](./yyy.md) | 功能一句話說明 | ⏳ 待實作 |
| [zzz.md](./zzz.md) | 功能一句話說明 | 🔄 進行中 |

---

## 開發模板

| 文件 | 說明 |
|------|------|
| [test_template.md](./test_template.md) | Playwright 測試模板（Flutter CanvasKit）|

---

## 實作記錄

| 文件 | 說明 | 完成日期 |
|------|------|---------|
| [vehicle_ui_implementation.md](./vehicle_ui_implementation.md) | 車輛新增/編輯 UI | 2026-01-15 |

---

**文件維護：** 每次任務完成後由 /doc-update 自動更新
```

---

## 狀態符號說明

| 符號 | 意義 |
|------|------|
| ✅ 已完成（YYYY-MM-DD）| 實作完成，已通過 code review |
| ⏳ 待實作 | 規劃完成，尚未開始實作 |
| 🔄 進行中 | 實作中，尚未完成 |

---

## 更新規則

1. **新增任務文件** → 在「任務文件狀態索引」表格新增一行，狀態為 `⏳ 待實作`
2. **任務完成** → 將對應行的狀態改為 `✅ 已完成（YYYY-MM-DD）`
3. **模板/參考文件** → 放在「開發模板」表格，無狀態欄
4. **最後更新日期** → 每次修改 readme.md 時同步更新頂部的日期
