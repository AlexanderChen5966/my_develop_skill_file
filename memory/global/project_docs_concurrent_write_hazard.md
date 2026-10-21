---
name: project-docs-concurrent-write-hazard
description: docs/ 在 .gitignore 內，並行編輯或整批複製失敗都會不可復原地遺失內容；約定單一寫入者，文字檔可從 session transcript 的 Write 呼叫原封還原
metadata: 
  node_type: memory
  type: project
  originSessionId: bf60a89d-a3d1-41ff-9c41-8bae9940d841
  modified: 2026-09-09T08:28:28.921Z
---

使用者常同時開多個 Claude session 在 b2b-manager 上工作（session 之間用 cross-session message 協調）。`/docs/` 在 `.gitignore` 第 80 行，因此 `docs/` 底下的改動 **`git status` 偵測不到、被覆蓋也無法用 git 復原**。

更精確地說：`git log -- docs/` 為 **0 筆**——`docs/` 是**從未被追蹤過**，不是「有紀錄但被 ignore」，所以連舊版本都不存在，沒有任何東西可以 checkout 回來。

`docs/issue/readme.md` 是多 session 共同維護的索引（處理順序表 ＋ 文件索引表），最容易發生並行寫入衝突。

**2026-09-07 實際發生過一次資料遺失**：一個 session 用 python **行號**定位（`lines[34] = ...`）改 readme，讀取行號到寫入之間另一個 session 插入了一列並重編號，行號整體位移 → 覆蓋掉相鄰的 `company_switch` 整列，並留下重複的舊列。靠 session 之間訊息裡留存的完整原文才還原回來。

**2026-09-08 16:05 另有一次「整批清空」事故（機制不同，別跟上面的並行覆蓋搞混）**：`docs/issue/staging_repro_guide_2026-09-07.md`、`docs/issue/dashboard_loading_optimization_2026-09-01.md`、以及 `docs/assets/` 底下 **14 個 PNG** 同時變成 0 bytes，mtime 全部是 `Sep 8 16:05:18`——與 `docs/issue/` 其他**有內容**的檔案是同一個時間戳。研判是 `docs/` 整批複製／還原時部分檔案傳輸失敗被截成 0，**不是**編輯覆蓋。發生後 `git status` 依然乾淨（docs 未被追蹤），所以完全無聲無息。

**🔧 復原手法（2026-09-09 實證有效）**：session transcript 保留了 Write 工具的完整 `input.content`，可以原封取回。
```bash
cd ~/.claude/projects/-Users-alexander-GitLab-b2b-manager
grep -l "檔名關鍵字" *.jsonl          # 先找哪些 session 提到它
# 再用 python 逐行 json.loads，挑 message.content 裡 type=='tool_use'
# 且 input.file_path 命中該檔、input.content 為字串者，取最後一次 Write
```
注意：① 只有 `Write` 會帶完整 `content`，`Edit` 只有 `old_string`/`new_string`，所以要確認該 transcript 對此檔**沒有後續 Edit**，否則取回的是舊版；② 二進位檔（PNG 等）不會進 transcript，**無法用這招救**——那 15 個 PNG 已永久遺失，只能請使用者重新截圖。

**Why:** 沒有版控保護的共享檔案，一旦覆蓋或截斷就是永久遺失；行號定位等於把 TOCTOU 競態寫死進流程。

**How to apply:**
- 發現 `docs/` 底下有 0 bytes 檔案時，先 `find docs -type f -size 0` ＋ 比對 mtime 判斷是「單檔覆蓋」還是「整批複製失敗」，再決定復原路徑
- 文字檔優先走上面的 transcript 復原；還原後在該檔變更紀錄註明「自 transcript 原封還原、內容未改寫」，避免日後誤認是重寫版
- 編輯 `docs/` 底下的共享檔案一律用**唯一字串比對**（並加 `assert count == 1`），**絕不用行號定位**
- 動 `docs/issue/readme.md` 前先問其他 session 有沒有在寫；約定**單一寫入者**，其他 session 把要改的內容傳給維護者代寫
- 改完做完整性檢查（編號連續、無重複列、無殘留過期敘述）
- 別用 session 名稱推斷其他 session 的工作範圍——名稱常與實際工作無關，要用「實際改了哪些檔案」對齊

相關：[[feedback-subagent-delegation]]
