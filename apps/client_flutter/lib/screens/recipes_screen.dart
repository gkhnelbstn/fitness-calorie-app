import 'package:flutter/material.dart';

import '../api.dart';
import '../widgets/common.dart';

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
  Future<List<dynamic>>? _result;
  String _mode = 'search'; // 'search' | 'cook'

  void _run() {
    final exclude = _excludeCtrl.text
        .split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
    setState(() {
      if (_mode == 'search') {
        _result = widget.api.searchRecipes(
          q: _qCtrl.text.trim().isEmpty ? null : _qCtrl.text.trim(),
          exclude: exclude,
        );
      } else {
        final have = _haveCtrl.text
            .split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
        _result = widget.api.cookWith(have: have, exclude: exclude);
      }
    });
  }

  Widget _recipeCard(Map r) {
    final notes = (r['notes'] as List?) ?? [];
    final ingredients = (r['ingredients'] as List?) ?? [];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Expanded(child: Text(r['title_tr'] ?? '', style: Theme.of(context).textTheme.titleMedium)),
              if (r['total_kcal'] != null) Text('${r['total_kcal']} kcal'),
            ]),
            if (r['region'] != null) Text('Bölge: ${r['region']}', style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 8),
            const Text('Malzemeler:'),
            for (final i in ingredients)
              _ingredientLine(i as Map),
            if (notes.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text('Notlar:', style: TextStyle(fontWeight: FontWeight.w600)),
              for (final n in notes) Text('• $n'),
            ],
            if ((r['steps'] as List? ?? []).isNotEmpty) ExpansionTile(
              title: const Text('Adımlar'),
              children: [
                for (final s in r['steps'])
                  ListTile(dense: true, title: Text('• $s')),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _ingredientLine(Map i) {
    final status = i['status'] as String? ?? 'ok';
    final qty = i['quantity'];
    final unit = i['unit'];
    final name = i['raw_name'] ?? '';
    final base = '${qty ?? ''} ${unit ?? ''} $name'.trim().replaceAll(RegExp(r'\s+'), ' ');
    Color? c;
    String suffix = '';
    if (status == 'removed') { c = Colors.orange; suffix = ' (çıkarıldı)'; }
    else if (status == 'substituted') { c = Colors.blue; suffix = ' → ${i['substitute']}'; }
    return Text('• $base$suffix', style: TextStyle(color: c));
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
          if (_mode == 'search')
            TextField(controller: _qCtrl, decoration: const InputDecoration(labelText: 'Arama (başlık)'))
          else
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
      Expanded(
        child: FutureBuilder<List<dynamic>>(
          future: _result,
          builder: (c, s) {
            if (_result == null) {
              return const EmptyState(icon: Icons.menu_book_outlined, message: 'Arama yap veya "Çalıştır" bas.');
            }
            if (s.connectionState != ConnectionState.done) return const LoadingView();
            if (s.hasError) {
              return ListView(padding: const EdgeInsets.all(12), children: [ErrorBanner(s.error)]);
            }
            final data = s.data ?? [];
            if (data.isEmpty) {
              return const EmptyState(icon: Icons.search_off, message: 'Sonuç yok.');
            }
            return ListView(
              padding: const EdgeInsets.fromLTRB(8, 0, 8, 24),
              children: [for (final r in data) _recipeCard(r as Map)],
            );
          },
        ),
      ),
    ]);
  }
}
