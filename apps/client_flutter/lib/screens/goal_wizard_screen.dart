import 'package:flutter/material.dart';

import '../api.dart';
import '../widgets/common.dart';

/// Hedef sihirbazı — TDEE + hedef kilo + hız → günlük kalori hedefi + süre,
/// /api/goal'a kaydet. (Plan kalıcılığı backend'de yok; özet client'ta hesaplanır.)
class GoalWizardScreen extends StatefulWidget {
  final ApiClient api;
  const GoalWizardScreen({super.key, required this.api});

  @override
  State<GoalWizardScreen> createState() => _GoalWizardScreenState();
}

class _GoalWizardScreenState extends State<GoalWizardScreen> {
  bool _loading = true;
  String? _error;
  double? _tdee;
  double? _weight;

  String _goal = 'kilo_ver';
  final _targetWeight = TextEditingController();
  double _pace = 0.5; // kg/hafta
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final rec = await widget.api.getRecommendation();
      final prof = await widget.api.getProfile();
      _tdee = (rec['energy']?['tdee'] as num?)?.toDouble();
      _weight = (prof['weight_kg'] as num?)?.toDouble();
    } catch (e) {
      _error = '$e';
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  // Günlük kalori deltası: pace kg/hafta × 7700 kcal/kg ÷ 7 gün
  double get _dailyDelta => _pace * 7700 / 7;

  int? get _targetKcal {
    if (_tdee == null) return null;
    if (_goal == 'koru') return _tdee!.round();
    return (_goal == 'kilo_ver' ? _tdee! - _dailyDelta : _tdee! + _dailyDelta).round();
  }

  int? get _weeks {
    final tw = double.tryParse(_targetWeight.text);
    if (_goal == 'koru' || _weight == null || tw == null || _pace <= 0) return null;
    return (( (_weight! - tw).abs() ) / _pace).ceil();
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      await widget.api.setGoal({'goal_type': _goal, if (_targetKcal != null) 'target_kcal': _targetKcal});
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Hata: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Hedef sihirbazı')),
      body: _loading
          ? const LoadingView()
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (_error != null) ErrorBanner(_error),
                if (_tdee == null)
                  const SectionCard(title: 'Profil eksik', icon: Icons.info_outline, children: [
                    Text('Önce Profil sekmesinden cinsiyet/kilo/boy/doğum yılı doldur; '
                        'TDEE hesaplanınca sihirbaz öneri verir.'),
                  ]),
                SectionCard(
                  title: 'Hedefin',
                  icon: Icons.flag_outlined,
                  children: [
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(value: 'kilo_ver', label: Text('Kilo ver')),
                        ButtonSegment(value: 'koru', label: Text('Koru')),
                        ButtonSegment(value: 'kas_yap', label: Text('Kas yap')),
                      ],
                      selected: {_goal},
                      onSelectionChanged: (s) => setState(() => _goal = s.first),
                    ),
                    if (_goal != 'koru') ...[
                      const SizedBox(height: 12),
                      TextField(
                        controller: _targetWeight,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(labelText: 'Hedef kilo (kg)'),
                        onChanged: (_) => setState(() {}),
                      ),
                      const SizedBox(height: 12),
                      Text('Haftalık hız: ${_pace.toStringAsFixed(2)} kg'),
                      Slider(
                        value: _pace,
                        min: 0.25,
                        max: 1.0,
                        divisions: 3,
                        label: '${_pace.toStringAsFixed(2)} kg/hafta',
                        onChanged: (v) => setState(() => _pace = v),
                      ),
                    ],
                  ],
                ),
                if (_tdee != null)
                  SectionCard(
                    title: 'Plan özeti',
                    icon: Icons.insights_outlined,
                    children: [
                      Wrap(spacing: 8, runSpacing: 8, children: [
                        StatChip(label: 'TDEE', value: _tdee!.toStringAsFixed(0)),
                        if (_targetKcal != null)
                          StatChip(label: 'Günlük hedef', value: '$_targetKcal kcal'),
                        if (_goal != 'koru')
                          StatChip(label: 'Günlük delta', value: '${_dailyDelta.toStringAsFixed(0)} kcal'),
                        if (_weeks != null) StatChip(label: 'Süre', value: '$_weeks hafta'),
                      ]),
                      const SizedBox(height: 8),
                      Text('Değerler yaklaşıktır; tıbbi tavsiye değildir.',
                          style: Theme.of(context).textTheme.bodySmall),
                    ],
                  ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: _saving ? null : _save,
                  icon: const Icon(Icons.save),
                  label: Text(_saving ? '...' : 'Hedefi kaydet'),
                ),
              ],
            ),
    );
  }
}
