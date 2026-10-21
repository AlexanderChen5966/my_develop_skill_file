---
name: ios-signing-cert-expiry
description: CI iOS 簽章憑證/描述檔到期日與 2026-10-16 Runner 修復紀錄位置
metadata:
  node_type: memory
  type: project
  originSessionId: 5a2c6959-bc94-44ab-af54-a9db57d73b0f
  modified: 2026-10-21T08:30:00.000Z
---

2026-10-16 CI iOS build 失敗（`No signing certificate "iOS Development"`），原因是公司 Apple Developer Team 的憑證與描述檔 10/14～10/16 全部到期，加上 Xcode 沒登入帳號。**不是換機器**（Runner 主機只是改名；Team ID、主機名稱見下方完整紀錄，2026-10-21 去敏）。已在 Runner 上重新申請憑證並更新描述檔。

- 新憑證與兩個描述檔（名稱見完整紀錄）：**2027/10/16 到期**（約 2027/10/01 開始更新）
- ⚠️ Apple Push Services（App 的推播憑證）**2026/11/14 到期**，尚未處理
- 完整紀錄：app01-double 的 `docs/ci-ios-signing-runner-fix.md`

**Why:** 憑證每年到期都會讓三條 iOS pipeline 一起失敗，log 看起來很像環境壞掉。
**How to apply:** 之後遇到 CI iOS 簽章錯誤，先查憑證是否到期，再懷疑 runner 環境。
