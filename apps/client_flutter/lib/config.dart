import 'package:shared_preferences/shared_preferences.dart';

class BackendConfig {
  String baseUrl;
  String token;
  BackendConfig({required this.baseUrl, required this.token});

  static const defaultBaseUrl = 'http://localhost:8000';
  static const defaultToken = 'dev-local-token';
}

class ConfigStore {
  static const _kBase = 'base_url';
  static const _kToken = 'api_token';

  static Future<BackendConfig> load() async {
    final p = await SharedPreferences.getInstance();
    return BackendConfig(
      baseUrl: p.getString(_kBase) ?? BackendConfig.defaultBaseUrl,
      token: p.getString(_kToken) ?? BackendConfig.defaultToken,
    );
  }

  static Future<void> save(BackendConfig c) async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_kBase, c.baseUrl);
    await p.setString(_kToken, c.token);
  }
}
