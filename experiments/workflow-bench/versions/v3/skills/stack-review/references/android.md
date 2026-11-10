# Android 程式碼審查檢查清單

本檢查清單適用於 Android 原生開發（Java 和 Kotlin）。

**建議**：同時參考 [common.md](common.md) 的通用檢查項目。

**語言標註**：
- ☕ Java 特定
- 🎯 Kotlin 特定
- 📱 兩者通用

## 1. 架構模式

### MVVM / MVI / MVP
- [ ] 是否遵循清晰的架構模式（MVVM/MVI/MVP）？
- [ ] ViewModel 是否只包含UI邏輯和狀態？
- [ ] ViewModel 是否不持有 Activity/Fragment 引用？
- [ ] 業務邏輯是否放在 Repository/UseCase 層？

### 分層架構
```
app/
├── data/
│   ├── local/          # Room Database, SharedPreferences
│   ├── remote/         # Retrofit API
│   └── repository/     # Repository 實作
├── domain/
│   ├── model/          # Domain Models
│   ├── repository/     # Repository 介面
│   └── usecase/        # Use Cases
└── presentation/
    ├── ui/             # Activities, Fragments
    └── viewmodel/      # ViewModels
```

- [ ] 是否分離 Data、Domain、Presentation 層？
- [ ] 是否遵循單向資料流？

## 2. Android Components

### Activity / Fragment
- [ ] 📱 Activity 是否只負責 UI 展示和事件處理？
- [ ] 📱 是否避免在 Activity/Fragment 中寫業務邏輯？
- [ ] 📱 生命週期方法是否正確處理？
- [ ] 📱 是否避免記憶體洩漏（取消訂閱、移除 Listener）？
- [ ] 📱 Fragment 是否正確使用 `viewLifecycleOwner`？
- [ ] 📱 是否避免在 Fragment 中保存大量資料？

### ViewModel
- [ ] 📱 是否使用 Jetpack ViewModel？
- [ ] 📱 ViewModel 是否透過 `ViewModelProvider` 或 `by viewModels()` 創建？
- [ ] 📱 ViewModel 是否不包含 Context/View 引用？
- [ ] 📱 ViewModel 是否使用 LiveData/StateFlow 暴露狀態？
- [ ] 📱 `onCleared()` 是否正確清理資源？

### LiveData / StateFlow / SharedFlow
- [ ] 📱 UI 狀態是否使用 LiveData 或 StateFlow？
- [ ] 🎯 Kotlin 專案是否優先使用 StateFlow/SharedFlow？
- [ ] 📱 是否使用 `observe` 監聽資料變化？
- [ ] 📱 是否避免在 ViewModel 中暴露可變的 LiveData/StateFlow？
  ```kotlin
  // ✅ 推薦
  private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
  val uiState: StateFlow<UiState> = _uiState.asStateFlow()

  // ❌ 避免
  val uiState = MutableStateFlow<UiState>(UiState.Loading)
  ```

## 3. 資料持久化

### Room Database
- [ ] 📱 Entity 是否正確定義（`@Entity`、`@PrimaryKey`）？
- [ ] 📱 DAO 方法是否使用 Suspend 函數或返回 LiveData/Flow？
- [ ] 📱 是否使用 Type Converter 處理複雜類型？
- [ ] 📱 Migration 是否正確實作？
- [ ] 📱 是否使用 `@Transaction` 處理多表操作？

### SharedPreferences / DataStore
- [ ] 📱 簡單鍵值對是否使用 SharedPreferences 或 DataStore？
- [ ] 📱 DataStore 是否優先於 SharedPreferences（Kotlin）？
- [ ] 📱 敏感資料是否加密儲存（EncryptedSharedPreferences）？

## 4. 網路層

### Retrofit
- [ ] 📱 API 介面是否清晰定義？
- [ ] 📱 是否使用 Suspend 函數或 Call/Observable？
- [ ] 📱 是否定義適當的 HTTP 方法（`@GET`、`@POST`、`@PUT`、`@DELETE`）？
- [ ] 📱 Request/Response Model 是否正確序列化（Gson/Moshi）？

