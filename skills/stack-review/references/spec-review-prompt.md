# 對照任務文件的 subagent 提示（stack-review Step 4b）

SKILL.md Step 4b 找到任務文件後，與 Step 4 同一則訊息派出本 subagent。

```
Task(
  subagent_type='general-purpose',
  description='Spec review against task doc',
  prompt='''
    Compare a code change against its task document. Do not review code style or quality.

    **Diff**: `git diff origin/<target>...HEAD` (commits: `git log --oneline origin/<target>..HEAD`)
    **Task document**: docs/shared/<file>.md — read it in full, especially 需求說明, 契約依據, 實作任務 and the checklist in 執行步驟.

    Report:
    (a) Missing or partial: things the task document asks for that the diff does not do
    (b) Scope creep: behaviour in the diff the task document did not ask for
    (c) Implemented but looks wrong: matches a requirement in name, but the behaviour differs
    (d) 後端依賴 / 跨服務契約: if the doc declares backend enums/DTOs, does the code handle them as the doc says?
    (e) doubt-check: for every task marked `**需 doubt-check：** 是…`, is there a doubt-check result
        (主張, 複查輪數, 結論) in 實作注意事項 or the task's comments? Missing → report it. Present but the
        code differs from what was reviewed → report it.

    Quote the task-document line for every finding, plus file:line in the diff.
    If the task document itself is ambiguous on a point, say so instead of guessing.
    Under 400 words.
  '''
)
```
