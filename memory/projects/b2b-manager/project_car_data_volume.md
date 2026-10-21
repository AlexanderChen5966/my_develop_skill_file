---
name: project-car-data-volume
description: 正式區單一企業車輛數最多約 3 萬台；staging 29 萬台是測試資料，大資料量效能處理屬預先補強
metadata:
  node_type: memory
  type: project
  originSessionId: 75d45ce5-bffb-4ff8-845f-30f7f00eccad
  modified: 2026-09-23T02:22:38.440Z
---

正式區單一企業車輛數目前最多約 **3 萬台**；staging「高雄市私立同安汽車駕駛人訓練班」的 29 萬台是測試資料（2026-09-23 使用者說明）。

**Why:** 批量車輛編輯頁（SSGS-13504）的效能處理是以 29 萬筆測試資料為壓力基準做的預先補強，使用者明確表示「等實際車輛數真的大到會出現測試資料的狀況時再處理」。

**How to apply:** 評估車輛相關的效能／body 大小風險時，以 3 萬台為實際量級判斷優先度；只在 29 萬筆才會出事的項目（如送出 3MB body 分批、`allSelectedHaveFuelDelivery` 增量計算）列為待辦，不要主動實作。細節見 `docs/shared/batch_edit_car_search_limit.md`「第二輪檢查」。
