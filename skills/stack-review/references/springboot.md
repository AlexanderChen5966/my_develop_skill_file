# Spring Boot 程式碼審查檢查清單

本檢查清單專為 Spring Boot 專案設計，涵蓋 Spring 框架、JPA/Hibernate、REST API 和最佳實踐。

**建議**：同時參考 [common.md](common.md) 的通用檢查項目。

## 1. Spring Bean 與依賴注入

### Bean 定義
- [ ] 是否使用正確的 Bean 註解（`@Component`、`@Service`、`@Repository`、`@Controller`）？
- [ ] Bean 作用域是否正確（`@Scope`：singleton/prototype/request/session）？
- [ ] 是否避免在單例 Bean 中注入請求作用域的 Bean？
- [ ] 配置類是否使用 `@Configuration` 註解？

### 依賴注入
- [ ] **優先使用建構子注入**（Constructor Injection），而非欄位注入？
  ```java
  // ✅ 推薦：建構子注入
  @Service
  public class UserService {
      private final UserRepository userRepository;

      public UserService(UserRepository userRepository) {
          this.userRepository = userRepository;
      }
  }

  // ❌ 避免：欄位注入
  @Service
  public class UserService {
      @Autowired
      private UserRepository userRepository;
  }
  ```
- [ ] 必填依賴是否使用 `final` 修飾？
- [ ] 是否避免循環依賴（Circular Dependency）？
- [ ] `@Autowired` 是否必要（建構子注入時可省略）？

### Bean 生命週期
- [ ] 初始化邏輯是否使用 `@PostConstruct`？
- [ ] 清理邏輯是否使用 `@PreDestroy`？
- [ ] 是否避免在建構子中執行複雜初始化？

## 2. RESTful API 設計

### Controller 層
- [ ] 是否使用 `@RestController` 而非 `@Controller + @ResponseBody`？
- [ ] Request Mapping 是否正確使用（`@GetMapping`、`@PostMapping`、`@PutMapping`、`@DeleteMapping`）？
- [ ] 是否定義適當的 HTTP 狀態碼（`@ResponseStatus` 或 `ResponseEntity`）？
- [ ] 路徑參數是否使用 `@PathVariable`？
- [ ] 查詢參數是否使用 `@RequestParam`？
- [ ] Request Body 是否使用 `@RequestBody` 和 `@Valid`？

### Request/Response DTO
- [ ] 是否使用 DTO（Data Transfer Object）而非直接暴露 Entity？
- [ ] DTO 是否有適當的驗證註解（`@NotNull`、`@Size`、`@Email`）？
- [ ] 是否使用 MapStruct 或 ModelMapper 進行 Entity-DTO 轉換？

### 錯誤處理
- [ ] 是否實作全域異常處理（`@ControllerAdvice` + `@ExceptionHandler`）？
  ```java
  @ControllerAdvice
  public class GlobalExceptionHandler {
      @ExceptionHandler(ResourceNotFoundException.class)
      public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException ex) {
          return ResponseEntity.status(HttpStatus.NOT_FOUND)
              .body(new ErrorResponse(ex.getMessage()));
      }
  }
  ```
- [ ] 自定義異常是否有意義且具體？
- [ ] 錯誤回應格式是否一致？
- [ ] 是否避免在回應中洩漏堆疊追蹤（Stack Trace）？

### API 版本控制
- [ ] 是否有 API 版本策略（URL、Header、Media Type）？
- [ ] 破壞性變更是否有新版本？

## 3. JPA / Hibernate

### Entity 設計
- [ ] Entity 是否正確使用 `@Entity` 和 `@Table`？
- [ ] 主鍵是否正確定義（`@Id`、`@GeneratedValue`）？
- [ ] 是否使用適當的主鍵生成策略（IDENTITY/SEQUENCE/UUID）？
- [ ] 關聯關係是否正確定義（`@OneToMany`、`@ManyToOne`、`@ManyToMany`）？
- [ ] Lazy/Eager Loading 是否適當設定？
- [ ] 是否避免雙向關聯的無限遞迴（使用 `@JsonIgnore` 或 DTO）？

