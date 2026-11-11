# React Web 程式碼審查檢查清單

本檢查清單適用於瀏覽器上的 React（含 Next.js App Router／Pages Router、Vite；TypeScript 與 JavaScript）。React Native 用 [react-native.md](react-native.md)。

**建議**：同時參考 [common.md](common.md) 的通用檢查項目。

**標註**：
- ⚛️ React 通用
- ▲ Next.js 特定
- 🔁 從其他前端（例如 Flutter Web）遷移過來的頁面

**先確認專案設定再套用**：`package.json` 的 React、Next.js 版本與 lock 檔實際版本；用 App Router 還是 Pages Router；是否 `output: 'export'`（純靜態，沒有伺服器端功能）；資料層用什麼（TanStack Query、SWR、zustand、Redux）；UI 元件庫（antd、Radix、自家 design system）與樣式方案（Tailwind、CSS Modules）。清單項目與專案設定衝突時，以專案設定為準。

## 1. 架構與專案結構

- [ ] ⚛️ 是否沿用專案既有的分層（頁面、元件、API client、hooks、store、design system），沒有另開一套？
- [ ] ⚛️ 頁面元件是否只負責組合與事件，API 呼叫與資料轉換放在 API 層或 hook？
- [ ] ⚛️ 共用元件（design system）是否沒有相依特定頁面的 store、路由或 API？
- [ ] ⚛️ 改到共用元件或共用 API client 時，是否列出所有使用者並確認其他頁面行為不變？
- [ ] ⚛️ 環境設定是否集中管理；新增的套件是否必要、仍在維護、支援專案的 React／Next 版本？

## 2. 元件與 Hooks

- [ ] ⚛️ Hooks 是否只在元件或自訂 hook 的最上層呼叫？
- [ ] ⚛️ `useEffect`／`useMemo`／`useCallback` 的相依陣列是否完整（`react-hooks/exhaustive-deps` 沒有被關掉或用 disable 註解跳過）？
- [ ] ⚛️ `useEffect` 是否有清理函式（事件監聽、計時器、訂閱、`AbortController`）？
- [ ] ⚛️ 是否避免用 `useEffect` 同步「可以直接從 props／state 算出來」的值？
- [ ] ⚛️ 非同步結果回來時，是否處理元件已卸載或請求已過期（舊請求晚回來蓋掉新結果）？
- [ ] ⚛️ 列表的 `key` 是否穩定且唯一（不用陣列索引，除非列表永遠不會重排或增刪）？
- [ ] ⚛️ 是否沒有在 render 內定義另一個元件？
- [ ] ⚛️ 條件渲染是否避免 `{count && <X/>}` 在 `count` 為 0 時印出 0？
- [ ] ⚛️ 受控與非受控元件是否沒有混用（`value` 從 `undefined` 變成有值會出警告並失控）？

## 3. 伺服器狀態（TanStack Query／SWR）

- [ ] ⚛️ query key 是否包含所有影響結果的參數（篩選、排序、分頁、公司／使用者），沒有漏掉造成快取串資料？
- [ ] ⚛️ 用 `placeholderData: keepPreviousData`（或同類設定）時，畫面與動作是否會誤用「上一組條件的舊資料」？例如匯出、計數、按鈕可用與否要看 `isPlaceholderData`
- [ ] ⚛️ 新增／編輯／刪除後是否 invalidate 正確的 key，沒有過度 invalidate 整個快取？
- [ ] ⚛️ `enabled` 條件是否正確（必要參數還沒有時不打 API）？
- [ ] ⚛️ 錯誤是否有畫面，且不會被 retry 預設值（3 次）拖慢或重複打寫入 API？
- [ ] ⚛️ 登出或切換公司時，快取與全域 store 是否清掉，不會短暫顯示上一個身分的資料？

## 4. 用戶端狀態（zustand／Redux／Context）

