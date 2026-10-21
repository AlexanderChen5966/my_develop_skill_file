---
name: project-overview
description: app01-double 是 Flutter 加油站 APP（sanlong）：Riverpod、單一大型控制器 SLController、自訂 SLRouter；含重要檔案路徑
metadata:
  type: project
  modified: 2026-10-21T07:50:00.000Z
---

- Flutter 加油站 APP（sanlong），版本 2.12.1+688（記錄當時；以 `pubspec.yaml` 為準）
- 狀態管理：Riverpod 2.6.1
- 單一大型控制器：`SLController`，方法命名 `on{Screen}{Action}`
- 路由：自定義 `SLRouter` + `NavStack`，Screen enum 在 `router/config.dart`
- DTO 用 Freezed，Data Model 用普通 class

## 重要檔案路徑
- Screen enum：`lib/app/router/config.dart`
- 路由映射：`lib/app/router/router_delegate.dart`
- 主控制器：`lib/app/controller/controller.dart`
- 本地儲存：`lib/app/controller/local.dart`
- DTO：`lib/app/common/dto/api.dart`
- Data Model：`lib/app/common/data/data.dart`
- 支付方式彈窗：`lib/app/utils/store_money_in_quick_mode.dart`（PayWaySelector）
- 空狀態 Widget：`lib/app/ui/widget/empty.dart`（EmptyWidget / ScrollableEmptyWidget）
- 首頁 Grid：`lib/app/ui/home/home_screen.dart`

相關：[[key-patterns]]
