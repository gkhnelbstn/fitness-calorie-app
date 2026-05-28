import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../api.dart';
import '../widgets/common.dart';

class HomeScreen extends StatefulWidget {
  final ApiClient api;
  const HomeScreen({super.key, required this.api});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  DateTime _date = DateTime.now();
  Future<List<Map<String, dynamic>>>? _data;

  String get _isoDate => DateFormat('yyyy-MM-dd').format(_date);

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _data = Future.wait([
        widget.api.getSummary(date: _isoDate),
        widget.api.getRecommendation(date: _isoDate),
      ]);
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

  static double _d(dynamic v) => v == null ? 0 : (v as num).toDouble();
  static String _n(dynamic v) =>
      v == null ? '-' : (v is num ? v.toStringAsFixed(v % 1 == 0 ? 0 : 1) : '$v');

  Widget _summaryCard(Map<String, dynamic> s, Map<String, dynamic> rec) {
    final energy = (rec['energy'] as Map?) ?? {};
    final target = energy['target_kcal'];
    final proteinTarget = energy['protein_target_g'];
    return SectionCard(
      title: 'Günlük denge',
      icon: Icons.local_fire_department_outlined,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            KcalRing(
              intake: _d(s['intake_kcal']),
              target: target == null ? null : _d(target),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                children: [
                  MacroBar(
                    label: 'Protein',
                    value: _d(s['protein_g']),
                    target: proteinTarget == null ? null : _d(proteinTarget),
                    color: const Color(0xFF2563EB),
                  ),
                  MacroBar(label: 'Karbonhidrat', value: _d(s['carb_g']), color: const Color(0xFFD97706)),
                  MacroBar(label: 'Yağ', value: _d(s['fat_g']), color: const Color(0xFFDB2777)),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text('${s['meal_count']} öğün • ${s['item_count']} kalem',
            style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }

  Widget _recCard(Map<String, dynamic> r) {
    final e = (r['energy'] as Map?) ?? {};
    final w = (r['workout'] as Map?) ?? {};
    final notes = (r['notes'] as List?) ?? [];
    final meals = (r['meal_suggestions'] as List?) ?? [];
    return SectionCard(
      title: 'Öneri',
      icon: Icons.tips_and_updates_outlined,
      children: [
        Wrap(spacing: 8, runSpacing: 8, children: [
          StatChip(label: 'BMR', value: _n(e['bmr'])),
          StatChip(label: 'TDEE', value: _n(e['tdee'])),
          StatChip(label: 'Hedef', value: _n(e['target_kcal'])),
          StatChip(
            label: 'Kalan',
            value: _n(e['remaining_kcal']),
            color: (e['remaining_kcal'] is num && e['remaining_kcal'] < 0)
                ? Theme.of(context).colorScheme.error
                : null,
          ),
          StatChip(label: 'Protein açığı', value: _n(e['protein_remaining_g'])),
        ]),
        const SizedBox(height: 12),
        Row(children: [
          Icon(Icons.fitness_center, size: 18, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 6),
          Expanded(
            child: Text('${w['focus'] ?? '-'} • ${w['weekly_minutes'] ?? '-'} dk/hafta',
                style: const TextStyle(fontWeight: FontWeight.w600)),
          ),
        ]),
        for (final d in (w['days'] as List? ?? []))
          Padding(
            padding: const EdgeInsets.only(left: 24, top: 2),
            child: Text('• $d', style: Theme.of(context).textTheme.bodySmall),
          ),
        if ((w['note'] ?? '').toString().isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text('${w['note']}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(fontStyle: FontStyle.italic)),
          ),
        if (meals.isNotEmpty) ...[
          const SizedBox(height: 12),
          Text('Öğün önerileri', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 6),
          Wrap(spacing: 6, runSpacing: 6, children: [
            for (final m in meals)
              Chip(
                avatar: const Icon(Icons.restaurant, size: 16),
                label: Text('${m['title_tr'] ?? ''}'),
              ),
          ]),
        ],
        if (notes.isNotEmpty) ...[
          const Divider(height: 20),
          for (final n in notes)
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('• '),
              Expanded(child: Text('$n', style: Theme.of(context).textTheme.bodyMedium)),
            ]),
        ],
        const SizedBox(height: 8),
        Text('Değerler yaklaşıktır; tıbbi tavsiye değildir.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async => _reload(),
      child: ListView(
        padding: const EdgeInsets.fromLTRB(12, 12, 12, 24),
        children: [
          Row(children: [
            Expanded(
              child: Text(DateFormat('d MMMM yyyy', 'tr').format(_date),
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
            ),
            IconButton.filledTonal(onPressed: _pickDate, icon: const Icon(Icons.calendar_month)),
          ]),
          const SizedBox(height: 4),
          FutureBuilder<List<Map<String, dynamic>>>(
            future: _data,
            builder: (c, s) {
              if (s.connectionState != ConnectionState.done) return const LoadingView();
              if (s.hasError) return ErrorBanner(s.error);
              final summary = s.data![0];
              final rec = s.data![1];
              return Column(children: [_summaryCard(summary, rec), _recCard(rec)]);
            },
          ),
        ],
      ),
    );
  }
}
