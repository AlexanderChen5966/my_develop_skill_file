---
name: ios-simulator-ui-automation
description: 用 CGEvent 驅動 iOS Simulator 做 UI 手動測試的可行方法與四個已驗證失敗的路徑
metadata: 
  node_type: memory
  type: project
  originSessionId: 6ea00d00-676b-4cea-a022-64a8edd36dc1
  modified: 2026-08-12T07:05:42.103Z
---

在 iOS Simulator 上自動點擊／輸入來驗證 APP 行為時，可行做法與死路（2026-08-12 實測於 iPhone 17 Pro）。

**前置**：`osascript` 需要「系統設定 → 隱私權與安全性 → 輔助使用」授權（Terminal / VS Code 都加）。授權即時生效，不必重啟終端。

**座標換算**：device 畫面區域用 `osascript` 取 Simulator 視窗的第一個 `AXGroup`（position + size），再按 logical 解析度換算。不要猜 title bar 高度。

```
osascript -e 'tell application "System Events" to tell process "Simulator" to tell window 1 to get {position, size} of (first UI element whose role is "AXGroup")'
```

**點擊**：用 Swift 寫小工具呼叫 `CGEvent(mouseEventSource:mouseType:.leftMouseDown/.leftMouseUp)` + `post(tap: .cghidEventTap)`，`xcrun swiftc -O` 預編譯成 binary（避免每次 script 編譯延遲）。點擊前**必須**確認 Simulator 是前景視窗（`frontmost is true`），否則 CGEvent 會打在座標處最上層的其他 app 上——實測誤點到 Android Studio。

**輸入**：只能送實體鍵 virtualKey（a=0, b=11, backspace=51）。間隔 2ms 會大量丟字（3996 次按鍵只進去約 495 個），**要用 12ms 以上**。清空欄位用 backspace 連按（次數多於總長）。

**四條死路，不要再試**：
1. `System Events` 的 `click at {x,y}` → 錯誤 -25204，不支援
2. `CGEvent.keyboardSetUnicodeString` → Simulator 只讀 virtualKey，中文／emoji 會變成該 virtualKey 的字元（打「測試」得到 `a`）
3. `CGEvent.flags = .maskCommand` → Simulator 不接受修飾鍵，⌘A / ⌘V 無效
4. Simulator 選單 `Edit > Paste` → 對 device 內的 Flutter TextField 無效（點選單也會讓輸入框失焦）

**中文／emoji 只能靠剪貼簿 + 人工 ⌘V**：`python3 -c "print('x'*N, end='')" | xcrun simctl pbcopy booted` 灌 device 剪貼簿，`| pbcopy` 灌 Mac 剪貼簿，貼上這一步需要人工操作。

**驗證「有沒有真的打 API」**：`flutter run` 用 `run_in_background` 跑，記錄 log 檔 byte 位置，操作後 `tail -c +<pos>` 比對新增段落 grep API path。比只看畫面可靠。

⚠️ 測試會寫入真實 dev 環境資料庫。字數上限這類測試若因丟字而未達門檻，會真的送出成功——先確認輸入字數正確再按送出。
