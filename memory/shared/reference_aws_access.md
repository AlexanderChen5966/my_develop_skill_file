---
name: reference-aws-access
description: 公司 AWS 走 Entra ID SAML 直連 IAM Role（非 Identity Center，aws configure sso 不適用）；帳號 ID、角色名稱不記在這裡，到 AWS Console 右上角或問 IT 查
metadata:
  node_type: memory
  type: reference
  originSessionId: 9b0616e8-b6ef-4622-b036-5287d625c666
  modified: 2026-10-21T07:45:00.000Z
---

- 登入路徑：Microsoft MyApps（myapps.microsoft.com）→ 點公司的 AWS SSO 圖示 → 直接進 AWS Console（沒有 awsapps.com 入口）
- 架構：Microsoft Entra ID **SAML 直連 IAM Role**，**不是** IAM Identity Center → `aws configure sso` 不適用
- 環境：dev、staging、prod 是**不同的 AWS 帳號、不同角色**；目前使用者只有 dev 的開發者角色
- 帳號 ID、角色名稱、Entra Tenant ID：**不記在記憶裡**（2026-10-21 去敏）。需要時到 AWS Console 右上角帳號選單查看，或問 IT
- 2026-09-23 使用者決定不處理本機 AWS CLI，已移除安裝（`~/.local/share/aws-cli` 與 `~/.local/bin/aws*`）；日後若再提起，先確認是否要重新安裝
- 本機 CLI 可行方案：CloudShell（免設定），或 `aws-azure-login`（需向 IT 要該 SSO 應用程式的 SAML Identifier / App ID URI）
- `.gitlab-ci.yml` 的 dockerize 不論 dev/stage/release tag 都推到 dev 帳號 ECR；deploy job 只在 `main` / `dev-x.y.z` 跑、只部署 dev 環境 → staging/prod 的部署不在這條 pipeline

相關：[[project-oauth-client-secret-rotation]]
