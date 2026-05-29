import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../api.dart';
import '../widgets/common.dart';

/// Antrenman ekranı — günlük plan + bugünün logları (ekle/sil) + katalog.
class WorkoutScreen extends StatefulWidget {
  final ApiClient api;
  const WorkoutScreen({super.key, required this.api});

  @override
  State<WorkoutScreen> createState() => _WorkoutScreenState();
}

class _WorkoutScreenState extends State<WorkoutScreen> {
  DateTime _date = DateTime.now();
  Future<List<dynamic>>? _data; // [plan, logs]
  String get _isoDate => DateFormat('yyyy-MM-dd').format(_date);

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _data = Future.wait([
        widget.api.workoutPlan(),
        widget.api.listWorkoutLogs(date: _isoDate),
      ]);
    });
  }

  Future<void> _logExercise(Map<String, dynamic> ex) async {
    try {
      await widget.api.addWorkoutLog(
        ex['slug'] as String,
        sets: ex['sets'] is int ? ex['sets'] as int : null,
        reps: ex['reps']?.toString(),
        minutes: 30,
        date: _isoDate,
      );
      _reload();
      _snack('${ex['name_tr']} eklendi');
    } catch (e) {
      _snack('Hata: $e');
    }
  }

  Future<void> _deleteLog(int id) async {
    try {
      await widget.api.deleteWorkoutLog(id);
      _reload();
    } catch (e) {
      _snack('Hata: $e');
    }
  }

  void _snack(String m) {
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(m)));
  }

  Widget _logsCard(List<dynamic> logs) {
    final total = logs.fold<int>(0, (a, l) => a + ((l['kcal'] as int?) ?? 0));
    return SectionCard(
      title: 'Bugünkü antrenman',
      icon: Icons.local_fire_department_outlined,
      trailing: total > 0 ? StatChip(label: 'Yakılan', value: '$total kcal') : null,
      children: [
        if (logs.isEmpty)
          Text('Henüz kayıt yok. Plandan egzersiz ekle.',
              style: Theme.of(context).textTheme.bodySmall)
        else
          for (final l in logs)
            ListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.fitness_center, size: 20),
              title: Text(l['name_tr'] ?? l['template_slug'] ?? ''),
              subtitle: Text([
                if (l['sets'] != null) '${l['sets']} set',
                if (l['reps'] != null) '${l['reps']} tekrar',
                '${l['minutes']} dk',
                if (l['kcal'] != null) '${l['kcal']} kcal',
              ].join(' • ')),
              trailing: IconButton(
                icon: const Icon(Icons.delete_outline),
                onPressed: () => _deleteLog(l['id'] as int),
              ),
            ),
      ],
    );
  }

  Widget _planDay(Map day) {
    final exercises = (day['exercises'] as List?) ?? [];
    return Card(
      child: ExpansionTile(
        shape: const Border(),
        title: Text('${day['day']} — ${day['title']}',
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text('${day['kind']} • ${day['minutes']} dk'),
        childrenPadding: const EdgeInsets.only(bottom: 8),
        children: [
          for (final e in exercises)
            ListTile(
              dense: true,
              leading: Icon(
                e['category'] == 'kardiyo' ? Icons.directions_run : Icons.fitness_center,
                size: 20,
              ),
              title: Text(e['name_tr'] ?? ''),
              subtitle: Text([
                if (e['sets'] != null) '${e['sets']} set',
                if (e['reps'] != null) '${e['reps']}',
                if (e['equipment'] != null) e['equipment'],
              ].join(' • ')),
              trailing: IconButton(
                icon: const Icon(Icons.add_circle_outline),
                tooltip: 'Bugüne ekle',
                onPressed: () => _logExercise(Map<String, dynamic>.from(e)),
              ),
            ),
        ],
      ),
    );
  }

  Widget _planCard(Map<String, dynamic> plan) {
    final days = (plan['days'] as List?) ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SectionCard(
          title: 'Haftalık plan',
          icon: Icons.calendar_month_outlined,
          children: [
            Wrap(spacing: 8, runSpacing: 8, children: [
              StatChip(label: 'Odak', value: '${plan['focus'] ?? '-'}'),
              StatChip(label: 'Haftalık', value: '${plan['weekly_minutes'] ?? '-'} dk'),
              StatChip(label: 'Gün', value: '${plan['days_per_week'] ?? '-'}'),
            ]),
            if ((plan['warmup'] ?? '').toString().isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text('${plan['warmup']}',
                    style: Theme.of(context).textTheme.bodySmall),
              ),
            if ((plan['note'] ?? '').toString().isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text('${plan['note']}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontStyle: FontStyle.italic)),
              ),
          ],
        ),
        for (final d in days) _planDay(d as Map),
      ],
    );
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context, initialDate: _date,
      firstDate: DateTime(2020), lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() => _date = picked);
      _reload();
    }
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
          FutureBuilder<List<dynamic>>(
            future: _data,
            builder: (c, s) {
              if (s.connectionState != ConnectionState.done) return const LoadingView();
              if (s.hasError) return ErrorBanner(s.error);
              final plan = s.data![0] as Map<String, dynamic>;
              final logs = s.data![1] as List<dynamic>;
              return Column(children: [_logsCard(logs), _planCard(plan)]);
            },
          ),
        ],
      ),
    );
  }
}
