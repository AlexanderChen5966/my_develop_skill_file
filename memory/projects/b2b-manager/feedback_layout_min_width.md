---
name: 雙面板 fill-viewport 佈局標準模式
description: 左右雙面板頁面的最終佈局策略：LayoutBuilder 取可用寬 + 固定最小面板像素 + 水平捲軸
type: feedback
originSessionId: 700e0458-acba-46a7-8b6b-2c0bd48a9f79
---
## 標準模式（已驗證，batch_edit_car_page.dart 採用）

參考 Dashboard 頁面做法。用 `LayoutBuilder` 取得 `CustomAnimatedContainer` 給予的實際可用寬度（已自動扣除側邊欄），再計算固定面板像素。

```dart
body: LayoutBuilder(
  builder: (context, constraints) {
    const double minPanelWidth = 560.0;
    const double sideGap = 85.0; // padding 42*2 + divider 1
    final double availableWidth = constraints.maxWidth;
    final double panelWidth = availableWidth >= minPanelWidth * 2 + sideGap
        ? (availableWidth - sideGap) / 2   // 夠寬：等分
        : minPanelWidth;                   // 不夠寬：固定最小值，出現捲軸
    final double contentWidth = panelWidth * 2 + sideGap;

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SizedBox(
        width: contentWidth,
        child: Column(
          children: [
            breadcrumb,
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(42, 16, 42, 0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    SizedBox(width: panelWidth, child: _buildLeftPanel(...)),
                    const VerticalDivider(width: 1, thickness: 1),
                    SizedBox(width: panelWidth, child: _buildRightPanel(...)),
                  ],
                ),
              ),
            ),
            Divider,
            footer,
          ],
        ),
      ),
    );
  },
),
```

**縮放行為**（以 1920px 螢幕 + 側邊欄 300px 展開為例）：

| 情境 | 可用寬 | 每個面板 | 水平捲軸 |
|------|--------|----------|---------|
| 1920px 全版 | 1620px | 767.5px | 無 |
| 1440px 全版 | 1140px | 527.5px | 無 |
| 1366px 全版 | 1066px | 560px（最小值）| 出現 |
| 縮小 / 縮放 | 任意 | 最少 560px | 出現 |

**Why:**
- `LayoutBuilder` 讓頁面不需要知道側邊欄狀態，`CustomAnimatedContainer` 已處理
- 不用 `Expanded` 防止面板無限縮窄導致跑版
- 水平捲軸取代版面崩潰，使用者可以捲動而非看到亂掉的排版

**How to apply:** 任何「左右兩欄 fill-viewport」頁面都套用此模式。調整 `minPanelWidth` 依頁面內容最小可用寬決定。

---

## 附：_buildEmptyState LayoutBuilder Bug 修正記錄

**Bug**：`maxSvgSize` 計算後未代入 `buildSvgImage`，SVG 固定 300px；中文標題換行後總高超出可用空間，溢出 92px。

**Fix**（batch_edit_car_page.dart `_buildEmptyState`）：
```dart
return LayoutBuilder(builder: (context, constraints) {
  // 文字估算 72px（允許中文大字換行為 2 行）
  final svgVisible = (constraints.maxHeight - 72).clamp(0.0, 200.0);
  final svgSize = svgVisible > 0 ? svgVisible / 0.8 : 0.0;
  return Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SLText.body(text: text, ..., fontSize: 24),
        if (svgSize > 0)
          ClipRect(
            child: Align(
              heightFactor: 0.8,
              child: buildSvgImage('...', svgSize, svgSize), // ← 使用計算值
            ),
          ),
      ],
    ),
  );
});
```

**Why:** 原始程式碼計算 `maxSvgSize` 但傳入固定 `300, 300`，計算結果完全沒有使用。
