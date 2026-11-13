# iOS 程式碼審查檢查清單

本檢查清單適用於 iOS 原生開發（Swift 和 Objective-C；SwiftUI 與 UIKit）。

**建議**：同時參考 [common.md](common.md) 的通用檢查項目。

**語言標註**：
- 🐦 Swift 特定
- 🅾️ Objective-C 特定
- 📱 兩者通用

**先確認專案設定再套用**：最低支援的 iOS 版本（`IPHONEOS_DEPLOYMENT_TARGET`）、Swift 版本與並行檢查等級（`SWIFT_VERSION`、`SWIFT_STRICT_CONCURRENCY`）決定哪些 API 與寫法可用。清單項目與專案設定衝突時，以專案設定為準。

## 1. 架構模式

### MVVM / MVC / TCA / VIPER
- [ ] 📱 是否沿用專案既有的架構模式，沒有在同一個模組混用兩種？
- [ ] 📱 ViewController／View 是否只負責畫面與事件，業務邏輯放在 ViewModel／Service／UseCase？
- [ ] 📱 ViewModel 是否不 import UIKit／SwiftUI 的畫面型別（方便單元測試）？
- [ ] 📱 是否避免 Massive View Controller（單一 ViewController 同時處理網路、解析、導覽）？
- [ ] 📱 導覽邏輯是否集中（Coordinator／Router／NavigationStack 的 path），不散在各畫面？

### 模組與相依
- [ ] 📱 相依方向是否單向（畫面 → 領域 → 資料）？
- [ ] 📱 相依是否透過初始化參數或 protocol 注入，而非在內部直接取 singleton？
- [ ] 📱 新增的第三方套件是否必要，SPM／CocoaPods 的版本是否鎖定？

## 2. 記憶體管理

iOS 用 ARC，審查重點是**循環引用**。

- [ ] 📱 逃逸 closure／block 捕捉 `self` 時，是否用 `[weak self]`／`__weak` 避免循環引用？
  ```swift
  // ✅ 推薦
  service.fetch { [weak self] result in
      guard let self else { return }
      self.apply(result)
  }

  // ❌ 避免：self 持有 service，service 的 closure 又持有 self
  service.fetch { result in
      self.apply(result)
  }
  ```
- [ ] 📱 delegate 屬性是否宣告為 `weak`？
- [ ] 📱 `Timer`、`CADisplayLink`、`NotificationCenter` 的 block 式觀察者，是否在適當時機 invalidate／移除？
- [ ] 🐦 `unowned` 是否只用在確定生命週期不會比對方長的地方？
- [ ] 🐦 `Task { }` 內長時間持有 `self` 時，是否在畫面消失時取消（保存 `Task` 並 `cancel()`，或用 `.task` modifier）？
- [ ] 🅾️ block 屬性是否用 `copy`；block 內是否用 weak–strong dance？
- [ ] 🅾️ Core Foundation 物件是否正確橋接與釋放（`__bridge_transfer`、`CFRelease`）？
- [ ] 📱 大型圖片是否縮圖後再顯示，沒有把原圖整張留在記憶體？

## 3. 並行（Concurrency）

### Swift Concurrency
- [ ] 🐦 更新畫面的程式是否在主執行緒（`@MainActor`、`MainActor.run`）？
- [ ] 🐦 ViewModel／畫面狀態是否標註 `@MainActor`？
- [ ] 🐦 是否使用結構化並行（`async let`、`TaskGroup`），而非散落的 `Task { }`？
- [ ] 🐦 `Task.detached` 是否有必要理由？
- [ ] 🐦 長時間工作是否檢查取消（`Task.checkCancellation()`、`Task.isCancelled`）？
- [ ] 🐦 跨 actor 傳遞的型別是否符合 `Sendable`；`@unchecked Sendable`、`nonisolated(unsafe)` 是否有說明為何安全？
- [ ] 🐦 `withCheckedContinuation` 是否保證每條路徑**剛好 resume 一次**？
- [ ] 🐦 actor 內 `await` 之後是否重新檢查狀態（actor reentrancy：暫停期間狀態可能已被改動）？

### GCD / OperationQueue
- [ ] 📱 是否避免在主執行緒做同步的網路、檔案、資料庫操作？
- [ ] 📱 是否避免 `DispatchQueue.main.sync`（從主執行緒呼叫會死結）？
- [ ] 📱 共用的可變狀態是否有保護（serial queue、lock、actor）？
- [ ] 📱 同一段流程是否避免混用 GCD 與 async/await 造成順序難以推理？

### Combine
- [ ] 🐦 `sink`／`assign` 的訂閱是否存進 `Set<AnyCancellable>`？
- [ ] 🐦 `assign(to:on:)` 指向 `self` 會造成循環引用，是否改用 `assign(to: &$property)` 或 `[weak self]` 的 `sink`？
- [ ] 🐦 更新畫面前是否 `receive(on: DispatchQueue.main)`？

