---
name: reference-figma-mcp-quota
description: 讀公司 Figma 檔時以 Professional/View 席位計，每月僅 6 次讀取、不能寫入；用完改請使用者給 PNG；以 Figma → Flutter 為主
metadata:
  node_type: memory
  type: reference
  originSessionId: 9db4508e-8758-4678-b28a-e19d02948c32
  modified: 2026-10-21T07:45:00.000Z
---

Figma MCP（`plugin:figma:figma`）登入的是使用者的**個人帳號**（自己的 team 是 Starter/View；帳號信箱不記在記憶裡，用 `whoami` 查）。
**讀公司設計檔時，是以公司 Professional 方案的 View 席位計算額度：每月最多 6 次讀取。** 2026-10-01 已觸發上限，錯誤訊息為 "You've reached the Figma MCP tool call limit for your View seat on the Professional plan"（2026-09 用掉 2 次，額度可能跨月累計或依帳單週期計算，確切重置日不明）。
公司設計檔的連結（file key）不記在記憶裡，向使用者要或從專案 `docs/` 的需求文件找。

- 會耗額度：get_screenshot / get_metadata / get_design_context / get_variable_defs 等讀取工具；不耗：`whoami`、`create_new_file`、`add_code_connect_map`
- **無法寫入**公司設計檔（View 席位）
- 解除限制：請公司把帳號升級為 Dev 或 Full 席位（Professional 方案每天 200 次）

**使用者需求**：以 **Figma → Flutter 程式碼**為主，不需要 code → Figma。

**How to apply:**
- 使用者的規則：**Figma 讀取失敗（用量上限等）時直接回報，使用者會改給 PNG；不可用猜的補設計細節**
- 每次讀取前先想清楚是否必要；一個畫面盡量 1 次（優先 get_screenshot 單一 frame），結構類資訊先查本機文件或程式碼
- 流程：先 `figma-to-requirements` 產出需求草稿（對應 `DESIGN.md` token）再實作；`get_design_context` 的 React/Tailwind 只當參考
- 截圖存 scratchpad 重複使用，不重抓同一節點
- Jira 為需求說明、**設計以 Figma 為準**（使用者 2026-10-01 指定）
