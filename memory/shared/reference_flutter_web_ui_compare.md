---
name: reference-flutter-web-ui-compare
description: 比對 Flutter Web（canvas）畫面要用使用者的 Chrome（Claude in Chrome）真實點擊，不用 Playwright；尺寸用已知元素換算截圖比例
metadata:
  type: reference
  modified: 2026-11-04
permalink: agents-memory/shared/reference-flutter-web-ui-compare
---

Flutter Web 畫在 canvas 上，DOM 沒有文字與元素可查。要跟 Flutter 並排比對 UI（例如改寫成 React 時）：

- **用使用者自己的 Chrome（Claude in Chrome 擴充功能）真實點擊**：展開選單、hover、tooltip、對話框都能穩定觸發
- ❌ **Playwright 不可靠**：canvas 點擊常點不開（要按住約 60ms 也不一定成功）、截圖會拿到沒更新的舊畫面、`wait_for` 等文字永遠等不到
- 截圖座標比例會隨視窗與分頁變動（同一個 1360 寬的頁面可能拿到 1456／1326 的座標系）：DOM 那一邊直接用 `getBoundingClientRect` 量 CSS px；Flutter 那邊用已知尺寸的元素（例如表頭 48、欄位寬 318）換算比例，再比數字，不要用肉眼比截圖
- 兩個分頁可能在不同 Chrome 視窗，`resize_window` 只影響其中一個；比對窄版時在**同一個分頁**先測 Flutter、再導到另一邊
- 已知 Flutter 實際行為常與「照原始碼推的預設值」不同（例：InkWell hover 被父層 Container 底色蓋住而不變色），以實測為準
- **每個元素都量座標並填表**（Flutter 截圖換算、React DOM），第一張截圖就列出所有區塊的上下左右——含頁碼列、提示框按鈕等小元素；只看「主要內容像不像」會漏（b2b-manager 頁碼列低 9px 是使用者事後發現）
- **互動狀態要比三種：hover、停用、tooltip**（Flutter `IconButton` 有 tooltip 時停用也會顯示）
- 套件／widget 的預設值（例：`PaginatedDataTable2` footer 56、`wrapInCard` 預設 true、Card margin 4）直接讀套件原始碼，不要憑記憶或沿用上一頁的設定

**How to apply:** 任何專案要驗證「與 Flutter 畫面一致」時照此做；b2b-manager 的實例與完整踩坑在該 repo `docs/shared/react_migration_report_schedule_retrospective.md` 第 6 節。