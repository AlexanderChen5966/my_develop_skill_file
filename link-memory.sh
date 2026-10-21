#!/usr/bin/env bash
# 把 Claude Code 的專案記憶接到共用記憶 ~/.agents/memory/projects/<專案>/。
#
#   ~/.agents/link-memory.sh          接上（預設，等同 link）
#   ~/.agents/link-memory.sh check    只檢查，不修改：各專案狀態＋孤兒記憶
#   ~/.agents/link-memory.sh unlink   把 symlink 換回實體資料夾（複製一份回去，共用記憶不動）
#
# link／check 也會同步／檢查其他 agent 的全域指引（GUIDE → GUIDE_TARGETS）。
#
# 做法：Claude 的 ~/.claude/projects/<編碼路徑>/memory 改成 symlink，指向共用記憶。
# Claude 照原本方式讀寫；其他 agent 讀 ~/.agents/memory/projects/<專案>/。
# 專案範圍寫在 ROOTS——每個 root 底下的 git 專案都納入，專案名稱＝資料夾名稱。
#
# 安全原則：
# - 絕不刪除有內容的檔案；兩邊都有內容時只回報、跳過
# - 沒有記憶的專案不預先建立（用到時才建；Claude 第一次寫入後，下次執行 link 就會接上）

set -u
MEM="$HOME/.agents/memory/projects"
CLAUDE_PROJECTS="$HOME/.claude/projects"
ROOTS=(
  "$HOME/GitLab"
)

# 其他 agent 的全域指令檔：內容整份由 GUIDE 同步（2026-10-21 以 canary 實測各工具確實讀取）。
# Claude Code 不在這裡——它用 ~/.claude/CLAUDE.md 的 @ 引入直接讀記憶索引。
# Cursor CLI 沒有全域指令檔（只讀專案 AGENTS.md／CLAUDE.md／.cursor/rules），靠專案 AGENTS.md。
GUIDE="$HOME/.agents/memory-guide.md"
GUIDE_TARGETS=(
  "$HOME/.codex/AGENTS.md"                  # Codex
  "$HOME/.copilot/copilot-instructions.md"  # Copilot CLI
  "$HOME/.config/opencode/AGENTS.md"        # opencode（沒有這個檔時不會改讀 CLAUDE.md）
  "$HOME/.gemini/AGENTS.md"                 # agy（也會讀 ~/.gemini/GEMINI.md，那份不動）
)
GUIDE_MARK="由 ~/.agents/link-memory.sh 同步"

mode="${1:-link}"
case "$mode" in link|check|unlink) ;; *) echo "用法：$0 [link|check|unlink]"; exit 2 ;; esac
[ -d "$CLAUDE_PROJECTS" ] || { echo "❌ 找不到 $CLAUDE_PROJECTS"; exit 1; }

# Claude Code 的專案資料夾編碼：絕對路徑中非英數字元一律換成 -
encode() { printf '%s' "$1" | sed 's/[^A-Za-z0-9]/-/g'; }

# 資料夾是否有檔案（含隱藏檔）
has_files() { [ -n "$(ls -A "$1" 2>/dev/null)" ]; }

problems=0
canon=()   # 已處理的 Claude 資料夾名稱，給孤兒偵測用