### Repository 層
- [ ] 是否繼承 `JpaRepository` 或 `CrudRepository`？
- [ ] 自定義查詢方法名稱是否遵循 Spring Data 命名規則？
- [ ] 複雜查詢是否使用 `@Query` 註解？
- [ ] 是否使用 `@Modifying` 標記更新/刪除查詢？
- [ ] Native Query 是否必要（優先使用 JPQL）？

### N+1 查詢問題
- [ ] **是否避免 N+1 查詢問題**？
- [ ] 是否使用 `JOIN FETCH` 預載入關聯資料？
- [ ] 是否使用 `@EntityGraph` 優化查詢？
- [ ] 是否啟用 Hibernate SQL 日誌檢查實際查詢？

### Transaction 管理
- [ ] Service 層方法是否使用 `@Transactional`？
- [ ] Transaction 邊界是否合理（避免過大或過小）？
- [ ] 是否正確設定 `readOnly = true` 對於唯讀操作？
- [ ] 是否正確處理 `@Transactional` 的 Propagation 和 Isolation？
- [ ] 是否避免在 `@Transactional` 方法外呼叫 Lazy Loading 屬性？

## 4. Service 層

### 職責分離
- [ ] Service 是否包含業務邏輯（而非 Controller）？
- [ ] 是否避免在 Controller 中直接使用 Repository？
- [ ] 複雜業務邏輯是否提取為獨立方法？

### 最佳實踐
- [ ] Service 介面是否必要（簡單情況可省略）？
- [ ] 是否使用 `@Service` 註解？
- [ ] 是否避免在 Service 中處理 HTTP 相關邏輯（Request/Response）？

## 5. 配置管理

### application.properties / application.yml
- [ ] 敏感資訊是否使用環境變數或外部配置？
- [ ] 是否區分不同環境的配置（dev/test/prod）？
- [ ] 是否使用 Spring Profiles（`@Profile`、`spring.profiles.active`）？
- [ ] 資料庫連線資訊是否正確配置？

### Configuration 類
- [ ] `@Configuration` 類是否組織清晰？
- [ ] `@Bean` 方法是否有清晰的命名？
- [ ] 是否使用 `@ConfigurationProperties` 綁定配置？
  ```java
  @ConfigurationProperties(prefix = "app")
  @Component
  public class AppProperties {
      private String name;
      private int timeout;
      // getters and setters
  }
  ```

## 6. 安全性

### Spring Security
- [ ] 是否正確配置 Spring Security（`SecurityFilterChain`）？
- [ ] 密碼是否使用 `BCryptPasswordEncoder` 或更強的加密？
- [ ] CSRF 保護是否適當啟用/停用？
- [ ] CORS 配置是否正確且安全？
- [ ] 是否實作適當的認證（JWT/OAuth2/Session）？

### 授權
- [ ] 是否使用方法級安全性（`@PreAuthorize`、`@Secured`）？
- [ ] 角色和權限是否正確定義？
- [ ] 敏感操作是否有授權檢查？

### 輸入驗證
- [ ] 是否使用 Bean Validation（`@Valid`、`@Validated`）？
- [ ] 自定義驗證器是否必要時實作？
- [ ] SQL Injection 是否防範（使用參數化查詢）？

## 7. 測試

### 單元測試
- [ ] Service 層是否有單元測試？
- [ ] 是否使用 `@Mock` 和 `@InjectMocks`（Mockito）？
- [ ] 測試是否獨立且可重複執行？

### 整合測試
- [ ] Controller 是否有整合測試（`@WebMvcTest`、`MockMvc`）？
- [ ] Repository 是否有測試（`@DataJpaTest`）？
- [ ] 是否使用測試資料庫（H2、Testcontainers）？
- [ ] `@SpringBootTest` 是否僅在必要時使用（較慢）？

### 測試覆蓋
- [ ] 關鍵業務邏輯是否有測試覆蓋？
- [ ] Edge case 是否有測試？
- [ ] 異常情況是否有測試？

## 8. 效能優化

### 快取
- [ ] 是否使用 Spring Cache（`@Cacheable`、`@CacheEvict`）？
- [ ] 快取策略是否合理（TTL、淘汰策略）？
- [ ] 是否避免快取穿透/擊穿/雪崩？

