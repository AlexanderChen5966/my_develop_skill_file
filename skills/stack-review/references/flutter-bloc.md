# Flutter + Bloc 程式碼審查檢查清單

本檢查清單專為使用 Bloc 狀態管理的 Flutter 專案設計。

**建議**：同時參考 [common.md](common.md) 的通用檢查項目。

## 1. Bloc 架構

### Bloc 層級結構
- [ ] 專案是否遵循 Bloc 架構模式（Bloc/Cubit - Event - State）？
- [ ] Bloc 是否只包含業務邏輯（不包含 UI 邏輯）？
- [ ] Bloc 是否使用 `Bloc` 類別（複雜邏輯）或 `Cubit` 類別（簡單邏輯）？

### Bloc 定義
- [ ] Bloc 是否繼承 `Bloc<Event, State>`？
- [ ] Cubit 是否繼承 `Cubit<State>`？
- [ ] 是否正確定義初始狀態（`super(initialState)`）？
- [ ] 是否使用 `on<Event>()` 註冊事件處理器？

### Event 設計
- [ ] Event 是否為不可變（immutable）類別？
- [ ] Event 是否使用 `sealed class` 或抽象類別？
- [ ] Event 命名是否清晰且使用過去式/祈使式（如 `UserLoggedIn`、`LoadUser`）？
- [ ] Event 是否只包含必要的資料？

### State 設計
- [ ] State 是否為不可變（immutable）類別？
- [ ] State 是否使用 `sealed class` 或抽象類別？
- [ ] State 是否清楚表示不同狀態（Initial/Loading/Success/Error）？
- [ ] State 是否使用 `Equatable` 或 `freezed` 套件？
- [ ] State 比較是否正確（避免不必要的 rebuild）？

## 2. Bloc 使用模式

### BlocProvider
- [ ] Bloc 是否透過 `BlocProvider` 提供？
- [ ] Provider 的層級是否適當（避免過高或過低）？
- [ ] 是否使用 `MultiBlocProvider` 管理多個 Bloc？
- [ ] 是否在不再需要時正確 dispose Bloc？

### BlocBuilder vs BlocListener vs BlocConsumer
- [ ] **BlocBuilder** 是否用於根據狀態建立 UI？
- [ ] **BlocListener** 是否用於執行副作用（導航、顯示 Snackbar）？
- [ ] **BlocConsumer** 是否用於同時需要建立 UI 和執行副作用？
- [ ] `buildWhen` 和 `listenWhen` 是否適當使用以優化效能？

### Context 使用
- [ ] 是否使用 `context.read<Bloc>()` 觸發事件？
- [ ] 是否使用 `context.watch<Bloc>()` 監聽狀態變化？
- [ ] 是否避免在 `build` 方法中使用 `context.read()`？

## 3. 事件處理

### Event Handler
- [ ] Event handler 是否為非同步（`on<Event>((event, emit) async {...})`）？
- [ ] 是否使用 `emit()` 發送新狀態？
- [ ] 是否避免在 handler 之外呼叫 `emit()`？
- [ ] 長時間運行的操作是否適當處理？

### Error Handling
- [ ] 異常是否被 `try-catch` 捕獲並發送錯誤狀態？
- [ ] 是否使用 `BlocObserver` 集中處理錯誤日誌？
- [ ] 錯誤訊息是否對使用者友善？

### Transformer
- [ ] 是否使用 `debounceTime` 防止重複事件（如搜尋）？
- [ ] 是否使用 `throttleTime` 限制事件頻率？
- [ ] 是否使用 `bloc_concurrency` 套件處理併發事件？

## 4. 依賴注入

### Repository Pattern
- [ ] Bloc 是否透過建構子接收 Repository？
- [ ] Repository 是否處理資料層邏輯（API、Database）？
- [ ] Bloc 是否不直接呼叫 API？

### Service Locator (GetIt)
- [ ] 是否使用 GetIt 或其他 DI 工具？
- [ ] Bloc 和 Repository 是否正確註冊？
- [ ] 是否避免在 Bloc 中使用 `GetIt.instance`（優先建構子注入）？

## 5. 測試

