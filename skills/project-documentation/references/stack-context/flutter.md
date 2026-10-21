# B2B Manager 專案上下文

本文件提供專案的核心資訊，用於產出一致且準確的文件。

## 專案概述

**B2B Manager（山隆 B2B 智慧平台）** 是一個純 Flutter Web 應用程式，用於石油 B2B 管理系統。

- ❌ 沒有 iOS 版本
- ❌ 沒有 Android 版本
- ✅ 僅支援網頁版（編譯為 JavaScript + WebAssembly）
- ✅ 透過 Docker/Nginx 部署

## 技術棧

### 核心框架
- Flutter: 3.3.0+
- Dart SDK: >=3.3.0 <4.0.0
- 平台: Web Only

### 狀態管理
- flutter_riverpod: ^2.6.1（主要）
- hooks_riverpod: ^2.6.1（Hooks 整合）
- StateNotifierProvider 用於複雜業務邏輯
- StateProvider 用於簡單狀態

### 網路層
- dio: ^5.4.2+1（HTTP 客戶端）
- retrofit: ^4.7.2（型別安全的 REST API）
- Retrofit 自動產生 API 客戶端
- Dio Interceptors 處理認證 token、401 錯誤

### 路由
- go_router: ^14.6.1（宣告式路由）
- ShellRoute 提供持久化導覽外殼
- 路徑式 URL（非 hash 模式）

### 認證
- oauth2: ^2.0.2（OAuth2 實作）
- OAuth2 Authorization Code Flow with PKCE
- TaskManager 單例模式防止重複 API 呼叫 ⚠️

## 目錄結構

```
lib/
├── api/                    # 所有 API 和網路層程式碼
│   ├── connector/          # HTTP 客戶端、OAuth2、TaskManager
│   ├── interceptor/        # Request/Response 攔截器
│   ├── restclient/         # Retrofit API 定義（自動產生）
│   ├── request/            # API 請求 DTO
│   ├── response/           # API 回應 DTO
│   └── notifier/           # StateNotifier（業務邏輯層）
│
├── page/                   # UI 頁面（依功能組織）
│   ├── home/              # 儀表板與圖表
│   ├── order/             # 訂單管理
│   ├── balance/           # 財務管理
│   ├── car/               # 車隊管理
│   ├── driver/            # 司機管理
│   └── page_route.dart    # GoRouter 路由配置
│
├── models/                # 資料模型與列舉
├── notifier/              # Riverpod 狀態管理
├── util/                  # 工具函數
└── main.dart              # 應用程式入口點
```

## 關鍵架構模式

### 1. TaskManager 單例模式
- 位置：`lib/api/connector/task_manager.dart`
- 目的：防止重複的 OAuth2 認證和 token 更新請求
- ⚠️ 絕對不可移除

### 2. Riverpod 狀態管理
- StateNotifierProvider：複雜業務邏輯（含方法）
- StateProvider：簡單狀態（布林值、數字）
- FutureProvider：非同步資料獲取

### 3. API 呼叫流程
```
Widget → StateNotifier → Retrofit API → Dio Interceptor → TaskManager → 後端
```

### 4. 程式碼產生
需要執行 build_runner 的情況：
- 新增或修改 `lib/api/restclient/*.dart`
- 新增或修改 `lib/api/request/*.dart`
- 新增或修改 `lib/api/response/*.dart`
- 新增 `@JsonSerializable()` 類別

## 文件格式要求

- Markdown 格式
- 繁體中文（zh-TW）
- 包含代碼位置標註（檔案路徑:行號）
- 清晰的章節結構和目錄
- 技術性且簡潔的說明風格