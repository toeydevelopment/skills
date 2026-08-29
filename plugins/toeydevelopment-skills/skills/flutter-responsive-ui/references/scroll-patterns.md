# Safe Scroll Patterns

Patterns for nested scrollables, complex scroll layouts, and sliver-based designs.

## Table of Contents

1. [Column with Scrollable Content](#1-column-with-scrollable-content)
2. [Multiple Lists in One View](#2-multiple-lists-in-one-view)
3. [Collapsible Header with List](#3-collapsible-header-with-list)
4. [TabBarView with Lists](#4-tabbarview-with-lists)
5. [Horizontal List inside Vertical Scroll](#5-horizontal-list-inside-vertical-scroll)
6. [Scrollable Form with Fixed Button](#6-scrollable-form-with-fixed-button)
7. [Pull-to-Refresh](#7-pull-to-refresh)

---

## 1. Column with Scrollable Content

```dart
// Pattern: Fixed header + scrollable list
Column(children: [
  // Fixed part — does not scroll
  Container(height: 56, child: Text('Header')),
  // Scrollable part — MUST be wrapped in Expanded
  Expanded(
    child: ListView.builder(
      itemCount: items.length,
      itemBuilder: (_, i) => ListTile(title: Text(items[i])),
    ),
  ),
])
```

## 2. Multiple Lists in One View

```dart
// BEST: CustomScrollView with Slivers
CustomScrollView(slivers: [
  const SliverToBoxAdapter(child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Section 1', style: TextStyle(fontSize: 20)),
  )),
  SliverList.builder(
    itemCount: section1.length,
    itemBuilder: (_, i) => ListTile(title: Text(section1[i])),
  ),
  const SliverToBoxAdapter(child: Divider()),
  const SliverToBoxAdapter(child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Section 2', style: TextStyle(fontSize: 20)),
  )),
  SliverGrid.count(
    crossAxisCount: 2,
    children: section2.map((e) => Card(child: Center(child: Text(e)))).toList(),
  ),
])
```

## 3. Collapsible Header with List

```dart
// NestedScrollView for coordinated scrolling
NestedScrollView(
  headerSliverBuilder: (context, innerBoxIsScrolled) => [
    SliverAppBar(
      expandedHeight: 200,
      floating: false,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        title: const Text('Title'),
        background: Image.network('header.jpg', fit: BoxFit.cover),
      ),
    ),
  ],
  body: ListView.builder(
    itemCount: 50,
    itemBuilder: (_, i) => ListTile(title: Text('Item $i')),
  ),
)
```

## 4. TabBarView with Lists

```dart
// Each tab has its own scrollable list
DefaultTabController(
  length: 3,
  child: NestedScrollView(
    headerSliverBuilder: (context, innerBoxIsScrolled) => [
      SliverAppBar(
        title: const Text('Tabs'),
        pinned: true,
        floating: true,
        bottom: const TabBar(tabs: [
          Tab(text: 'Tab 1'),
          Tab(text: 'Tab 2'),
          Tab(text: 'Tab 3'),
        ]),
      ),
    ],
    body: TabBarView(children: [
      ListView.builder(itemCount: 30, itemBuilder: (_, i) => ListTile(title: Text('Tab1: $i'))),
      ListView.builder(itemCount: 30, itemBuilder: (_, i) => ListTile(title: Text('Tab2: $i'))),
      ListView.builder(itemCount: 30, itemBuilder: (_, i) => ListTile(title: Text('Tab3: $i'))),
    ]),
  ),
)
```

## 5. Horizontal List inside Vertical Scroll

```dart
// Horizontal list needs explicit height — it receives unbounded width from scroll, but needs height constraint
SingleChildScrollView(
  child: Column(children: [
    const Text('Featured'),
    SizedBox(
      height: 200, // REQUIRED — horizontal list needs bounded height
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: 10,
        itemBuilder: (_, i) => SizedBox(
          width: 150,
          child: Card(child: Center(child: Text('Card $i'))),
        ),
      ),
    ),
    const Text('All Items'),
    // Use shrinkWrap here since it's inside SingleChildScrollView
    ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: 20,
      itemBuilder: (_, i) => ListTile(title: Text('Item $i')),
    ),
  ]),
)

// BETTER: Sliver-based approach for long vertical list
CustomScrollView(slivers: [
  const SliverToBoxAdapter(child: Text('Featured')),
  SliverToBoxAdapter(
    child: SizedBox(
      height: 200,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: 10,
        itemBuilder: (_, i) => SizedBox(width: 150, child: Card(child: Center(child: Text('Card $i')))),
      ),
    ),
  ),
  const SliverToBoxAdapter(child: Text('All Items')),
  SliverList.builder(
    itemCount: 20,
    itemBuilder: (_, i) => ListTile(title: Text('Item $i')),
  ),
])
```

## 6. Scrollable Form with Fixed Button

```dart
// Pattern: Form scrolls, button stays fixed at bottom
Scaffold(
  body: SafeArea(
    child: Column(children: [
      // Scrollable form — takes all remaining space
      Expanded(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(decoration: const InputDecoration(labelText: 'Name')),
              const SizedBox(height: 16),
              TextFormField(decoration: const InputDecoration(labelText: 'Email')),
              const SizedBox(height: 16),
              TextFormField(decoration: const InputDecoration(labelText: 'Message'), maxLines: 5),
            ],
          ),
        ),
      ),
      // Fixed button at bottom
      Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          width: double.infinity,
          child: ElevatedButton(onPressed: () {}, child: const Text('Submit')),
        ),
      ),
    ]),
  ),
)
```

## 7. Pull-to-Refresh

```dart
// RefreshIndicator wraps a scrollable
RefreshIndicator(
  onRefresh: () async { /* fetch data */ },
  child: ListView.builder(
    // physics must allow overscroll for RefreshIndicator to trigger
    physics: const AlwaysScrollableScrollPhysics(),
    itemCount: items.length,
    itemBuilder: (_, i) => ListTile(title: Text(items[i])),
  ),
)

// For CustomScrollView
RefreshIndicator(
  onRefresh: () async { /* fetch data */ },
  child: CustomScrollView(
    physics: const AlwaysScrollableScrollPhysics(),
    slivers: [
      SliverList.builder(
        itemCount: items.length,
        itemBuilder: (_, i) => ListTile(title: Text(items[i])),
      ),
    ],
  ),
)
```
