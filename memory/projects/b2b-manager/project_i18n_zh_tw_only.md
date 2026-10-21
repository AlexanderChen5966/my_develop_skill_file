---
name: project-i18n-zh-tw-only
description: 本專案 i18n 實際只有繁體中文生效，en/zh_CN 的 arb 不需翻譯
metadata: 
  node_type: memory
  type: project
  originSessionId: d4d587cf-ef0c-4be9-826d-379ba38613cb
  modified: 2026-08-26T09:30:00.000Z
---

寫新 i18n key 時**只需要繁體中文**，`intl_en.arb` / `intl_zh_CN.arb` 的值一律填**同一句繁中**（三份 arb 都要有 key，產生器需要 key 齊全，但那兩份的內容永遠不會被顯示）。

**Why:** `lib/main.dart:158` 硬寫 `locale: const Locale('zh', 'TW')`，且 app 沒有語言切換入口。現況佐證（2026-08-26 實測）：三份 arb 各 1038 個 key，其中 **1034 個是繁中原文照抄**，只有 4 個 `not_restrict_*` 曾真的翻譯過。arb 檔看起來是三語系，很容易誤判成需要翻譯。

**How to apply:** 任務文件與實作都不要列 zh_CN / en 譯文欄位，也不要把「三語系文案皆正確」寫進驗收清單——改成「繁中文案正確」即可。若日後真要開多語，需先加語言切換並回填 1034 個 key，屆時屬獨立任務。

**後端側一致（2026-08-26，b2b-backend session 回報）：** `GET /public/enums` 的 `locale` 參數（`PublicController.listEnums()`）**完全沒被讀取**，`label` 一律來自中文常數，傳 `en_US` 與 `zh_TW` 回應相同。前端仍必須傳（`required`，不傳會 400），但**不需要做語系判斷**。故「只有繁中生效」是前後端一致的現況，不是前端單方面簡化。

相關：[[feedback-no-screenutil]]
