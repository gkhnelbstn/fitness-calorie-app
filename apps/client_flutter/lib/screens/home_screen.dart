import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../api.dart';

class HomeScreen extends StatefulWidget {
  final ApiClient api;
  const HomeScreen({super.key, required this.api});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  DateTime _date = DateTime.now();
  Future<Map<String, dynamic>>? _summary;
  Future<Map<String, dynamic>>? _rec;

  String get _isoDate => DateFormat('yyyy-MM-dd').format(_date);

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _summary = widget.api.getSummary(date: _isoDate);
      _rec = widget.api.getRecommendation(date: _isoDate);
    });
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _date,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() => _date = picked);
      _reload();
    }
  }

  Widget _summaryCard(Map<String, dynamic> s) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Günlük özet — ${s['day']}',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Wrap(spacing: 16, runSpacing: 8, children: [
              _kv('Kalori', '${s['intake_kcal']} kcal'),
              _kv('Protein', '${s['protein_g']} g'),
              _kv('Karb.', '${s['carb_g']} g'),
              _kv('Yağ', '${s['fat_g']} g'),
              _kv('Öğün', '${s['meal_count']}'),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _recCard(Map<String, dynamic> r) {
    final e = (r['energy'] as Map?) ?? {};
    final w = (r['workout'] as Map?) ?? {};
    final notes = (r['notes'] as List?) ?? [];
    final meals = (r['meal_suggestions'] as List?) ?? [];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Öneri', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Wrap(spacing: 16, runSpacing: 8, children: [
              _kv('BMR', _num(e['bmr'])),
              _kv('TDEE', _num(e['tdee'])),
              _kv('Hedef', _num(e['target_kcal'])),
              _kv('Kalan', _num(e['remaining_kcal'])),
              _kv('Protein hedef', _num(e['protein_target_g'])),
              _kv('Protein kalan', _num(e['protein_remaining_g'])),
            ]),
            const Divider(),
            Text('Antrenman: ${w['focus'] ?? '-'}  •  ${w['weekly_minutes'] ?? '-'} dk/hafta',
                style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 4),
            for (final d in (w['days'] as List? ?? [])) Text('• $d'),
            const SizedBox(height: 4),
            Text((w['note'] ?? '') as String,
                style: Theme.of(context).textTheme.bodySmall),
            if (notes.isNotEmpty) ...[
              const Divider(),
              for (final n in notes) Text('• $n'),
            ],
            if (meals.isNotEmpty) ...[
              const Divider(),
              const Text('Öğün önerileri:'),
              const SizedBox(height: 4),
              Wrap(spacing: 6, children: [
                for (final m in meals)
                  Chip(label: Text((m['title_tr'] ?? '') as String)),
              ]),
            ],
          ],
        ),
      ),
    );
  }

  static Widget _kv(String k, String v) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(k, style: const TextStyle(fontSize: 11, color: Colors.grey)),
          Text(v, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      );

  static String _num(dynamic v) =>
      v == null ? '-' : (v is num ? v.toStringAsFixed(v % 1 == 0 ? 0 : 1) : v.toString());

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async => _reload(),
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          Row(children: [
            Expanded(child: Text('Tarih: $_isoDate')),
            TextButton.icon(
              onPressed: _pickDate,
              icon: const Icon(Icons.calendar_today),
              label: const Text('Değiştir'),
            ),
          ]),
          FutureBuilder<Map<String, dynamic>>(
            future: _summary,
            builder: (c, s) => s.connectionState != ConnectionState.done
                ? const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()))
                : s.hasError
                    ? _err(s.error)
                    : _summaryCard(s.data!),
          ),
          FutureBuilder<Map<String, dynamic>>(
            future: _rec,
            builder: (c, s) => s.connectionState != ConnectionState.done
                ? const SizedBox.shrink()
                : s.hasError
                    ? _err(s.error)
                    : _recCard(s.data!),
          ),
        ],
      ),
    );
  }

  Widget _err(Object? e) => Card(
        color: Colors.red.shade50,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Text('Hata: $e', style: TextStyle(color: Colors.red.shade900)),
        ),
      );
}