### OkHttp Interceptor
- [ ] 📱 是否使用 Interceptor 添加 Header（如 Auth Token）？
- [ ] 📱 是否實作 Logging Interceptor（僅 Debug 模式）？
- [ ] 📱 錯誤處理是否統一處理（如 401 自動登出）？

### 錯誤處理
- [ ] 📱 網路錯誤是否適當處理（Timeout、No Connection）？
- [ ] 📱 是否使用 Sealed Class/Enum 表示網路狀態？
  ```kotlin
  sealed class Result<out T> {
      data class Success<T>(val data: T) : Result<T>()
      data class Error(val exception: Exception) : Result<Nothing>()
      object Loading : Result<Nothing>()
  }
  ```

## 5. 依賴注入

### Hilt / Dagger
- [ ] 📱 是否使用 Hilt 或 Dagger 進行依賴注入？
- [ ] 📱 Application 類是否使用 `@HiltAndroidApp`？
- [ ] 📱 ViewModel 是否使用 `@HiltViewModel`？
- [ ] 📱 模組是否正確定義（`@Module`、`@InstallIn`）？
- [ ] 📱 Scope 是否適當使用（`@Singleton`、`@ActivityScoped`）？

### Koin (Kotlin)
- [ ] 🎯 是否在 Application 中初始化 Koin？
- [ ] 🎯 模組定義是否清晰？
- [ ] 🎯 是否使用 `by inject()` 或 `by viewModel()` 注入？

## 6. UI 開發

### XML Layouts
- [ ] 📱 Layout 是否使用 ConstraintLayout（提升效能）？
- [ ] 📱 是否避免過深的 View 層級？
- [ ] 📱 是否使用 `<merge>` 和 `<include>` 優化？
- [ ] 📱 是否使用 ViewBinding 或 DataBinding？
- [ ] 📱 硬編碼字串是否移至 `strings.xml`？
- [ ] 📱 顏色和尺寸是否定義在 `colors.xml` 和 `dimens.xml`？

### Jetpack Compose (Kotlin)
- [ ] 🎯 Composable 是否無副作用（純函數）？
- [ ] 🎯 是否使用 `remember` 和 `rememberSaveable` 保存狀態？
- [ ] 🎯 是否使用 `LaunchedEffect` 處理副作用？
- [ ] 🎯 是否避免在 Composable 中直接呼叫 ViewModel 方法？
- [ ] 🎯 `collectAsState()` 是否正確使用收集 Flow？
- [ ] 🎯 是否適當使用 Modifier？
- [ ] 🎯 大型列表是否使用 LazyColumn/LazyRow？

### RecyclerView
- [ ] 📱 是否使用 RecyclerView 而非 ListView？
- [ ] 📱 ViewHolder 模式是否正確實作？
- [ ] 📱 是否使用 DiffUtil 優化列表更新？
- [ ] 📱 Item 點擊是否透過介面回調？

## 7. 非同步處理

### Kotlin Coroutines
- [ ] 🎯 是否使用 Coroutines 而非 Thread/AsyncTask？
- [ ] 🎯 是否在正確的 Scope 中啟動 Coroutine？
  - `viewModelScope` - ViewModel
  - `lifecycleScope` - Activity/Fragment
  - `GlobalScope` - 避免使用
- [ ] 🎯 是否使用 `Dispatchers.IO` 處理 IO 操作？
- [ ] 🎯 是否使用 `Dispatchers.Main` 更新 UI？
- [ ] 🎯 錯誤是否在 `try-catch` 或 `CoroutineExceptionHandler` 中處理？

### RxJava (Java)
- [ ] ☕ 是否正確訂閱和取消訂閱（使用 CompositeDisposable）？
- [ ] ☕ 是否使用適當的 Scheduler（io()、mainThread()）？
- [ ] ☕ 錯誤處理是否完善（onError）？

## 8. Kotlin 特定最佳實踐

### Null Safety
- [ ] 🎯 是否善用 Kotlin Null Safety（`?`、`!!`、`?.`、`?:`）？
- [ ] 🎯 是否避免過度使用 `!!`（非空斷言）？
- [ ] 🎯 是否使用 `let`、`apply`、`run` 等 Scope 函數？

