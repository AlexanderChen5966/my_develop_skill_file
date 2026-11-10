#!/usr/bin/env bash
# 建立一次回放：scripts/setup_run.sh <ticket> <version> <n>
# 產出 runs/<ticket>-<version>-r<n>/{origin.git,repo,run.json}
set -euo pipefail
BENCH="$(cd "$(dirname "$0")/.." && pwd)"
TICKET="$1"; VER="$2"; N="$3"
source "$BENCH/tickets/$TICKET/meta.env"
[ -d "$BENCH/versions/$VER/skills" ] || { echo "沒有版本 $VER"; exit 1; }
R="$BENCH/runs/$TICKET-$VER-r$N"
[ -e "$R" ] && { echo "已存在 $R"; exit 1; }
mkdir -p "$R/rounds"

# 1. 只保留到 BASE_COMMIT 的歷史（未來的 commit 與答案分支都不帶進來）
git clone -q --bare --no-tags "$SOURCE_REPO" "$R/origin.git"
git -C "$R/origin.git" for-each-ref --format='%(refname)' | while read -r ref; do
  git -C "$R/origin.git" update-ref -d "$ref"; done
git -C "$R/origin.git" update-ref refs/heads/main "$BASE_COMMIT"
git -C "$R/origin.git" symbolic-ref HEAD refs/heads/main
git -C "$R/origin.git" reflog expire --expire=now --all
git -C "$R/origin.git" gc -q --prune=now
git -C "$R/origin.git" cat-file -e "$TRUTH_COMMIT" 2>/dev/null && { echo "❌ 答案 commit 還在"; exit 1; }

git clone -q "$R/origin.git" "$R/repo"
git -C "$R/repo" checkout -q -b "$BRANCH"

# 2. 不在版控的專案脈絡（濾掉會洩漏答案的）
S="$SOURCE_REPO"; D="$R/repo"
for f in AGENTS.md CLAUDE.md DESIGN.md .claudeignore; do [ -e "$S/$f" ] && cp -p "$S/$f" "$D/$f"; done
mkdir -p "$D/.claude"; cp -Rp "$S/.claude/rules" "$D/.claude/rules"
rsync -a --exclude 'shared/' --exclude 'issue/' --exclude 'agent-handoff/' --exclude '.DS_Store' "$S/docs/" "$D/docs/"
cat > "$D/CHANGELOG.md" <<'EOF'
# B2B Manager 變更記錄

本文件記錄 B2B Manager 專案的重要變更。所有值得注意的變更都會記錄在這個檔案中。

**格式遵循：** [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)

---

## [Unreleased]
EOF
if grep -rqE "$TICKET|${TICKET#SSGS-}" "$D/docs" "$D"/*.md "$D/.claude/rules" 2>/dev/null; then
  echo "❌ 脈絡檔仍提到 $TICKET："; grep -rlE "$TICKET" "$D/docs" "$D"/*.md "$D/.claude/rules"; exit 1; fi

# 3. 凍結的版本 skill 放專案層
cp -Rp "$BENCH/versions/$VER/skills" "$D/.claude/skills"
# 版本若有個人層記憶的替代品（bench 不讀 ~/.agents/memory），以專案層 CLAUDE.local.md 帶入
[ -f "$BENCH/versions/$VER/CLAUDE.local.md" ] && cp -p "$BENCH/versions/$VER/CLAUDE.local.md" "$D/CLAUDE.local.md"
grep -qx 'CLAUDE.local.md' "$D/.git/info/exclude" 2>/dev/null || echo 'CLAUDE.local.md' >> "$D/.git/info/exclude"

# 4. 依賴
(cd "$D" && flutter pub get >/dev/null 2>&1) || echo "⚠️ flutter pub get 失敗"

cat > "$R/run.json" <<EOF
{"ticket":"$TICKET","version":"$VER","n":$N,"base":"$BASE_COMMIT","branch":"$BRANCH","created":"$(date '+%F %T')","model":"claude-opus-5-5","rounds":[]}
EOF
echo "✅ $R"
