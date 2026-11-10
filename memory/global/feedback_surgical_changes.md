---
name: feedback-surgical-changes
description: 改既有程式只動必須動的：每一行變更都要對應到需求；不順手改格式、註解、旁邊的程式；自己造成的孤兒要清，原有死碼只回報；多步任務先寫「步驟 → 怎麼驗證」
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-09
permalink: agents-memory/global/feedback-surgical-changes
---

修改既有程式時，範圍以「需求要求的那幾行」為界：

- **每一行變更都要能對應到需求**。說不出這行是為了哪條需求，就不要改
- 不順手「改善」旁邊的程式、註解、空白或格式；不重構沒壞的東西；沿用檔案既有的寫法，即使自己會寫得不一樣
- **自己這次造成的孤兒要清掉**（因為這次修改而沒人用的 import、變數、函式）
- **原本就存在的死碼、怪寫法只回報，不刪不改**；要處理另外開任務
- 多步驟的任務先列「步驟 → 怎麼驗證」（跑哪個測試、哪個指令、看哪個畫面），每一步驗證過再往下；成功條件要寫成可以檢查的樣子，不寫「讓它能動」

**Why:** 使用者 2026-11-09 決定採用（觀念來自 Karpathy 準則，原作無授權，這裡是自己的寫法）。模型常順手改無關的程式或格式，讓 diff 變大、review 變難、還可能改壞不懂的地方；各 repo 原有的「最小化變更」規則是架構層級，管不到這種行層級的動作。放個人層是因為 AI 相關文件不進公司 repo，只在個人 git 備份，這裡是所有 agent 都讀得到的地方。

**How to apply:** 所有 repo、所有 agent 都適用。stack-review 的 `references/common.md`「變更範圍」會檢查同一件事；requirements 的任務文件每個任務都要有「驗證：」。跟 b2b-manager `change-policy.md`（架構層級禁止清單）互補，不取代。
