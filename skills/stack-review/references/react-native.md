# React Native 程式碼審查檢查清單

本檢查清單適用於 React Native 開發（含 Expo；TypeScript 與 JavaScript）。

**建議**：同時參考 [common.md](common.md) 的通用檢查項目。

**標註**：
- ⚛️ React／React Native 通用
- 🧭 Expo 特定
- 🔩 原生層（`android/`、`ios/`）

**先確認專案設定再套用**：`package.json` 的 React Native 與 Expo SDK 版本、是否啟用 New Architecture、Expo 是 managed 還是有 `android/`／`ios/` 的 prebuild／bare 專案，決定哪些 API 與套件可用。Expo SDK 會綁定 React Native 與各 `expo-*` 套件的版本，清單項目與專案設定衝突時，以專案設定為準。

## 1. 架構與專案結構

- [ ] ⚛️ 是否沿用專案既有的資料夾分層（畫面、元件、API、store、utils），沒有另開一套？
- [ ] ⚛️ 畫面元件是否只負責顯示與事件，API 呼叫與業務邏輯放在 hook／service／store？
- [ ] ⚛️ 共用元件是否不直接相依特定畫面的 store 或路由？
- [ ] ⚛️ 環境設定（API 網址、金鑰）是否集中管理，沒有散在各檔案？
- [ ] ⚛️ 新增的套件是否必要、是否仍在維護、是否支援專案的 RN 版本與架構？

## 2. 元件與 Hooks

- [ ] ⚛️ Hooks 是否只在元件或自訂 hook 的最上層呼叫（不在條件、迴圈、巢狀函式內）？
- [ ] ⚛️ `useEffect`／`useMemo`／`useCallback` 的相依陣列是否完整（`react-hooks/exhaustive-deps` 沒有被關掉）？
- [ ] ⚛️ `useEffect` 是否有清理函式（訂閱、計時器、事件監聽、AppState、鍵盤、定位）？
  ```tsx
  // ✅ 推薦
  useEffect(() => {
    const sub = AppState.addEventListener('change', onChange);
    return () => sub.remove();
  }, [onChange]);

  // ❌ 避免：沒有移除監聽，離開畫面後仍會觸發
  useEffect(() => {
    AppState.addEventListener('change', onChange);
  }, []);
  ```
- [ ] ⚛️ 非同步結果回來時，是否處理元件已卸載或請求已過期（AbortController、旗標、請求序號）？
- [ ] ⚛️ 是否避免用 `useEffect` 同步「可以直接從 props／state 算出來」的值？
- [ ] ⚛️ 列表的 `key` 是否穩定且唯一（不用陣列索引）？
- [ ] ⚛️ 元件是否沒有在 render 內定義另一個元件（每次 render 都會重新掛載）？

## 3. 狀態管理

- [ ] ⚛️ 狀態是否放在最小需要的範圍（區域狀態用 `useState`，跨畫面才進全域 store）？
- [ ] ⚛️ 是否沒有重複儲存可推導的狀態？
- [ ] ⚛️ zustand／Redux 是否用 selector 只訂閱需要的欄位，避免整個 store 變動就重繪？
  ```tsx
  // ✅ 推薦
  const userName = useUserStore((s) => s.user.name);

  // ❌ 避免：store 任何欄位變動都會重繪
  const { user } = useUserStore();
  ```
- [ ] ⚛️ selector 回傳新物件或陣列時，是否用淺比較（zustand 的 `useShallow`）避免無限重繪？
- [ ] ⚛️ 狀態更新是否不可變（不直接改陣列或物件）？
- [ ] ⚛️ 登出或切換帳號時，全域 store 與快取是否重置？
- [ ] ⚛️ 伺服器資料是否與畫面狀態分開（有 TanStack Query 等工具時交給它管快取與重新抓取）？

## 4. 導覽（React Navigation / Expo Router）

- [ ] ⚛️ 路由參數是否有型別，是否只傳可序列化的小資料（id），不傳整個物件或函式？
- [ ] ⚛️ 需要登入的畫面是否有守門，登出後是否清掉導覽堆疊？
- [ ] ⚛️ 畫面回到前景要重新整理時，是否用 focus 事件（`useFocusEffect`），而非只靠 `useEffect`（切換分頁時畫面不會卸載）？
- [ ] ⚛️ Android 實體返回鍵的行為是否正確？
- [ ] ⚛️ Deep Link／推播點擊傳入的參數是否驗證後才導頁？
- [ ] 🧭 Expo Router 的檔案路由：新增的檔名、`_layout`、路由群組 `(group)` 是否符合既有結構；`app/` 內是否沒有放非路由的檔案？

