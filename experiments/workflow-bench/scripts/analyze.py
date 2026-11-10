#!/usr/bin/env python3
"""分析一次回放：analyze.py <run_dir>  → 寫 <run_dir>/report.json、report.md

只統計「軟體開發角色」的模組（DEV_SKILLS / DEV_AGENTS），其他工具只算總數。
token 來源：claude-home/projects 下的主對話與 subagent transcript（依 message.id 去重）；
費用與回合數：每一輪 stream-json 的 result 事件。
"""
import glob, json, os, re, subprocess, sys, collections

BENCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_SKILLS = ["requirements", "figma-to-requirements", "grilling", "grill-me", "diagnosing-bugs",
              "tdd", "stack-review", "doc-update", "pr"]
DEV_AGENTS = ["code-reviewer", "general-purpose"]
USAGE_KEYS = ["input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"]


def load(path):
    out = []
    for l in open(path, encoding="utf-8"):
        try:
            out.append(json.loads(l))
        except Exception:
            pass
    return out


def transcript_stats(path, label):
    usage = collections.Counter(); seen = set(); seen_tu = set(); calls = []; models = collections.Counter()
    for d in load(path):
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        if m.get("role") == "assistant" and m.get("usage") and m.get("id") not in seen:
            seen.add(m.get("id"))
            for k in USAGE_KEYS:
                usage[k] += m["usage"].get(k) or 0
            models[m.get("model")] += 1
        for c in m.get("content") or [] if isinstance(m.get("content"), list) else []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                if c.get("id") in seen_tu:  # transcript 會重複記同一個 tool_use
                    continue
                seen_tu.add(c.get("id"))
                inp = c.get("input") or {}
                name = c["name"]
                if name == "Skill":
                    calls.append({"where": label, "kind": "skill", "name": inp.get("skill") or inp.get("command"), "ts": d.get("timestamp")})
                elif name in ("Agent", "Task"):
                    calls.append({"where": label, "kind": "agent", "name": inp.get("subagent_type") or "general-purpose",
                                  "desc": inp.get("description"), "ts": d.get("timestamp")})
                else:
                    calls.append({"where": label, "kind": "tool", "name": name, "ts": d.get("timestamp")})
    return usage, calls, models


