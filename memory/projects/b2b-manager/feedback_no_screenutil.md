---
name: feedback-no-screenutil
description: 全專案新增或修改的程式碼禁止使用 screenutil，改用固定像素值；規則已寫入 CLAUDE.md
type: feedback
originSessionId: 700e0458-acba-46a7-8b6b-2c0bd48a9f79
---
全專案新增或修改的程式碼禁止使用 `flutter_screenutil`（不加 `.w`、`.h`、`.sp`）。

**Why:** 近期最大功能（批次編輯車輛，SSGS-7469）完全採用固定 px，方向已明確；規則於 2026-04-24 正式寫入 CLAUDE.md Section 6。

**How to apply:** 一律用固定 px 值（如 `SizedBox(height: 40)`、`EdgeInsets.all(8)`），不加 `.w/.h/.sp`，不 import `flutter_screenutil`。現有程式碼中的 screenutil 寫法不強制遷移，但修改到尺寸部分時建議順手改成固定 px。

**參考範例：** `car_page.dart`、`batch_edit_car_page.dart` 及其拆分 widgets。
