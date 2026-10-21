#!/usr/bin/env python3
"""multiagent-handoff skill 的確定性部分：git 快照、分派基準、範圍檢查、對話紀錄備援。

所有子指令都只讀 git / 寫 .handoff/，不修改工作區檔案、不 commit。

  handoff.py init                     建 .handoff/ 並加入 .git/info/exclude
  handoff.py snapshot                 目前分支 / HEAD / 未提交修改摘要（save、resume 用）
  handoff.py new-task <slug> [--to X] 開任務單，記錄分派當下的基準（delegate 用）
  handoff.py run <task-id> --agent A  以非互動模式叫起指定 agent 執行 report（delegate --run 用）
  handoff.py review <task-id>         列出分派後實際改動的檔案、標出超出範圍者（review 用）
  handoff.py sessions [--tool T]      前一手的對話紀錄摘要（resume 找不到交接檔時的備援）
  handoff.py log "<內容>"             在 .handoff/log.md 追加一行
"""
import argparse
import datetime
import fnmatch
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HANDOFF = '.handoff'
# realpath：經由 symlink（~/.claude/skills/multiagent-handoff 等）呼叫時，一律解析回本體 ~/.agents/skills/multiagent-handoff
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SCRIPT = os.path.join(SKILL_DIR, 'scripts', 'handoff.py')


def sh(cmd, check=True):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f'❌ {" ".join(cmd)}\n{r.stderr.strip()}')
    return r.stdout.rstrip('\n')


def repo_root():
    r = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('❌ 不在 git repo 內——handoff 以 git 為狀態來源，無法運作')
    return r.stdout.strip()


ROOT = repo_root()


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')


def untracked():
    out = sh(['git', 'ls-files', '--others', '--exclude-standard'])
    return [f for f in out.splitlines() if f and not f.startswith(HANDOFF + '/')]


def file_hash(path):
    try:
        with open(os.path.join(ROOT, path), 'rb') as fh:
            return hashlib.sha1(fh.read()).hexdigest()
    except OSError:
        return None


# ---------------------------------------------------------------- init

def cmd_init(_):
    os.makedirs(os.path.join(ROOT, HANDOFF, 'tasks'), exist_ok=True)
    git_dir = sh(['git', 'rev-parse', '--git-common-dir'])
    exclude = os.path.join(ROOT, git_dir, 'info', 'exclude')
    os.makedirs(os.path.dirname(exclude), exist_ok=True)
    lines = open(exclude).read().splitlines() if os.path.exists(exclude) else []
    if f'{HANDOFF}/' not in lines:
        with open(exclude, 'a') as fh:
            fh.write(f'\n# multiagent-handoff skill（本機交接檔，不進 git）\n{HANDOFF}/\n')
        print(f'✅ 已將 `{HANDOFF}/` 加入 .git/info/exclude')
    else:
        print(f'⏭ `{HANDOFF}/` 已在 .git/info/exclude')
    print(f'✅ `{HANDOFF}/tasks/` 就緒')


# ---------------------------------------------------------------- snapshot

def cmd_snapshot(_):
    print(f'- repo：`{ROOT}`')
    print(f'- 分支：`{sh(["git", "branch", "--show-current"]) or "(detached)"}`')
    print(f'- HEAD：`{sh(["git", "log", "-1", "--format=%h %s"])}`')
    print(f'- 時間：{now()}\n')
    status = sh(['git', 'status', '--short', '--', '.', f':(exclude){HANDOFF}'])
    if not status:
        print('工作區乾淨（無未提交修改）')
        return
    print('### 未提交修改（git status --short）\n```')
    print(status)
    print('```\n### 變更量（tracked，含 staged）\n```')
    print(sh(['git', 'diff', 'HEAD', '--stat']) or '(只有 untracked 檔案)')
    print('```')
    cur = os.path.join(ROOT, HANDOFF, 'CURRENT.md')
    if os.path.exists(cur):
        age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(cur))
        print(f'\nℹ️ `CURRENT.md` 最後更新於 {int(age.total_seconds() // 60)} 分鐘前')
        newer = [f for f in status_files(status)
                 if os.path.exists(os.path.join(ROOT, f))
                 and os.path.getmtime(os.path.join(ROOT, f)) > os.path.getmtime(cur)]
        if newer:
            print(f'⚠️ 有 {len(newer)} 個檔案在 CURRENT.md 之後才被修改（交接檔可能過期）：')
            for f in newer[:20]:
                print(f'  - `{f}`')
    else:
        print('\nℹ️ 尚無 `CURRENT.md`')


