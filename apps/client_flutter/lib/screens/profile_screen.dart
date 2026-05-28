import 'package:flutter/material.dart';

import '../api.dart';

class ProfileScreen extends StatefulWidget {
  final ApiClient api;
  const ProfileScreen({super.key, required this.api});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _name = TextEditingController();
  final _sex = TextEditingController();
  final _birth = TextEditingController();
  final _height = TextEditingController();
  final _weight = TextEditingController();
  String _activity = 'moderate';
  String _goalType = 'koru';
  final _targetKcal = TextEditingController();
  final _targetProtein = TextEditingController();
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final p = await widget.api.getProfile();
      _name.text = p['name'] ?? '';
      _sex.text = p['sex'] ?? '';
      _birth.text = p['birth_year']?.toString() ?? '';
      _height.text = p['height_cm']?.toString() ?? '';
      _weight.text = p['weight_kg']?.toString() ?? '';
      _activity = p['activity_level'] ?? 'moderate';
      final g = await widget.api.getGoal();
      if (g != null) {
        _goalType = g['goal_type'] ?? 'koru';
        _targetKcal.text = g['target_kcal']?.toString() ?? '';
        _targetProtein.text = g['target_protein_g']?.toString() ?? '';
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Yükleme hatası: $e')));
    } finally {
      if (mounted) setState(() => _loaded = true);
    }
  }

  Future<void> _save() async {
    try {
      await widget.api.putProfile({
        if (_name.text.isNotEmpty) 'name': _name.text.trim(),
        if (_sex.text.isNotEmpty) 'sex': _sex.text.trim(),
        if (_birth.text.isNotEmpty) 'birth_year': int.tryParse(_birth.text),
        if (_height.text.isNotEmpty) 'height_cm': double.tryParse(_height.text),
        if (_weight.text.isNotEmpty) 'weight_kg': double.tryParse(_weight.text),
        'activity_level': _activity,
      });
      await widget.api.setGoal({
        'goal_type': _goalType,
        if (_targetKcal.text.isNotEmpty) 'target_kcal': int.tryParse(_targetKcal.text),
        if (_targetProtein.text.isNotEmpty) 'target_protein_g': double.tryParse(_targetProtein.text),
      });
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Kaydedildi.')));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Hata: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_loaded) return const Center(child: CircularProgressIndicator());
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Profil', style: Theme.of(context).textTheme.titleMedium),
        TextField(controller: _name, decoration: const InputDecoration(labelText: 'İsim')),
        TextField(controller: _sex, decoration: const InputDecoration(labelText: 'Cinsiyet (erkek/kadın)')),
        TextField(controller: _birth, decoration: const InputDecoration(labelText: 'Doğum yılı'), keyboardType: TextInputType.number),
        TextField(controller: _height, decoration: const InputDecoration(labelText: 'Boy (cm)'), keyboardType: TextInputType.number),
        TextField(controller: _weight, decoration: const InputDecoration(labelText: 'Kilo (kg)'), keyboardType: TextInputType.number),
        DropdownButtonFormField<String>(
          initialValue: _activity,
          decoration: const InputDecoration(labelText: 'Aktivite seviyesi'),
          items: const [
            DropdownMenuItem(value: 'sedentary', child: Text('Hareketsiz')),
            DropdownMenuItem(value: 'light', child: Text('Hafif')),
            DropdownMenuItem(value: 'moderate', child: Text('Orta')),
            DropdownMenuItem(value: 'active', child: Text('Aktif')),
            DropdownMenuItem(value: 'very_active', child: Text('Çok aktif')),
          ],
          onChanged: (v) => setState(() => _activity = v ?? 'moderate'),
        ),
        const SizedBox(height: 16),
        Text('Hedef', style: Theme.of(context).textTheme.titleMedium),
        DropdownButtonFormField<String>(
          initialValue: _goalType,
          decoration: const InputDecoration(labelText: 'Hedef türü'),
          items: const [
            DropdownMenuItem(value: 'kilo_ver', child: Text('Kilo ver')),
            DropdownMenuItem(value: 'koru', child: Text('Koru')),
            DropdownMenuItem(value: 'kas_yap', child: Text('Kas yap')),
          ],
          onChanged: (v) => setState(() => _goalType = v ?? 'koru'),
        ),
        TextField(controller: _targetKcal, decoration: const InputDecoration(labelText: 'Hedef kcal (opsiyonel — boşsa otomatik)'), keyboardType: TextInputType.number),
        TextField(controller: _targetProtein, decoration: const InputDecoration(labelText: 'Hedef protein g (opsiyonel — boşsa 1.6 g/kg)'), keyboardType: TextInputType.number),
        const SizedBox(height: 24),
        FilledButton.icon(onPressed: _save, icon: const Icon(Icons.save), label: const Text('Kaydet')),
      ],
    );
  }
}
