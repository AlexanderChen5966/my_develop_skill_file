---
name: android-flavor-entrypoints
description: Android 各 flavor 有獨立進入點，flutter build 必須帶 --target 否則失敗
metadata: 
  node_type: memory
  type: project
  originSessionId: 8667a7bb-a333-4ca6-ab4c-86dcc7833098
  modified: 2026-07-22T01:56:17.392Z
---

Android 各 flavor 有**獨立的 Dart 進入點**，`lib/main.dart` 只有 `mainCommon()` 沒有 `main()`。只下 `--flavor` 而不帶 `--target` 會失敗，報 `main.dart: No 'main' method found`。

| Flavor | 進入點 |
|--------|--------|
| product（正式，apiProdUrl） | `lib/main_android_release_debug.dart` |
| staging | `lib/main_android_staging_debug.dart` |
| dev | `lib/main_android_debug.dart` |

正式版建置指令：
```
flutter build appbundle --flavor product --release --target lib/main_android_release_debug.dart
```

簽章需 `android/key.properties`（已存在）。iOS 進入點另有 `main_ios_*.dart`。
