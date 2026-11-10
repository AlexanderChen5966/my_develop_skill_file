# 跨專案層記憶索引（shared）

> 換專案仍成立、限特定技術或公司的知識（公司後端、GitLab CI、AWS、Figma、iOS 工具）。所有 agent 適用；只有 Claude 寫入。

- [不確定就查後端](~/.agents/memory/shared/feedback_verify_backend_when_unsure.md) — 後端行為（回應碼／enum／權限）不確定時讀 b2b-backend 原始碼，不留「需實測」
- [iOS Simulator UI 自動化](~/.agents/memory/shared/ios-simulator-ui-automation.md) — CGEvent 驅動點擊/按鍵，四條死路（click at / unicodeString / ⌘鍵 / Edit>Paste）別再試
- [dockerize dind MTU](~/.agents/memory/shared/project_dockerize_dind_mtu.md) — GitLab SaaS dind 內 apt 逾時＝MTU 1360/1500 不一致；已用 --network host 繞過；重跑舊 tag 吃舊 CI 設定
- [auth server 換 client secret](~/.agents/memory/shared/project_oauth_client_secret_rotation.md) — 前端 PKCE 不持有 secret 不用改；前端全站 API 失敗先查 b2b-backend introspect secret（ECS env，改完要重新部署）
- [AWS 存取方式](~/.agents/memory/shared/reference_aws_access.md) — Entra SAML 直連 IAM Role（非 Identity Center，aws configure sso 不適用）；帳號 ID／角色不記，到 Console 或問 IT
- [公司前端技術棧](~/.agents/memory/shared/reference_company_frontend_stacks.md) — TMS：Next15+antd，當 SPA 用、Node 跑在 EKS；FMS：Next14.2+Radix；共通層是 zustand+TanStack Query+Tailwind；後台優先對齊 TMS
- [比對 Flutter Web 畫面](~/.agents/memory/shared/reference_flutter_web_ui_compare.md) — canvas 畫面用使用者的 Chrome（Claude in Chrome）真實點擊比對，不用 Playwright；React 用 DOM 量、Flutter 用已知元素換算截圖比例；每個元素（含頁碼列等小元素）量座標填表，可點元件比 hover／停用／tooltip；預設值讀套件原始碼
- [Figma MCP 額度](~/.agents/memory/shared/reference_figma_mcp_quota.md) — 公司檔以 Professional/View 計，每月僅 6 次讀取、不能寫入；用完改請使用者給 PNG；以 Figma→Flutter 為主，先走 figma-to-requirements
