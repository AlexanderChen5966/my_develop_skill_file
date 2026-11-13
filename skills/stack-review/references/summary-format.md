# 審查摘要格式（stack-review Step 6）

SKILL.md Step 6 輸出摘要時照本檔。

```markdown
## Code Review Summary

**Tech Stack**: [Detected Stack]
**Files Reviewed**: [Count] files
**Overall Status**: [✅ Approved / ⚠️ Needs Attention / ❌ Requires Changes]

### Critical Issues (🔴)
1. **[file:line]** - [Issue]
   - **Problem**: [Explanation]
   - **Fix**: [Recommendation with code]
   - **Reference**: [Checklist section]

### Warnings (🟡)
[List with file:line references]

### Suggestions (🟢)
[List optional improvements]

### Spec Check (vs `docs/shared/<file>.md`)
<!-- or: "Spec: no task document, skipped" -->
- **Missing / partial**: [requirement quote] → [file:line or "not found"]
- **Scope creep**: [file:line] — [what it does that wasn't asked]
- **Looks wrong**: [requirement quote] vs [file:line]
- **Contract**: [backend dependency handled as documented? yes / issue]
- **Doubt-check**: [tasks marked 需 doubt-check → result recorded? yes / missing / code differs from reviewed version / none marked]

### Compliance Checklist
- [x] Architecture pattern correct
- [x] State management follows best practices
- [ ] All resources properly disposed (file.dart:123)
- [x] Security best practices followed

### Recommendations
1. [Priority 1 action]
2. [Priority 2 action]

### References
- [references/common.md](references/common.md)
- [references/[stack].md](references/[stack].md)
```
