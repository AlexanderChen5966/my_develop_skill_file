---
name: project_dockerize_dind_mtu
description: dockerize job 在 GitLab SaaS runner 的 dind 內 apt-get 逾時＝MTU 不一致；已用 docker build --network host 繞過
metadata:
  node_type: memory
  type: project
  originSessionId: f838ebc2-fd28-4c3d-9a04-dedaa83be7cf
  modified: 2026-10-14T00:59:19.373Z
---

2026-10-13 打 tag `stage-3.6.6` 時 dockerize job 連兩次失敗：Dockerfile `apt-get update` 對 deb.debian.org 出現 `Get:… [140 kB]` 後 30 秒 `Connection timed out`。同設定的 stage-3.6.5（2026-09-23）是成功的。

成因（GitLab 官方於 2026-05 說明）：saas-linux-small-amd64 外層 Docker MTU 被調成 1360，dind 內層 bridge 預設 1500，大封包被靜默丟棄，連線會卡住。job 容器與 dind daemon 本身走 1360，所以不受影響。

處置：branch `feature/handle-dockerize-fail`（44fd5309）在 `.gitlab-ci.yml` 的 docker build 加 `--network host`，pipeline 已成功。根治方式是在 dind service 加 `command: ["--mtu=1360"]`，尚未採用。

**Why:** 重跑舊 tag 會沿用舊的 .gitlab-ci.yml，修正必須先進 main 再重打 tag。
**How to apply:** CI 再出現 dind 內外連逾時的狀況，先往 MTU 方向查，不要當成外部網站故障。CI build 用的 Flutter 是 Dockerfile 的 3.35.4，本機是 3.38.0。