def status_files(status):
    files = []
    for line in status.splitlines():
        path = line[3:]
        if ' -> ' in path:
            path = path.split(' -> ', 1)[1]
        files.append(path.strip('"'))
    return files


# ---------------------------------------------------------------- delegate

TASK_TEMPLATE = """# 任務：{title}
- 任務 ID：{tid}
- 對應需求：（docs/shared/xxx.md，沒有就寫「無」）
- 分支：{branch}
- 開始時的 commit：{head}
- 分派基準 ref：`{ref}`（含分派當下未提交的修改，驗收以此為準）
- 指派給：{to}
- 建立時間：{created}
- 狀態：待執行

## 目標

## 可以動的檔案
<!-- 每行一個 `路徑或 glob`（反引號包住），review 會依此檢查範圍 -->

## 不能動的檔案
<!-- 同上格式 -->

## 禁止事項
<!-- 專案硬規則中與本任務相關者，例：禁止 .w/.h/.sp、禁止改 DataTable2 fixedWidth -->

## 完成標準
<!-- 可執行的驗證指令優先，例：flutter analyze 無新錯誤 -->

## 背景資訊

---
## 回報（由被分派的 agent 填寫）
### 修改內容（每檔一行）
### 驗證方式與結果（貼實際指令與輸出摘要）
### 未處理事項／疑問

---
## 驗收結果（由主 agent 填寫）
"""


def cmd_new_task(a):
    cmd_init_quiet()
    slug = re.sub(r'[^\w-]+', '-', a.slug).strip('-').lower() or 'task'
    tid = f'{datetime.date.today():%Y%m%d}-{slug}'
    path = os.path.join(ROOT, HANDOFF, 'tasks', f'{tid}.md')
    if os.path.exists(path):
        sys.exit(f'❌ 任務單已存在：{path}')
    head = sh(['git', 'rev-parse', '--short', 'HEAD'])
    # `git stash create` 產生涵蓋「目前 tracked 修改」的 commit 物件，不動工作區。
    # 工作區乾淨時回傳空字串，此時基準就是 HEAD。
    base = sh(['git', 'stash', 'create', f'handoff base {tid}']) or sh(['git', 'rev-parse', 'HEAD'])
    ref = f'refs/handoff/{tid}'
    sh(['git', 'update-ref', ref, base])  # 防止 stash 物件被 gc
    meta = {'base': base, 'ref': ref, 'head': head,
            'untracked': {f: file_hash(f) for f in untracked()}}
    with open(path[:-3] + '.base.json', 'w') as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    with open(path, 'w') as fh:
        fh.write(TASK_TEMPLATE.format(
            title=a.slug, tid=tid, branch=sh(['git', 'branch', '--show-current']),
            head=head, ref=ref, to=a.to or '（待填）', created=now()))
    dirty = base != sh(['git', 'rev-parse', 'HEAD'])
    print(f'✅ 任務單：{os.path.relpath(path, ROOT)}')
    print(f'✅ 基準：`{ref}` → {base[:10]}' + ('（含分派當下的未提交修改）' if dirty else '（= HEAD）'))
    print(f'   untracked 檔案 {len(meta["untracked"])} 個已記錄雜湊')


def cmd_init_quiet():
    if not os.path.isdir(os.path.join(ROOT, HANDOFF, 'tasks')):
        cmd_init(None)


# ---------------------------------------------------------------- review

def section_body(text, heading):
    """某個 `## 標題` 底下的內容（去掉 HTML 註解）；標題不存在回傳空字串。"""
    m = re.search(rf'^## {heading}\s*\n(.*?)(?=^## |^---|\Z)', text, re.S | re.M)
    return re.sub(r'<!--.*?-->', '', m.group(1), flags=re.S).strip() if m else ''


