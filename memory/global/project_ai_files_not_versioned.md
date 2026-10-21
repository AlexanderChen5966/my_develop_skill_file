---
name: project-ai-files-not-versioned
description: 所有 AI 相關檔案（AGENTS.md／CLAUDE.md／GEMINI.md／.claude/／docs/）刻意不上版控，屬個人使用；未經公司允許前不可提議納入 git
metadata:
  type: project
---

b2b-manager 的 AI 相關檔案**全部刻意排除在版控之外**，`.gitignore` 明列：
`/.claude/`（62）、`/.claudeignore`（64）、`/CLAUDE.md`（67）、`/CLAUDE.md.backup-*`（68）、
`/AGENTS.md`（69）、`/GEMINI.md`（70）、`/docs/`（80）。

**這是刻意的政策，不是疏漏**：2026-09-11 使用者說明——AI 相關內容目前**只有個人使用**，
**除非公司允許，否則不上版控**。

**Why:** 我在 2026-09-11 改完 `AGENTS.md` 的驗證指令後，發現它不在版控，
主動建議「要不要加進版控讓其他平台 agent 共用」。使用者澄清這是公司層面的授權問題，
不是技術選擇。

**範圍：** 這條只管**公司專案的 repo**。2026-10-21 使用者確認：AI 資訊屬個人使用，
`~/.agents/`（共用 skill、長期記憶）備份到**個人 GitHub**（my_develop_skill_file，公開）是可以的，不必再提出疑慮。

**How to apply:**
- ❌ 不要提議把 `AGENTS.md`／`CLAUDE.md`／`.claude/`／`docs/` 加進 git 或改 `.gitignore`
- 改完這些檔案後，**明確告知使用者「這次修改不會出現在 `git status`、不隨 commit 推送」**，
  因為它們也不會出現在任何 diff 檢查中，容易被誤以為沒生效
- 這同時代表**沒有 git 可復原**——編輯共享檔案的防護手法見 [[project-docs-concurrent-write-hazard]]
- `AGENTS.md` 的內容維護原則另見 [[feedback-agents-md-self-sufficient]]
