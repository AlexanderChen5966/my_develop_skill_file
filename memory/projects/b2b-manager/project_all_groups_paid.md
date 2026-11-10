---
name: project-all-groups-paid
description: 目前沒有分免費版／專業版，所有公司都是專業版；基本版畫面與升級提醒卡片不需實機驗證
metadata:
  node_type: memory
  type: project
  modified: 2026-11-03 08:58:45.323000+00:00
  originSessionId: e8ff2875-7c38-41b0-a211-32f958a49b20
permalink: agents-memory/projects/b2b-manager/project-all-groups-paid
---

目前沒有分免費版與專業版，所有公司都是專業版（使用者 2026-11-03 確認）。

**Why:** Flutter 仍保留 `isPaidUser`（看 `/api/user/groups` 的 `paidSubscriber`）切換「專業版／基本版」標章與側選單的升級提醒卡片 `UnPaidRemind`，但實際資料都是付費，基本版畫面在真實環境看不到。

**How to apply:** 遷移或驗收時不要把「基本版／升級卡片」列成待驗證項目，也不必找基本版公司實測；程式照 Flutter 保留 `paidSubscriber` 判斷即可（React 主框架已如此），除非使用者要求移除。相關：[[project-react-nextjs-migration]]