### 非同步處理
- [ ] 長時間運行的任務是否使用 `@Async`？
- [ ] 是否配置適當的 ThreadPoolTaskExecutor？
- [ ] 非同步方法是否有適當的錯誤處理？

### 資料庫優化
- [ ] 是否使用資料庫索引？
- [ ] 分頁查詢是否使用 `Pageable`？
- [ ] Batch Insert/Update 是否適當使用？
- [ ] 是否避免 SELECT \*（只查詢需要的欄位）？

## 9. 日誌與監控

### 日誌
- [ ] 是否使用 SLF4J 而非直接使用 Logback/Log4j？
- [ ] 日誌級別是否適當（DEBUG/INFO/WARN/ERROR）？
- [ ] 敏感資訊是否避免記錄？
- [ ] 是否使用 MDC（Mapped Diagnostic Context）記錄請求 ID？

### 監控
- [ ] 是否整合 Spring Boot Actuator？
- [ ] Health Check 端點是否正確配置？
- [ ] Metrics 是否暴露給監控系統（Prometheus/Grafana）？

## 10. Lombok 使用

### 適當使用
- [ ] 是否使用 `@Data`、`@Getter`、`@Setter` 減少樣板程式碼？
- [ ] 是否使用 `@Builder` 建立複雜物件？
- [ ] 是否使用 `@Slf4j` 簡化日誌？
- [ ] 是否使用 `@RequiredArgsConstructor` 進行建構子注入？

### 避免過度使用
- [ ] 是否避免在 Entity 上使用 `@Data`（可能導致性能問題）？
- [ ] 是否避免在 DTO 上使用 `@ToString` 包含敏感欄位？
- [ ] `@EqualsAndHashCode` 是否正確處理關聯關係？

## 11. 專案結構

### Package 組織
- [ ] 是否遵循分層架構（controller/service/repository/entity）？
- [ ] 或是否使用功能模組化組織（feature-based）？
- [ ] 是否避免循環依賴？

### 檔案命名
- [ ] Controller 是否以 `Controller` 結尾？
- [ ] Service 是否以 `Service` 結尾？
- [ ] Repository 是否以 `Repository` 結尾？
- [ ] DTO 是否清楚標示（`Request`、`Response`、`DTO`）？

## 12. API 文件

### Swagger / OpenAPI
- [ ] 是否整合 SpringDoc OpenAPI 或 Swagger？
- [ ] API 是否有清楚的描述（`@Operation`、`@ApiResponse`）？
- [ ] DTO 欄位是否有說明（`@Schema`）？

## 13. 常見錯誤檢查

### Anti-Patterns
- [ ] **是否避免在 Repository 中寫業務邏輯**？
- [ ] **是否避免在 Controller 中寫業務邏輯**？
- [ ] **是否避免 Service 依賴 Service 形成複雜依賴鏈**？
- [ ] **是否避免使用 `@Autowired` 在欄位注入**？
- [ ] **是否避免過度使用 `Optional`（僅在真正可能為空時使用）**？

### 記憶體洩漏
- [ ] 是否避免在單例 Bean 中持有大量資料？
- [ ] Stream 是否正確關閉？
- [ ] 是否避免在 ThreadLocal 中儲存大量資料不清理？

---

## 使用建議

1. **與通用檢查清單結合**：
   - 先檢查 [common.md](common.md) 的安全性和程式碼品質
   - 再檢查本檢查清單的 Spring Boot 特定項目

2. **優先級**：
   - 🔴 Critical: N+1 查詢、SQL Injection、密碼明文儲存
   - 🟡 Warning: 不當的 Bean 作用域、缺少事務管理
   - 🟢 Suggestion: Lombok 使用、程式碼組織

3. **工具輔助**：
   - 使用 SonarQube 檢查程式碼品質
   - 使用 SpotBugs 檢查潛在 bug
   - 啟用 Hibernate SQL 日誌檢查查詢效能

4. **持續學習**：
   - 參考 Spring Boot 官方文件
   - 學習 Spring Framework 核心概念
   - 關注 Spring Boot 版本更新和最佳實踐演進
