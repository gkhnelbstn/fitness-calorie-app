import 'package:flutter/material.dart';

import '../config.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlCtrl = TextEditingController();
  final _tokenCtrl = TextEditingController();
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    ConfigStore.load().then((c) {
      _urlCtrl.text = c.baseUrl;
      _tokenCtrl.text = c.token;
      setState(() => _loaded = true);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ayarlar')),
      body: !_loaded
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextField(
                    controller: _urlCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Backend URL',
                      helperText: 'Örn: http://localhost:8000',
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _tokenCtrl,
                    decoration: const InputDecoration(
                      labelText: 'API Token',
                      helperText: 'services/api/.env içindeki API_TOKEN',
                    ),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: () async {
                      await ConfigStore.save(BackendConfig(
                        baseUrl: _urlCtrl.text.trim().replaceAll(RegExp(r'/+$'), ''),
                        token: _tokenCtrl.text.trim(),
                      ));
                      if (mounted) Navigator.pop(context);
                    },
                    child: const Text('Kaydet'),
                  ),
                ],
              ),
            ),
    );
  }
}
