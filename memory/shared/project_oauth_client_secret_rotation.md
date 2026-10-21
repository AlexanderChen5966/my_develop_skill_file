---
name: project-oauth-client-secret-rotation
description: auth server 換 client secret 時要跟進的是 b2b-backend／03ManageCenter 的 AWS ECS 環境變數，前端（PKCE public client）不持有 secret；前端全站 API 失敗先懷疑 introspect secret 沒同步
metadata:
  node_type: memory
  type: project
  originSessionId: 77cf892e-47e7-475d-99b4-3572b5d3d5b3
  modified: 2026-10-21T07:45:00.000Z
---

2026-10-21 auth server 更新 OAuth client secret 時的盤點結論（已結案；完整紀錄在 b2b-manager `docs/issue/oauth_client_secret_rotation_2026-10-21.md`）：

- b2b-manager 是 PKCE public client，不持有、不送 secret → 換 secret 時前端**不用改**，也不可為此在前端加 secret
- 持有 secret 的是 b2b-backend（`/oauth2/introspect` 用，錯了 → 前端全部 API 失敗）與 03ManageCenter（mock-user grant 用）；環境變數名稱見上述文件
- 值在 **AWS ECS task definition**，不在 GitLab；CI deploy 只換 image、沿用最新 revision 的 env → 改完要重新部署，且要改在最新 revision

**Why:** 「auth server 問題」第一直覺會去改前端 OAuth 流程，但前端與 secret 無關。
**How to apply:** 症狀若是前端全站 API 失敗，先懷疑 b2b-backend introspect 用的 secret 沒同步；再遇到 auth server／client secret 問題，先讀上述 docs/issue 文件；AWS 存取見 [[reference-aws-access]]。auth server 另有一項待處理的設定問題，詳見上述 docs/issue 文件（2026-10-21 去敏，不在公開記憶寫出細節）。
