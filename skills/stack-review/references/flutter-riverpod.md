# Flutter + Riverpod 程式碼審查檢查清單

本檢查清單專為 B2B Manager Flutter Web 專案設計，涵蓋架構規範、程式碼品質和最佳實踐。

## 1. State 管理架構

### State 類型選擇
- [ ] State 類型選擇是否正確？
  - **CacheableState**: 複雜搜尋條件需要快取的列表頁面
  - **SingleTaskState**: 需要任務管理但不需快取的儀表板/詳細頁面
  - **ConsumerState**: 簡單的路由頁面、設定頁面、靜態頁面

### ConsumerState 規範
- [ ] Widget 是否繼承 `StatefulHookConsumerWidget`？
- [ ] State 是否繼承 `ConsumerState<T>`？
- [ ] 是否定義 `static const String ROUTE_NAME`？
- [ ] 建構子是否使用 `const`？

### SingleTaskState 規範
- [ ] State 是否繼承 `SingleTaskState<T>`？
- [ ] 是否實作 `onVisibleChange(bool isVisible)` 方法？
- [ ] 是否實作 `onRefresh()` 方法？
- [ ] 是否實作 `buildContent(BuildContext context)` 方法？
- [ ] `dispose()` 是否釋放所有資源（Timer、Controller）？

### CacheableState 規範
- [ ] State 是否繼承 `CacheableState<T, R>`？
- [ ] 是否混入 `SingleTickerProviderStateMixin`（如需要 TabController）？
- [ ] 是否實作 `getCacheableRequest()` 方法？
- [ ] 是否正確處理快取載入後的欄位清空？
- [ ] `dispose()` 是否釋放 `paginatorController`（如有）？

## 2. Riverpod 使用規範

### ref.watch vs ref.read
- [ ] **讀取狀態** 是否使用 `ref.watch()`？
  - 監聽 UI 更新時必須使用 `ref.watch()`
  - 建議使用 `select()` 優化效能：`ref.watch(notifier.select((s) => s.data))`
- [ ] **寫入狀態** 是否使用 `ref.read().notifier`？
  - 執行操作時使用 `ref.read(notifier.notifier).method()`
- [ ] **避免在 build 方法中使用 `ref.read()` 讀取會變化的狀態**

### Provider 使用
- [ ] StateNotifier 是否正確定義？
- [ ] Provider 是否使用 `final` 宣告？
- [ ] 是否避免在不必要的地方創建 Provider？

## 3. 生命週期管理

### initState 規範
- [ ] 是否使用 `WidgetsBinding.instance.addPostFrameCallback()`？
- [ ] 是否記錄 FCM 事件（如需要）？
- [ ] 是否更新首頁狀態（如需要）？
- [ ] 是否檢查並載入依賴資料（群組、站點、產品等）？

### dispose 規範
- [ ] 是否釋放 Timer？
- [ ] 是否釋放 Controller（PaginatorController、ScrollController、TabController）？
- [ ] 是否取消所有未完成的任務？

## 4. TaskManager 單例模式

### OAuth2 和認證
- [ ] **關鍵任務** 是否使用 TaskManager 避免重複執行？
  ```dart
  await taskManager.executeTask(
    TaskManager.handleAuthorizationResponseTask,
    () => handleAuthorizationResponse(context),
    timeout: Duration(seconds: 30),
  );
  ```
- [ ] 是否避免直接調用 OAuth2 相關方法？
- [ ] Token 刷新邏輯是否交由 Dio Interceptor 處理？

### API 呼叫
- [ ] 是否避免重複的 API 請求？
- [ ] 列表頁面是否使用 `addTask()` 管理任務？
- [ ] 是否在切換頁面前取消未完成的任務？

## 5. UI 架構規範

### Scaffold 結構
- [ ] 背景色是否使用 `SLColor.primaryBackground`？
- [ ] Padding 是否使用 `kPagePadding`？
- [ ] 是否使用適當的佈局方式（Column、ListView、SingleChildScrollView）？

### AppBar
- [ ] 標題是否正確？
- [ ] 是否使用適當的背景色？
- [ ] 是否需要 AppBar（路由頁面通常不需要）？

### 分頁表格
- [ ] 使用 `PaginatedDataTable2` 時是否宣告 `PaginatorController`？
- [ ] 是否在 `dispose()` 中釋放 `paginatorController`？
- [ ] DataTable 是否包裝在 `DataTableWithShimmer` 中？
- [ ] 是否正確傳遞 `pageStatus`？

