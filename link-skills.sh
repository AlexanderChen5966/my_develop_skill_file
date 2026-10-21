#!/usr/bin/env bash
# 把 ~/.agents/skills/ 底下的每個 skill 連結到「不讀 ~/.agents/skills 的工具」。
#
#   ~/.agents/link-skills.sh          建立缺少的 symlink（預設，等同 link）
#   ~/.agents/link-skills.sh check    只檢查，不修改：缺少／失效／被實體資料夾佔用
#   ~/.agents/link-skills.sh unlink   移除本腳本建立的 symlink（只刪指向本體的 symlink）
#
# 原生讀 ~/.agents/skills 的工具不需要連結：Codex、Copilot CLI、opencode（依各自官方文件）。
# 需要連結的工具與路徑寫在 TARGETS——工具改路徑時只改這裡。
#
# 安全原則：絕不覆寫或刪除實體檔案／資料夾；遇到同名實體資料夾只回報、跳過。

set -u
SRC="$HOME/.agents/skills"
TARGETS=(
  "$HOME/.claude/skills"                    # Claude Code
  "$HOME/.gemini/config/skills"             # Antigravity CLI（agy）
  # ⚠️ agy 路徑以實測為準：官方網頁寫 ~/.gemini/antigravity-cli/skills，但 agy 1.4.2 實際只讀
  #    ~/.gemini/config/skills（2026-10-19 實測：前者放實體資料夾也讀不到；後者實體與 symlink 皆可）。
  #    ~/.gemini/config/skills.json 的 entries 指向 ~/.agents/skills 同樣實測無效。agy 升版後先重測。
)

mode="${1:-link}"
case "$mode" in link|check|unlink) ;; *) echo "用法：$0 [link|check|unlink]"; exit 2 ;; esac
[ -d "$SRC" ] || { echo "❌ 找不到本體資料夾 $SRC"; exit 1; }

problems=0
for target in "${TARGETS[@]}"; do
  echo "── ${target/#$HOME/~}"
  [ "$mode" = link ] && mkdir -p "$target"

  for skill in "$SRC"/*/; do
    [ -f "$skill/SKILL.md" ] || continue          # 只處理真正的 skill 資料夾
    name="$(basename "$skill")"
    want="$SRC/${name}"
    dest="$target/${name}"

    if [ -L "$dest" ]; then
      if [ "$(readlink "$dest")" = "$want" ]; then
        if [ "$mode" = unlink ]; then rm "$dest" && echo "  🗑  ${name}（已移除連結）"
        else echo "  ✅ ${name}"; fi
      else
        echo "  ⚠️  ${name} → 指向別處：$(readlink "$dest")（未處理）"; problems=$((problems+1))
      fi
    elif [ -e "$dest" ]; then
      echo "  ⚠️  ${name} 已是實體資料夾，跳過（不會覆寫；要改用共用版請自行先移走）"; problems=$((problems+1))
    else
      case "$mode" in
        link)   ln -s "$want" "$dest" && echo "  🔗 ${name}（新建連結）" ;;
        check)  echo "  ❌ ${name} 尚未連結（執行 link 補上）"; problems=$((problems+1)) ;;
        unlink) ;;
      esac
    fi
  done

  # 失效連結：指向本體、但本體已不存在（改名或刪除後殘留）
  for dest in "$target"/*; do
    [ -L "$dest" ] || continue
    link="$(readlink "$dest")"
    case "$link" in "$SRC"/*) ;; *) continue ;; esac
    if [ ! -e "$dest" ]; then
      if [ "$mode" = check ]; then
        echo "  💀 $(basename "$dest") 失效連結 → $link"; problems=$((problems+1))
      else
        rm "$dest" && echo "  🧹 $(basename "$dest")（移除失效連結）"
      fi
    fi
  done
done

[ "$problems" -eq 0 ] && echo "✅ 沒有問題" || echo "⚠️ $problems 個項目需要處理"
[ "$problems" -eq 0 ]
