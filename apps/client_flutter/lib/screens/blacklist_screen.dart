import 'package:flutter/material.dart';

import '../api.dart';
import '../widgets/common.dart';

class BlacklistScreen extends StatefulWidget {
  final ApiClient api;
  const BlacklistScreen({super.key, required this.api});

  @override
  State<BlacklistScreen> createState() => _BlacklistScreenState();
}

class _BlacklistScreenState extends State<BlacklistScreen> {
  Future<List<dynamic>>? _items;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _items = widget.api.listBlacklist();
    });
  }

  Future<void> _add() async {
    final ctrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Kara listeye ekle'),
        content: TextField(
          controller: ctrl,
          decoration: const InputDecoration(labelText: 'Malzeme adı (ör: sarımsak)'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('İptal')),
          FilledButton(onPressed: () => Navigator.pop(c, true), child: const Text('Ekle')),
        ],
      ),
    );
    if (ok == true && ctrl.text.trim().isNotEmpty) {
      try {
        await widget.api.addBlacklist(ctrl.text.trim());
        _reload();
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Hata: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder<List<dynamic>>(
        future: _items,
        builder: (c, s) {
          if (s.connectionState != ConnectionState.done) return const LoadingView();
          if (s.hasError) {
            return ListView(padding: const EdgeInsets.all(12), children: [ErrorBanner(s.error)]);
          }
          final data = s.data ?? [];
          if (data.isEmpty) {
            return const EmptyState(icon: Icons.block, message: 'Kara liste boş.\n+ ile malzeme ekle.');
          }
          return RefreshIndicator(
            onRefresh: () async => _reload(),
            child: ListView.separated(
              itemCount: data.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (c, i) {
                final it = data[i] as Map;
                return ListTile(
                  leading: const Icon(Icons.block, color: Colors.red),
                  title: Text(it['name_tr'] ?? ''),
                  subtitle: Text(it['slug'] ?? ''),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline),
                    onPressed: () async {
                      try {
                        await widget.api.removeBlacklist(it['canonical_id'] as int);
                        _reload();
                      } catch (e) {
                        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Hata: $e')));
                      }
                    },
                  ),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(onPressed: _add, child: const Icon(Icons.add)),
    );
  }
}
