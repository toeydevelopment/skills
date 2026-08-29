---
name: flutter-responsive-ui
description: Expert-level Flutter responsive UI implementation with zero overflow errors and zero layout issues. Provides constraint-aware widget composition, responsive breakpoint patterns, safe Flex/Scroll nesting, and platform-adaptive layouts. Trigger when writing Flutter UI code, building layouts, fixing overflow errors, implementing responsive designs, using Row/Column/ListView/Expanded/Flexible, creating adaptive navigation, or when user mentions "responsive", "overflow", "layout issue", "RenderFlex overflowed", "unbounded height", "adaptive UI", or "breakpoints" in a Flutter/Dart context.
---

# Flutter Responsive UI Expert

Build Flutter UIs that never overflow, adapt to any screen size, and follow the constraint system correctly.

## The Golden Rule

**"Constraints go down. Sizes go up. Parent sets position."**

Before placing any widget, ask: "What constraints will this widget receive, and how will it size itself?"

## Constraint Types

| Type | Condition | Example |
|---|---|---|
| **Tight** | min == max | Screen root, `SizedBox(width: 100)` |
| **Loose** | min < max (min can be 0) | Inside `Center`, `Align` |
| **Unbounded** | max == infinity | Scroll direction of `ListView`, main axis of `Row`/`Column` inside scroll |

## Critical Safety Rules

These rules prevent the most common Flutter layout failures.

### Rule 1: Constrain children in Flex widgets
```dart
// WRONG — Text overflows Row
Row(children: [Icon(Icons.star), Text('Very long text that will overflow')])

// CORRECT
Row(children: [Icon(Icons.star), Expanded(child: Text('Very long text'))])
```

### Rule 2: Constrain scrollables inside Flex
```dart
// WRONG — "Vertical viewport was given unbounded height"
Column(children: [Text('Header'), ListView.builder(...)])

// CORRECT
Column(children: [Text('Header'), Expanded(child: ListView.builder(...))])
```

### Rule 3: Never put Expanded/Flexible inside a scrollable
```dart
// WRONG — Expanded has no bounded constraint to fill
SingleChildScrollView(child: Column(children: [Expanded(child: Box())]))

// CORRECT — use explicit size
SingleChildScrollView(child: Column(children: [SizedBox(height: 200, child: Box())]))
```

### Rule 4: Constrain TextFields in Row
```dart
// WRONG — "An InputDecorator cannot have an unbounded width"
Row(children: [TextField()])

// CORRECT
Row(children: [Expanded(child: TextField())])
```

### Rule 5: Expanded/Flexible only inside Row/Column/Flex
```dart
// WRONG — "Incorrect use of ParentDataWidget"
Container(child: Expanded(child: Text('x')))

// Expanded/Flexible → only inside Row, Column, Flex
// Positioned → only inside Stack
```

### Rule 6: Use MediaQuery.sizeOf, not MediaQuery.of
```dart
// WRONG — rebuilds on ANY MediaQuery change (keyboard, padding, etc.)
final size = MediaQuery.of(context).size;

// CORRECT — only rebuilds when size changes
final size = MediaQuery.sizeOf(context);
```

### Rule 7: Wrap Scaffold body in SafeArea
```dart
// Handle notches, status bars, navigation bars
Scaffold(
  body: SafeArea(child: YourContent()),
)
```

### Rule 8: Constrain content width on large screens
```dart
// WRONG — text/content stretches across 2000px monitor
Scaffold(body: ListView(children: [...]))

// CORRECT
Scaffold(
  body: Center(
    child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 840),
      child: ListView(children: [...]),
    ),
  ),
)
```

## Responsive Breakpoints (Material 3)

| Window Class | Width | Navigation | Layout |
|---|---|---|---|
| Compact | < 600 | BottomNavigationBar | Single column |
| Medium | 600–839 | NavigationRail | 2-column / master-detail |
| Expanded | 840–1199 | NavigationRail + labels | Multi-column |
| Large | >= 1200 | Permanent drawer | Multi-column, max-width |

## Responsive Implementation

Use `LayoutBuilder` for component-level, `MediaQuery.sizeOf` for app-level decisions.

```dart
// App-level: choose navigation style
final width = MediaQuery.sizeOf(context).width;
if (width < 600) return _MobileScaffold();
if (width < 1200) return _TabletScaffold();
return _DesktopScaffold();

// Component-level: adapt grid columns
LayoutBuilder(builder: (context, constraints) {
  final cols = switch (constraints.maxWidth) {
    < 400 => 1,
    < 800 => 2,
    _ => 3,
  };
  return GridView.count(crossAxisCount: cols, children: items);
})
```

## Widget Selection Guide

| Need | Widget | Key behavior |
|---|---|---|
| Fill ALL remaining space | `Expanded` | Forces child to fill allocated flex space |
| Fill UP TO remaining space | `Flexible` | Allows child to be smaller |
| Exact fixed dimension | `SizedBox` | Tight constraints |
| Percentage of parent | `FractionallySizedBox` | Fraction-based sizing |
| Min/max bounds | `ConstrainedBox` | Adds constraint layer |
| Items that may overflow a Row | `Wrap` | Flows to next line |
| Long text in a Row | `Expanded` + `Text(overflow: TextOverflow.ellipsis)` | Prevents overflow |
| Scale text to fit | `FittedBox(fit: BoxFit.scaleDown)` | Auto-shrinks |

## Common Anti-Patterns

| Anti-pattern | Why it's wrong | Do instead |
|---|---|---|
| `Platform.isAndroid` for layout | Foldables/tablets break assumption | Use `MediaQuery.sizeOf` width |
| `OrientationBuilder` for layout | Orientation != available space | Use `LayoutBuilder` |
| Locking orientation | Breaks foldables, multi-window, a11y | Support all orientations |
| Hardcoded pixel sizes (375, 812) | Only fits one device | Use relative/constraint-based sizing |
| `IntrinsicHeight` in lists | O(N^2) layout per item | Use `CrossAxisAlignment.stretch` |
| `shrinkWrap: true` on long lists | Disables lazy rendering, O(N) | Use Slivers or Expanded |
| `MediaQuery.of(context).size` | Rebuilds on keyboard/padding changes | Use `MediaQuery.sizeOf(context)` |

## Reference Guides

- **Overflow Prevention Catalog** — Every common overflow error with cause and fix: [references/overflow-prevention.md](references/overflow-prevention.md)
- **Safe Scroll Patterns** — Nested scrollables, slivers, complex scroll layouts: [references/scroll-patterns.md](references/scroll-patterns.md)
- **Responsive Layout Recipes** — Adaptive nav, master-detail, responsive grid, forms: [references/responsive-recipes.md](references/responsive-recipes.md)

## Pre-Implementation Checklist

Before writing any layout widget, verify:

1. **What constraints does this widget receive?** (tight, loose, unbounded)
2. **How does this widget size itself?** (maximize, match child, fixed)
3. **Is any child inside a Flex (Row/Column) without constraint?** Add Expanded/Flexible
4. **Is a scrollable inside a Flex?** Wrap in Expanded or give fixed height
5. **Is Expanded/Flexible inside a scrollable?** Replace with SizedBox
6. **Could text or content exceed available width?** Add overflow handling
7. **Does the layout work at 320px AND 1920px?** Test both extremes
8. **Is content max-width constrained for large screens?** Add ConstrainedBox
