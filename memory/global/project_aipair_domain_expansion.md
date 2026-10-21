---
name: project-aipair-domain-expansion
description: AI-Pair v4.2 跨領域遷移可行性分析結論 — 哪些領域可用、遷移條件與最小改動範圍
metadata: 
  node_type: memory
  type: project
  originSessionId: 50f99cbc-7da6-470f-9051-588812358665
---

# AI-Pair v4.2 跨領域遷移可行性結論

**核心結論：** ai-pair 的本質是「結構化多視角審查工作流程」，不限於程式碼或文章，任何具備「初稿 + 多維度審查」特性的領域都可遷移。

**Why:** 框架的強項在於讓不同模型（GPT / Claude / Gemini）各自關注不同維度，三者的盲點互補，而非重複審查同一面向。

**How to apply:** 新領域只需改寫 3 個 reviewer 的 focus prompt；Tier 系統、Quota Fallback、壓縮協議、Review Cache 可直接複用，不需重寫架構。

---

## 高可行性領域

| 領域 | author 角色 | reviewer 分工重點 |
|---|---|---|
| 法律文件 | 起草合約條款 | 邏輯漏洞 / 語言歧義 / 條款完整性 |
| 商業計畫 | 寫策略文件 | 財務邏輯 / 論述結構 / 市場覆蓋遺漏 |
| 翻譯品質 | 初步翻譯 | 語意準確 / 語感自然度 / 原文覆蓋率 |
| 資料分析報告 | 寫分析結論 | 統計方法 / 結論與資料一致性 / 指標遺漏 |
| 教育課程設計 | 設計課綱/題目 | 知識點準確 / 學習路徑邏輯 / 學習目標覆蓋 |

---

## 遷移的三個必要條件

1. **有明確的需求文件** — reviewer 需要規格基準才能對齊，否則只是風格檢查
2. **可拆成創作 + 審查兩個角色** — 必須有初稿供審查
3. **多視角真的有差別** — 三個模型審查不同維度才有意義

---

## 最小改動清單

新增一個 team mode 時只需：
1. 在 SKILL.md 新增 `/ai-pair {domain}-team` 指令
2. 重寫 3 個 reviewer 的 focus 描述（agent prompt）
3. 調整需求文件格式以符合該領域驗收標準

框架本身不需動。

---

**分析日期：** 2026-05-19
**依據版本：** ai-pair-main-v4.2（Phase 1 驗證完成）
