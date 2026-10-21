---
name: reference-staging-run-semantics
description: flutter run --dart-define=DEPLOY=staging 跑的是本機工作區前端＋staging 後端，不可推論已部署環境
metadata: 
  node_type: memory
  type: reference
  originSessionId: f0a7cac0-141a-4605-b748-859ebfc4ffe4
  modified: 2026-09-07T07:08:43.316Z
---

`flutter run -d chrome -t lib/main_dev.dart --dart-define=DEPLOY=staging --web-port=9001`
中的 `DEPLOY=staging` **只切換 API base URL**，前端程式碼一律由本機 `lib/` 現編。

所以這個組合是「**本機工作區前端（含未 commit 變更）＋ staging 後端**」，
**不是**已部署的 staging 前端。

**為什麼重要：** 用它做的實機驗證可以證明「本機修正有效」，
但**不能**推論已部署環境的行為——線上跑的是另一個版本，修正未部署前問題依然存在。
2026-09-07 有 peer session 據此誤判驗證結果無效，差點推翻一個正確的結論。

**如何證明當下跑的確實是工作區程式碼：** 在 log 找只存在於未 push commit 的字串
（例如某個新增檔案印出的訊息），再用 `git cat-file -e <base>:<path>` 確認該檔在
基準版本不存在。

驗證前端修正效果時，記得在報告裡明講這個界定。相關：[[project-docs-concurrent-write-hazard]]