## 5. 樣式與版面

- [ ] ⚛️ 樣式是否沿用專案做法（`StyleSheet.create`、NativeWind 等），沒有混用新的方案？
- [ ] ⚛️ 是否避免在 render 內建立大量 inline style 物件（列表項目尤其要注意）？
- [ ] ⚛️ 是否處理 Safe Area（`react-native-safe-area-context`）與鍵盤遮擋（`KeyboardAvoidingView` 在 iOS／Android 行為不同）？
- [ ] ⚛️ 是否考慮不同螢幕尺寸與系統字級放大，沒有寫死會被截斷的寬高？
- [ ] ⚛️ `Platform.OS`／`Platform.select` 的平台分支，兩個平台是否都有處理？
- [ ] ⚛️ 文字是否都包在 `<Text>` 內（裸字串在原生平台會當掉）；條件渲染是否避免 `{count && <View/>}` 在 `count` 為 0 時印出 0？
- [ ] ⚛️ 可點擊區域是否夠大（`hitSlop`），是否有按下回饋？

## 6. 列表與效能

- [ ] ⚛️ 長列表是否用 `FlatList`／`SectionList`／FlashList，而非 `ScrollView` 加 `map`？
- [ ] ⚛️ `FlatList` 是否提供穩定的 `keyExtractor`，`renderItem` 是否穩定（`useCallback`）、列表項目是否 `React.memo`？
- [ ] ⚛️ 是否沒有把 `FlatList` 放進同方向的 `ScrollView`（虛擬化會失效）？
- [ ] ⚛️ 圖片是否指定尺寸、使用適當解析度與快取？
- [ ] ⚛️ 耗時計算是否避開 render（`useMemo`）或移出 JS 主執行緒？
- [ ] ⚛️ 動畫是否跑在 UI 執行緒（Reanimated worklet，或 `Animated` 的 `useNativeDriver: true`）？
- [ ] ⚛️ Reanimated worklet 內是否只用可在 UI 執行緒執行的東西，回呼 JS 是否經 `runOnJS`？
- [ ] ⚛️ Release 版是否移除或關閉 `console.log`（大量輸出會拖慢 JS 執行緒）？
- [ ] ⚛️ 套件是否按需匯入，沒有整包匯入大型函式庫？

## 7. 網路與資料

- [ ] ⚛️ API 呼叫是否走專案共用的 client（統一 base URL、header、逾時、錯誤格式）？
- [ ] ⚛️ 401／token 過期是否集中處理，是否避免多個請求同時觸發重複 refresh？
- [ ] ⚛️ 載入中、失敗、空資料三種狀態是否都有畫面？
- [ ] ⚛️ 離線與弱網路是否處理（行動裝置常態），重試是否有上限？
- [ ] ⚛️ 後端回應是否處理欄位缺少、`null`、未知 enum 值（對照 [common.md](common.md) 的跨服務契約）？
- [ ] ⚛️ 日期字串是否用明確格式解析（`new Date('yyyy-MM-dd HH:mm:ss')` 在不同 JS 引擎結果不同）？
- [ ] ⚛️ 重複送出是否有防護（按鈕停用、請求去重）？

## 8. 儲存與安全性

- [ ] ⚛️ token、密碼等敏感資料是否存在安全儲存（Keychain／Keystore，例如 `expo-secure-store`、`react-native-keychain`），而非 AsyncStorage（未加密）？
- [ ] ⚛️ AsyncStorage 的 key 是否集中定義，讀出的 JSON 是否處理解析失敗與舊版格式？
- [ ] ⚛️ 是否記得**打包進 JS bundle 的內容都能被取出**：密鑰、私有 API key 不可寫在程式或 `EXPO_PUBLIC_*`／`extra` 設定裡？
- [ ] ⚛️ Log、錯誤回報是否沒有輸出 token 與個資？
- [ ] ⚛️ `WebView` 是否限制可載入的來源，`onMessage` 收到的資料是否驗證？
- [ ] ⚛️ 是否全程 HTTPS；Android 的 cleartext、iOS 的 ATS 是否沒有為了方便而放寬？

## 9. 原生層與權限

