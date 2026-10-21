---
name: project-carwash-ssgs9377
description: 預約洗車（SSGS-9377）已合併 main 但從未上架；保留的設計決定：訂單詳情用 pushMain、本地儲存登出不清除、設計圖 4-1/4-2 檔名對調
metadata:
  type: project
  modified: 2026-10-21T07:50:00.000Z
---

SSGS-9377 預約洗車：規劃文件在 `docs/car_wash/`（17 個任務）。分支 `feature/SSGS-9377` 已合併進 main（2026-10-21 以 git 確認）。
⚠️ 洗車**從未上架**；版本線索見 [[release-line-vs-tag-mismatch]]。

決定（再改洗車時沿用）：
- 訂單詳情用 `pushMain`（非 popup）——有三個入口加上複雜導航（popToRoot）
- 本地儲存：**登出不清除**，僅帳號移除時清除
- 設計圖注意：`4-1.png` 是失敗、`4-2.png` 是成功（檔名與內容對調）
- 開發當時 API 與 icon 尚未就緒，用 mock；接真實 API 時先確認 mock 是否已移除
