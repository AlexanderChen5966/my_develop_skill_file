# Spring Boot 專案上下文

## 專案概述

- **框架：** Spring Boot 3.4.3
- **Java 版本：** 17
- **建構工具：** Maven（多模組）
- **部署方式：** Docker / AWS ECS (Fargate)
- **資料存取：** Spring Data JDBC（非 JPA）
- **API 文件：** Swagger / OpenAPI 3 (`@Operation`, `@Tag`)
- **權限控制：** Spring Security + `@PreAuthorize`
- **物件映射：** ModelMapper + Lombok

## 多模組結構

```
ssgs-b2b/
├── pom.xml                          # 父 POM（依賴管理）
├── ssgs-b2b-app/                    # 應用層（Controller、Config、DTO）
│   └── src/main/java/com/slc/ssgsb2b/app/
│       ├── ApiApplication.java
│       ├── configs/                 # 配置（Security、Filter、Interceptor）
│       │   ├── filters/
│       │   ├── interceptors/
│       │   └── security/
│       │       └── annotations/
│       ├── controllers/             # REST Controller
│       └── dto/                     # DTO（Request/Response）
│           ├── requests/
│           └── responses/
├── ssgs-b2b-dao/                    # 資料存取層（Entity、Repository、Enum）
│   └── src/main/java/com/slc/ssgsb2b/dao/
│       ├── configs/
│       │   ├── converters/
│       │   └── security/
│       ├── domain/                  # Entity（@Table + Lombok）
│       │   └── interfaces/
│       ├── enums/                   # 列舉型別
│       ├── repositories/            # CrudRepository 介面
│       │   └── mongodb/
│       └── utils/
└── ssgs-b2b-lib/                    # 商業邏輯層（Service、Domain、Constraint）
    └── src/main/java/com/slc/ssgsb2b/lib/
        ├── annotations/
        ├── configs/
        │   └── modelmapper/converters/
        ├── constraints/             # 自訂驗證（@ValidCarId 等）
        ├── domain/                  # 領域物件
        │   ├── aggregates/
        │   ├── requests/            # 請求物件
        │   └── responses/           # 回應物件
        ├── enums/
        ├── exceptions/              # 自訂例外
        ├── interfaces/
        ├── notifications/
        ├── services/                # 商業邏輯 Service
        │   ├── aggregators/
        │   ├── eip/                 # EIP 整合服務
        │   ├── firebase/            # Firebase 推播服務
        │   └── serverless/uec/      # Serverless 函數呼叫
        └── utils/
```

## 關鍵架構模式

### Controller → Service → Repository

```
Controller (app)  →  Service (lib)  →  Repository (dao)
     ↓                    ↓                   ↓
  DTO 轉換           商業邏輯           Spring Data JDBC
  權限檢查           交易管理           SQL 查詢
  Swagger 標註       驗證邏輯           Entity 映射
```

### Entity 定義風格

```java
@Table("group_car")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CarEntity {
    @Id
    private Long id;
    // Lombok 自動產生 getter/setter
}
```

### Repository 風格

```java
@Repository
public interface CarRepository extends CrudRepository<CarEntity, Long>, CustomRepository {
    Optional<CarEntity> findByIdAndGroupIdIn(Long id, List<Long> groupIds);

    @Query("SELECT ... FROM ... WHERE ...")
    boolean existsAsUserCarByPlateNumber(String plateNumber);
}
```

### Controller 風格

```java
@Tag(name = "Cars")
@RestController
@RequestMapping("/cars")
public class CarController extends BaseController {

    @PostMapping("/search")
    @Operation(summary = "Search cars")
    @PreAuthorize("hasAuthority('cars:read')")
    public SearchResult<CarSearchResult> search(...) { }
}
```

## 文件格式要求

- **語言：** 繁體中文（zh-TW）
- **格式：** Markdown
- **代碼標註：** 完整類別路徑 + 行號（`CarController.java:52`）
- **風格：** 技術性且簡潔
