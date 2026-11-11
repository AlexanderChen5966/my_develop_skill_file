---
name: stack-review
description: Comprehensive code review for multiple tech stacks with automatic technology detection. Supports Flutter (Riverpod/Bloc), Java Spring Boot, Android (Java/Kotlin), iOS (Swift/Objective-C), React Native (Expo), and React web (Next.js/Vite). Use when the user requests code review (e.g., "/review", "review this code", "check my changes"), after completing feature development, or for pre-commit checks. Automatically detects project type and applies appropriate architectural standards, security checks, and best practices.
metadata:
  version: 1.9.0
  last-updated: 2026-11-11
---

# Code Review

Multi-stack code review with automatic technology detection and specialized analysis.

## Overview

This skill provides comprehensive code reviews for various technology stacks:

- **Flutter + Riverpod** - State management architecture, lifecycle, OAuth2
- **Flutter + Bloc** - Bloc/Cubit patterns, event handling, state design
- **Java Spring Boot** - Bean management, JPA/Hibernate, REST API, security
- **Android (Java/Kotlin)** - MVVM, Jetpack components, Coroutines, performance
- **iOS (Swift/Objective-C)** - Retain cycles, Swift Concurrency, SwiftUI/UIKit, privacy
- **React Native (Expo)** - Hooks, state, navigation, lists, native permissions, OTA updates

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
| **iOS (Swift/Objective-C)** | `*.xcodeproj` / `*.xcworkspace` / `Package.swift` at the project root | [ios.md](references/ios.md) |
| **React Native (Expo)** | `package.json` + `react-native` dependency | [react-native.md](references/react-native.md) |
| **React web (Next.js/Vite)** | `package.json` + `react` dependency, **no** `react-native` | [react-web.md](references/react-web.md) |

**Check cross-platform first.** Flutter and React Native projects contain `android/` and `ios/` folders, so they also match the Android and iOS criteria. If `pubspec.yaml` or a `react-native` dependency exists, the project is Flutter or React Native; add `android.md` / `ios.md` only when the diff touches native code inside those folders.

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

# Check for iOS
ls -d *.xcodeproj *.xcworkspace Package.swift

# Check for React Native
grep '"react-native"\|"expo"' package.json