def section_globs(text, heading):
    return re.findall(r'`([^`]+)`', section_body(text, heading))


def match(path, globs):
    return any(fnmatch.fnmatch(path, g) or path == g.rstrip('/') or path.startswith(g.rstrip('/') + '/')
               for g in globs)


def find_task(task_id):
    tdir = os.path.join(ROOT, HANDOFF, 'tasks')
    path = os.path.join(tdir, task_id if task_id.endswith('.md') else task_id + '.md')
    if os.path.exists(path):
        return path
    cands = sorted(glob.glob(os.path.join(tdir, f'*{task_id}*.md')))
    if len(cands) != 1:
        sys.exit(f'❌ 找不到唯一的任務單：{task_id}（候選 {len(cands)} 個）')
    return cands[0]


def task_status(text):
    m = re.search(r'^- 狀態：\s*(\S+)', text, re.M)
    return m.group(1) if m else None


# ---------------------------------------------------------------- run

# 各 agent 的非互動指令。prompt 一律放最後一個參數。
# 權限旗標是必要的：非互動模式沒有人能按「核准」，少了它 agent 會卡住或「假成功」。
def toolchain_writable_dirs():
    """Flutter 專案需要額外開放寫入的工具鏈目錄（只回傳實際存在的）。

    2026-10-20 實測：Codex `workspace-write` sandbox 只能寫 workspace，`flutter analyze` 依序卡在
    `<flutter>/bin/cache/engine.stamp` → `~/.dart-tool/dart-flutter-telemetry-session.json`；
    開放這兩處即可完整跑完。`~/.pub-cache` analyze 用不到，但 `pub get`／`intl_utils:generate`
    需下載套件時會寫入，存在就一併開放。
    """
    try:
        is_flutter = 'flutter' in open(os.path.join(ROOT, 'pubspec.yaml'), encoding='utf-8').read()
    except OSError:
        return []
    flutter = shutil.which('flutter')
    if not is_flutter or not flutter:
        return []
    sdk = os.path.dirname(os.path.dirname(os.path.realpath(flutter)))
    dirs = [os.path.join(sdk, 'bin', 'cache'), os.path.expanduser('~/.dart-tool'),
            os.path.expanduser('~/.pub-cache')]
    return [d for d in dirs if os.path.isdir(d)]


def add_dirs(dirs):
    return [x for d in dirs for x in ('--add-dir', d)]


AGENTS = {
    'codex': {
        # sandbox 只能寫 workspace；Flutter 專案自動開放工具鏈目錄，否則跑不了 analyze／test
        'name': 'Codex CLI', 'bin': 'codex',
        'cmd': lambda m, t: ['codex', 'exec', '--skip-git-repo-check', '-s', 'workspace-write']
                            + add_dirs(toolchain_writable_dirs()) + (['-m', m] if m else []),
    },
    'agy': {
        # --dangerously-skip-permissions：缺它會 exit 0 但沒做事（ai-pair 實測）
        # --print-timeout：預設 0 = 不限時；外層 subprocess timeout 只是保險
        'name': 'Antigravity CLI', 'bin': 'agy',
        # --add-dir：agy 只看得到 workspace，skill 本體在 ~/.agents/ 底下要另外開放
        'cmd': lambda m, t: ['agy', '--dangerously-skip-permissions', '--print-timeout', f'{t}s',
                             '--add-dir', SKILL_DIR]
                            + (['--model', m] if m else []) + ['-p'],
    },
    'copilot': {
        'name': 'Copilot CLI', 'bin': 'copilot',
        'cmd': lambda m, t: ['copilot', '--allow-all-tools', '--add-dir', SKILL_DIR]
                            + (['--model', m] if m else []) + ['-p'],
    },
    'cursor': {
        # -p 有寫檔與 shell 權限，但指令仍需核准 → --force；--trust 跳過「信任此 workspace」提問
        'name': 'Cursor CLI', 'bin': 'cursor-agent',
        'cmd': lambda m, t: ['cursor-agent', '-p', '--trust', '--force', '--add-dir', SKILL_DIR]
                            + (['--model', m] if m else []),
    },
    'opencode': {
        # 不用 --standalone：2026-10-19 實測啟動私有 server 卡住 >5 分鐘、零進度
        'name': 'opencode', 'bin': 'opencode',
        'cmd': lambda m, t: ['opencode', 'run', '--auto'] + (['-m', m] if m else []),
        # 2026-10-19 實測：預設模型（deepseek-v4.1-flash → elorian/glimpse）重複讀任務單 55 次、
        # 逾時未回報；指定 github-copilot/gpt-5.4-mini 後 12 秒完成
        'warn_no_model': 'opencode 預設模型實測會卡在迴圈，建議加 --model github-copilot/gpt-5.4-mini',
    },
}


