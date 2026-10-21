# Memory Index

> app01-double 專案層記憶。個人層與跨專案層見 `~/.agents/memory/global/MEMORY.md`、`~/.agents/memory/shared/MEMORY.md`。
> 任務進度不放這裡，放 `.handoff/`。

- [專案概況與重要路徑](project_overview.md) — Flutter 加油站 APP（sanlong）：Riverpod、SLController（on{Screen}{Action}）、SLRouter；主控制器／DTO／路由檔案位置
- [關鍵寫法](key_patterns.md) — Bottom Sheet 用 showModalBottomSheet（showFlexibleBottomSheet 會崩潰）、全頁用 pushMain、防重複提交用 bool flag
- [預約洗車 SSGS-9377](project_carwash_ssgs9377.md) — 已合併 main 但從未上架；訂單詳情用 pushMain、本地儲存登出不清除、設計圖 4-1/4-2 檔名對調
- [tag 與上架線錯位](release-line-vs-tag-mismatch.md) — 不要用 tag 名稱推斷版本先後；上架線是從 2.21.0 分出的旁支
- [Flavor 進入點](android_flavor_entrypoints.md) — build 須帶 --target，各 flavor 獨立 main 檔（product→main_android_release_debug.dart）
- [targetSdk 36 升級](android_target_sdk_36.md) — 因 Google Play 政策升到 Android 16 (API 36)，改 build.gradle.kts
- [iOS 憑證到期](ios-signing-cert-expiry.md) — CI 簽章失敗先查憑證到期；下次 2027/10/16，**APNs 憑證 2026/11/14 到期**
- [Firebase CI/CD 失敗](firebase_cicd_diagnosis.md) — 表面是 --token 棄用，根因是 Mac runner 上傳速率慢導致 timeout；2026-04 診斷，修好與否未確認
- [車號阻擋邏輯](ref_car_plate_validation.md) — 參照 b2b-manager 新增車輛時的 5 步驟車號驗證（長度 ≤7、Regex 大寫字母+數字）
