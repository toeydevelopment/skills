# Responsive Layout Recipes

Ready-to-use responsive patterns for common Flutter UI scenarios.

## Table of Contents

1. [Adaptive Navigation Scaffold](#1-adaptive-navigation-scaffold)
2. [Master-Detail Layout](#2-master-detail-layout)
3. [Responsive Grid](#3-responsive-grid)
4. [Responsive Form Layout](#4-responsive-form-layout)
5. [Adaptive Dialog / Bottom Sheet](#5-adaptive-dialog--bottom-sheet)
6. [Responsive Card Grid](#6-responsive-card-grid)
7. [Max-Width Content Wrapper](#7-max-width-content-wrapper)
8. [Responsive Data Table](#8-responsive-data-table)
9. [Adaptive App Bar](#9-adaptive-app-bar)

---

## 1. Adaptive Navigation Scaffold

Switches between bottom nav (mobile), rail (tablet), and permanent drawer (desktop).

```dart
class AdaptiveScaffold extends StatefulWidget {
  final List<AdaptiveDestination> destinations;
  final List<Widget> pages;
  const AdaptiveScaffold({super.key, required this.destinations, required this.pages});

  @override
  State<AdaptiveScaffold> createState() => _AdaptiveScaffoldState();
}

class _AdaptiveScaffoldState extends State<AdaptiveScaffold> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;

    // Desktop: permanent side navigation
    if (width >= 1200) {
      return Scaffold(
        body: Row(children: [
          NavigationDrawer(
            selectedIndex: _index,
            onDestinationSelected: (i) => setState(() => _index = i),
            children: [
              const SizedBox(height: 16),
              ...widget.destinations.map((d) =>
                NavigationDrawerDestination(icon: d.icon, label: Text(d.label))),
            ],
          ),
          Expanded(child: widget.pages[_index]),
        ]),
      );
    }

    // Tablet: navigation rail
    if (width >= 600) {
      return Scaffold(
        body: Row(children: [
          NavigationRail(
            selectedIndex: _index,
            onDestinationSelected: (i) => setState(() => _index = i),
            labelType: width >= 840
                ? NavigationRailLabelType.all
                : NavigationRailLabelType.selected,
            destinations: widget.destinations.map((d) =>
              NavigationRailDestination(icon: d.icon, label: Text(d.label))).toList(),
          ),
          const VerticalDivider(thickness: 1, width: 1),
          Expanded(child: widget.pages[_index]),
        ]),
      );
    }

    // Mobile: bottom navigation
    return Scaffold(
      body: widget.pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: widget.destinations.map((d) =>
          NavigationDestination(icon: d.icon, label: d.label)).toList(),
      ),
    );
  }
}

class AdaptiveDestination {
  final Icon icon;
  final String label;
  const AdaptiveDestination({required this.icon, required this.label});
}
```

## 2. Master-Detail Layout

Side-by-side on wide screens, push navigation on narrow.

```dart
class MasterDetailLayout<T> extends StatefulWidget {
  final List<T> items;
  final Widget Function(T item, bool isSelected) masterBuilder;
  final Widget Function(T item) detailBuilder;
  final Widget emptyDetail;

  const MasterDetailLayout({
    super.key,
    required this.items,
    required this.masterBuilder,
    required this.detailBuilder,
    this.emptyDetail = const Center(child: Text('Select an item')),
  });

  @override
  State<MasterDetailLayout<T>> createState() => _MasterDetailLayoutState<T>();
}

class _MasterDetailLayoutState<T> extends State<MasterDetailLayout<T>> {
  T? _selected;

  @override
  Widget build(BuildContext context) {
    final isWide = MediaQuery.sizeOf(context).width >= 840;

    Widget masterList = ListView.builder(
      itemCount: widget.items.length,
      itemBuilder: (_, i) {
        final item = widget.items[i];
        return GestureDetector(
          onTap: () {
            if (isWide) {
              setState(() => _selected = item);
            } else {
              Navigator.push(context, MaterialPageRoute(
                builder: (_) => Scaffold(
                  appBar: AppBar(),
                  body: widget.detailBuilder(item),
                ),
              ));
            }
          },
          child: widget.masterBuilder(item, _selected == item),
        );
      },
    );

    if (!isWide) return masterList;

    return Row(children: [
      SizedBox(width: 360, child: masterList),
      const VerticalDivider(thickness: 1, width: 1),
      Expanded(
        child: _selected != null
            ? widget.detailBuilder(_selected as T)
            : widget.emptyDetail,
      ),
    ]);
  }
}
```

## 3. Responsive Grid

Adapts column count based on available width.

```dart
class ResponsiveGrid extends StatelessWidget {
  final List<Widget> children;
  final double minItemWidth;
  final double spacing;

  const ResponsiveGrid({
    super.key,
    required this.children,
    this.minItemWidth = 300,
    this.spacing = 16,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      final cols = (constraints.maxWidth / minItemWidth).floor().clamp(1, 4);
      return GridView.count(
        crossAxisCount: cols,
        mainAxisSpacing: spacing,
        crossAxisSpacing: spacing,
        padding: EdgeInsets.all(spacing),
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        children: children,
      );
    });
  }
}

// Usage inside a scrollable
SingleChildScrollView(
  child: Column(children: [
    const Text('Products'),
    ResponsiveGrid(children: products.map((p) => ProductCard(p)).toList()),
  ]),
)
```

## 4. Responsive Form Layout

Fields stack vertically on mobile, arrange in rows on wider screens.

```dart
class ResponsiveFormRow extends StatelessWidget {
  final List<Widget> children;

  const ResponsiveFormRow({super.key, required this.children});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      // Stack vertically on narrow screens
      if (constraints.maxWidth < 600) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: children.map((c) => Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: c,
          )).toList(),
        );
      }

      // Side by side on wider screens
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: children.asMap().entries.map((e) => Expanded(
          child: Padding(
            padding: EdgeInsets.only(
              left: e.key > 0 ? 8 : 0,
              right: e.key < children.length - 1 ? 8 : 0,
            ),
            child: e.value,
          ),
        )).toList(),
      );
    });
  }
}

// Usage
SingleChildScrollView(
  padding: const EdgeInsets.all(16),
  child: Column(children: [
    ResponsiveFormRow(children: [
      TextFormField(decoration: const InputDecoration(labelText: 'First Name')),
      TextFormField(decoration: const InputDecoration(labelText: 'Last Name')),
    ]),
    ResponsiveFormRow(children: [
      TextFormField(decoration: const InputDecoration(labelText: 'Email')),
    ]),
    ResponsiveFormRow(children: [
      TextFormField(decoration: const InputDecoration(labelText: 'City')),
      TextFormField(decoration: const InputDecoration(labelText: 'State')),
      TextFormField(decoration: const InputDecoration(labelText: 'Zip')),
    ]),
  ]),
)
```

## 5. Adaptive Dialog / Bottom Sheet

Show dialog on wide screens, bottom sheet on mobile.

```dart
Future<T?> showAdaptive<T>({
  required BuildContext context,
  required WidgetBuilder builder,
  double breakpoint = 600,
}) {
  final width = MediaQuery.sizeOf(context).width;

  if (width >= breakpoint) {
    return showDialog<T>(
      context: context,
      builder: (ctx) => Dialog(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560, maxHeight: 600),
          child: builder(ctx),
        ),
      ),
    );
  }

  return showModalBottomSheet<T>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    builder: (ctx) => DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (_, controller) => SingleChildScrollView(
        controller: controller,
        child: builder(ctx),
      ),
    ),
  );
}
```

## 6. Responsive Card Grid

Cards that reflow and resize based on available space.

```dart
// Using Wrap for auto-flowing cards
LayoutBuilder(builder: (context, constraints) {
  final itemWidth = constraints.maxWidth < 600 ? constraints.maxWidth : 280.0;

  return SingleChildScrollView(
    padding: const EdgeInsets.all(16),
    child: Wrap(
      spacing: 16,
      runSpacing: 16,
      children: items.map((item) => SizedBox(
        width: itemWidth,
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.title, style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Text(item.description),
              ],
            ),
          ),
        ),
      )).toList(),
    ),
  );
})
```

## 7. Max-Width Content Wrapper

Prevent content from stretching on ultra-wide screens.

```dart
class MaxWidthContent extends StatelessWidget {
  final Widget child;
  final double maxWidth;

  const MaxWidthContent({super.key, required this.child, this.maxWidth = 840});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: maxWidth),
        child: child,
      ),
    );
  }
}

// Usage — wrap any page content
Scaffold(
  body: MaxWidthContent(
    child: ListView(children: [/* content */]),
  ),
)
```

## 8. Responsive Data Table

Full table on wide screens, card list on narrow.

```dart
class ResponsiveDataView<T> extends StatelessWidget {
  final List<T> items;
  final List<String> columns;
  final List<String> Function(T item) rowBuilder;
  final Widget Function(T item) cardBuilder;
  final double breakpoint;

  const ResponsiveDataView({
    super.key,
    required this.items,
    required this.columns,
    required this.rowBuilder,
    required this.cardBuilder,
    this.breakpoint = 600,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      if (constraints.maxWidth >= breakpoint) {
        return SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columns: columns.map((c) => DataColumn(label: Text(c))).toList(),
            rows: items.map((item) => DataRow(
              cells: rowBuilder(item).map((v) => DataCell(Text(v))).toList(),
            )).toList(),
          ),
        );
      }

      return ListView.builder(
        itemCount: items.length,
        itemBuilder: (_, i) => cardBuilder(items[i]),
      );
    });
  }
}
```

## 9. Adaptive App Bar

Compact on mobile, expanded with search on desktop.

```dart
AppBar buildAdaptiveAppBar(BuildContext context, {required String title}) {
  final width = MediaQuery.sizeOf(context).width;
  final isWide = width >= 840;

  return AppBar(
    title: isWide
        ? Row(children: [
            Text(title),
            const SizedBox(width: 24),
            Expanded(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 400),
                child: TextField(
                  decoration: InputDecoration(
                    hintText: 'Search...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                ),
              ),
            ),
            const Spacer(),
          ])
        : Text(title),
    actions: isWide
        ? [
            IconButton(icon: const Icon(Icons.notifications), onPressed: () {}),
            IconButton(icon: const Icon(Icons.account_circle), onPressed: () {}),
          ]
        : [
            IconButton(icon: const Icon(Icons.search), onPressed: () {}),
            IconButton(icon: const Icon(Icons.more_vert), onPressed: () {}),
          ],
  );
}
```
