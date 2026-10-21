---
name: reference-artifact-style-ssgs3444
description: 開發／測試流程展示 Artifact 的參考樣板：docs/assets/SSGS-3444 測試報告.html 的版面、互動與寫法
metadata:
  node_type: memory
  type: reference
  originSessionId: 9db4508e-8758-4678-b28a-e19d02948c32
  modified: 2026-10-01T09:28:28.939Z
---

使用者指定的流程展示 Artifact 參考檔：`docs/assets/SSGS-3444 測試報告.html`（2026-09-30 由另一個 session 產出，約 850KB，大部分是 base64 截圖；讀之前先用 sed 把 `data:image/...;base64,...` 換掉）。

**版面（由上到下）**：header（eyebrow + 標題 + 副標 + Jira 連結按鈕）→ 流程列 panel → 摘要（通過／失敗／無法判定三格數字 + `dl.meta` 環境資訊 + 結論 callout）→ 步驟明細（`details` 折疊，「需要處理」排在「通過」前面，失敗預設展開）→ Bug 重現說明（含「複製」按鈕）→ 其他觀察 → footer 註明資料來源。

**流程列做法**：每站是 `.station`（編號／標題／一句說明），站與站之間是 `.link` 連線；站內 `.tools` 用 chip 列出這一站實際用到的 **MCP 名稱與工具名**（如 Atlassian MCP：`getJiraIssue`、Claude in Chrome MCP：`computer`），再加一行說明限制（例如「MCP 讀不到 QAlity 步驟」）。控制鈕：上一步／播放（暫停、繼續）／下一步，`aria-live` 的 caption 顯示「n / N · 這一站的成果數字」；播放間隔 1400ms，預設停在最後一站。

**樣式**：顏色全用 `:root` token（`--accent` 藍、`--pass`/`--fail`/`--warn` 各有 `-soft` 底色），深色模式兩段寫法；字型 IBM Plex Sans + Noto Sans TC，數字與代號用 IBM Plex Mono；`max-width:960px` 單欄；640px 以下流程改直排；`prefers-reduced-motion` 關掉轉場。資料（步驟）放在 JS 陣列再 render。

**How to apply:** 這只是**參考範例，不是固定樣板**（使用者 2026-10-01 明確說可依內容調整成適合的形式）。做「SSGS-13976 開發流程」Artifact（該任務已於 2026-10-12 合併）（以及之後的開發／測試流程展示）時，可借用它的元素（流程站＋工具 chip、播放控制、摘要、折疊明細、token 配色），但版面與區塊依該任務性質重新設計，不必照抄。**SSGS-13976 不可放 PNG**，設計那一站改用文字對照表。
