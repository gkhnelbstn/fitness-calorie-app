import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../api.dart';

class MealPlanScreen extends StatefulWidget {
  final ApiClient api;
  const MealPlanScreen({super.key, required this.api});

  @override
  State<MealPlanScreen> createState() => _MealPlanScreenState();
}

class _MealPlanScreenState extends State<MealPlanScreen> {
  final _ctrl = TextEditingController(text: '# Gün 0\n- Kahvaltı: 2 yumurta, 1 simit\n- Öğle: 1 kase pilav, 1 ayran\n# Gün 1\n- Kahvaltı: omlet\n');
  DateTime _base = DateTime.now();
  List<dynamic>? _preview;
  String? _msg;

  String get _isoDate => DateFormat('yyyy-MM-dd').format(_base);

  Future<void> _doPreview() async {
    try {
      final entries = await widget.api.previewPlan(_ctrl.text);
      setState(() { _preview = entries; _msg = '${entries.length} öğün ayrıştırıldı.'; });
    } catch (e) {
      setState(() => _msg = 'Hata: $e');
    }
  }

  Future<void> _doApply() async {
    try {
      final res = await widget.api.applyPlan(_ctrl.text, baseDate: _isoDate);
      setState(() => _msg = '${res['created_meal_ids'].length} yemek oluşturuldu (${res['base_date']}).');
    } catch (e) {
      setState(() => _msg = 'Hata: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Yemek planı yükle')),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Format: "# Gün N" başlığı + "- öğün: yemek" satırları.'),
            const SizedBox(height: 8),
            Expanded(
              child: TextField(
                controller: _ctrl,
                maxLines: null,
                expands: true,
                decoration: const InputDecoration(border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(height: 8),
            Row(children: [
              Expanded(child: Text('Başlangıç tarihi: $_isoDate')),
              TextButton(
                onPressed: () async {
                  final p = await showDatePicker(
                    context: context, initialDate: _base,
                    firstDate: DateTime(2020), lastDate: DateTime(2100),
                  );
                  if (p != null) setState(() => _base = p);
                },
                child: const Text('Değiştir'),
              ),
            ]),
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: _doPreview, child: const Text('Önizle'))),
              const SizedBox(width: 8),
              Expanded(child: FilledButton(onPressed: _doApply, child: const Text('Uygula'))),
            ]),
            if (_msg != null) Padding(padding: const EdgeInsets.only(top: 8), child: Text(_msg!)),
            if (_preview != null)
              Expanded(
                child: ListView(
                  children: [
                    for (final e in _preview!) ListTile(
                      dense: true,
                      title: Text('Gün ${e['day_offset']} — ${e['meal_type']}'),
                      subtitle: Text(e['raw_text']),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
