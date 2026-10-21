# 個人層記憶索引（global）

> 不管做哪個專案都成立的工作習慣、偏好與原則。所有 agent 適用；只有 Claude 寫入。

- [AGENTS.md 要自給自足](~/.agents/memory/global/feedback_agents_md_self_sufficient.md) — AGENTS.md 給其他平台 agent 用，不可為省 context 縮減或把規則移進 .claude/rules/
- [ai-pair 何時派 copilot-developer](~/.agents/memory/global/feedback_aipair_developer.md) — 同 pattern 重複任務直接實作更快；copilot-developer 適合複雜多檔案任務
- [ai-pair 啟動條件](~/.agents/memory/global/feedback_aipair_trigger.md) — 只有產生需求文件的任務才走 ai-pair；其他小改動直接手動
- [copilot-reviewer 會虛構路徑](~/.agents/memory/global/feedback_copilot_reviewer.md) — copilot-reviewer 可能回報虛構檔案路徑，出現時標記 ERR:MODEL 跳過
- [agent 不自動 commit](~/.agents/memory/global/feedback_no_auto_commit.md) — ai-pair／任何 agent 任務禁止 git add/commit/push，由使用者人工處理；派工時寫進限制
- [AI 檔案不上版控](~/.agents/memory/global/project_ai_files_not_versioned.md) — 公司 repo 內 AGENTS.md/CLAUDE.md/.claude/docs 不入 git；~/.agents 備份到個人 GitHub 可以
- [ai-pair 跨領域可行性](~/.agents/memory/global/project_aipair_domain_expansion.md) — AI-Pair v4.2 跨領域遷移可行性結論：法律/商業/翻譯/分析/教育等領域皆可用，只需改 reviewer prompt
- [多 session 並行寫入風險](~/.agents/memory/global/project_docs_concurrent_write_hazard.md) — 多個 session 同時改同一檔（不在版控的 docs、共用記憶索引）會互蓋且無法復原；一律用字串比對編輯、不用行號
- [跨 agent 共用 skill](~/.agents/memory/global/reference_cross_agent_skills.md) — 本體 ~/.agents/skills＋link-skills.sh；agy 1.4.2 實讀 ~/.gemini/config/skills（官方網頁寫錯）