def main(R):
    R = os.path.abspath(R)
    meta = json.load(open(f"{R}/run.json"))
    sids = list(dict.fromkeys(r["session_id"] for r in meta["rounds"] if r.get("session_id")))
    usage_main, usage_sub = collections.Counter(), collections.Counter()
    calls, models, sub_count = [], collections.Counter(), 0
    for sid in sids:
        for p in glob.glob(f"{BENCH}/claude-home/projects/*/{sid}.jsonl"):
            u, c, m = transcript_stats(p, "main"); usage_main += u; calls += c; models += m
        for p in sorted(glob.glob(f"{BENCH}/claude-home/projects/*/{sid}/subagents/*.jsonl")):
            sub_count += 1
            u, c, m = transcript_stats(p, "sub:" + os.path.basename(p)[:-6]); usage_sub += u; calls += c; models += m

    skill_calls = collections.Counter(c["name"] for c in calls if c["kind"] == "skill")
    agent_calls = collections.Counter(c["name"] for c in calls if c["kind"] == "agent")
    tool_calls = collections.Counter(c["name"] for c in calls if c["kind"] == "tool")
    timeline = [f'{c["where"]}:{c["kind"]}:{c["name"]}' + (f' ({c["desc"]})' if c.get("desc") else "")
                for c in calls if c["kind"] != "tool"]

    # 準確度
    repo = f"{R}/repo"
    chk = json.loads(subprocess.run([sys.executable, "-I", f"{BENCH}/tickets/{meta['ticket']}/check.py", repo, meta["base"]],
                                    capture_output=True, text=True).stdout or "{}")
    lib_changed = [f for f in chk.get("changed_files_all", []) if f.startswith("lib/") and f.endswith(".dart")]
    an = subprocess.run(["flutter", "analyze", "--no-pub", *lib_changed], cwd=repo, capture_output=True, text=True) if lib_changed else None
    analyze_out = (an.stdout + an.stderr) if an else ""
    analyze = {"errors": len(re.findall(r"^\s*error •", analyze_out, re.M)),
               "warnings": len(re.findall(r"^\s*warning •", analyze_out, re.M)),
               "infos": len(re.findall(r"^\s*info •", analyze_out, re.M))}
    tests = chk.get("tests_added", [])
    test_res = None
    if tests:
        files = [f for f in tests if f.endswith("_test.dart")]
        t = subprocess.run(["flutter", "test", "--no-pub", *files], cwd=repo, capture_output=True, text=True)
        platform = "vm"
        if t.returncode != 0 and "dart:html" in (t.stdout + t.stderr):  # 相依鏈含 dart:html → 改用 chrome
            t = subprocess.run(["flutter", "test", "--no-pub", "--platform", "chrome", *files], cwd=repo, capture_output=True, text=True)
            platform = "chrome"
        out = t.stdout + t.stderr
        m = re.findall(r"\+(\d+)(?: -(\d+))?: (?:All tests passed|Some tests failed)", out)
        test_res = {"exit": t.returncode, "platform": platform,
                    "passed": int(m[-1][0]) if m else None, "failed": int(m[-1][1] or 0) if m else None, "tail": out[-400:]}

    docs = sorted(glob.glob(f"{repo}/docs/shared/*.md"))
    task_docs = [os.path.basename(d) for d in docs if os.path.basename(d) != "readme.md"]
    changelog = open(f"{repo}/CHANGELOG.md", encoding="utf-8").read()
    rounds = meta["rounds"]
    report = {
        "run": os.path.basename(R), "version": meta["version"], "ticket": meta["ticket"],
        "rounds": len(rounds), "user_answer_rounds": max(0, len(rounds) - 1),
        "cost_usd": round(sum(r.get("cost_usd") or 0 for r in rounds), 4),
        "wall_s": sum(r.get("wall_s") or 0 for r in rounds),
        "num_turns": sum(r.get("num_turns") or 0 for r in rounds),
        "permission_denials": sum(r.get("permission_denials") or 0 for r in rounds),
        "terminal": [r.get("terminal_reason") for r in rounds],
        "tokens_main": dict(usage_main), "tokens_subagents": dict(usage_sub),
        "tokens_total": dict(usage_main + usage_sub), "subagent_transcripts": sub_count, "models": dict(models),
        "dev_skill_calls": {k: skill_calls.get(k, 0) for k in DEV_SKILLS},
        "other_skill_calls": {k: v for k, v in skill_calls.items() if k not in DEV_SKILLS},
        "agent_calls": dict(agent_calls), "tool_calls_total": sum(tool_calls.values()),
        "tool_calls_top": tool_calls.most_common(10), "timeline": timeline,
        "accuracy": {k: chk.get(k) for k in ["fix_points_pass", "fix_points_review", "fix_points_fail", "fix_points_total",
                                             "file_recall", "file_precision", "truth_files_missed", "extra_lib_files",
                                             "touched_external_libs", "touched_already_correct", "tests_added"]},
        "points": chk.get("points"), "flutter_analyze_changed": analyze, "tests_run": test_res,
        "artifacts": {"task_docs": task_docs, "changelog_updated": meta["ticket"] in changelog or "清除" in changelog,
                      "mr_description": os.path.exists(f"{repo}/MR_DESCRIPTION.md")},
    }
    json.dump(report, open(f"{R}/report.json", "w"), ensure_ascii=False, indent=1)

    a = report["accuracy"]; t = report["tokens_total"]
    md = [f"# {report['run']}", "",
          f"- 版本 {report['version']}｜輪數 {report['rounds']}（使用者回答 {report['user_answer_rounds']} 次）｜回合 {report['num_turns']}｜耗時 {report['wall_s']//60} 分｜費用 ${report['cost_usd']}｜權限拒絕 {report['permission_denials']}",
          f"- 準確度：修正點 {a['fix_points_pass']}/{a['fix_points_total']} PASS（REVIEW {a['fix_points_review']}、FAIL {a['fix_points_fail']}）｜檔案 recall {a['file_recall']}、precision {a['file_precision']}",
          f"- 漏改 {a['truth_files_missed']}｜多改 {a['extra_lib_files']}｜動到 external_libs {a['touched_external_libs']}｜動到原本正確的檔 {a['touched_already_correct']}",
          f"- 測試：新增 {a['tests_added']}｜執行 {test_res and test_res['exit']}｜analyze（改到的檔）{analyze}",
          f"- token：input {t.get('input_tokens',0):,}｜cache 建立 {t.get('cache_creation_input_tokens',0):,}｜cache 讀取 {t.get('cache_read_input_tokens',0):,}｜output {t.get('output_tokens',0):,}（subagent transcript {sub_count} 份）",
          f"- 開發模組叫用：{ {k:v for k,v in report['dev_skill_calls'].items() if v} }｜subagent：{report['agent_calls']}",
          f"- 產出：任務文件 {task_docs}｜CHANGELOG {report['artifacts']['changelog_updated']}｜MR 說明 {report['artifacts']['mr_description']}",
          "", "## 時間線（skill／agent）", *[f"1. {x}" for x in timeline]]
    open(f"{R}/report.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1])