- [ ] ⚛️ 狀態是否放在最小需要的範圍；伺服器資料不重複存進 store？
- [ ] ⚛️ selector 是否只訂閱需要的欄位；回傳新物件或陣列時是否用淺比較（zustand 的 `useShallow`）？
- [ ] ⚛️ 狀態更新是否不可變？
- [ ] ⚛️ Context 的 value 是否穩定（每次 render 建新物件會讓所有消費者重繪）？
- [ ] ⚛️ 存進 `localStorage`／`sessionStorage` 的資料：key 是否集中定義、讀取時是否處理解析失敗與舊格式、是否沒有放 token 以外不該放的個資？

## 5. 路由與權限

- [ ] ⚛️ 需要登入的頁面是否有守門；權限不足時是隱藏入口還是擋整頁，是否和專案既有慣例一致？
- [ ] ⚛️ 前端權限判斷是否只當體驗層，真正的防護在後端？
- [ ] ⚛️ URL 參數（query string、動態路由）是否驗證後才使用？
- [ ] ⚛️ 篩選、分頁是否需要反映在 URL（重新整理或分享連結後狀態要保留時）？
- [ ] ▲ App Router：`'use client'` 是否只加在需要的元件，沒有把整棵樹變成 client component？
- [ ] ▲ App Router：`layout`／`page`／`loading`／`error` 的檔案位置是否符合既有結構？
- [ ] ▲ 用 `next/navigation`（App Router）還是 `next/router`（Pages Router）是否和專案一致？
- [ ] ▲ `output: 'export'` 的專案是否沒有用到需要伺服器的功能（Server Actions、`cookies()`、動態 route handler、ISR）？
- [ ] 🔁 兩套前端並存時：跳轉到另一套的連結（整頁跳轉 vs `<Link>`）是否照路由對照表，登入狀態是否能延續？

## 6. Next.js 伺服器端（有用到時）

- [ ] ▲ Server Component 是否沒有使用瀏覽器 API、事件處理、client hooks？
- [ ] ▲ 傳給 Client Component 的 props 是否可序列化，且沒有夾帶不該給前端的欄位？
- [ ] ▲ 只能在伺服器端用的程式（含密鑰）是否標 `server-only` 或放在 server 檔案，不會被打包進 client？
- [ ] ▲ `fetch` 的快取行為（`cache`、`revalidate`）是否符合預期；依版本確認預設值（Next 14 與 15 不同）？
- [ ] ▲ Server Actions 是否驗證輸入並檢查權限（它是公開的 POST 端點）？
- [ ] ▲ 是否處理 hydration 不一致（render 時用 `Date.now()`、`Math.random()`、`window`、使用者時區）？

## 7. 網路與資料

- [ ] ⚛️ API 呼叫是否走專案共用的 client（base URL、header、逾時、錯誤格式、欄位命名轉換）？
- [ ] ⚛️ 401／token 過期是否集中處理，同時多個請求是否只觸發一次 refresh？
- [ ] ⚛️ 載入中、失敗、空資料三種狀態是否都有畫面，且和專案既有頁面一致？
- [ ] ⚛️ 後端回應是否處理欄位缺少、`null`、未知 enum 值（對照 [common.md](common.md) 的跨服務契約）？
- [ ] ⚛️ 分頁、排序是由後端做還是前端做，是否和後端端點的實際行為一致（有些端點要全抓再於前端分頁）？
- [ ] ⚛️ 日期與時區：解析是否用明確格式，顯示是否用專案統一的格式與時區？
- [ ] ⚛️ 下載檔案（Excel、CSV）是否處理錯誤回應（後端回 JSON 錯誤卻被當成檔案存下）與檔名編碼？
- [ ] ⚛️ 重複送出是否有防護（按鈕停用、請求去重）？

## 8. 樣式、版面與 UI 一致性

- [ ] ⚛️ 是否沿用專案的樣式方案與 design token（顏色、字級、間距），沒有寫死新的色碼或尺寸？
- [ ] ⚛️ UI 元件庫（antd、Radix 等）的用法是否和既有頁面一致，沒有同時引進第二套？
- [ ] ⚛️ 版面在專案的基準解析度與最小寬度下是否不跑版；超寬內容是捲動還是換行，和既有頁面一致？
- [ ] ⚛️ 字型是否和設計一致（字型檔是否載入、fallback 是否會改變行高與寬度）？
- [ ] 🔁 遷移頁面：是否和舊版並排比對過（有 `flutter-ui-compare` 時照它做），包含頁面外框（標題列、側選單）、hover、停用、tooltip、空狀態？
- [ ] 🔁 遷移頁面：文案、欄位順序、數字與日期格式、排序預設值是否和舊版一致？