def cmd_run(a):
    path = find_task(a.task_id)
    text = open(path).read()
    tid = os.path.basename(path)[:-3]
    spec = AGENTS[a.agent]

    # 任務單沒填就派出去，對方只會拿到空殼——先擋下來
    missing = [h for h in ('目標', '完成標準') if not section_body(text, h)]
    if not section_globs(text, '可以動的檔案'):
        missing.append('可以動的檔案')
    if missing:
        sys.exit(f'❌ 任務單尚未填寫：{"、".join(missing)}——填完再派工')
    if task_status(text) != '待執行' and not a.force:
        sys.exit(f'❌ 任務狀態是「{task_status(text)}」，不是「待執行」。確定要重跑請加 --force')
    if not shutil.which(spec['bin']):
        sys.exit(f'❌ 找不到 `{spec["bin"]}` 指令，{spec["name"]} 未安裝或不在 PATH')

    # 絕對路徑：skill 已移到專案外（~/.agents/skills/），相對路徑會指到錯的地方
    skill_md = os.path.join(SKILL_DIR, 'SKILL.md')
    prompt = (f'讀 {skill_md}，你是被分派的 agent（{spec["name"]}），執行其中的 report 流程，'
              f'任務單是 {os.path.relpath(path, ROOT)}。只改任務單允許的檔案；'
              f'需要動範圍外的檔案就停下來寫進「未處理事項／疑問」。')
    cmd = spec['cmd'](a.model, a.timeout) + [prompt]
    log_path = path[:-3] + '.run.log'

    if not a.model and spec.get('warn_no_model'):
        print(f'⚠️ {spec["warn_no_model"]}')

    if a.dry_run:
        print('（dry-run，不執行）')
        print(' '.join(c if re.fullmatch(r'[\w./:=-]+', c) else repr(c) for c in cmd))
        return

    # 先把「指派給」更新成實際執行者，任務單才與事實一致
    text = re.sub(r'^- 指派給：.*$', f'- 指派給：{spec["name"]}' + (f'（{a.model}）' if a.model else ''),
                  text, count=1, flags=re.M)
    open(path, 'w').write(text)
    cmd_log_line(f'主 agent → {spec["name"]}｜{tid} 以非互動模式派工')

    print(f'▶ 啟動 {spec["name"]}' + (f'（{a.model}）' if a.model else '') + f'，上限 {a.timeout} 秒')
    print(f'  輸出：{os.path.relpath(log_path, ROOT)}')
    started = datetime.datetime.now()
    # 輸出直接落檔、不經 shell 變數（控制字元會弄壞內容；agy 1.0.x 非 TTY 時 stdout 還可能是空的）
    with open(log_path, 'w') as fh:
        fh.write(f'# {now()}  {" ".join(cmd[:-1])} <prompt>\n\n')
        fh.flush()
        try:
            rc = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, timeout=a.timeout + 60).returncode
        except subprocess.TimeoutExpired:
            rc = 'timeout'
    secs = int((datetime.datetime.now() - started).total_seconds())

    after = task_status(open(path).read())
    print(f'■ 結束：exit={rc}，耗時 {secs} 秒，任務單狀態：{after}')
    if after != '已回報':
        # exit 0 不代表有做事：agy 漏權限旗標、prompt 被忽略時都會這樣
        print('⚠️ **任務單狀態沒有變成「已回報」**——可能是假成功、逾時或中途失敗。')
        print(f'   看輸出最後幾行：tail -30 {os.path.relpath(log_path, ROOT)}')
        cmd_log_line(f'{spec["name"]} → 主 agent｜{tid} 執行結束但未回報（exit={rc}）')
    else:
        print(f'✅ 已回報。下一步：python3 {SCRIPT} review {tid}')


