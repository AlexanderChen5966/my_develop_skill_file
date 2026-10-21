---
name: key-patterns
description: app01 慣用寫法：Bottom Sheet 用 showModalBottomSheet（showFlexibleBottomSheet 會崩潰）、全頁導航用 pushMain、防重複提交用 controller bool flag、待支付本地檢查
metadata:
  type: feedback
  modified: 2026-10-21T07:50:00.000Z
---

- Bottom Sheet 用 `showModalBottomSheet(isScrollControlled: true)`；❌ `showFlexibleBottomSheet` 搭 `ConsumerStatefulWidget` 會 `parentDataDirty` 崩潰（2026-07-28 校正舊記錄）
- 待支付檢查：APP 端本地檢查 `isWaiting` flag，非 API 端
- 防重複提交：controller 裡用 bool flag（如 `isStoringMoney`）
- 導航全頁用 `pushMain(NavConfig(screen:, data:, isTopPadding:, isDraggable:))`

相關：[[project-overview]]