- [ ] 🔩 用到相機、定位、相簿、通知等功能時，兩個平台的權限宣告是否都有（iOS `Info.plist` 的用途說明、Android `AndroidManifest.xml`）；Expo 專案是否寫在 `app.json`／`app.config.js`？
- [ ] 🔩 執行期是否先檢查並請求權限，使用者拒絕時是否有對應畫面？
- [ ] 🔩 背景定位、背景工作、前景服務的宣告與使用，是否符合兩個平台的規定與商店審核要求？
- [ ] 🔩 新增含原生程式的套件後，是否需要重新建置原生 App（不能只靠 JS 更新）？
- [ ] 🔩 `android/`、`ios/` 的變更是否是這次需求要的；prebuild 產生的專案，手改內容是否會被下次 prebuild 蓋掉（應改用 config plugin）？
- [ ] 🔩 `patch-package` 的 patch 是否對應目前鎖定的套件版本，升級套件時是否一併檢查？
- [ ] 🔩 推播（FCM／APNs）的 token 更新、前景與背景訊息、點擊導頁是否都處理？

## 10. Expo 特定

- [ ] 🧭 `expo-*` 套件版本是否與 Expo SDK 相容（用 `npx expo install` 安裝、`npx expo-doctor` 檢查）？
- [ ] 🧭 `app.json`／`app.config.js` 的變更（版本號、權限、plugins、scheme）是否是這次需求要的？
- [ ] 🧭 **OTA 更新（`expo-updates`）只能更新 JS 與資源**：這次變更若動到原生程式、原生相依或權限，是否改走商店發版並更新 runtime version，避免把不相容的 JS 推給舊版原生 App？
- [ ] 🧭 更新頻道（channel）與環境的對應是否正確，沒有把測試環境的更新推到正式頻道？
- [ ] 🧭 `eas.json` 的 build profile 與環境變數是否區分環境？

## 11. TypeScript 與程式品質

- [ ] ⚛️ 是否避免 `any`、非空斷言 `!`、`as` 強制轉型蓋掉真正的型別問題？
- [ ] ⚛️ API 回應、路由參數、store 是否有型別？
- [ ] ⚛️ 元件 props 是否有型別，選填 props 是否有預設值？
- [ ] ⚛️ 是否通過專案的 ESLint 與 Prettier 設定，沒有新增 `eslint-disable`（有的話是否附理由）？
- [ ] ⚛️ `Promise` 是否都有處理失敗（沒有未處理的 rejection）？

## 12. 在地化與無障礙

- [ ] ⚛️ 使用者看得到的字串是否走 i18n（例如 i18next），所有語系檔是否都補上新 key？
- [ ] ⚛️ 日期、數字、金額是否依地區格式化，時區是否正確？
- [ ] ⚛️ 可互動元件是否有 `accessibilityLabel` 與 `accessibilityRole`？

## 13. 測試

- [ ] ⚛️ 業務邏輯、hook、store 是否有單元測試（Jest）？
- [ ] ⚛️ 元件測試是否用 React Native Testing Library，以使用者看得到的內容查詢，而非實作細節？
- [ ] ⚛️ 原生模組、導覽、計時器是否正確 mock？
- [ ] ⚛️ 關鍵流程（登入、主要作業）是否有端對端測試或手動驗證紀錄，**iOS 與 Android 都要驗**？

---

## 使用建議

1. **與通用檢查清單結合**：
   - 先檢查 [common.md](common.md) 的安全性和程式碼品質
   - 再檢查本檢查清單的 React Native 特定項目
   - 變更含 `android/` 或 `ios/` 的原生程式時，加看 [android.md](android.md) 或 [ios.md](ios.md)

2. **優先級**：
   - 🔴 Critical: 敏感資料存在 AsyncStorage 或打包進 bundle、缺少權限宣告造成當機、OTA 更新與原生版本不相容、未清理的監聽造成洩漏、裸字串等會當機的寫法
   - 🟡 Warning: 相依陣列不完整、列表效能、狀態重複、缺少測試、只驗了一個平台
   - 🟢 Suggestion: 程式碼風格、型別收緊、元件拆分

3. **工具輔助**：
   - ESLint（`eslint-plugin-react-hooks`、`eslint-plugin-react-native`）、TypeScript
   - React DevTools 的 Profiler、React Native DevTools
   - `npx expo-doctor`（Expo 專案）
   - Xcode Instruments、Android Studio Profiler（原生層效能與記憶體）

4. **學習資源**：
   - React Native 官方文件（reactnative.dev）
   - Expo 官方文件（docs.expo.dev）
   - React 官方文件（react.dev）