## 4. SwiftUI

- [ ] 🐦 狀態的擁有者是否正確：自己擁有用 `@State`／`@StateObject`，外部傳入用 `@Binding`／`@ObservedObject`？
  ```swift
  // ❌ 避免：每次父層重繪都會重建 ViewModel
  @ObservedObject var viewModel = OrderViewModel()

  // ✅ 推薦
  @StateObject private var viewModel = OrderViewModel()
  ```
- [ ] 🐦 iOS 17 以上使用 `@Observable` 時，是否用 `@State` 持有、`@Bindable` 取得 binding（不再用 `@StateObject`／`@ObservedObject`）？
- [ ] 🐦 `body` 是否沒有副作用（不在 `body` 內發請求、改狀態）？
- [ ] 🐦 非同步載入是否用 `.task`（畫面消失自動取消），而非 `.onAppear` 裡開 `Task`？
- [ ] 🐦 `ForEach` 的 `id` 是否穩定且唯一（不用陣列索引、不用每次重算的 `UUID()`）？
- [ ] 🐦 長列表是否用 `List`／`LazyVStack`？
- [ ] 🐦 `@EnvironmentObject` 是否確定上層有注入（缺少時會在執行期當掉）？
- [ ] 🐦 大型 View 是否拆成小 View，縮小重繪範圍？
- [ ] 🐦 是否避免用 `AnyView` 抹掉型別造成效能問題？

## 5. UIKit

- [ ] 📱 生命週期方法是否呼叫 `super`，工作放在對的時機（`viewDidLoad` 一次性設定、`viewWillAppear` 每次顯示）？
- [ ] 📱 Auto Layout 約束是否完整、沒有衝突（執行時不出現 unsatisfiable constraints 警告）？
- [ ] 📱 `UITableView`／`UICollectionView` 的 cell 是否重用，`prepareForReuse` 是否清掉舊狀態（圖片、非同步工作）？
- [ ] 📱 cell 的非同步圖片載入，是否處理重用後圖片錯位？
- [ ] 📱 列表更新是否用 diffable data source 或正確的 batch update，而非一律 `reloadData`？
- [ ] 📱 是否避免強制解包 `IBOutlet` 以外的 storyboard 取值、是否避免字串硬寫 identifier 散落各處？
- [ ] 📱 鍵盤遮擋、Safe Area、橫直向、Dynamic Type 是否處理？

## 6. Swift 語言最佳實踐

### Optional 與錯誤處理
- [ ] 🐦 是否避免 `!` 強制解包、`try!`、`as!`（僅限程式邏輯保證不會失敗的地方，並有說明）？
- [ ] 🐦 是否用 `guard let` 提早返回，避免巢狀 `if let`？
- [ ] 🐦 `try?` 是否沒有靜默吞掉需要回報的錯誤？
- [ ] 🐦 錯誤是否用具體的 `Error` 型別，使用者看到的訊息是否與內部錯誤分開？

### 型別設計
- [ ] 🐦 資料模型是否優先用 `struct`；需要共享身分或繼承時才用 `class`？
- [ ] 🐦 有限狀態是否用 `enum`，`switch` 是否窮舉（對自家 enum 不加 `default`，新增 case 時編譯器會提醒）？
- [ ] 🐦 存取權限是否最小化（`private`、`fileprivate`、`internal`）？
- [ ] 🐦 `Codable` 是否處理後端欄位缺少、型別不符、未知 enum 值（對照 [common.md](common.md) 的跨服務契約）？
- [ ] 🐦 日期解析是否指定格式、時區與 `Locale(identifier: "en_US_POSIX")`？

## 7. Objective-C 特定最佳實踐

- [ ] 🅾️ 標頭檔是否標註 nullability（`NS_ASSUME_NONNULL_BEGIN`、`nullable`），讓 Swift 橋接出正確的 Optional？
- [ ] 🅾️ 屬性修飾是否正確（`NSString`／block 用 `copy`、delegate 用 `weak`、基本型別用 `assign`）？
- [ ] 🅾️ 集合是否使用泛型標註（`NSArray<NSString *> *`）？
- [ ] 🅾️ 是否記得對 `nil` 發訊息會靜默回傳 0／nil，需要時明確檢查？
- [ ] 🅾️ 錯誤是否用 `NSError **` 回報並檢查回傳值，而非用例外控制流程？
- [ ] 📱 Swift 與 Objective-C 混編時，bridging header 與 `@objc` 暴露的範圍是否最小？

## 8. 資料持久化

- [ ] 📱 密碼、token 等敏感資料是否存 Keychain，而非 `UserDefaults` 或明文檔案？
- [ ] 📱 `UserDefaults` 是否只放小量設定，key 是否集中定義？
- [ ] 📱 Core Data 的 `NSManagedObject` 是否只在所屬 context 的佇列上使用（`perform`／`performAndWait`）？
- [ ] 📱 Core Data／SwiftData 的 schema 變更是否有 migration？
- [ ] 🐦 SwiftData 的 `ModelContext` 是否沒有跨 actor 傳遞？
- [ ] 📱 檔案是否放對目錄（Documents 會備份、Caches 可被系統清除、tmp 暫存）？

