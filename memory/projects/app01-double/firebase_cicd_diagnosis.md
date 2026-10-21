---
name: firebase-cicd-diagnosis
description: Firebase App Distribution CI 失敗：表面是 --token 認證被棄用，根本原因是 Mac runner 上傳速率異常導致 timeout（2026-04-17 診斷，修好與否未確認）
metadata:
  type: project
  originSessionId: 2cdded01-42b9-4a32-96c4-baa906dca49e
  modified: 2026-10-21T07:45:00.000Z
---

**最後診斷日期**：2026-04-17（Mac runner 本機驗證）。之後是否已修好**未確認**，再遇到時先問使用者現況。

### 表面症狀：認證方式被棄用
- GitLab CI 用 `--token "$FIREBASE_TOKEN"` 認證，Firebase CLI 12.x 已棄用（deprecated warning）
- CLI 回傳 HTML 錯誤頁而非 JSON：`Unable to parse JSON: SyntaxError: Unexpected token < in JSON at position 0`
- 已驗證有效：Service Account JSON 金鑰、取得 Google access token、App Distribution API 權限、Firebase CLI 12.4.1
- 解法：改用 **`GOOGLE_APPLICATION_CREDENTIALS`** 環境變數（官方標準），`.gitlab-ci.yml` 有 3 處要改：`debug_build_android`、`staging_build_android`、`release_build_android` 的 `firebase appdistribution:distribute`
- Service Account JSON：當時放在**某位同事電腦上的寫死路徑**（路徑不記在記憶裡，2026-10-21 去敏）。長期應改用 **GitLab Variables（File 類型）** 管理，不要寫死路徑

### 根本原因（2026-04-17 發現）
- ⚠️ **Mac runner 網路上傳速率異常緩慢**（不明原因），上傳 APK 時頻繁 timeout
- 認證問題只是表面症狀
- 解決思路：檢查 runner 網路品質、調高 Firebase 指令 timeout、監控上傳速度

**How to apply:** Firebase 上傳失敗時，不要只修認證；先確認 runner 上傳速度。診斷資訊不要 commit 進專案。