# Check for React web (only when there is no react-native dependency)
grep '"react"\|"next"\|"vite"' package.json
```

**Multiple Stacks**: If the project contains multiple stacks (e.g., Flutter + Spring Boot backend), review each stack separately with its appropriate checklist. A stack can live in a subfolder (e.g., a Flutter repo with a React web app in `next/`): run the detection in the nearest folder above each changed file that has `package.json`／`pubspec.yaml`, not only at the repo root.

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

**iOS**:
- **Views/ViewControllers** (SwiftUI/UIKit) - State ownership, lifecycle, main-thread UI updates
- **ViewModels/Services** - Retain cycles, concurrency (`@MainActor`, `Task`, `Sendable`)
- **Networking/Models** - `Codable`, error handling, token refresh
- **Project settings** (`Info.plist`, entitlements, `project.pbxproj`) - Permissions, privacy manifest, unrelated churn

**React Native**:
- **Screens/Components** - Hooks dependencies, effect cleanup, lists
- **Stores/Hooks** - Selectors, derived state, reset on logout
- **Navigation** (React Navigation / Expo Router) - Params, guards, focus refresh
- **Native & config** (`android/`, `ios/`, `app.config.js`, `eas.json`, `patches/`) - Permissions, OTA vs store release

See stack-specific checklists in `references/` for detailed focus areas.

### Step 4: Invoke Code-Reviewer Subagent

Use the Task tool to launch the code-reviewer subagent for deep analysis. When the agent is installed through the personal Claude Code plugin, its name is `dev:code-reviewer`; use the name shown in the available agent list.

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

### Step 4b: Spec Review (parallel, when a task document exists)

The checklist review above answers "is the code written well?". It cannot answer "is this the code
the task asked for?" — code can pass every checklist and still implement the wrong thing, skip a
requirement, or add unrequested behaviour. A second subagent checks the diff against the task
document.

**Find the spec** (stop at the first hit):

1. A path the user passed
2. `docs/shared/*.md` whose `**分支編號：**` matches the Jira key in the branch name or commit messages (e.g. `SSGS-12345`)
3. `docs/shared/*.md` with `**狀態：** 🔄 進行中` or `⏳ 待實作` whose `**影響路徑：**` overlaps the changed files
4. Several candidates or none → ask the user. If they say there is no task document, skip this step and say so in the summary ("Spec: no task document, skipped")

**Launch it in the same message as the Step 4 code-reviewer call**, so both run in parallel and
neither pollutes the other's context:

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

> **Agents without a subagent/Task tool**: do the spec pass yourself *after* finishing the checklist
> pass, and keep the two sets of notes separate.

### Step 5: Process Review Results

After the code-reviewer subagent (and the spec subagent, if launched) completes:

1. **Categorize Findings** by severity:
   - 🔴 **Critical**: Security, architecture violations, performance issues (N+1, memory leaks)
   - 🟡 **Warning**: Code smells, missing tests, style inconsistencies
   - 🟢 **Suggestion**: Optional improvements, refactoring opportunities

2. **Prioritize Issues**: Address critical first, group related issues, provide actionable fixes with code examples

3. **Verify Against Checklists**: Cross-reference with stack-specific and common checklists

4. **Keep spec findings separate**: do not merge them into the 🔴/🟡/🟢 lists or rerank them against
   checklist findings. A change can pass one axis and fail the other; merging lets one mask the other.
   Present them under their own heading (see Step 6).

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

### iOS (Swift/Objective-C)
**Checklist**: [references/ios.md](references/ios.md)

**Key checks**: Retain cycles (`[weak self]`, delegates), Swift Concurrency (`@MainActor`, cancellation, `Sendable`), SwiftUI state ownership, UIKit cell reuse, Keychain, `Info.plist` usage strings, privacy manifest

### React Native (Expo)
**Checklist**: [references/react-native.md](references/react-native.md)

**Key checks**: Hooks rules and effect cleanup, store selectors, navigation params and guards, FlatList performance, secure storage, permissions on both platforms, OTA updates vs native changes

### React web (Next.js/Vite)
**Checklist**: [references/react-web.md](references/react-web.md)

**Key checks**: Hooks rules and effect cleanup, query keys and stale `keepPreviousData` results, cache reset on logout or company switch, client vs server components, secrets in `NEXT_PUBLIC_*`, shared component blast radius, side-by-side comparison for migrated pages

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

## Common Excuses（常見藉口）

Before skipping a step, check this table:

| Excuse | Why it doesn't hold |
|---|---|
| 「本地 main 應該是新的，不用 fetch」 | 2026-07-29 b2b-manager：本地 main 落後 7 週，上游 13 天前已合併的任務被重複實作，review 乾淨通過，最後在 MR 才以合併衝突浮現 |
| 「diff 很小，看一下就好，不用跑完整流程」 | 小 diff 一樣會改到 enum／DTO 契約；前端零 diff 的契約漂移本來就抓不到，能抓的更不能放 |
| 「沒有任務文件，spec 審查跳過就好」 | 先照 Step 4b 的順序找；真的沒有才跳過，而且摘要要寫 `Spec: no task document, skipped` |
| 「code-reviewer 說沒問題，就是沒問題」 | reviewer 也會漏也會錯；它的發現要對照程式原文再分類，0 個發現時至少自己看過高風險檔案 |
| 「順手改的格式不影響行為，不用提」 | 它讓 diff 變大、遮住真正的修改；照 `common.md`「最小化變更」列出來 |
| 「這個框架用法看起來沒問題」 | 看起來對的舊版寫法最難發現；沒有出處就要求標未驗證 |
| 「spec 和規範的發現合在一起排比較清楚」 | 合併會讓一軸蓋掉另一軸；兩邊分開列 |

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
- **Spec subagent** - Diff vs `docs/shared/` task document (Step 4b), reported separately
- **doubt-check** - In-flight adversarial check for single high-risk decisions during development; stack-review is the after-the-fact gate on the whole diff
- **Common checklist** - Universal checks
- **Stack-specific checklists** - Specialized standards
- **Project docs** (CLAUDE.md, or AGENTS.md for non-Claude agents; architecture docs) - Project rules

Always reference both common and stack-specific checklists for comprehensive coverage.