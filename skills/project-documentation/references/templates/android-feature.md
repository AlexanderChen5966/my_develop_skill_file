# Android 功能文件範本

> **TODO**: 此範本待完成。當需要產出 Android 功能文件時填充。

## 預期章節結構

### 1. 功能概述
- 功能描述
- 主要 Activity/Fragment
- ViewModel 名稱

### 2. UI 層
```markdown
## UI 組件

### Activity/Fragment
- **路徑**: `com.company.ui.FeatureActivity`
- **Layout**: `activity_feature.xml` 或 Composable 函數
- **功能**: 說明
```

### 3. ViewModel 與狀態管理
- ViewModel 類別
- LiveData/StateFlow 定義
- UI 事件處理

### 4. 資料層
- Repository 介面和實作
- Data Source（Local/Remote）
- Room Entity 或 Retrofit API

### 5. API 整合（如適用）
- Retrofit 介面定義
- Request/Response 模型
- 錯誤處理

### 6. 導航
- Navigation Graph 定義
- Deep Links
- 傳遞參數

---

**範本格式參考**:
- 參考 Flutter 範本結構
- 調整為 Android MVVM 架構