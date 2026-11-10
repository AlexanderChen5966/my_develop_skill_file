---
name: stack-review
description: Comprehensive code review for multiple tech stacks with automatic technology detection. Supports Flutter (Riverpod/Bloc), Java Spring Boot, and Android (Java/Kotlin). Use when the user requests code review (e.g., "/review", "review this code", "check my changes"), after completing feature development, or for pre-commit checks. Automatically detects project type and applies appropriate architectural standards, security checks, and best practices.
metadata:
  version: 1.1.0
  last-updated: 2026-01-08
---

# Code Review

Multi-stack code review with automatic technology detection and specialized analysis.

## Overview

This skill provides comprehensive code reviews for various technology stacks:

- **Flutter + Riverpod** - State management architecture, lifecycle, OAuth2
- **Flutter + Bloc** - Bloc/Cubit patterns, event handling, state design
- **Java Spring Boot** - Bean management, JPA/Hibernate, REST API, security
- **Android (Java/Kotlin)** - MVVM, Jetpack components, Coroutines, performance

**Key Features**:
1. Automatic project type detection
2. Stack-specific architectural compliance
3. Unified security and code quality checks
4. Integration with code-reviewer subagent for deep analysis

## Review Workflow

### Step 1: Identify Changed Files

#### 1a. Establish a fresh, correct review base (do this FIRST)

**Never diff against a local branch ref without fetching.** A stale base silently invalidates the
entire review: you will miss work already merged upstream, mistake existing files for new ones,
and can even "approve" a duplicate reimplementation of something already on the target branch.

```bash
# 1. Always fetch first — a local `main`/`master` ref can be weeks out of date
git fetch origin

# 2. Is the branch behind the target? If so, STOP and resolve before reviewing
git log --oneline HEAD..origin/main        # commits on target that this branch lacks

# 3. Diff against the REMOTE ref, never the local one
git diff origin/main...HEAD               # ✅ correct (3 dots = merge-base diff)
# git diff main...HEAD                    # ❌ local ref may be stale
```

**If the branch is behind the target**: recommend merging (or rebasing) the target in *before*
reviewing. Reviewing a stale branch means the conclusions describe a state that will not exist
after the merge — and any conflicts found later force a second review pass anyway.

> Real failure this rule prevents: a review ran with `git diff main...HEAD` where the local `main`
> was 7 weeks stale. A task already merged upstream 13 days earlier had been reimplemented on the
> branch; the review passed cleanly, and the duplicate only surfaced as merge conflicts in the MR.

#### 1b. Determine the scope

```bash
# Uncommitted work
git status
git diff
git diff --cached

# Whole-branch review (most common for feature branches / MRs)
git diff --stat origin/main...HEAD
git log --oneline origin/main..HEAD
```

If the user hasn't specified which files to review, ask or infer: uncommitted changes only, or the
whole branch vs its target? For an MR/PR review it is almost always the whole branch.

**Exclude from findings** (report them only if they are themselves the defect): generated files
(`*.g.dart`, `*.freezed.dart`, `lib/generated/**`, `build/`), lockfiles, and vendored/third-party
directories. Verify a suspected generated file really is generated before dismissing it.

### Step 2: Detect Project Type

Based on project indicators, automatically determine the tech stack:

| Tech Stack | Detection Criteria | Checklist |
|------------|-------------------|-----------|
| **Flutter + Riverpod** | `pubspec.yaml` + `flutter_riverpod` dependency | [flutter-riverpod.md](references/flutter-riverpod.md) |
| **Flutter + Bloc** | `pubspec.yaml` + `flutter_bloc` dependency | [flutter-bloc.md](references/flutter-bloc.md) |
| **Spring Boot** | `pom.xml` or `build.gradle` + `@SpringBootApplication` | [springboot.md](references/springboot.md) |
| **Android (Java/Kotlin)** | `build.gradle` (app module) + Android SDK | [android.md](references/android.md) |

**Detection Commands**:
```bash
# Check for Flutter
ls pubspec.yaml
grep "flutter_riverpod\|flutter_bloc" pubspec.yaml

# Check for Spring Boot
ls pom.xml build.gradle
grep "@SpringBootApplication" -r src/

# Check for Android
ls app/build.gradle
grep "com.android.application" -r .
```

**Multiple Stacks**: If the project contains multiple stacks (e.g., Flutter + Spring Boot backend), review each stack separately with its appropriate checklist.

### Step 3: Determine Review Scope

Based on changed files and detected stack, identify review focus areas:

**Flutter (Riverpod/Bloc)**:
- **Pages** (`lib/page/**/*.dart`) - State architecture, lifecycle, UI
- **StateNotifiers/Bloc** - State patterns, event handling
- **API/Models** - Serialization, networking
- **Widgets** - Reusability, performance

**Spring Boot**:
- **Controllers** (`*Controller.java`) - REST API, request mapping
- **Services** (`*Service.java`) - Business logic, transactions
- **Repositories** (`*Repository.java`) - JPA queries, N+1 problems
- **Entities** - Relationships, lazy loading
- **Config** - Bean definitions, security

**Android**:
- **Activities/Fragments** - Lifecycle, memory leaks
- **ViewModels** - State management, LiveData/StateFlow
- **Repositories** - Data layer, Room/Retrofit
- **UI** (XML/Compose) - Layout optimization, Composables

See stack-specific checklists in `references/` for detailed focus areas.

### Step 4: Invoke Code-Reviewer Subagent

Use the Task tool to launch the code-reviewer subagent for deep analysis.

