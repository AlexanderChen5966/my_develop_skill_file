# code-reviewer 的呼叫範本（stack-review Step 4）

SKILL.md Step 4 要派 code-reviewer 時照本檔填。

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
