# Android 專案上下文

> **TODO**: 此文件待完成。當需要支援 Android 專案文件產出時填充。

## 預期內容

### 專案概述
- Android SDK 版本（minSdk, targetSdk, compileSdk）
- 語言（Java/Kotlin）
- 架構模式（MVVM/MVI/MVP）

### 技術棧
- 核心框架（Jetpack components）
- 狀態管理（LiveData/StateFlow, ViewModel）
- 網路層（Retrofit, OkHttp）
- 資料庫（Room, SQLite）
- 依賴注入（Hilt/Dagger/Koin）
- UI（XML Layouts/Jetpack Compose）

### 目錄結構
```
app/src/main/java/com/company/project/
├── data/
│   ├── local/          # Room Database
│   ├── remote/         # Retrofit API
│   └── repository/     # Repository Pattern
├── domain/
│   ├── model/          # Domain Models
│   └── usecase/        # Use Cases
└── presentation/
    ├── ui/             # Activities, Fragments
    └── viewmodel/      # ViewModels
```

### 關鍵架構模式
- MVVM 架構
- Repository Pattern
- ViewModel 與 LiveData/StateFlow
- Jetpack Compose（如適用）
- Coroutines 非同步處理

### 文件格式要求
- Markdown 格式
- 繁體中文（zh-TW）
- 包含代碼位置標註（類別名稱:行號）

---

**參考**:
- Android Developers: https://developer.android.com
- Android Architecture Components
- Kotlin 官方文件: https://kotlinlang.org