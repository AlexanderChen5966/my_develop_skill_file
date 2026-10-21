---
name: feedback-agents-md-self-sufficient
description: AGENTS.md 必須自給自足，不可為省 context 把規則移進 .claude/rules/
metadata:
  type: feedback
---

`AGENTS.md` 是給**其他平台 agent** 讀的（Codex、Antigravity、OpenCode、Gemini CLI、Copilot），
它們**不會載入 `.claude/rules/`**（那是 Claude Code 專屬目錄）。

因此 `AGENTS.md` 與 `.claude/rules/` 內容重疊（例如權限 gating 段約 3KB）**不是浪費**，
❌ 不可提議「把細節移到 rules、AGENTS.md 只留摘要」來精簡 context。

**Why:** 2026-08-19 我曾建議縮短 `AGENTS.md` 的權限 gating 段以省 context，
使用者指出這會讓其他平台 agent 永久失去該規則。此建議違反 `CLAUDE.md` 開頭的維護原則
（共用規則只改 `AGENTS.md`；Claude Code 專屬才進 `.claude/rules/`）。

**How to apply:** 討論 context 精簡時，`AGENTS.md` 視為不可縮減。
規則若屬共用性質 → 兩邊都要有，重複是刻意的。
`rules` 檔尾的 `> 詳見 AGENTS.md` 是給**維護者**的同步提示，不是 agent 導航用，也別刪。
相關：[[project-aipair-domain-expansion]]
