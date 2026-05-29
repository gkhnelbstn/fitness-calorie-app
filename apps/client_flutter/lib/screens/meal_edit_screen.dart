import 'package:flutter/material.dart';

import '../api.dart';

/// Öğün düzenleme — öğün tipi + kalem listesi (ad/miktar/birim/makro) + ekle/sil.
/// Kaydedince PUT /api/meals/{id} ile kalemler değişir, total yeniden hesaplanır.
class MealEditScreen extends StatefulWidget {
  final ApiClient api;
  final Map meal;
  const MealEditScreen({super.key, required this.api, required this.meal});

  @override
  State<MealEditScreen> createState() => _MealEditScreenState();
}

class _ItemRow {
  final TextEditingController name;
  final TextEditingController qty;
  final TextEditingController unit;
  final TextEditingController kcal;
  final TextEditingController protein;
  final TextEditingController carb;
  final TextEditingController fat;
  _ItemRow(Map it)
      : name = TextEditingController(text: '${it['raw_name'] ?? ''}'),
        qty = TextEditingController(text: it['quantity']?.toString() ?? ''),
        unit = TextEditingController(text: '${it['unit'] ?? ''}'),
        kcal = TextEditingController(text: it['kcal']?.toString() ?? ''),
        protein = TextEditingController(text: it['protein_g']?.toString() ?? ''),
        carb = TextEditingController(text: it['carb_g']?.toString() ?? ''),
        fat = TextEditingController(text: it['fat_g']?.toString() ?? '');

  Map<String, dynamic> toJson() => {
        'raw_name': name.text.trim(),
        'quantity': double.tryParse(qty.text),
        'unit': unit.text.trim().isEmpty ? null : unit.text.trim(),
        'kcal': double.tryParse(kcal.text),
        'protein_g': double.tryParse(protein.text),
        'carb_g': double.tryParse(carb.text),
        'fat_g': double.tryParse(fat.text),
      };
}

class _MealEditScreenState extends State<MealEditScreen> {
  late String? _mealType;
  late List<_ItemRow> _rows;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _mealType = widget.meal['meal_type'] as String?;
    _rows = [for (final it in (widget.meal['items'] as List? ?? [])) _ItemRow(it as Map)];
    if (_rows.isEmpty) _rows.add(_ItemRow({}));
  }

  double get _totalKcal =>
      _rows.fold(0.0, (a, r) => a + (double.tryParse(r.kcal.text) ?? 0));

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final items = _rows.where((r) => r.name.text.trim().isNotEmpty).map((r) => r.toJson()).toList();
      await widget.api.updateMeal(widget.meal['id'] as int, {
        'meal_type': _mealType,
        'items': items,
      });
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Hata: $e')));
      }
    }
  }

  Widget _itemEditor(int i) {
    final r = _rows[i];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(children: [
          Row(children: [
            Expanded(
              child: TextField(controller: r.name, decoration: const InputDecoration(labelText: 'Malzeme')),
            ),
            IconButton(
              icon: const Icon(Icons.delete_outline),
              onPressed: _rows.length > 1 ? () => setState(() => _rows.removeAt(i)) : null,
            ),
          ]),
          Row(children: [
            Expanded(child: TextField(controller: r.qty, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Miktar'))),
            const SizedBox(width: 8),
            Expanded(child: TextField(controller: r.unit, decoration: const InputDecoration(labelText: 'Birim'))),
            const SizedBox(width: 8),
            Expanded(child: TextField(controller: r.kcal, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'kcal'))),
          ]),
          Row(children: [
            Expanded(child: TextField(controller: r.protein, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Protein g'))),
            const SizedBox(width: 8),
            Expanded(child: TextField(controller: r.carb, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Karb. g'))),
            const SizedBox(width: 8),
            Expanded(child: TextField(controller: r.fat, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Yağ g'))),
          ]),
        ]),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Öğünü düzenle'),
        actions: [
          TextButton(
            onPressed: _saving ? null : _save,
            child: Text(_saving ? '...' : 'Kaydet'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          DropdownButtonFormField<String>(
            initialValue: _mealType,
            decoration: const InputDecoration(labelText: 'Öğün tipi'),
            items: const [
              DropdownMenuItem(value: 'kahvalti', child: Text('Kahvaltı')),
              DropdownMenuItem(value: 'ogle', child: Text('Öğle')),
              DropdownMenuItem(value: 'aksam', child: Text('Akşam')),
              DropdownMenuItem(value: 'atistirma', child: Text('Atıştırma')),
            ],
            onChanged: (v) => setState(() => _mealType = v),
          ),
          const SizedBox(height: 8),
          for (var i = 0; i < _rows.length; i++) _itemEditor(i),
          TextButton.icon(
            onPressed: () => setState(() => _rows.add(_ItemRow({}))),
            icon: const Icon(Icons.add),
            label: const Text('Kalem ekle'),
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerRight,
            child: Text('Toplam: ${_totalKcal.toStringAsFixed(0)} kcal',
                style: const TextStyle(fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
  }
}