### Bloc 測試
- [ ] 是否使用 `bloc_test` 套件？
- [ ] 是否測試所有重要的事件和狀態轉換？
- [ ] Mock Repository 是否正確設定？
- [ ] 測試是否涵蓋錯誤情況？

### 測試範例
```dart
blocTest<UserBloc, UserState>(
  'emits [Loading, Success] when LoadUser is added',
  build: () => UserBloc(repository: mockRepository),
  act: (bloc) => bloc.add(LoadUser()),
  expect: () => [
    UserLoading(),
    UserSuccess(user),
  ],
);
```

## 6. 效能優化

### 避免過度 Rebuild
- [ ] 是否使用 `buildWhen` 過濾不必要的 rebuild？
- [ ] State 比較是否正確實作（Equatable/freezed）？
- [ ] 是否避免在 Bloc 中包含 UI 相關邏輯？

### Bloc 生命週期
- [ ] Bloc 是否在適當的位置 dispose？
- [ ] 是否避免記憶體洩漏（取消訂閱、關閉 Stream）？
- [ ] 長時間運行的 Stream 是否正確取消？

## 7. Hydrated Bloc（狀態持久化）

### 使用 Hydrated Bloc
- [ ] 是否正確初始化 `HydratedBloc.storage`？
- [ ] Bloc 是否繼承 `HydratedBloc` 或 `HydratedCubit`？
- [ ] `fromJson` 和 `toJson` 是否正確實作？
- [ ] 敏感資料是否避免持久化？

## 8. Flutter 通用檢查

### Widget 樹
- [ ] 是否使用 `const` 建構子優化效能？
- [ ] 是否避免在 `build` 方法中進行複雜計算？
- [ ] 是否適當使用 `ListView.builder` 處理長列表？

### 響應式設計
- [ ] UI 是否適應不同螢幕尺寸？
- [ ] 是否使用 `MediaQuery` 或 `LayoutBuilder`？

### 路由
- [ ] 路由是否使用 `go_router` 或類似套件？
- [ ] 深層連結是否正確處理？

## 9. 專案結構

### 目錄組織
```
lib/
├── core/
│   ├── di/              # 依賴注入
│   ├── error/           # 錯誤處理
│   └── utils/           # 工具函數
├── features/
│   └── user/
│       ├── data/
│       │   ├── models/
│       │   └── repositories/
│       ├── domain/
│       │   ├── entities/
│       │   └── repositories/
│       └── presentation/
│           ├── bloc/
│           ├── pages/
│           └── widgets/
```

- [ ] 是否遵循功能模組化結構？
- [ ] 是否分離 Data、Domain、Presentation 層？

## 10. 常見錯誤檢查

### Anti-Patterns
- [ ] **是否避免在 UI 中直接處理業務邏輯**？
- [ ] **是否避免在 Bloc 中處理 UI 邏輯（導航、顯示對話框）**？
- [ ] **是否避免在 Bloc 中使用 BuildContext**？
- [ ] **是否避免 Bloc 之間直接通信**（使用事件或 Stream）？
- [ ] **是否避免在 Event Handler 外使用 `emit()`**？

### 狀態管理問題
- [ ] 是否避免將整個物件作為 State（使用不可變的 State）？
- [ ] 是否避免多個 Bloc 共享可變狀態？
- [ ] 是否避免在 Bloc 中保存 Widget 引用？

---

## 使用建議

1. **與通用檢查清單結合**：
   - 先檢查 [common.md](common.md) 的安全性和程式碼品質
   - 再檢查本檢查清單的 Bloc 特定項目

2. **優先級**：
   - 🔴 Critical: Bloc 中包含 BuildContext、狀態洩漏
   - 🟡 Warning: 不當的 Provider 層級、缺少錯誤處理
   - 🟢 Suggestion: 測試覆蓋、效能優化

3. **工具輔助**：
   - 使用 `flutter analyze` 檢查程式碼
   - 使用 `very_good_analysis` 或 `lint` 套件
   - 使用 `bloc_test` 進行測試

4. **學習資源**：
   - Bloc官方文件：https://bloclibrary.dev
   - Bloc 架構教學
   - Flutter 官方文件