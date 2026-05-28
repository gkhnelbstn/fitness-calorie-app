import 'package:flutter/material.dart';

import 'api.dart';
import 'config.dart';
import 'theme.dart';
import 'screens/blacklist_screen.dart';
import 'screens/home_screen.dart';
import 'screens/meal_plan_screen.dart';
import 'screens/meals_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/recipes_screen.dart';
import 'screens/settings_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cfg = await ConfigStore.load();
  runApp(FitnessApp(cfg: cfg));
}

class FitnessApp extends StatefulWidget {
  final BackendConfig cfg;
  const FitnessApp({super.key, required this.cfg});

  @override
  State<FitnessApp> createState() => _FitnessAppState();
}

class _FitnessAppState extends State<FitnessApp> {
  late ApiClient api;

  @override
  void initState() {
    super.initState();
    api = ApiClient(widget.cfg);
  }

  Future<void> _reload() async {
    final c = await ConfigStore.load();
    setState(() {
      api.cfg = c;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Beslenme & Fitness',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.system,
      home: RootScaffold(api: api, onSettingsChanged: _reload),
    );
  }
}

class RootScaffold extends StatefulWidget {
  final ApiClient api;
  final Future<void> Function() onSettingsChanged;
  const RootScaffold({super.key, required this.api, required this.onSettingsChanged});

  @override
  State<RootScaffold> createState() => _RootScaffoldState();
}

class _RootScaffoldState extends State<RootScaffold> {
  int _idx = 0;

  List<Widget> get _tabs => [
        HomeScreen(api: widget.api),
        MealsScreen(api: widget.api),
        RecipesScreen(api: widget.api),
        BlacklistScreen(api: widget.api),
        ProfileScreen(api: widget.api),
      ];

  static const _titles = ['Özet', 'Yemekler', 'Tarifler', 'Kara Liste', 'Profil'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_idx]),
        actions: [
          IconButton(
            icon: const Icon(Icons.event_note),
            tooltip: 'Yemek planı yükle',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => MealPlanScreen(api: widget.api)),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Ayarlar',
            onPressed: () async {
              await Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
              await widget.onSettingsChanged();
            },
          ),
        ],
      ),
      body: IndexedStack(index: _idx, children: _tabs),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _idx,
        onDestinationSelected: (i) => setState(() => _idx = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), label: 'Özet'),
          NavigationDestination(icon: Icon(Icons.restaurant_menu), label: 'Yemek'),
          NavigationDestination(icon: Icon(Icons.menu_book), label: 'Tarif'),
          NavigationDestination(icon: Icon(Icons.block), label: 'Kara liste'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profil'),
        ],
      ),
    );
  }
}
