---
name: project-dashboard-switch-company-remount-regression
description: dashboard 首頁卡片「只在 initState 打 API」靠 unmount/remount 刷新的隱性依賴；P2 拿掉 remount 後切公司五張卡片卡舊，2026-09-09 以 ref.listen(selectCompany.id)+X_Group_Id 去重修好；context.replace 對 const route 不重建；select(groups) 同 List 實例不觸發
metadata: 
  node_type: memory
  type: project
  originSessionId: 590929a8-ea86-44be-a222-c0c091506190
  modified: 2026-09-09T08:23:36.705Z
---

`dashboard_loading_optimization_2026-09-01.md` 第一批 P2 把 `home_board_page.dart` 兩層 loading gate 從「整棵子樹換成 SlLoading（卡片 unmount/remount）」改成「Stack 疊覆蓋層」，2026-09-09 staging 實機量測證實這移除了五張卡片唯一的資料刷新機制（切公司後卡片 API 0 次、畫面全是舊公司資料）。同日以方案 ① 修好並實測通過（切公司後各卡片 API 恰 1 次、資料正確），尚未 commit。

**Why（根因）**：
- `Pie/Bar/RecentOrder/RecentLog/BillingDate` 只在 `initState` 打一次 API，沒監聽公司切換；`refreshWhileSwitchId()` 也不含它們的 notifier。過去純靠 gate 造成的 unmount/remount 重跑 `initState`。`StoreValue` 是 `build()` 內 `ref.watch`，天生反應式，所以沒事。
- `page_route.dart` 的 `HomePage`/`HomeBoardPage` 是 `const` 建構、沒有隨 `X_Group_Id` 變化的 `Key`，GoRouter 對同一路徑 `context.replace` **不會**重建 State——計劃風險分析①「預期會，需實測」實測不成立。
- 第一版 P4 用 `ref.listen(select((s) => s.groups))` 幾乎是死的：`fetchGroupsFromApi` 是 `_originalGroup.clear()` 後 `copyWith(groups: _originalGroup)`，List 實例不變，`select` 視為未變（只有 app 啟動第一次會觸發）。

**修法（已驗證有效）**：五張卡片在 `buildContent` 內 `ref.listen(groupStateNotifier.select((s) => s.selectCompany.id))`；`-1` 跳過；四張 header 範疇的卡片以 `ApiConnector.X_Group_Id != _lastFetchedGroupId` 去重（`StoreValueWidget` 自己的下拉也呼叫 `setSelectCompany`，不能只看 id）；`BillingDate` 以 `resolveCurrentGroup(ref).id` 去重；`RecentOrder` 筆數改依 `selectCompany.requireInvoice`（`userData` 在 Step 7 才更新）。

**2026-09-09 後續：版型翻轉 remount 造成的兩個低機率畫面異常（已修）**
`DashboardContent` 的 `RequireInvoiceDashboard` / `CreditAccountDashboard` 是不同 widget type，切換公司時 `requireInvoice` 一變（發票 ↔ 簽帳客戶）或 `userGroup` 短暫解析為 `empty()`（groups 在 Step 6 更新、userData 在 Step 7），整棵卡片子樹會 unmount/remount；舊實例的在途請求不會取消，仍寫進共享 notifier。導致：
- 長條圖 x 軸出現 24 個標籤（`bar_chart_state_notifier` 原本「開頭 `clear()` ＋ 回應時 append 12 筆」，兩請求重疊變 24；`getMonthIndex` 對 index ≥ 12 回 0 → 全印「一月」）
- 圓餅圖品項永久轉圈（`pie_chart_state_notifier` 在 `.then` 內 `ref.read(stationStateNotifier)` → 卡片已 dispose 時拋 `Bad state: Cannot use "ref" after the widget was disposed`，`copyWith` 沒跑；且 Step 8 `refreshWhileSwitchId` 會清空 stations；再加上 widget 把「空圖例」畫成 `SlLoading()`）

