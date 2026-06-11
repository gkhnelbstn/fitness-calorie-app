// Tek giriş noktası — eski index.html script sırası birebir korunur.
// Dosyalar window.* globalleri üzerinden haberleşir (modül-içi import yok).
// ÖNEMLİ: globals.js ilk import olmalı (React/ReactDOM window'a oradan kurulur).
import './globals.js';
import './styles.css';
import './supabase.js'; // window.supabase (env yoksa null → mock auth)
import '../tweaks-panel.jsx';
import './mock.jsx';
import './ai.jsx';
import './icons.jsx';
import './ui.jsx';
import './muscle-map.jsx';
import './auth.jsx';
import './screens-dashboard.jsx';
import './screens-meals.jsx';
import './screens-recipes.jsx';
import './screens-workout.jsx';
import './screens-misc.jsx';
import './modals.jsx';
import './app.jsx'; // en son: #root'a render eder
