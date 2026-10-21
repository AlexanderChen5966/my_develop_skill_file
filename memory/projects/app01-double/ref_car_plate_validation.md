---
name: ref-car-plate-validation
description: 另一個專案的新增車輛車號阻擋邏輯（驗證順序與規則）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1d997c83-282e-40de-a33a-6bc2798d0d4c
---

## 新增車輛 車號阻擋邏輯（另一個專案）

實作位置：`lib/page/car/widgets/car_drawer.dart`（`_FooterBtn` widget 的 `onPressed`）

### 驗證順序

1. **群組選擇檢查**：`groupId == 0` → toast `"select_group"`
2. **車號空值檢查**：`plateNumber` 為空 → toast `"input_plate_number"`
3. **車號長度檢查**：超過 7 字元 → toast `"input_correct_plate_number"`
4. **別名長度檢查**：`alias` 超過 20 字元 → toast `"input_correct_alias"`
5. **車號格式（Regex）**：`lib/util/regular_regex.dart`
   ```dart
   plateNumberRegex = RegExp(r'^[A-Z\d]+(\d*[A-Z\d]*)*$');
   ```
   只允許大寫字母和數字，不符合 → toast `"plate_number_validate_message"`
