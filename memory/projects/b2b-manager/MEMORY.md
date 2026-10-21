# Memory Index

> b2b-manager 專案層記憶。個人層與跨專案層見 `~/.agents/memory/global/MEMORY.md`、`~/.agents/memory/shared/MEMORY.md`。
> 任務進度不放這裡，放 `.handoff/`。

- [feedback_layout_min_width.md](feedback_layout_min_width.md) — 雙面板頁面最小寬度 1400px + 水平捲軸防止縮放崩版
- [禁用 screenutil](feedback_no_screenutil.md) — 新增／修改程式碼不用 .w/.h/.sp，改固定 px（已寫入 AGENTS.md）
- [feedback_subagent_delegation.md](feedback_subagent_delegation.md) — 不採用自動 subagent 分工；僅盤點/跨 repo/3+獨立樣板才派工
- [project_batch_edit_car.md](project_batch_edit_car.md) — 批次編輯車輛頁面拆分與重構記錄（SSGS-7469）
- [車輛資料量級](project_car_data_volume.md) — 正式區最多約 3 萬台，staging 29 萬是測試資料；大量資料處理屬預先補強
- [dashboard 卡片刷新依賴 remount](project_dashboard_switch_company_remount_regression.md) — 卡片只在 initState 打 API；已用 listen(selectCompany.id)+X_Group_Id 去重修好；context.replace 不重建 const route；勿 select(groups)
- [i18n 只有繁中生效](project_i18n_zh_tw_only.md) — 新 key 只寫繁中，en/zh_CN 填同一句
- [RWD／重寫評估](project_rwd_rewrite_evaluation.md) — 2026-10-21 評估未立案；結論與工時在 docs/shared/rwd_and_web_rewrite_evaluation.md；重寫不需 Next/Nuxt
- [流程展示 Artifact 樣板](reference_artifact_style_ssgs3444.md) — 參考 docs/assets/SSGS-3444 測試報告.html：流程站＋MCP 工具 chip＋播放控制、摘要三格、details 步驟
- [staging 實機驗證的語意](reference_staging_run_semantics.md) — DEPLOY=staging 只切 API URL，前端仍是本機工作區，不可推論已部署環境
