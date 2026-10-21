# 全域指引（由 ~/.agents/link-memory.sh 同步，請改 ~/.agents/memory-guide.md）

## 回覆語言

一律使用繁體中文台灣用語；技術術語與程式碼識別符保留原文。

## 長期記憶（唯讀）

使用者在多個 AI agent 之間切換工作。為了不重新學一次，長期記憶集中放在 `~/.agents/memory/`，所有 agent 共用同一份：

| 層 | 索引 | 內容 |
|---|---|---|
| 個人層 | `~/.agents/memory/global/MEMORY.md` | 不管做哪個專案都成立的習慣、偏好、原則 |
| 跨專案層 | `~/.agents/memory/shared/MEMORY.md` | 公司後端、GitLab CI、AWS、Figma、iOS 工具等跨專案知識 |
| 專案層 | `~/.agents/memory/projects/<專案資料夾名稱>/MEMORY.md` | 只跟該專案有關的決定、規則、外部資源 |

- **開工時先讀個人層索引**；做的是某個專案時，也讀該專案的索引。
- 遇到技術問題或要做設計決定時，先查跨專案層索引。
- 索引一條一行，摘要寫在破折號後面；需要細節時再讀該行連結的檔案。
- 這裡是**正式來源**：與你自己的內建記憶衝突時，以這裡為準。

### 不要直接修改

- ❌ 不要新增、修改或刪除 `~/.agents/memory/` 底下的任何檔案（只有 Claude Code 寫入）。
- 你學到值得長期記住的事（決定與原因、踩過的坑、試過但失敗的做法）時，寫進 multiagent-handoff 的交接檔（`.handoff/CURRENT.md`）或任務單的「建議記憶」一節，格式：
  `- [層：project/shared/global] 內容……（原因：……）`
- 沒有在用 multiagent-handoff 時，直接在回覆裡告訴使用者「建議記住：……」。

### 其他規則

- 不要把密碼、token、secret 寫進任何交接檔或回覆。
- 任務進度（做到哪、下一步）屬於 `.handoff/`，不是長期記憶。
