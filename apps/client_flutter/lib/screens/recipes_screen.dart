import 'package:flutter/material.dart';

import '../api.dart';
import '../widgets/common.dart';

const _recipesPage = 24;

class RecipesScreen extends StatefulWidget {
  final ApiClient api;
  const RecipesScreen({super.key, required this.api});

  @override
  State<RecipesScreen> createState() => _RecipesScreenState();
}

class _RecipesScreenState extends State<RecipesScreen> {
  final _qCtrl = TextEditingController();
  final _excludeCtrl = TextEditingController();
  final _haveCtrl = TextEditingController();
  String _mode = 'search'; // 'search' | 'cook'
  bool _live = false;

  // search (paginated)
  final List<dynamic> _items = [];
  int _offset = 0;
  bool _hasMore = false;
  bool _loading = false;
  String? _error;

  // cook
  Future<List<dynamic>>? _cookResult;

  List<String> get _exclude => _excludeCtrl.text
      .split(',')
      .map((s) => s.trim())
      .where((s) => s.isNotEmpty)
      .toList();

  Future<void> _runSearch({required bool reset}) async {
    if (reset) {
      _items.clear();
      _offset = 0;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final page = await widget.api.searchRecipes(
        q: _qCtrl.text.trim().isEmpty ? null : _qCtrl.text.trim(),
        exclude: _exclude,
        limit: _recipesPage,
        offset: _offset,
        live: _live && _offset == 0,
      );
      setState(() {
        _items.addAll(page);
        _hasMore = page.length == _recipesPage;
        _offset += page.length;
      });
    } catch (e) {
      setState(() => _error = '$e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _runCook() {
    final have = _haveCtrl.text
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
    setState(() => _cookResult = widget.api.cookWith(have: have, exclude: _exclude));
  }

  void _run() {
    if (_mode == 'search') {
      _runSearch(reset: true);
    } else {
      _runCook();
    }
  }

  Widget _ingredientLine(Map i) {
    final status = i['status'] as String? ?? 'ok';
    final name = i['raw_name'] ?? '';
    final qty = i['quantity'];
    final unit = i['unit'];
    final base = '${qty ?? ''} ${unit ?? ''} $name'.trim().replaceAll(RegExp(r'\s+'), ' ');
    Color? c;
    var suffix = '';
    if (status == 'removed') {
      c = const Color(0xFFD97706);
      suffix = ' (çıkarıldı)';
    } else if (status == 'substituted') {
      c = const Color(0xFF2563EB);
      suffix = ' → ${i['substitute']}';
    }
    return Text('• $base$suffix', style: TextStyle(color: c, fontSize: 13));
  }

  Widget _recipeCard(Map r) {
    final notes = (r['notes'] as List?) ?? [];
    final ingredients = (r['ingredients'] as List?) ?? [];
    final t = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Expanded(
                child: Text(r['title_tr'] ?? '',
                    style: t.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
              ),
              if (r['total_kcal'] != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: t.colorScheme.primary.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text('${(r['total_kcal'] as num).toStringAsFixed(0)} kcal',
                      style: TextStyle(color: t.colorScheme.primary, fontWeight: FontWeight.w700, fontSize: 12)),
                ),
            ]),
            if (r['region'] != null)
              Text('Bölge: ${r['region']}', style: t.textTheme.bodySmall),
            const SizedBox(height: 8),
            const Text('Malzemeler', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
            for (final i in ingredients) _ingredientLine(i as Map),
            if (notes.isNotEmpty) ...[
              const SizedBox(height: 8),
              for (final n in notes)
                Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Icon(Icons.info_outline, size: 14, color: t.colorScheme.primary),
                  const SizedBox(width: 6),
                  Expanded(child: Text('$n', style: t.textTheme.bodySmall)),
                ]),
            ],
            if ((r['steps'] as List? ?? []).isNotEmpty)
              ExpansionTile(
                tilePadding: EdgeInsets.zero,
                title: Text('Hazırlanışı (${(r['steps'] as List).length} adım)',
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                children: [
                  for (final (idx, s) in (r['steps'] as List).indexed)
                    ListTile(
                      dense: true,
                      leading: CircleAvatar(radius: 12, child: Text('${idx + 1}', style: const TextStyle(fontSize: 11))),
                      title: Text('$s'),
                    ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _searchBody() {
    if (_items.isEmpty && _loading) return const LoadingView();
    if (_error != null) {
      return ListView(padding: const EdgeInsets.all(12), children: [ErrorBanner(_error)]);
    }
    if (_items.isEmpty) {
      return const EmptyState(icon: Icons.menu_book_outlined, message: 'Arama yap veya "Çalıştır" bas.');
    }
    return ListView(
      padding: const EdgeInsets.fromLTRB(8, 0, 8, 24),
      children: [
        for (final r in _items) _recipeCard(r as Map),
        if (_hasMore)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: OutlinedButton.icon(
              onPressed: _loading ? null : () => _runSearch(reset: false),
              icon: const Icon(Icons.expand_more),
              label: Text(_loading ? 'Yükleniyor…' : 'Daha fazla tarif'),
            ),
          ),
      ],
    );
  }

  Widget _cookBody() {
    return FutureBuilder<List<dynamic>>(
      future: _cookResult,
      builder: (c, s) {
        if (_cookResult == null) {
          return const EmptyState(icon: Icons.kitchen_outlined, message: 'Malzemeleri yaz, "Çalıştır" bas.');
        }
        if (s.connectionState != ConnectionState.done) return const LoadingView();
        if (s.hasError) {
          return ListView(padding: const EdgeInsets.all(12), children: [ErrorBanner(s.error)]);
        }
        final data = s.data ?? [];
        if (data.isEmpty) return const EmptyState(icon: Icons.search_off, message: 'Sonuç yok.');
        return ListView(
          padding: const EdgeInsets.fromLTRB(8, 0, 8, 24),
          children: [for (final r in data) _recipeCard(r as Map)],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Padding(
        padding: const EdgeInsets.all(8),
        child: Column(children: [
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'search', label: Text('Arama'), icon: Icon(Icons.search)),
              ButtonSegment(value: 'cook', label: Text('Şununla pişer'), icon: Icon(Icons.kitchen)),
            ],
            selected: {_mode},
            onSelectionChanged: (s) => setState(() => _mode = s.first),
          ),
          const SizedBox(height: 8),
          if (_mode == 'search') ...[
            TextField(
              controller: _qCtrl,
              decoration: const InputDecoration(labelText: 'Tarif ara (ör. tavuk, köfte, salata)'),
              onSubmitted: (_) => _runSearch(reset: true),
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              dense: true,
              value: _live,
              onChanged: (v) => setState(() => _live = v),
              title: const Text("Web'de ara (TheMealDB)", style: TextStyle(fontSize: 13)),
              subtitle: const Text('Sonuçlar Türkçeye çevrilip kaydedilir', style: TextStyle(fontSize: 11)),
            ),
          ] else
            TextField(
              controller: _haveCtrl,
              decoration: const InputDecoration(
                labelText: 'Elimde olanlar (virgülle)',
                hintText: 'yumurta, tuz',
              ),
            ),
          TextField(
            controller: _excludeCtrl,
            decoration: const InputDecoration(
              labelText: 'İstenmeyen malzemeler (virgülle)',
              hintText: 'sarımsak, soğan',
            ),
          ),
          const SizedBox(height: 8),
          FilledButton.icon(onPressed: _run, icon: const Icon(Icons.search), label: const Text('Çalıştır')),
        ]),
      ),
      Expanded(child: _mode == 'search' ? _searchBody() : _cookBody()),
    ]);
  }
}
