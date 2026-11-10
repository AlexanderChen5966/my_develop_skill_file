---
name: project-dev-main-workflow
description: 使用者的開發主流程是 Jira MCP → figma-to-requirements（視需要）→ requirements → Claude
  開發 → stack-review → doc-update；multiagent-handoff 只是額度用完的備援
metadata:
  type: project
  modified: 2026-11-09
permalink: agents-memory/global/project-dev-main-workflow
---

主流程（使用者 2026-11-09 親口確認）：

1. Jira MCP 確認需求
2. figma-to-requirements（有設計稿才做）
3. requirements → `docs/shared/*.md`
4. Claude 開發
5. stack-review
6. doc-update

之後由使用者人工 commit、push、開 MR（見 [[feedback_no_auto_commit]]）。

**不屬於主流程的：**
- multiagent-handoff：只在 Claude 額度快用完、要交給其他平台 agent 接手時用，不是常駐流程。功能已完成、可實際運作（使用者 2026-11-09 確認），不要標成「測試中」。
- Matt Pocock skills（b2b-manager 的 grill-me／to-spec／to-tickets／implement／tdd／matt-code-review／pr）：在 React 遷移中測試，不是主流程。
- ai-pair：比較複雜的開發需求與 review 才用，取代第 4、5 步（Claude 開發＋stack-review）；前提是需求文件已存在（見 [[feedback_aipair_trigger]]）。7 週沒叫過不代表要淘汰，只是近期沒有複雜任務。

**Why:** 盤點對話紀錄時看到 handoff 與 Matt skill 被頻繁叫用，就誤判成常駐流程，使用者出面更正。

**How to apply:** 整理或建議流程時以這 6 步為骨幹，其他工具標成「備援」或「測試中」，不要因為使用次數多就升格成主流程。