### Data Class
- [ ] 🎯 Model 類別是否使用 `data class`？
- [ ] 🎯 是否利用 `copy()` 方法？

### Extension Functions
- [ ] 🎯 通用工具函數是否定義為 Extension Function？
- [ ] 🎯 是否避免過度使用導致程式碼難以理解？

### Sealed Class
- [ ] 🎯 有限狀態是否使用 `sealed class`？
- [ ] 🎯 `when` 表達式是否窮舉所有情況？

## 9. Java 特定最佳實踐

### Null 處理
- [ ] ☕ 是否使用 `@Nullable` 和 `@NonNull` 註解？
- [ ] ☕ 是否避免 NullPointerException？
- [ ] ☕ Optional 是否適當使用（Android 需要 Java 8+）？

### Lombok (可選)
- [ ] ☕ 是否使用 Lombok 減少樣板程式碼（`@Data`、`@Builder`）？

## 10. 效能優化

### 記憶體
- [ ] 📱 Bitmap 是否適當處理和回收？
- [ ] 📱 大型物件是否避免在 Activity/Fragment 中持有？
- [ ] 📱 是否使用 Memory Profiler 檢查記憶體洩漏？
- [ ] 📱 是否避免在 Application 類中保存大量資料？

### 卡頓優化
- [ ] 📱 主執行緒是否避免耗時操作？
- [ ] 📱 RecyclerView 滑動是否流暢（避免在 onBind 中複雜計算）？
- [ ] 📱 過度繪製是否優化（使用 GPU 過度繪製工具）？

### 啟動優化
- [ ] 📱 Application 初始化是否延遲或非同步？
- [ ] 📱 冷啟動時間是否合理？

## 11. 安全性

### ProGuard / R8
- [ ] 📱 Release 版本是否啟用程式碼混淆？
- [ ] 📱 ProGuard 規則是否正確配置？
- [ ] 📱 第三方庫是否有對應的 ProGuard 規則？

### 敏感資料
- [ ] 📱 API Key 是否儲存在 `local.properties` 或環境變數？
- [ ] 📱 敏感資料是否加密儲存？
- [ ] 📱 Log 是否避免輸出敏感資訊（Release 版本移除）？

### 網路安全
- [ ] 📱 是否使用 HTTPS？
- [ ] 📱 是否實作 Certificate Pinning（高安全性需求）？
- [ ] 📱 WebView 是否禁用 JavaScript（如不需要）？

## 12. 測試

### 單元測試
- [ ] 📱 ViewModel 邏輯是否有單元測試？
- [ ] 📱 Repository 是否有測試？
- [ ] 📱 是否使用 Mockito/MockK 模擬依賴？

### UI 測試
- [ ] 📱 關鍵流程是否有 Espresso/Compose UI 測試？
- [ ] 📱 是否使用 Hilt Test 注入測試依賴？

## 13. 版本控制與 CI/CD

### Gradle
- [ ] 📱 依賴版本是否統一管理（Version Catalog 或 buildSrc）？
- [ ] 📱 是否使用 Gradle Kotlin DSL（`.kts`）？
- [ ] 📱 Build 時間是否優化（Gradle Daemon、Build Cache）？

### Git
- [ ] 📱 是否避免提交 `build/` 和 `.idea/` 目錄？
- [ ] 📱 `.gitignore` 是否正確配置？

---

## 使用建議

1. **與通用檢查清單結合**：
   - 先檢查 [common.md](common.md) 的安全性和程式碼品質
   - 再檢查本檢查清單的 Android 特定項目

2. **優先級**：
   - 🔴 Critical: 記憶體洩漏、主執行緒阻塞、敏感資料洩漏
   - 🟡 Warning: 架構不清晰、缺少測試、效能問題
   - 🟢 Suggestion: 程式碼風格、Kotlin 慣用法

3. **工具輔助**：
   - Android Lint
   - Memory Profiler / CPU Profiler
   - Layout Inspector
   - ktlint (Kotlin)
   - Detekt (Kotlin 靜態分析)

4. **學習資源**：
   - Android Developers 官方文件
   - Kotlin 官方文件
   - Android Architecture Components
   - Now in Android 範例專案