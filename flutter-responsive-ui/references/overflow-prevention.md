# Overflow Prevention Catalog

Every common Flutter overflow error with root cause and fix.

## Table of Contents

1. [RenderFlex Overflowed](#1-renderflex-overflowed)
2. [Vertical Viewport Unbounded Height](#2-vertical-viewport-unbounded-height)
3. [InputDecorator Unbounded Width](#3-inputdecorator-unbounded-width)
4. [RenderBox Not Laid Out](#4-renderbox-not-laid-out)
5. [BoxConstraints Forces Infinite Size](#5-boxconstraints-forces-infinite-size)
6. [Incorrect ParentDataWidget](#6-incorrect-parentdatawidget)
7. [Expanded in Scrollable](#7-expanded-in-scrollable)
8. [Nested ListViews](#8-nested-listviews)
9. [Stack Overflow with Positioned](#9-stack-overflow-with-positioned)
10. [Image Overflow](#10-image-overflow)
11. [Keyboard Overflow](#11-keyboard-overflow)
12. [IntrinsicHeight/Width Performance](#12-intrinsicheightwidth-performance)

---

## 1. RenderFlex Overflowed

**Error:** `A RenderFlex overflowed by X pixels on the right/bottom.`

**Cause:** Children of Row/Column exceed available space along the main axis.

**Scenarios and fixes:**

```dart
// Scenario A: Long text in Row
// BAD
Row(children: [Icon(Icons.star), Text('Very long text that keeps going')])
// FIX: Wrap text in Expanded
Row(children: [Icon(Icons.star), Expanded(child: Text('Very long text', overflow: TextOverflow.ellipsis))])

// Scenario B: Multiple fixed-width items exceed Row width
// BAD
Row(children: List.generate(10, (_) => SizedBox(width: 80, child: Chip(label: Text('Tag')))))
// FIX: Use Wrap instead of Row
Wrap(spacing: 8, runSpacing: 8, children: List.generate(10, (_) => Chip(label: Text('Tag'))))

// Scenario C: Column overflows vertically
// BAD — many fixed-height children
Column(children: List.generate(20, (_) => SizedBox(height: 60, child: ListTile(title: Text('Item')))))
// FIX: Make it scrollable
SingleChildScrollView(child: Column(children: [...]))
// Or use ListView directly
ListView.builder(itemCount: 20, itemBuilder: (_, i) => ListTile(title: Text('Item $i')))
```

## 2. Vertical Viewport Unbounded Height

**Error:** `Vertical viewport was given unbounded height.`

**Cause:** A scrollable widget (ListView, GridView) inside an unconstrained vertical context (Column without Expanded, another ListView).

```dart
// BAD
Column(children: [
  Text('Header'),
  ListView.builder(itemCount: 50, itemBuilder: (_, i) => Text('$i')),
])

// FIX Option 1: Expanded (preferred)
Column(children: [
  Text('Header'),
  Expanded(child: ListView.builder(itemCount: 50, itemBuilder: (_, i) => Text('$i'))),
])

// FIX Option 2: Fixed height
Column(children: [
  Text('Header'),
  SizedBox(height: 300, child: ListView.builder(itemCount: 50, itemBuilder: (_, i) => Text('$i'))),
])

// FIX Option 3: shrinkWrap (use sparingly — disables lazy rendering)
Column(children: [
  Text('Header'),
  ListView.builder(
    shrinkWrap: true,
    physics: const NeverScrollableScrollPhysics(),
    itemCount: 50,
    itemBuilder: (_, i) => Text('$i'),
  ),
])
```

## 3. InputDecorator Unbounded Width

**Error:** `An InputDecorator, which is typically created by a TextField, cannot have an unbounded width.`

**Cause:** TextField/TextFormField placed in Row/unconstrained context without width constraints.

```dart
// BAD
Row(children: [Text('Label'), TextField()])

// FIX
Row(children: [Text('Label'), SizedBox(width: 8), Expanded(child: TextField())])

// BAD — TextField in Column inside Row (Column has unbounded width from Row)
Row(children: [
  Column(children: [TextField()]),
])

// FIX
Row(children: [
  Expanded(child: Column(children: [TextField()])),
])
```

## 4. RenderBox Not Laid Out

**Error:** `RenderBox was not laid out: RenderFlex#xxxxx`

**Cause:** Usually a downstream effect of unbounded constraints. A widget couldn't determine its size because its parent gave it infinite constraints.

```dart
// BAD — Column inside Row without constraint
Row(children: [
  Column(children: [Text('A'), Text('B')]),
  Column(children: [Text('C'), Text('D')]),
])

// FIX — constrain columns
Row(children: [
  Expanded(child: Column(children: [Text('A'), Text('B')])),
  Expanded(child: Column(children: [Text('C'), Text('D')])),
])
```

## 5. BoxConstraints Forces Infinite Size

**Error:** `BoxConstraints forces an infinite width/height.`

**Cause:** A widget that tries to expand (like Container without explicit size) receives unbounded constraints.

```dart
// BAD — Container tries to maximize inside unconstrained context
Row(children: [Container(color: Colors.red)])

// FIX — give it explicit size or use Expanded
Row(children: [Expanded(child: Container(color: Colors.red))])
// or
Row(children: [SizedBox(width: 100, child: Container(color: Colors.red))])
```

## 6. Incorrect ParentDataWidget

**Error:** `Incorrect use of ParentDataWidget.`

**Cause:** Using a parent-data widget outside its required parent.

| Widget | Required parent |
|---|---|
| `Expanded` | `Row`, `Column`, `Flex` |
| `Flexible` | `Row`, `Column`, `Flex` |
| `Positioned` | `Stack` |
| `TableCell` | `Table` |

```dart
// BAD
Container(child: Expanded(child: Text('oops')))
// BAD
Column(children: [Positioned(child: Text('oops'))])

// FIX — use only inside correct parent
Row(children: [Expanded(child: Text('correct'))])
Stack(children: [Positioned(top: 0, child: Text('correct'))])
```

## 7. Expanded in Scrollable

**Error:** `RenderFlex children have non-zero flex but incoming height constraints are unbounded.`

**Cause:** Expanded/Flexible inside a Column that is inside a scrollable (SingleChildScrollView, ListView). The scrollable gives the Column unbounded height, so Expanded has no finite space to fill.

```dart
// BAD
SingleChildScrollView(
  child: Column(children: [
    Text('Top'),
    Expanded(child: Container(color: Colors.blue)), // Unbounded!
    Text('Bottom'),
  ]),
)

// FIX — use explicit size instead of Expanded
SingleChildScrollView(
  child: Column(children: [
    Text('Top'),
    SizedBox(height: 300, child: Container(color: Colors.blue)),
    Text('Bottom'),
  ]),
)

// FIX — if you need Expanded to fill the screen height
LayoutBuilder(builder: (context, constraints) {
  return SingleChildScrollView(
    child: ConstrainedBox(
      constraints: BoxConstraints(minHeight: constraints.maxHeight),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Top'),
          SizedBox(height: 300, child: Container(color: Colors.blue)),
          Text('Bottom'),
        ],
      ),
    ),
  );
})
```

## 8. Nested ListViews

**Cause:** ListView inside Column or another ListView without constraints.

```dart
// BAD — both unbounded
Column(children: [ListView(), ListView()])

// FIX Option 1: Expanded for each
Column(children: [
  Expanded(child: ListView(...)),
  Expanded(child: ListView(...)),
])

// FIX Option 2: CustomScrollView with Slivers (best performance)
CustomScrollView(slivers: [
  SliverList(delegate: SliverChildBuilderDelegate((_, i) => Text('List 1: $i'), childCount: 20)),
  const SliverToBoxAdapter(child: Divider()),
  SliverList(delegate: SliverChildBuilderDelegate((_, i) => Text('List 2: $i'), childCount: 20)),
])

// FIX Option 3: shrinkWrap (avoid for long lists — O(N) layout)
Column(children: [
  ListView(shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), children: [...]),
  ListView(shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), children: [...]),
])
```

## 9. Stack Overflow with Positioned

**Cause:** Positioned widget extends beyond Stack bounds without clipping.

```dart
// BAD — child overflows Stack
SizedBox(
  height: 100,
  child: Stack(children: [
    Positioned(top: -20, child: Container(height: 50, color: Colors.red)),
  ]),
)

// FIX — use clipBehavior
SizedBox(
  height: 100,
  child: Stack(
    clipBehavior: Clip.none, // Allow overflow (intentional)
    children: [Positioned(top: -20, child: Container(height: 50, color: Colors.red))],
  ),
)

// Or constrain the Stack size properly
```

## 10. Image Overflow

**Cause:** Image has intrinsic size larger than available constraints.

```dart
// BAD — image may be wider than screen
Row(children: [Image.network('large-image.jpg'), Text('Caption')])

// FIX
Row(children: [
  Expanded(child: Image.network('large-image.jpg', fit: BoxFit.cover)),
  Expanded(child: Text('Caption')),
])

// For standalone images that must fit
ConstrainedBox(
  constraints: BoxConstraints(maxWidth: 400, maxHeight: 300),
  child: Image.network('large-image.jpg', fit: BoxFit.contain),
)
```

## 11. Keyboard Overflow

**Cause:** When the keyboard opens, it reduces available height, causing a Column to overflow.

```dart
// BAD — fixed layout overflows when keyboard appears
Scaffold(
  body: Column(children: [
    // ... many widgets
    TextField(), // keyboard pushes everything up
  ]),
)

// FIX Option 1: Make scrollable
Scaffold(
  body: SingleChildScrollView(
    child: Column(children: [
      // ... many widgets
      TextField(),
    ]),
  ),
)

// FIX Option 2: resizeToAvoidBottomInset
Scaffold(
  resizeToAvoidBottomInset: false, // Only if you handle padding manually
  body: Column(children: [...]),
)

// FIX Option 3: Use padding to account for keyboard
Scaffold(
  body: SingleChildScrollView(
    padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(context).bottom),
    child: Column(children: [...]),
  ),
)
```

## 12. IntrinsicHeight/Width Performance

**Not an error** but a common performance pitfall.

`IntrinsicHeight` and `IntrinsicWidth` cause **O(N^2)** layout passes. Use sparingly.

```dart
// AVOID in hot paths (lists, grids)
ListView.builder(
  itemBuilder: (_, i) => IntrinsicHeight(child: Row(children: [...])), // O(N^2) per item!
)

// PREFER Expanded/Flexible for cross-axis sizing
Row(
  crossAxisAlignment: CrossAxisAlignment.stretch, // All children match Row height
  children: [Expanded(child: CardA()), Expanded(child: CardB())],
)
```
