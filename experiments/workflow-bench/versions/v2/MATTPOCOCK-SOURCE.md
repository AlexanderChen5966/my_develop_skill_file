# Matt Pocock skills 來源與本機修改

- 來源：mattpocock/skills@5beb35b（2026-10-19）plugin v1.3.1，MIT 授權，授權全文見同目錄 `LICENSE-mattpocock`
- 2026-11-09 從 b2b-manager `.claude/skills/` 搬到這裡共用（依桌面〈開發流程與MattPocock截長補短.md〉第 6 節）
- 共用的 7 個：grilling、grill-me、diagnosing-bugs、tdd、pr、writing-for-agents、retro
- 其他 Matt skill（to-tickets、implement、matt-code-review、codebase-design 等）仍只在 b2b-manager，待 React 遷移結束後回顧

## 本機修改

- `tdd/SKILL.md`：叫用 `codebase-design` 改成「repo 有才叫」；重構歸屬改指 `stack-review`（有 `matt-code-review` 的 repo 照舊）
- `pr/CREDITS.md`：原樣保留（pr 改寫自 Humanlayer 的 show-me）

## 更新上游時

先比對本檔「本機修改」再覆蓋，覆蓋後重做上述修改；同名 skill 不要再放進任何 repo 的 `.claude/skills/`，否則專案版會蓋過共用版。
