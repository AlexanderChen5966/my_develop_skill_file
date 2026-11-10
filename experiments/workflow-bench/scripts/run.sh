#!/usr/bin/env bash
# 跑一輪：scripts/run.sh <run_dir> [回答檔]
#   沒有回答檔 → 第一輪（送出題目）；有回答檔 → --resume 接續上一輪
# 權限：settings.json 白名單（讀檔、改 repo 內檔案、flutter/dart、唯讀 git）；其他工具在 -p 模式下自動拒絕
set -euo pipefail
BENCH="$(cd "$(dirname "$0")/.." && pwd)"
R="$(cd "$1" && pwd)"; ANS="${2:-}"
TICKET=$(python3 -c "import json;print(json.load(open('$R/run.json'))['ticket'])")
source "$BENCH/tickets/$TICKET/meta.env"
N=$(ls "$R/rounds" | grep -c '\.jsonl$' || true); N=$((N+1)); NN=$(printf %02d $N)

ARGS=(-p --model claude-opus-5-5 --output-format stream-json --verbose
      --settings "$BENCH/settings.json" --max-budget-usd 30)
if [ -z "$ANS" ]; then
  PROMPT=$(python3 - "$BENCH/prompt.md" "$BENCH/tickets/$TICKET/ticket.md" "$BRANCH" <<'EOF'
import sys; p=open(sys.argv[1]).read(); t=open(sys.argv[2]).read().strip()
print(p.replace('{{TICKET}}',t).replace('{{BRANCH}}',sys.argv[3]))
EOF
)
else
  SID=$(python3 -c "import json;print(json.load(open('$R/run.json'))['rounds'][-1]['session_id'])")
  PROMPT="$(cat "$ANS")"; ARGS+=(--resume "$SID"); cp "$ANS" "$R/rounds/$NN.answer.md"
fi

cd "$R/repo"
START=$(date +%s)
CLAUDE_CONFIG_DIR="$BENCH/claude-home" claude "${ARGS[@]}" "$PROMPT" > "$R/rounds/$NN.jsonl" 2> "$R/rounds/$NN.stderr" || true
END=$(date +%s)

python3 - "$R" "$NN" "$START" "$END" <<'EOF'
import json, sys
R, NN, s, e = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
sid, result = None, {}
for l in open(f"{R}/rounds/{NN}.jsonl"):
    try: d = json.loads(l)
    except Exception: continue
    sid = d.get("session_id") or sid
    if d.get("type") == "result": result = d
open(f"{R}/rounds/{NN}.result.md", "w").write(result.get("result") or "(沒有 result，見 stderr)")
meta = json.load(open(f"{R}/run.json"))
meta["rounds"].append({"round": NN, "session_id": sid, "wall_s": e - s,
    "cost_usd": result.get("total_cost_usd"), "num_turns": result.get("num_turns"),
    "permission_denials": len(result.get("permission_denials") or []),
    "terminal_reason": result.get("terminal_reason") or result.get("subtype")})
json.dump(meta, open(f"{R}/run.json", "w"), ensure_ascii=False, indent=1)
print(f"round {NN}: session={sid} turns={result.get('num_turns')} cost={result.get('total_cost_usd')} wall={e-s}s denials={len(result.get('permission_denials') or [])}")
EOF
echo "--- 這一輪最後的回覆：$R/rounds/$NN.result.md"