修法：兩個 chart notifier 改「本地組好資料再一次性指派」（不要 clear+append）；pie 的產品清單改在**發請求前**讀取；空圖例顯示「尚無資料顯示」而非 loading。另外實測發現「載入狀態用可變旗標（`isMultipleLoading`／`_isFetching`）＋ 先 `clearData()`」會產生新的永久轉圈，已改為**只看 `result == null`** 判載入、`try/finally` 保證旗標重設、補抓前不清資料。

**2026-09-09 三批全部收尾**（批一 `ba32e48c`、批二 `96110d77` 已 commit；第三批完成 3 項尚未 commit）
- 第三批做了：**P10** 兩個 chart notifier 的 `copyWith`/`clearData` 加 `if (!mounted) return`（bar 是 autoDispose，在途回應會對已 dispose 的 StateNotifier 設 state）＋ **pie notifier 移除 `WidgetRef` 參數**（改收 productList，讓「在 `.then` 用已 dispose 的 ref」型別上不可能）＋ `callPieChartApi` 在 await stations 後補 `state.mounted`；**P8** 移除 5 個 `dio.close()`（先證實無作用：全庫 57 支 API 走 Retrofit `fetch()`、且 interceptor 每個回應都關而 App 照常）並移除 interceptor 內 `as IOHttpClientAdapter` 死程式碼（web 專案，該轉型會拋錯，只因 `extra['dio']` 從未設定才沒炸）；**P13** 兩版型合併為單一 `DashboardCards`，各欄用**依內容命名的 `ValueKey`**（`Wrap` children 靠 key 比對、不受 index 影響）→ 圖表欄與儲值/日誌欄跨版型保留，API 由 2 輪降 1 次
- **P9／P3 評估後不做**：P9（recentOrder keepAlive）只省 1 支請求，卻要背「殘留前一家公司訂單」的風險（`notifier_utils` 有 4 個清除點）；P3（LoadingProvider 語意改造）的使用者可見痛點已在批一繞過（載入判斷改成只看 `result == null`），剩餘是全站架構債（10 檔＋interceptor），應與 `optimization_audit` 第 5／6 項合併另開任務

**How to apply**：
- 動 `home_board_page.dart` 的 gate 或任何「靠 unmount/remount 換資料」的機制前，逐卡盤點資料來源：`ref.watch` 的安全；「只在 `initState` 打一次」的必須另補刷新機制。
- 監聽 `groupStateNotifier` 用值型欄位（`selectCompany.id`），**不可 select `groups`**。
- 不要假設 `context.replace` 到同一 const 路由會重建 State。
- 切換公司流程時序：Step 3 換 `X_Group_Id` → Step 5 `setSelectCompany`（在舊清單找，可能 -1）→ Step 6 重抓 groups 再 `setSelectCompany` → Step 7 才更新 `userData`。任何「切換完成」的判斷別依賴 `userData`。
- 計數 API 用頁內 `performance.clearResourceTimings()` ＋ `getEntriesByType('resource')`（輸出去掉 query string，否則被隱私過濾擋）；擴充功能的 `read_network_requests` 對這個 Flutter web 只抓得到 OPTIONS。
- notifier 內「先 clear 再於回應時累積」的寫法在任何併發下都會壞（首頁兩個 chart 都犯過）；一律**本地組好再一次性指派**。
- notifier 的 `.then`／`catchError` 內**不可用 `ref`**（卡片可能已 dispose）；需要的外部狀態在發請求前先讀成區域變數。
- 載入中狀態盡量由**資料本身**推導（如 `result == null`），不要依賴可變旗標——旗標漏重設就是永久轉圈；空資料也不要畫成 loading。
- 這個 dashboard 的公司清單有兩筆同名「全鋒汽車股份有限公司」但 group id／版型不同（一筆簽帳、一筆發票），是測試版型翻轉的現成素材。
- 相關：[[project-docs-concurrent-write-hazard]]