### const 優化
- [ ] 靜態 Widget 是否使用 `const`？
- [ ] 子頁面是否使用 `const` 建構子？
- [ ] 建構子參數是否使用 `const` 修飾（如適用）？

## 6. 程式碼品質

### 硬編碼和 Magic Number
- [ ] 是否避免硬編碼字串？（使用 i18n 或常數）
- [ ] 是否避免 magic number？（定義有意義的常數）
- [ ] 顏色是否使用 `SLColor` 定義？
- [ ] Padding/Spacing 是否使用預定義常數？

### 命名規範
- [ ] 類別名稱是否使用 PascalCase？
- [ ] 變數和方法是否使用 camelCase？
- [ ] 常數是否使用 UPPER_CASE 或 camelCase（Dart 風格）？
- [ ] 檔案名稱是否使用 snake_case？

### 錯誤處理
- [ ] API 呼叫是否有適當的錯誤處理？
- [ ] 是否顯示使用者友善的錯誤訊息？
- [ ] 是否記錄錯誤日誌（使用 `logError()`）？

### 效能考量
- [ ] 是否避免不必要的 rebuild？
- [ ] 長列表是否使用 ListView.builder？
- [ ] 圖片是否適當優化和快取？
- [ ] 是否避免在 build 方法中進行複雜計算？

## 7. 安全性檢查

### OAuth2 流程
- [ ] 是否使用 PKCE（Authorization Code + PKCE）？
- [ ] Token 是否安全儲存（使用 FlutterSecureStorage）？
- [ ] 是否避免在 URL 中傳遞敏感資訊？
- [ ] Refresh token 邏輯是否正確實作？

### API 安全
- [ ] 是否驗證 API 回應？
- [ ] 是否防範 XSS（雖然 Flutter Web 較安全）？
- [ ] 是否避免在日誌中記錄敏感資訊？
- [ ] 是否使用 HTTPS？

### 輸入驗證
- [ ] 使用者輸入是否經過驗證？
- [ ] 是否防範 SQL Injection（使用參數化查詢）？
- [ ] 檔案上傳是否有檔案類型和大小限制？

## 8. 變更政策遵循

### 最小化、漸進式變更
- [ ] **是否只修改必要的部分**？
- [ ] 是否避免「順手重構」？
- [ ] 是否避免修改未相關的檔案？
- [ ] 變更範圍是否清晰可控？

### 風險分析
- [ ] 此變更會影響哪些模組？
- [ ] 是否會破壞現有的 OAuth2 流程？
- [ ] 是否會影響 TaskManager 單例模式？
- [ ] 是否會影響其他頁面的 State 管理？

### 架構一致性
- [ ] 新增程式碼是否遵循現有架構模式？
- [ ] 是否使用專案既有的工具類別和元件？
- [ ] 是否符合 CLAUDE.md 和架構文件規範？

## 9. 測試和文件

### 測試覆蓋
- [ ] 關鍵邏輯是否有單元測試？
- [ ] API 呼叫是否有 Mock 測試？
- [ ] Widget 是否有必要的測試？

### 程式碼註解
- [ ] 複雜邏輯是否有註解說明？
- [ ] 暫時性解決方案是否標記 TODO/FIXME？
- [ ] 公開 API 是否有文件註解？

### 提交訊息
- [ ] Commit 訊息是否清楚描述變更？
- [ ] 是否遵循專案的 commit 訊息規範？

## 10. 專案特定檢查

### 路由管理
- [ ] 是否使用 GoRouter？
- [ ] 路由路徑是否正確定義（不使用 hash）？
- [ ] 是否定義 `ROUTE_NAME` 常數？

### 響應式設計
- [ ] 是否使用 `flutter_screenutil`？
- [ ] 基準解析度是否為 1920×1024？
- [ ] UI 是否在不同螢幕尺寸下測試？

### 部署環境
- [ ] 環境配置是否正確（dev、staging、release）？
- [ ] 環境變數是否從 .env 載入？
- [ ] 是否避免在程式碼中硬編碼環境設定？

---

## 使用建議

1. **審查前**: 先確認變更的檔案類型和架構層級
2. **分類審查**: 根據 State 類型和模組進行分類檢查
3. **優先級**: 先檢查安全性和架構規範，再檢查程式碼品質
4. **工具輔助**: 使用 `flutter analyze` 和 `dart format` 自動檢查
5. **持續改進**: 根據實際問題更新此檢查清單
