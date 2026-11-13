# 各技術棧備註與範例（stack-review）

非必讀；要確認某技術棧的審查重點或看呼叫範例時才讀。

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