## 9. 網路層

- [ ] 📱 是否使用 HTTPS，`Info.plist` 是否沒有放寬 ATS（`NSAllowsArbitraryLoads`）？
- [ ] 📱 是否檢查 HTTP 狀態碼，而不只看有沒有 `error`？
- [ ] 📱 逾時、離線、取消是否各自處理？
- [ ] 📱 token 更新是否避免多個請求同時觸發重複 refresh？
- [ ] 📱 Request／Response 的解析錯誤是否有記錄並回報，而非靜默顯示空畫面？
- [ ] 📱 分頁、重試是否有上限？

## 10. 效能

- [ ] 📱 主執行緒是否沒有耗時工作（圖片解碼、大量 JSON 解析、同步 I/O）？
- [ ] 📱 列表捲動是否流暢（cell 內沒有同步載圖、沒有離屏渲染的陰影與圓角濫用）？
- [ ] 📱 App 啟動時的初始化是否延後或非同步？
- [ ] 📱 `DateFormatter`、`NumberFormatter` 等昂貴物件是否重用？
- [ ] 📱 背景工作是否用對 API（`BGTaskScheduler`、背景 URLSession），並在時限內結束？

## 11. 安全性與隱私

- [ ] 📱 API key、憑證是否沒有寫死在程式或進版控（用 xcconfig／CI 變數）？
- [ ] 📱 Log 是否沒有輸出 token、個資（`os_log` 的隱私標註、Release 不印敏感資料）？
- [ ] 📱 用到相機、定位、相簿、追蹤等權限時，`Info.plist` 是否有對應的用途說明字串（缺少會在執行期當掉或被審核退件）？
- [ ] 📱 新增或更新的第三方 SDK，是否檢查 Privacy Manifest（`PrivacyInfo.xcprivacy`）與 required reason API 的宣告？
- [ ] 📱 Universal Link／URL Scheme 傳入的參數是否驗證？
- [ ] 📱 `WKWebView` 是否限制可載入的網域、注入的 JavaScript 是否必要？
- [ ] 📱 高安全性需求是否有 Certificate Pinning？

## 12. 在地化與無障礙

- [ ] 📱 使用者看得到的字串是否走在地化（String Catalog／`NSLocalizedString`），沒有寫死？
- [ ] 📱 日期、數字、金額是否用 Formatter 依地區格式化？
- [ ] 📱 可互動元件是否有 accessibility label，VoiceOver 的閱讀順序是否合理？
- [ ] 📱 是否支援 Dynamic Type 與深色模式（顏色用 asset catalog 或語意顏色）？

## 13. 測試

- [ ] 📱 ViewModel、Service 的邏輯是否有單元測試（XCTest 或 Swift Testing）？
- [ ] 📱 網路與時間相依是否透過 protocol 替換，測試不打真實 API？
- [ ] 🐦 非同步測試是否用 `async` 測試函式或 expectation，而非 `sleep`？
- [ ] 📱 關鍵流程是否有 UI 測試（XCUITest），元件是否有 accessibility identifier？

## 14. 專案設定與版本控制

- [ ] 📱 `project.pbxproj` 的變更是否只包含這次需要的檔案與設定（沒有夾帶無關的重排）？
- [ ] 📱 Signing、Bundle ID、Entitlements 的變更是否是這次需求要的？
- [ ] 📱 Build Configuration／Scheme 是否區分環境，沒有把測試環境網址帶進 Release？
- [ ] 📱 `Package.resolved`／`Podfile.lock` 是否隨相依變更一起提交？
- [ ] 📱 是否沒有提交 `xcuserdata/`、`DerivedData/`、`.DS_Store`？

---

## 使用建議

1. **與通用檢查清單結合**：
   - 先檢查 [common.md](common.md) 的安全性和程式碼品質
   - 再檢查本檢查清單的 iOS 特定項目

2. **優先級**：
   - 🔴 Critical: 循環引用造成的記憶體洩漏、主執行緒阻塞或非主執行緒更新畫面、data race、強制解包造成當機、敏感資料存放不當、缺少權限用途說明
   - 🟡 Warning: 架構不清晰、缺少測試、狀態擁有者用錯、效能問題
   - 🟢 Suggestion: 程式碼風格、Swift 慣用法

3. **工具輔助**：
   - Xcode 的編譯警告與 Swift 並行檢查
   - Instruments（Leaks、Allocations、Time Profiler）、Memory Graph Debugger
   - Thread Sanitizer、Main Thread Checker
   - SwiftLint、SwiftFormat（專案有設定時）

4. **學習資源**：
   - Apple Developer Documentation
   - The Swift Programming Language（swift.org）
   - Swift Evolution 提案（查某個語言功能從哪一版開始）