def cmd_review(a):
    path = find_task(a.task_id)
    meta_path = path[:-3] + '.base.json'
    if not os.path.exists(meta_path):
        sys.exit(f'❌ 缺少基準檔 {os.path.basename(meta_path)}——此任務單不是用 new-task 建立的')
    meta = json.load(open(meta_path))
    text = open(path).read()

    tracked = [f for f in sh(['git', 'diff', '--name-only', meta['base']]).splitlines()
               if f and not f.startswith(HANDOFF + '/')]
    before = meta.get('untracked', {})
    new_untracked = [f for f in untracked() if before.get(f) != file_hash(f)]
    changed = sorted(set(tracked) | set(new_untracked))

    allow = section_globs(text, '可以動的檔案')
    deny = section_globs(text, '不能動的檔案')

    print(f'## 驗收：{os.path.basename(path)}\n')
    print(f'- 基準：`{meta["ref"]}`（{meta["base"][:10]}），分派時 HEAD `{meta["head"]}`')
    print(f'- 目前 HEAD：`{sh(["git", "log", "-1", "--format=%h %s"])}`\n')
    if not changed:
        print('⚠️ **分派後沒有任何檔案變動**——若回報說已完成，回報與事實不符')
        return
    print(f'### 實際變動的檔案（{len(changed)}）\n')
    out_of_scope = []
    for f in changed:
        if deny and match(f, deny):
            mark = '🔴 禁止範圍'
            out_of_scope.append(f)
        elif allow and not match(f, allow):
            mark = '🟡 範圍外'
            out_of_scope.append(f)
        else:
            mark = '✅' if allow else '·'
        print(f'- {mark} `{f}`' + ('（untracked）' if f in new_untracked and f not in tracked else ''))
    print()
    if not allow:
        print('ℹ️ 任務單未列「可以動的檔案」，無法自動判斷範圍\n')
    if out_of_scope:
        print(f'⚠️ **{len(out_of_scope)} 個檔案超出任務單允許範圍**，需逐一確認\n')
    print('### diff 統計（tracked）\n```')
    print(sh(['git', 'diff', '--stat', meta['base']]) or '(無)')
    print('```')
    print('\n下一步：用 `git diff ' + meta['ref'] + ' -- <檔案>` 逐檔看內容，並自行重跑「完成標準」的驗證指令。')


# ---------------------------------------------------------------- sessions

def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text')
    return ''


def claude_sessions(n):
    proj = os.path.expanduser('~/.claude/projects/' + re.sub(r'[^A-Za-z0-9]', '-', ROOT))
    files = sorted(glob.glob(os.path.join(proj, '*.jsonl')), key=os.path.getmtime, reverse=True)
    out = []
    for f in files[:n]:
        users, last_asst = [], ''
        for line in open(f, errors='replace'):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get('message') or {}
            if d.get('type') == 'user' and not d.get('isMeta') and msg.get('role') == 'user':
                t = text_of(msg.get('content')).strip()
                if t and not t.startswith('<') and 'tool_result' not in str(msg.get('content'))[:50]:
                    users.append(t)
            elif d.get('type') == 'assistant':
                t = text_of(msg.get('content')).strip()
                if t:
                    last_asst = t
        out.append(('Claude Code', f, users, last_asst))
    return out


def codex_sessions(n):
    files = sorted(glob.glob(os.path.expanduser('~/.codex/sessions/*/*/*/*.jsonl')),
                   key=os.path.getmtime, reverse=True)
    out = []
    for f in files:
        if len(out) >= n:
            break
        cwd, users, last_asst = None, [], ''
        for line in open(f, errors='replace'):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            p = d.get('payload') or {}
            if d.get('type') == 'session_meta':
                cwd = p.get('cwd')
            elif d.get('type') == 'event_msg' and p.get('type') == 'user_message':
                users.append((p.get('message') or '').strip())
            elif d.get('type') == 'event_msg' and p.get('type') == 'agent_message':
                last_asst = (p.get('message') or '').strip()
        if cwd and os.path.realpath(cwd) == os.path.realpath(ROOT):
            out.append(('Codex CLI', f, users, last_asst))
    return out


