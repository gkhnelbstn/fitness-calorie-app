import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../api.dart';

class MealsScreen extends StatefulWidget {
  final ApiClient api;
  const MealsScreen({super.key, required this.api});

  @override
  State<MealsScreen> createState() => _MealsScreenState();
}

class _MealsScreenState extends State<MealsScreen> {
  DateTime _date = DateTime.now();
  Future<List<dynamic>>? _meals;
  String get _isoDate => DateFormat('yyyy-MM-dd').format(_date);

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _meals = widget.api.listMeals(date: _isoDate);
    });
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

  Future<void> _addNaturalLanguage() async {
    final textCtrl = TextEditingController();
    String? mealType;
    final result = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Doğal dilde yemek ekle'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(
            controller: textCtrl,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Ör: 1 kase pilav, 1 ayran',
            ),
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            initialValue: mealType,
            decoration: const InputDecoration(labelText: 'Öğün (opsiyonel)'),
            items: const [
              DropdownMenuItem(value: 'kahvalti', child: Text('Kahvaltı')),
              DropdownMenuItem(value: 'ogle', child: Text('Öğle')),
              DropdownMenuItem(value: 'aksam', child: Text('Akşam')),
              DropdownMenuItem(value: 'atistirma', child: Text('Atıştırma')),
            ],
            onChanged: (v) => mealType = v,
          ),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('İptal')),
          FilledButton(onPressed: () => Navigator.pop(c, true), child: const Text('Ekle')),
        ],
      ),
    );
    if (result == true && textCtrl.text.trim().isNotEmpty) {
      try {
        await widget.api.createMeal(rawText: textCtrl.text.trim(), mealType: mealType);
        _reload();
      } catch (e) {
        _snack('Hata: $e');
      }
    }
  }

  Future<void> _addByBarcode() async {
    final bcCtrl = TextEditingController();
    final gramsCtrl = TextEditingController(text: '100');
    final result = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Barkod ile ekle'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: bcCtrl, decoration: const InputDecoration(labelText: 'Barkod')),
          TextField(
            controller: gramsCtrl,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Miktar (gram)'),
          ),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('İptal')),
          FilledButton(onPressed: () => Navigator.pop(c, true), child: const Text('Ekle')),
        ],
      ),
    );
    if (result == true && bcCtrl.text.trim().isNotEmpty) {
      try {
        await widget.api.createMealByBarcode(
          bcCtrl.text.trim(),
          double.tryParse(gramsCtrl.text) ?? 100,
        );
        _reload();
      } catch (e) {
        _snack('Hata: $e');
      }
    }
  }

  Future<void> _addPhoto() async {
    final picked = await FilePicker.pickFiles(
      type: FileType.image, withData: true,
    );
    if (picked == null || picked.files.isEmpty) return;
    final f = picked.files.first;
    if (f.bytes == null) return;
    final textCtrl = TextEditingController();
    final go = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: Text('Foto: ${f.name}'),
        content: TextField(
          controller: textCtrl,
          maxLines: 2,
          decoration: const InputDecoration(
            labelText: 'İsteğe bağlı: ne yedin? (manuel)',
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('İptal')),
          FilledButton(onPressed: () => Navigator.pop(c, true), child: const Text('Yükle')),
        ],
      ),
    );
    if (go == true) {
      try {
        await widget.api.uploadPhoto(
          f.bytes!, f.name,
          rawText: textCtrl.text.trim().isEmpty ? null : textCtrl.text.trim(),
        );
        _reload();
      } catch (e) {
        _snack('Hata: $e');
      }
    }
  }

  void _snack(String msg) {
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.all(8),
          child: Row(children: [
            Expanded(child: Text('Tarih: $_isoDate')),
            TextButton.icon(onPressed: _pickDate, icon: const Icon(Icons.calendar_today), label: const Text('Değiştir')),
          ]),
        ),
        Expanded(
          child: FutureBuilder<List<dynamic>>(
            future: _meals,
            builder: (c, s) {
              if (s.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
              if (s.hasError) return Center(child: Text('Hata: ${s.error}'));
              final data = s.data ?? [];
              if (data.isEmpty) return const Center(child: Text('Bu gün için kayıt yok.'));
              return RefreshIndicator(
                onRefresh: () async => _reload(),
                child: ListView.separated(
                  itemCount: data.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (c, i) {
                    final m = data[i] as Map;
                    final items = (m['items'] as List? ?? []).map((it) => it['raw_name']).join(', ');
                    return ListTile(
                      leading: const Icon(Icons.restaurant),
                      title: Text(m['raw_text'] ?? items.toString()),
                      subtitle: Text('${m['meal_type'] ?? '-'} • ${m['total_kcal'] ?? '-'} kcal'),
                    );
                  },
                ),
              );
            },
          ),
        ),
      ]),
      floatingActionButton: SpeedDial(
        onText: _addNaturalLanguage,
        onBarcode: _addByBarcode,
        onPhoto: _addPhoto,
      ),
    );
  }
}

class SpeedDial extends StatefulWidget {
  final VoidCallback onText;
  final VoidCallback onBarcode;
  final VoidCallback onPhoto;
  const SpeedDial({super.key, required this.onText, required this.onBarcode, required this.onPhoto});

  @override
  State<SpeedDial> createState() => _SpeedDialState();
}

class _SpeedDialState extends State<SpeedDial> {
  bool _open = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        if (_open) ...[
          FloatingActionButton.small(
            heroTag: 'text', onPressed: () { setState(() => _open = false); widget.onText(); },
            child: const Icon(Icons.text_fields),
          ),
          const SizedBox(height: 8),
          FloatingActionButton.small(
            heroTag: 'bc', onPressed: () { setState(() => _open = false); widget.onBarcode(); },
            child: const Icon(Icons.qr_code_2),
          ),
          const SizedBox(height: 8),
          FloatingActionButton.small(
            heroTag: 'photo', onPressed: () { setState(() => _open = false); widget.onPhoto(); },
            child: const Icon(Icons.photo_camera),
          ),
          const SizedBox(height: 8),
        ],
        FloatingActionButton(
          onPressed: () => setState(() => _open = !_open),
          child: Icon(_open ? Icons.close : Icons.add),
        ),
      ],
    );
  }
}
