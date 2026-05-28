import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import 'config.dart';

class ApiException implements Exception {
  final int status;
  final String body;
  ApiException(this.status, this.body);
  @override
  String toString() => 'ApiException($status): $body';
}

class ApiClient {
  BackendConfig cfg;
  ApiClient(this.cfg);

  Map<String, String> get _headers => {
        'Authorization': 'Bearer ${cfg.token}',
        'Content-Type': 'application/json',
      };

  Uri _u(String path, [Map<String, dynamic>? q]) {
    final base = Uri.parse('${cfg.baseUrl}$path');
    if (q == null || q.isEmpty) return base;
    final params = <String, List<String>>{};
    q.forEach((k, v) {
      if (v == null) return;
      if (v is Iterable) {
        params[k] = v.map((e) => e.toString()).toList();
      } else {
        params[k] = [v.toString()];
      }
    });
    return base.replace(queryParameters: params);
  }

  dynamic _decode(http.Response r) {
    if (r.statusCode >= 200 && r.statusCode < 300) {
      if (r.body.isEmpty) return null;
      return jsonDecode(utf8.decode(r.bodyBytes));
    }
    throw ApiException(r.statusCode, utf8.decode(r.bodyBytes));
  }

  Future<dynamic> _get(String path, [Map<String, dynamic>? q]) async =>
      _decode(await http.get(_u(path, q), headers: _headers));

  Future<dynamic> _post(String path, Object body) async =>
      _decode(await http.post(_u(path), headers: _headers, body: jsonEncode(body)));

  Future<dynamic> _put(String path, Object body) async =>
      _decode(await http.put(_u(path), headers: _headers, body: jsonEncode(body)));

  Future<dynamic> _delete(String path) async =>
      _decode(await http.delete(_u(path), headers: _headers));

  // --- Health ---
  Future<Map<String, dynamic>> health() async => Map.from(await _get('/health'));

  // --- Profile / Goal ---
  Future<Map<String, dynamic>> getProfile() async => Map.from(await _get('/api/profile'));
  Future<Map<String, dynamic>> putProfile(Map<String, dynamic> body) async =>
      Map.from(await _put('/api/profile', body));
  Future<Map<String, dynamic>?> getGoal() async {
    try {
      return Map.from(await _get('/api/goal'));
    } on ApiException catch (e) {
      if (e.status == 404) return null;
      rethrow;
    }
  }
  Future<Map<String, dynamic>> setGoal(Map<String, dynamic> body) async =>
      Map.from(await _put('/api/goal', body));

  // --- Meals ---
  Future<List<dynamic>> listMeals({String? date}) async {
    final res = await _get('/api/meals', {'date': date});
    return List.from(res);
  }
  Future<Map<String, dynamic>> createMeal({
    String? rawText,
    String? mealType,
    List<Map<String, dynamic>> items = const [],
  }) async {
    final body = <String, dynamic>{'items': items};
    if (rawText != null) body['raw_text'] = rawText;
    if (mealType != null) body['meal_type'] = mealType;
    return Map.from(await _post('/api/meals', body));
  }
  Future<Map<String, dynamic>> createMealByBarcode(
    String barcode, double grams, {String? mealType}) async {
    final body = <String, dynamic>{'barcode': barcode, 'grams': grams};
    if (mealType != null) body['meal_type'] = mealType;
    return Map.from(await _post('/api/meals/by-barcode', body));
  }
  Future<Map<String, dynamic>> uploadPhoto(
    Uint8List bytes,
    String filename, {
    String? rawText,
    String? mealType,
  }) async {
    final req = http.MultipartRequest('POST', _u('/api/meals/photo'));
    req.headers['Authorization'] = 'Bearer ${cfg.token}';
    req.files.add(http.MultipartFile.fromBytes('photo', bytes, filename: filename));
    if (rawText != null) req.fields['raw_text'] = rawText;
    if (mealType != null) req.fields['meal_type'] = mealType;
    final streamed = await req.send();
    return Map.from(_decode(await http.Response.fromStream(streamed)));
  }

  // --- Summary ---
  Future<Map<String, dynamic>> getSummary({String? date}) async =>
      Map.from(await _get('/api/summary', {'date': date}));

  // --- Recipes ---
  Future<List<dynamic>> searchRecipes({String? q, List<String> exclude = const []}) async {
    final res = await _get('/api/recipes', {'q': q, 'exclude': exclude});
    return List.from(res);
  }
  Future<List<dynamic>> cookWith({List<String> have = const [], List<String> exclude = const []}) async {
    final res = await _get('/api/recipes/cook-with', {'have': have, 'exclude': exclude});
    return List.from(res);
  }

  // --- Blacklist ---
  Future<List<dynamic>> listBlacklist() async => List.from(await _get('/api/blacklist'));
  Future<Map<String, dynamic>> addBlacklist(String name) async =>
      Map.from(await _post('/api/blacklist', {'name': name}));
  Future<void> removeBlacklist(int canonicalId) async =>
      _delete('/api/blacklist/$canonicalId');

  // --- Recommendations ---
  Future<Map<String, dynamic>> getRecommendation({String? date}) async =>
      Map.from(await _get('/api/recommendations', {'date': date}));
  Future<void> sendFeedback(int recId, String action, {String? note}) async {
    final body = <String, dynamic>{'recommendation_id': recId, 'action': action};
    if (note != null) body['note'] = note;
    await _post('/api/recommendations/feedback', body);
  }

  // --- Meal plans ---
  Future<List<dynamic>> previewPlan(String text) async {
    final res = await _post('/api/meal-plans/preview', {'text': text});
    return List.from(res['entries']);
  }
  Future<Map<String, dynamic>> applyPlan(String text, {String? baseDate}) async {
    final body = <String, dynamic>{'text': text};
    if (baseDate != null) body['base_date'] = baseDate;
    return Map.from(await _post('/api/meal-plans/apply', body));
  }
}