def agy_sessions(n):
    """agy 只有 history.jsonl 是純文字（使用者輸入＋workspace）；agent 回覆存在 conversations/*.db，暫不解析。"""
    hist = os.path.expanduser('~/.gemini/antigravity-cli/history.jsonl')
    if not os.path.exists(hist):
        return []
    convs = {}
    for line in open(hist, errors='replace'):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get('type') == 'slash_command' or not d.get('workspace'):
            continue
        if os.path.realpath(d['workspace']) != os.path.realpath(ROOT):
            continue
        cid = d.get('conversationId') or '(未知)'
        c = convs.setdefault(cid, {'ts': 0, 'users': []})
        c['users'].append((d.get('display') or '').strip())
        c['ts'] = max(c['ts'], d.get('timestamp') or 0)
    out = []
    for cid, c in sorted(convs.items(), key=lambda x: x[1]['ts'], reverse=True)[:n]:
        out.append(('Antigravity CLI', f'{hist}#{cid}', c['users'],
                    '（agy 的回覆存在 conversations/*.db，未解析）', c['ts'] / 1000))
    return out


def clip(t, limit):
    t = re.sub(r'\s+', ' ', t)
    return t if len(t) <= limit else t[:limit] + '…'


def cmd_sessions(a):
    found = []
    if a.tool in ('all', 'claude'):
        found += claude_sessions(a.n)
    if a.tool in ('all', 'codex'):
        found += codex_sessions(a.n)
    found = [(t, f, u, l, os.path.getmtime(f)) for t, f, u, l in found]
    if a.tool in ('all', 'agy'):
        found += agy_sessions(a.n)
    if not found:
        print('（找不到本專案的對話紀錄）')
        return
    found.sort(key=lambda x: x[4], reverse=True)
    for tool, f, users, last, mtime in found:
        ts = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        print(f'## {tool}｜最後活動 {ts}\n- 檔案：`{f}`')
        print(f'- 使用者訊息 {len(users)} 則，最後 {min(3, len(users))} 則：')
        for u in users[-3:]:
            print(f'  - {clip(u, 300)}')
        print(f'- 最後一則 agent 回覆：{clip(last, 600) or "（無）"}\n')
    print('ℹ️ Copilot CLI / opencode 的紀錄格式尚未支援；agy 只讀得到使用者輸入。')


# ---------------------------------------------------------------- log

def cmd_log_line(text):
    cmd_init_quiet()
    with open(os.path.join(ROOT, HANDOFF, 'log.md'), 'a') as fh:
        fh.write(f'- {now()}｜{text}\n')


def cmd_log(a):
    cmd_log_line(a.text)
    print('✅ 已追加至 .handoff/log.md')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init').set_defaults(fn=cmd_init)
    sub.add_parser('snapshot').set_defaults(fn=cmd_snapshot)
    t = sub.add_parser('new-task')
    t.add_argument('slug')
    t.add_argument('--to')
    t.set_defaults(fn=cmd_new_task)
    rn = sub.add_parser('run')
    rn.add_argument('task_id')
    rn.add_argument('--agent', required=True, choices=sorted(AGENTS))
    rn.add_argument('--model', help='傳給該 agent 的模型名稱，不填用其預設')
    rn.add_argument('--timeout', type=int, default=1800, help='秒，預設 1800')
    rn.add_argument('--dry-run', action='store_true', help='只印出指令，不執行')
    rn.add_argument('--force', action='store_true', help='狀態不是「待執行」也照跑')
    rn.set_defaults(fn=cmd_run)
    r = sub.add_parser('review')
    r.add_argument('task_id')
    r.set_defaults(fn=cmd_review)
    s = sub.add_parser('sessions')
    s.add_argument('--tool', choices=['all', 'claude', 'codex', 'agy'], default='all')
    s.add_argument('-n', type=int, default=1, help='每個工具取最近幾個 session')
    s.set_defaults(fn=cmd_sessions)
    lg = sub.add_parser('log')
    lg.add_argument('text')
    lg.set_defaults(fn=cmd_log)
    a = p.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
