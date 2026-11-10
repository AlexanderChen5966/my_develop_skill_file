---
name: feedback-skill-mcp-change-sync
description: skill 新增或更新後要同步存檔＋SKILL_INDEX.md＋my-technical-notes skills-list；MCP 新增或更新要改 mcp-list
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-09
permalink: agents-memory/global/feedback-skill-mcp-change-sync
---

skill 有新增或更新（含版本號變動、外部 skill 搬進來）時，同一個任務內要做完這三件事：

1. 把 skill 本體複製到 `~/Desktop/紀錄文件資料夾/實驗用文件/Skill存檔/` 的合適分類（`dev/`、`general/`、`pkm/`；外部套件放一個資料夾，例如 `dev/mattpocock-skills/`）
2. 更新 `Skill存檔/SKILL_INDEX.md`：檔頭「最後更新」、目錄、該 skill 條目（版本、路徑、最後更新、新增功能段＋起因）、「作用中安裝位置」（共用位置有變時）、最下方「版本彙整表」加一列
3. 更新 `~/notes/my-technical-notes/agent-skills/skills-list.md`：檔頭「最後更新」與作用中安裝位置、該 skill 列的描述／版本／日期、統計

MCP 有新增或更新時，更新 `~/notes/my-technical-notes/agent-mcp/mcp-list.md`。

**Why:** 使用者 2026-11-09 指定；作用中本體在 `~/.agents/skills/`，存檔與兩份清單是使用者自己查版本與歷程的地方，不同步就會落後（例如 stack-review 本體檔頭曾停在 1.1.0，存檔已到 1.4.0）。

**How to apply:**
- 改前先備份兩份索引為 `*.bak-YYYYMMDD`（兩邊既有慣例）；改用字串比對編輯，不整檔重寫
- 版本號以存檔的版本歷程為準，不要只看本體檔頭
- `my-technical-notes` 不在 basic-memory MCP 的專案裡（MCP 只接 agents-memory），直接改檔案
