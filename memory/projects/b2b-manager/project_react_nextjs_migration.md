---
name: project-react-nextjs-migration
description: 2026-10-29 決定方向：比照 TMS 改 React+Next（未立案）；report_schedule POC、主框架（11-03）、標籤設定（11-04，0.6 人天）、額度分配列表（11-04）、儲值紀錄（11-05，0.3 人天）已完成，全站估 61 人天；決策與估算全文在
  docs/shared/react_nextjs_migration_evaluation.md
metadata:
  type: project
  modified: 2026-11-05
permalink: agents-memory/projects/b2b-manager/project-react-nextjs-migration
---

2026-10-29 經 grilling 定案的方向（未立案）：動機是與公司其他專案統一技術棧；Next 15 + React 19 + antd + zustand + TanStack Query + Tailwind；`output: 'export'` 沿用 Nginx+ECS、`/app/*` 分流；React 端自跑 PKCE（靠 authserver 8h session），不動 Flutter OAuth2；同 repo `next/` 子資料夾（`web/` 已被 Flutter 占用）；React 讀 Flutter 存的 `X-Group-Id`（2026-11-03 改為切換公司時寫回，見下）、按選單群組逐步替換；UI 視覺要與 Flutter 一致（非像素級）。下一步：report_schedule 2–4 週 POC，驗收條件見文件第六節；POC spec 在 `.scratch/report-schedule-react-poc/spec.md`，authserver redirect URI 只阻塞免登入／跳轉耗時兩項驗收。

**Why:** B2B 成員（Flutter 背景）轉 React，工時未經驗證，需 POC 校正；新需求照常交付，所以不能一次切換。
**How to apply:** 再談改寫／POC 時先讀 `docs/shared/react_nextjs_migration_evaluation.md` 接續，不重新討論已定的決策。它修正了 [[project-rwd-rewrite-evaluation]] 的「不需要 Next」結論。ApiPaginatedDataTable 的 BATCH_SIZE／isClear 規則不移植到 React，但 `orderBy` 由前端傳的後端契約要保留。

2026-10-30 POC 功能完成（分支 `FlutterToReactPOC`，未 push）：使用者要求 UI「全部照 Flutter」而非只求視覺接近。遷移下一頁前先讀 `docs/shared/react_migration_report_schedule_retrospective.md`——有範圍邊界、票外修改、可沿用的 `next/src/design-system/` 元件與踩坑檢查清單（antd 覆寫須用 token／inline 不可靠 globals.css、表格列高固定、貼上換行、localhost:9001 storage 共用、Playwright 固定 viewport 等）。

2026-10-30 全站工時估算已記在評估文件第八節：分類每頁取上限——簡單 0.75／中等 1.5（report_schedule 基準）／複雜 4.5（×3）／特大 9.5（報表分析、批次編輯車輛），31 頁合計約 61 人天。使用者定案「先照這樣估」，再估或調整時以該節為準，遷移下一頁後回頭校正。

2026-11-03 主框架（HomePage）遷移完成（commit `e928ccda`＋`e4705434`，同分支未 push；spec／票在 `.scratch/react-app-shell/`，工時待填）。之後遷移一頁＝在 `next/src/app-shell/page-registry.ts` 填該頁 `reactPath`，選單自動改走 client-side、未遷移頁整頁跳回 Flutter。已定的決策：切換公司時**寫回** `flutter.X-Group-Id_TAG`，並把 `/groups/search` 那一筆轉 snake_case、再 JSON encode 寫回 `flutter.SELECT_COMPANY_KEY`（Flutter 讀回尚未驗證）；切換後**停在目前頁**（不跟 Flutter 回儀表板）；Flutter 程式一律不改，Flutter 側選單改連 React 留到立案。版本號差異（CI `build_next` 早於 `update_pubspec`）與字型使用者說不用處理。

**How to apply（比對方法）:** 與 Flutter 比對 UI 用使用者的 Chrome（Claude in Chrome）真實點擊，不用 Playwright（canvas 點不開、截圖不更新）；兩分頁可能在不同視窗，窄版要同一分頁先測 Flutter 再開 React；React 尺寸用 DOM 量、Flutter 用已知元素換算截圖比例。`next/` 關掉 Tailwind preflight → 固定高＋padding 要 `boxSizing: 'border-box'`。細節與新踩的坑在回顧文件第 6 節。相關：[[project-all-groups-paid]]

2026-11-04 標籤設定（LabelListPage）遷移完成（`2441f8d6`～`0265866a`，實際 0.6 人天，簡單頁估值暫維持 0.75），反覆修改的根因整理在回顧文件 7.6。之後遷移照這幾條做：
- **API 錯誤改自訂文案**：在 `mutationFn` 內 catch 轉成結果值（例 `'duplicate'`），不要靠 `onError`——全域 `MutationCache.onError` 會先跳出後端原始訊息
- **orval 先查 openapi 的實際 operationId**：springdoc 可能直接用 Controller 方法名（labels search 是 `get`，不是 `search_N`），`operations` 指錯會產生 `useMutation`
- **列表頁先讀該頁 `*_data_table.dart` 的 DataTable2 參數**：`wrapInCard`（預設 true，報表寄送設定是 false）、`horizontalMargin`／`columnSpacing` 各頁不同，照實際值傳給 `DataTable` 的 `wrapInCard`／`spacing`
- **`next/` 沒有 prettier 設定**：❌ 不要對既有檔案跑 `npx prettier`（會整檔重排）；照周圍格式手寫，改完看 `git diff --stat`

2026-11-04 額度分配列表（BalanceDistributeListPage）遷移完成（`c98110d3`～`efec526a`，工時待填），子頁「額度分配」仍在 Flutter（按鈕整頁跳轉，往返要等 dev 部署才能實測）。新共用元件：`DateRangeSelector`（自繪月曆）、`FlutterTooltip`（Flutter 預設 tooltip：下方、grey[700] 小字——**一律用它，不用 antd Tooltip**）、`DataTable` 的排序（`sortKey`＋`sort`／`onSortChange`）與欄寬比例（`sizeRatio`）。比對時：
- **先把 React 切到和 Flutter 相同的公司**（localhost 的 localStorage 會殘留別間公司）
- **確認 Flutter 沒有還原快取的篩選條件**（`CacheableState` 會還原，React 不會）
- **Flutter 元件尺寸以 Chrome 實測為準**：`Container(width:)` 在 tight constraints 下會被撐開（確定鈕原始碼 100、實際 110）；`MenuAnchor` 實際 padding 也和 M3 文件不同
細節在回顧文件第 9 節。

2026-11-05 儲值紀錄（RechargesPage）遷移完成（`f71e084f`、`cd1a013f`，實際 0.3 人天），Chrome 比對後不需修正。新共用工具 `api/download-file.ts`（`downloadFile`＋`excelFileName`，包成 mutation 會自動出現「處理中...」），之後有 Excel 下載的頁面直接用。
- **下載不要把 Accept 限定成 xlsx**：錯誤回應是 JSON，只收 xlsx 會讀不到 400 的訊息
- **判斷付費寫成 `paidSubscriber === false` 才算基本版**：資料還沒載入時當成付費，否則載入瞬間與測試裡日期會被鎖成只能選今天
細節在回顧文件第 10 節。