> **Agents without a subagent/Task tool** (Codex, Copilot CLI, opencode, agy, Cursor): skip the launch and perform the same deep review yourself in the current session, using the prompt below as your checklist. Output format (Step 5) is unchanged.

**Invocation Template**:
```
Task(
  subagent_type='code-reviewer',
  description='Review [STACK] changes',
  prompt='''
    Review the following code changes for a [TECH_STACK] project:

    **Files to review**:
    - [file1_path] ([type])
    - [file2_path] ([type])

    **Focus areas**:
    1. [Focus area from Step 3]
    2. [Focus area from Step 3]
    ...

    **Project context**:
    - Technology stack: [STACK]
    - Architecture pattern: [e.g., MVVM, Clean Architecture]
    - [Stack-specific context]

    **Checklists to reference**:
    - Common (all stacks): references/common.md
    - Stack-specific: references/[stack].md

    **Output format**:
    Categorize findings by severity with file:line references:
    - 🔴 Critical: Security, architecture violations, breaking changes
    - 🟡 Warning: Code smells, performance, style issues
    - 🟢 Suggestion: Optional improvements
  '''
)
```

**Example (Flutter + Riverpod)**:
```
Review Flutter + Riverpod Web project:

Files: order_stats_page.dart (SingleTaskState), order_stats_notifier.dart

Focus: State type compliance, Riverpod patterns (ref.watch vs ref.read),
lifecycle (initState/dispose/onVisibleChange), UI structure

Context: Flutter Web, Riverpod, OAuth2 PKCE, TaskManager singleton

Checklists: references/common.md, references/flutter-riverpod.md
```

**Example (Spring Boot)**:
```
Review Spring Boot project:

Files: UserController.java, UserService.java, UserRepository.java

Focus: REST API design, Bean injection (constructor), JPA N+1 queries,
transaction management

Context: Spring Boot 3.x, JPA/Hibernate, RESTful architecture

Checklists: references/common.md, references/springboot.md
```

### Step 5: Process Review Results

After the code-reviewer subagent completes:

1. **Categorize Findings** by severity:
   - 🔴 **Critical**: Security, architecture violations, performance issues (N+1, memory leaks)
   - 🟡 **Warning**: Code smells, missing tests, style inconsistencies
   - 🟢 **Suggestion**: Optional improvements, refactoring opportunities

2. **Prioritize Issues**: Address critical first, group related issues, provide actionable fixes with code examples

3. **Verify Against Checklists**: Cross-reference with stack-specific and common checklists

### Step 6: Present Review Summary

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

## Supported Tech Stacks

### Flutter + Riverpod
**Checklist**: [references/flutter-riverpod.md](references/flutter-riverpod.md)

**Key checks**: State types (ConsumerState/SingleTaskState/CacheableState), Riverpod patterns, lifecycle, TaskManager, OAuth2

### Flutter + Bloc
**Checklist**: [references/flutter-bloc.md](references/flutter-bloc.md)

**Key checks**: Bloc/Cubit architecture, Event/State design, BlocProvider, transformers, testing

### Java Spring Boot
**Checklist**: [references/springboot.md](references/springboot.md)

**Key checks**: Bean DI (constructor injection), JPA/Hibernate (N+1 queries), REST API, transactions, Spring Security

### Android (Java/Kotlin)
**Checklist**: [references/android.md](references/android.md)

**Key checks**: MVVM/MVI, ViewModel/LiveData/StateFlow, memory leaks, Jetpack Compose, Coroutines

## Common Checks (All Stacks)

[references/common.md](references/common.md) provides universal checks:

- **Security**: Input validation, SQL Injection/XSS/CSRF, auth, sensitive data, dependencies
- **Code Quality**: Naming, function complexity, DRY, error handling, comments
- **Performance**: DB/API optimization, algorithms, memory, async patterns
- **Maintainability**: Code organization, SOLID, design patterns, testing

## Usage Examples

**Flutter Riverpod**:
```
User: "我剛完成訂單統計頁面，幫我審查一下"

1. git status → order_stats_page.dart, order_stats_notifier.dart
2. Detect: Flutter + Riverpod (pubspec.yaml)
3. Identify: SingleTaskState page
4. Invoke subagent with flutter-riverpod.md checklist
5. Report:
   - 🔴 Timer not disposed
   - 🟡 ref.read() in build method
   - 🟢 Can use select for optimization
```

**Spring Boot**:
```
User: "/review"

1. git diff → UserController.java, UserService.java, UserRepository.java
2. Detect: Spring Boot (pom.xml + @SpringBootApplication)
3. Identify: REST API changes
4. Invoke subagent with springboot.md checklist
5. Report:
   - 🔴 N+1 query in UserRepository.findAllWithOrders()
   - 🟡 Missing @Transactional in Service
   - 🟢 Use constructor injection instead of field injection
```

**Mixed Stack**:
```
User: "Review all my changes"

1. git status → Flutter + Spring Boot changes
2. Detect both stacks
3. Review separately:
   - Flutter files with flutter-riverpod.md
   - Spring Boot files with springboot.md
4. Generate two review reports
```

## Adding New Tech Stacks

To support a new stack:

1. Create `references/[stack-name].md` with stack-specific checks
2. Update detection criteria in Step 2
3. Define file patterns and focus areas in Step 3
4. Test on sample projects

**Template** for new checklists: See existing checklists for structure

## Integration

This skill integrates with:
- **code-reviewer subagent** - Deep analysis
- **Common checklist** - Universal checks
- **Stack-specific checklists** - Specialized standards
- **Project docs** (CLAUDE.md, or AGENTS.md for non-Claude agents; architecture docs) - Project rules

Always reference both common and stack-specific checklists for comprehensive coverage.