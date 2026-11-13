---
name: design-md-init
description: 為一個專案或作品建立 DESIGN.md（色彩、字型、間距、圓角、元件、icon 規格），作為之後畫面的唯一規格來源。專案還沒有 DESIGN.md、要開始畫新畫面或 icon 之前使用。Trigger：建立 DESIGN.md、design-md-init、定設計規格、先定色彩字型、沒有 DESIGN.md、設計 token。
metadata:
  version: 0.1.0
  last-updated: 2026-11-13
  status: 試用中
---

# 建立 DESIGN.md

目的：讓顏色、字型、間距、icon 的每一個值都來自**一次明確的選擇**，而不是模型每次臨時給的預設值。

## 流程

1. **先找有沒有**：往上找 `DESIGN.md`。已經有就**不要覆蓋**，改成問使用者要補哪一段
2. **看既有素材再問**：專案若已有畫面、`theme`、`tailwind.config`、`ThemeData`、色票檔，先讀出實際用到的色與字型，當作「現況」。只問讀不出來、只有人能決定的事（品牌調性、主色、要不要深色模式、目標裝置）
3. **一次一個決定，附 2～3 個具體選項與取捨**，不問開放式的「你想要什麼風格」。用 `grilling` 的問法
4. **每個 token 要有值、有用途**：只寫會用到的；不確定的標「待定」，不要補一個看起來合理的數字
5. 依 [references/design-md-template.md](references/design-md-template.md) 的結構寫成 `DESIGN.md`，放在專案根目錄
6. 寫完用 `anti-ai-look` 的「視覺」前兩節自查：定出來的色票與字型本身是不是落入第二層 AI 味的預設（奶油＋赤陶、近黑＋螢光綠等）。是的話跟使用者確認是不是刻意

## 不做

- 不憑空編品牌故事、客戶、數字
- 不在這裡畫任何畫面
- 公司專案若已有 `DESIGN.md`，以公司的為準，不另建
