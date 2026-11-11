# 已知的差異原因

`flutter-ui-compare` 第 7 步用。依症狀查，照「驗算」確認是不是這個原因，再套「修法」。

| 症狀 | 原因 | 驗算 | 修法 |
|---|---|---|---|
| Flutter 文字比網頁寬 3～5%（數字多的更明顯） | Flutter `ThemeData` 沒關 Material 3，TextTheme 帶字距：bodyMedium 0.25、titleSmall／labelLarge 0.1、bodySmall 0.4、bodyLarge 0.5 | 字數 × 字距 ≈ 寬度差 | 網頁對應的文字加同樣的 `letter-spacing` |
| 按鈕裡的文字字型或字寬不對 | 原生 `<button>` 不繼承字型與字距（Chrome 預設 Arial、字距 normal） | 讀 `getComputedStyle(button).fontFamily` | 全站樣式加 `button { font-family: inherit; letter-spacing: inherit }` |
| 固定高度的區塊比 Flutter 高（差值剛好是上下 padding 或框線） | Flutter `Container(height:, padding:)` 的 height 含 padding；網頁元素是 `content-box`（關掉 CSS reset 的專案、antd Modal 內部都是） | 高度差 = padding＋框線 | 該元素加 `box-sizing: border-box` |
| 多行或單行文字的區塊高度不同 | Flutter 文字行高約 1.5 倍（NotoSansTC） | 字級 × 1.5 ≈ Flutter 的行高 | 網頁給 `line-height: 1.5` |
| 輸入框、下拉的文字距左框不同 | Flutter 輸入元件的內距是「框線＋padding＋contentPadding」相加，和 UI 套件預設不同 | 讀 Flutter widget 原始碼把三個值相加 | 調整網頁元件的 `padding-inline-start` |
| 標題列比 Flutter 高幾 px | `inline-flex` 對齊 baseline，放在標題元素裡會多出下伸部空白 | 把 display 改成 `flex` 後重量 | 用 block 層級的 flex |
| hover 時網頁變色、Flutter 不變 | Flutter InkWell 的墨水被父層 `Container(color:)` 蓋住 | 在 Flutter 上真實 hover 截圖 | 以 Flutter 實測為準，網頁不加 hover 底色 |
| 停用的按鈕 Flutter 仍有 tooltip | Flutter `IconButton` 有 tooltip 時停用也會顯示 | 在 Flutter 上 hover 停用的按鈕 | 網頁停用狀態保留 tooltip |
| 下拉選單可見高度差很多 | UI 套件的選單高度上限和 Flutter 元件不同（antd Select 預設 256） | 讀 Flutter 下拉元件的上限 | 設定網頁元件的選單高度 |
| icon 粗細或形狀略有不同 | 兩邊 icon 字型版本不同（例：FontAwesome Pro 對免費版） | 比對兩邊載入的字型檔 | 由使用者決定 |
| 粗體字筆畫不同 | Flutter 打包了各字重的字型檔，網頁只宣告 Regular、粗體由瀏覽器合成 | 查網頁 `@font-face` 宣告了哪些字重 | 由使用者決定 |
| 日期在某些瀏覽器顯示錯誤 | 後端回 `yyyy-MM-dd HH:mm:ss`（空白分隔），Safari 的 `new Date()` 不接受 | 看實際回應的日期字串 | 解析前轉成 ISO 格式 |
