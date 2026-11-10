---
name: reference-company-frontend-stacks
description: 公司 Web 前端技術棧對照：TMS 用 Next 15+antd（當 SPA 用、Node 跑在 EKS），FMS 用 Next 14.2+Radix；共通層是
  zustand+TanStack Query+Tailwind
metadata:
  type: reference
  modified: 2026-10-29
permalink: agents-memory/shared/reference-company-frontend-stacks
---

2026-10-29 實查（FMS 為使用者口述，repo 權限不足無法 clone）：

- **tms-frontend**（`~/GitLab/tms-frontend`）：Next 15.5 App Router、React 19、antd 6、Tailwind、zustand、TanStack Query、axios、react-i18next；大量 `'use client'`，實質是 SPA；token 存在 localStorage，由前端加鎖做 refresh（`libs/tokenRefresh.ts`），沒有 BFF；部署是 `deployment/Dockerfile` 跑 `npm start`（Node 常駐），CodeBuild 部署到 EKS
- **tms-system-manager-frontend**：Next 14.2、React 18、antd 5、zustand、MSAL
- **FMS**：Next 14.2 App Router、React 18、Radix UI + Tailwind、zustand、TanStack Query、Google Maps、Recharts
- 共通層：Next App Router + zustand + TanStack Query + Tailwind；UI 元件庫分成 antd（TMS）和 Radix（FMS）兩派

**How to apply:** 新前端專案或改寫要「比照公司慣例」時，以這份對照為起點；資料密集的後台優先對齊 TMS（antd）。版本可能已經更新，引用前先看該 repo 的 `package.json`。