for root in "${ROOTS[@]}"; do
  [ -d "$root" ] || continue
  echo "── ${root/#$HOME/~}"
  for proj in "$root"/*/; do
    proj="${proj%/}"
    [ -d "$proj/.git" ] || continue
    name="$(basename "$proj")"
    enc="$(encode "$proj")"
    canon+=("${enc}")
    cdir="$CLAUDE_PROJECTS/${enc}/memory"
    mdir="$MEM/${name}"

    if [ -L "${cdir}" ]; then
      if [ "$(readlink "${cdir}")" = "${mdir}" ] && [ -d "${mdir}" ]; then
        if [ "$mode" = unlink ]; then
          rm "${cdir}" && cp -R "${mdir}" "${cdir}" && echo "  ↩️  ${name}（已換回實體資料夾）"
        else
          echo "  ✅ ${name}"
        fi
      else
        echo "  ⚠️  ${name}：symlink 指向 $(readlink "${cdir}")，不是共用記憶"
        problems=$((problems + 1))
      fi
      continue
    fi

    [ "$mode" = unlink ] && continue

    if [ -d "${cdir}" ]; then
      if ! has_files "${cdir}" && ! { [ -d "${mdir}" ] && has_files "${mdir}"; }; then
        # 兩邊都空：沒有記憶，不接
        continue
      fi
      if [ -d "${mdir}" ] && has_files "${mdir}" && has_files "${cdir}"; then
        if diff -rq "${cdir}" "${mdir}" >/dev/null 2>&1; then
          # 兩邊內容完全相同（例如 unlink 後再 link）：Claude 端是副本，可直接換成連結
          if [ "$mode" = check ]; then
            echo "  🔸 ${name}：尚未接上（兩邊內容相同，link 可直接接上）"
            problems=$((problems + 1))
          else
            rm -r "${cdir}" && ln -s "${mdir}" "${cdir}" && echo "  🔗 ${name}（內容相同，已接上）"
          fi
          continue
        fi
        echo "  ❌ ${name}：Claude 與共用記憶兩邊都有內容，需手動合併後再執行"
        problems=$((problems + 1))
        continue
      fi
      if [ "$mode" = check ]; then
        echo "  🔸 ${name}：尚未接上（Claude 端為實體資料夾）"
        problems=$((problems + 1))
        continue
      fi
      mkdir -p "$MEM"
      if has_files "${cdir}"; then
        # Claude 端有內容、共用端沒有（或為空）：搬過去
        [ -d "${mdir}" ] && rmdir "${mdir}"
        mv "${cdir}" "${mdir}" || { echo "  ❌ ${name}：搬移失敗"; problems=$((problems + 1)); continue; }
      else
        # Claude 端為空、共用端有內容
        rmdir "${cdir}"
      fi
      ln -s "${mdir}" "${cdir}" && echo "  🔗 ${name}（已接上）"
    elif [ -d "${mdir}" ]; then
      # 共用端有記憶，但 Claude 從沒在這個專案開過
      if [ "$mode" = check ]; then
        echo "  🔸 ${name}：共用記憶存在，Claude 端尚未連結"
        problems=$((problems + 1))
      else
        mkdir -p "$(dirname "${cdir}")" && ln -s "${mdir}" "${cdir}" && echo "  🔗 ${name}（已建立連結）"
      fi
    fi
  done
done

# 其他 agent 的全域指引：只覆寫「不存在」或「本腳本產生過（含 GUIDE_MARK）」的檔案
if [ "$mode" != unlink ] && [ -f "$GUIDE" ]; then
  echo "── 其他 agent 的全域指引"
  for t in "${GUIDE_TARGETS[@]}"; do
    short="${t/#$HOME/~}"
    if [ -f "$t" ] && cmp -s "$GUIDE" "$t"; then
      echo "  ✅ ${short}"
    elif [ -f "$t" ] && ! grep -q "$GUIDE_MARK" "$t"; then
      echo "  ❌ ${short}：已有使用者自己的內容，不覆寫；請手動合併"
      problems=$((problems + 1))
    elif [ "$mode" = check ]; then
      echo "  🔸 ${short}：$( [ -f "$t" ] && echo 內容過時 || echo 不存在 )"
      problems=$((problems + 1))
    else
      mkdir -p "$(dirname "$t")" && cp "$GUIDE" "$t" && echo "  📝 ${short}（已同步）"
    fi
  done
fi

# 孤兒記憶：同一個專案從其他路徑開啟（worktree、Downloads 副本、scratchpad）產生的記憶
if [ "$mode" != unlink ]; then
  echo "── 孤兒記憶（其他路徑開啟同一專案產生）"
  found=0
  for d in "$CLAUDE_PROJECTS"/*/memory; do
    [ -e "$d" ] || continue
    [ -L "$d" ] && continue
    enc="$(basename "$(dirname "$d")")"
    skip=0
    for c in ${canon[@]+"${canon[@]}"}; do [ "$c" = "${enc}" ] && skip=1 && break; done
    [ $skip = 1 ] && continue
    for root in "${ROOTS[@]}"; do
      for proj in "$root"/*/; do
        name="$(basename "${proj%/}")"
        pat="$(encode "${name}")"
        case "${enc}" in
          *-"$pat"-*|*-"$pat")
            n=$(ls -A "$d" | wc -l | tr -d ' ')
            if [ "${n}" = 0 ]; then
              echo "  ⚪ ${enc}（空，可刪除）"
            else
              echo "  🟡 ${enc}（${n} 個檔案，可能需合併到 ${name}）"
              problems=$((problems + 1))
            fi
            found=1
            break 2
            ;;
        esac
      done
    done
  done
  [ $found = 0 ] && echo "  （無）"
fi

if [ $problems -eq 0 ]; then echo "✅ 沒有問題"; else echo "⚠️  $problems 個項目需要處理"; fi
[ $problems -eq 0 ]
