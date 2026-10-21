---
name: reference-cross-agent-skills
description: 跨 agent 共用 skill 放 ~/.agents/skills＋link-skills.sh；agy 1.4.2 實際讀 ~/.gemini/config/skills（官方網頁寫錯）
metadata:
  node_type: memory
  type: reference
  originSessionId: 654b6d59-535e-4992-8457-183b1a62ade6
  modified: 2026-10-19T08:54:30.454Z
---

跨工具共用的 skill 本體放 `~/.agents/skills/<name>/`（Codex／Copilot CLI／opencode／Cursor CLI 原生讀；
Cursor 同時讀 `~/.claude/skills/`，同一實體會去重，實測 1 份），
Claude Code 與 agy 用 `~/.agents/link-skills.sh`（link／check／unlink）建 symlink。2026-10-20 起共用 7 個（multiagent-handoff（2026-10-21 由 handoff 改名，避開 Matt Pocock 的 /handoff）、stack-review、requirements、doc-update、project-documentation、figma-to-requirements、cross-platform-archive-agent），六工具實測各 1 份。
**只有 ai-pair 留在 `~/.claude/skills/`**（使用者指定；Claude 專屬）。ai-pair 有 disable-model-invocation，模型清單本來就看不到它，屬正常。

**agy 路徑以實測為準**：官方網頁說 CLI 讀 `~/.gemini/antigravity-cli/skills/`，但 agy 1.4.2 實際只讀
`~/.gemini/config/skills/`（實體與 symlink 皆可）；`~/.gemini/config/skills.json` entries 指向外部資料夾實測無效。
`npx skills`、Skills Hub 也都把 agy 路徑設錯。驗證法：`agy -p` 詢問「multiagent-handoff skill 出現幾次」，並以 workspace `.agents/skills/` 當對照組。

**Why:** 第三方管理工具（Skills Manager #256 會刪使用者自加檔案、Skills Hub 未簽章）風險高於自管 symlink。
**How to apply:** 新增跨工具 skill → 放 `~/.agents/skills/` 後跑 `link-skills.sh`；工具升版後跑 `check` 並重測 agy。
使用者要求 `~/.agents/` 暫不 git init；快照兼備份在 b2b-manager `docs/agent-handoff/install/`（`install.sh diff|install|export`，改本體後要 export）。
⚠️ `cursor agent …` 在未安裝 cursor-agent 時會自動從 cursor.com/install 下載安裝，查 help 請直接用 `cursor-agent`。相關：[[project-ai-files-not-versioned]]