## 9. 效能

- [ ] ⚛️ 大型列表是否分頁或虛擬化？
- [ ] ⚛️ 耗時計算是否避開每次 render（`useMemo`），且只在真的有成本時才用？
- [ ] ⚛️ 大型套件是否按需匯入或動態載入（`next/dynamic`、`React.lazy`）？
- [ ] ⚛️ 圖片是否指定尺寸（▲ 用 `next/image` 時是否設定 `sizes`／遠端網域）？
- [ ] ⚛️ Production 是否沒有留下大量 `console.log`？

## 10. 安全性

- [ ] ⚛️ 是否沒有 `dangerouslySetInnerHTML` 渲染未消毒的內容？
- [ ] ⚛️ 是否記得**打包進前端的內容都看得到**：密鑰不可寫在程式或 `NEXT_PUBLIC_*`／`VITE_*` 環境變數？
- [ ] ⚛️ token 存放位置是否符合專案既有做法；有 XSS 風險時不要擴大能讀到 token 的範圍？
- [ ] ⚛️ 外部連結 `target="_blank"` 是否有 `rel="noopener noreferrer"`？
- [ ] ⚛️ Log、錯誤回報、匯出的檔案是否沒有輸出 token 與不該有的個資？

## 11. TypeScript 與程式品質

- [ ] ⚛️ 是否沒有新增 `any`、`as` 強制轉型、`@ts-ignore` 來壓錯誤？
- [ ] ⚛️ API 回應型別是否和後端實際格式一致（欄位名稱轉換後的名稱，而非 wire 上的名稱）？
- [ ] ⚛️ ESLint、TypeScript、build 是否都通過，沒有用關掉規則的方式過關？

## 12. 在地化與無障礙

- [ ] ⚛️ 使用者看得到的文字是否走專案的多語系機制，沒有寫死？
- [ ] ⚛️ 可點擊元素是否是 `<button>`／`<a>`，而不是加了 `onClick` 的 `<div>`？
- [ ] ⚛️ 表單欄位是否有 label，對話框是否處理焦點與 Esc 關閉？

## 13. 測試

- [ ] ⚛️ 新的邏輯（資料轉換、權限判斷、篩選條件組裝）是否有單元測試？
- [ ] ⚛️ API 串接是否用 MSW 等工具測到 client 的實際行為（含錯誤與 401），而不是只測純函式？
- [ ] ⚛️ 測試資料的格式是否照後端實際回應（例如分頁結構、欄位名稱），不是憑印象寫？
- [ ] ⚛️ 測試是否測行為（使用者看到什麼、按了會怎樣），不測實作細節？

## 使用建議

1. **審查順序**：先看第 1、3、5、7 節（架構、伺服器狀態、權限、資料），這些錯了會影響資料正確性；再看樣式與效能。

2. **優先級**：
   - 🔴 Critical: 密鑰打包進前端、XSS、權限只靠前端、query key 漏參數造成串資料、舊資料被當成新條件的結果使用、改壞共用元件影響其他頁面
   - 🟡 Warning: 相依陣列不完整、載入／錯誤／空狀態缺漏、遷移頁面和舊版不一致、缺少測試
   - 🟢 Suggestion: 程式碼風格、型別收緊、元件拆分

3. **工具輔助**：
   - ESLint（`eslint-plugin-react-hooks`、`@next/eslint-plugin-next`）、TypeScript
   - React DevTools 的 Profiler、TanStack Query Devtools
   - 瀏覽器 DevTools 的 Network、Performance、Lighthouse

4. **學習資源**：
   - React 官方文件（react.dev）
   - Next.js 官方文件（nextjs.org/docs，依專案版本選）
   - TanStack Query 官方文件（tanstack.com/query）
