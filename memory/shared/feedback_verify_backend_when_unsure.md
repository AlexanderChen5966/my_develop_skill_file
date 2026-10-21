---
name: feedback-verify-backend-when-unsure
description: 對後端行為不確定時（回應碼、enum 值、權限、驗證）要去 b2b-backend 原始碼查證，不可只標「需實測」
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4d2349fd-c923-4e3b-975f-c6c21333640e
  modified: 2026-10-07T03:33:35.826Z
---

不確定後端行為時，直接去 `/Users/alexander/GitLab/b2b-backend` 讀原始碼確認（controller 的 `@PreAuthorize`／`@ValidGroupId`、service 的 throw、enum 定義），不要留「信心：需實測」或「依 commit 註解得知」就交差。

**Why:** 2026-10-07 review SSGS-13896 時，reviewer 對「NOT_ONBOARDED 公司 settings 回什麼」「NotificationChannel 有哪些值」都只寫推測；使用者要求查後端，一查就找到 403／400／404 三條實際失敗路徑，讓風險判斷從「可能」變成「確定」。

**How to apply:** review、需求分析、風險評估中，只要結論取決於後端行為，就先 grep 後端再下結論；派 subagent review 時也在 prompt 寫明「不確定就查 b2b-backend」。相關：[[reference-staging-run-semantics]]
