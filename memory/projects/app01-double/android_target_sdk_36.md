---
name: android-target-sdk-36
description: 已升級 Android targetSdk/compileSdk 到 36 (Android 16) 因應 Google Play 政策
metadata: 
  node_type: memory
  type: project
  originSessionId: 8667a7bb-a333-4ca6-ab4c-86dcc7833098
  modified: 2026-07-22T01:56:24.324Z
---

因應 Google Play 政策（2026-08-31 起應用更新須 target Android 16 / API 36），已於 2026-07-22 升級。

**改動檔案：`android/app/build.gradle.kts`**
- `defaultConfig` 內 `targetSdk = 36`
- 頂層 `android {}` 的 `compileSdk = 36`
- 移除了 `defaultConfig` 內重複且會覆蓋頂層的 `compileSdk`（compileSdk 只該放 android 頂層）

環境已就緒無須改：Gradle 8.11.1、AGP 8.9.1、buildToolsVersion 36.0.0、NDK 27、minSdk 26。

已用 `flutter build appbundle --flavor product --release`（見 [[android-flavor-entrypoints]]）驗證能成功編譯出 AAB。上架前重點測 API 36 行為變更：前景服務、通知權限、返回手勢、生物辨識登入。
