---
name: release-line-vs-tag-mismatch
description: git tag 命名與實際上架線嚴重錯位；洗車服務(SSGS-9377)雖在 main 上但從未上架
metadata: 
  node_type: memory
  type: project
  originSessionId: c82ffa25-5e9b-4819-8968-5731d8621df2
  modified: 2026-08-21T03:25:01.691Z
---

2026-08-21 為出版 2.24.2 追查得出。**不要用 tag 名稱推斷版本先後或內容。**

## 實際上架線 ≠ main 線

上架線是從 `1a2c24df`(tag `2.21.0`, 2026-04-30「現金儲值開啟」)分出的**旁支**：

- tag `2.24.0` = `9b281382`，`git diff 2.21.0 2.24.0` 只有 **3 檔 8 行**(targetSdk 36 + .gitlab-ci.yml + 版號)
- tag `2.21.1` = `4cf333b0`，也是從 `1a2c24df` 分出的另一條旁支，只有一顆「修改版本號」
- 所以 `2.21.1` 與 `2.24.0` **互不包含**，merge-base 是 `1a2c24df`

main 線(`2.22.0` → `2.23.3` → `2.24.1`)含洗車服務，**從未送審上架**。

## 兩個「2.24.0」

| tag | commit | pubspec | 位置 |
|---|---|---|---|
| `2.24.0` | `9b281382` | `2.24.0+704` | 旁支，無洗車 |
| `2.23.3` | `31d26e74` | **`2.24.0+706`** | main 線，含洗車 |

`2.23.2`(`1fd2f8fb`)同樣是不在 `2.24.1` 線上的旁支。

## 洗車入口從 2.22.0 就開著

不是 2.24.1 才上線。`be1a8501`(2026-05-21)把首頁 Grid 第三格從「人工站支付碼」(`card` / `onHomeScreenTapCard`)換成洗車，連續 7 個 tag(`2.22.0`~`2.23.3`、`2.24.1`)都是開著的。`2.24.0` 乾淨純粹因為它是洗車進 main 之前分出去的。

## 洗車與非洗車在 commit 層級深度交織

無法只 cherry-pick 非洗車功能：

- `c12e15ec`(tag `2.23.0`) 一顆同時做了快速洗車設定 **+ 快速加油設定 + 快速通行設定頁 + 支付設定頁**
- `cd0a081d`(tag `2.23.3`) 同時做了快速通行設定按鈕 **+ 支付方式選單重構**(`payway_option_list.dart`、`quick_mode_setting_utils.dart`)
- `be1a8501` 夾帶**信用卡申辦 banner** 和 gradle wrapper，直接 revert 會連帶砍掉

## 移除洗車只需斷兩個入口

程式碼再多，使用者摸得到的入口只有：

1. `lib/app/ui/home/home_screen.dart` 首頁 Grid 第三格 → `onHomeScreenTapCarWashEntry()`
2. `lib/app/ui/quick_pass_setting/quick_pass_setting_screen.dart` →「快速洗車設定」`showQuickWashBottomSheet()`

`station/widget/tile.dart` 和 `common/data/data.dart` 的「洗車服務」是**站點篩選標籤**，2.24.0 就有，與預約洗車無關，不要動。

## 地雷：SKIP_FORCE_UPDATE_CHECK

`lib/app/router/tab.dart` 有 `const bool SKIP_FORCE_UPDATE_CHECK = true`，強制更新檢查完全失效。由 `be1a8501` 帶入，所以只存在於 main 線；`2.24.0` 那條沒有。走 main 出版前務必改回 `false`。

相關：[[ios-simulator-ui-automation]]
