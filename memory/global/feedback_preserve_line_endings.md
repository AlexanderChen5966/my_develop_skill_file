---
name: feedback_preserve_line_endings
description: 改既有檔案優先用 Edit 工具；用 Python 改檔要 newline='' 或二進位模式，改完看 git diff --stat，避免
  CRLF 被轉成 LF 造成整檔 diff
metadata:
  type: feedback
  modified: 2026-11-03
permalink: agents-memory/global/feedback-preserve-line-endings
---

改既有檔案時，**優先用 Edit 工具**，它不會動換行字元。必須用 Python 改檔時，讀寫都加 `newline=''`（或用 `'rb'` / `'wb'` 處理 bytes）；改完一律跑 `git diff --stat`，行數遠超預期就是換行被改了。

**Why:** Python `open()` 文字模式預設 universal newlines，讀檔把 `\r\n` 轉成 `\n`，寫檔在 macOS／Linux 寫 `\n`，CRLF 檔案讀進來再寫出去整檔變 LF，git 看到每行都不同。專案裡 CRLF 與 LF 檔案混用，改之前看不出來。2026-11-03 在 app01-double 改 `phone_verification.dart`（原為 CRLF）時實際踩到，整檔出現在 diff，事後以二進位模式還原。

**How to apply:**
- 多段取代也先考慮 Edit（可多次呼叫）；只有批次或腳本化需求才用 Python
- Python 寫法：`open(p, encoding='utf-8', newline='').read()` 與 `open(p, 'w', encoding='utf-8', newline='').write(s)`
- 改前可用 `git show HEAD:<檔> | file -` 確認原檔換行（`with CRLF line terminators` 即 CRLF）
- 還原：以 `'rb'` 讀入，`replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')` 後以 `'wb'` 寫回
- 不在版控的檔案（如 `docs/`）沒有 diff 可看，更要靠 Edit 工具避免改到換行