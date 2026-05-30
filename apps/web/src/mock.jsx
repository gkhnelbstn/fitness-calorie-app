// mock.jsx — Backend sözleşmesine (gkhnelbstn/fitness-calorie-app) hizalı mock + API.
// Canlı backend açıksa gerçek FastAPI'ye fetch (Bearer); kapalıysa localStorage mock.
// Şema alan adları backend ile birebir: sex, activity_level(EN), title_tr, status, canonical_id...
// Tüm uçların backend karşılığı mevcut (meals PUT/DELETE, goal/plan, workout* dahil).
(function () {
  const LS = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  };

  const SETTINGS_KEY = 'fk.settings';
  function getSettings() { return LS.get(SETTINGS_KEY, { baseUrl: 'http://localhost:8000', token: '', live: false }); }
  function setSettings(s) { LS.set(SETTINGS_KEY, s); }

  function todayStr() { return new Date().toISOString().slice(0, 10); }
  const cap = (s) => (s ? s.charAt(0).toLocaleUpperCase('tr') + s.slice(1) : s);
  function isoAt(date, h, m) { return new Date(date + 'T' + String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':00').toISOString(); }

  // ---------- Enerji (backend energy.py birebir) ----------
  const ACTIVITY_FACTORS = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725, very_active: 1.9 };
  const GOAL_DELTA = { kilo_ver: -500, koru: 0, kas_yap: 300 };
  const MALE = new Set(['erkek', 'male', 'm', 'e']);
  const DEFAULT_PROTEIN_PER_KG = 1.6;
  function age(by) { return Math.max(0, new Date().getFullYear() - by); }
  function bmrMifflin(sex, w, h, a) { return Math.round((10 * w + 6.25 * h - 5 * a + (MALE.has((sex || '').toLowerCase()) ? 5 : -161)) * 10) / 10; }
  function computeEnergy(p, goalType) {
    if (!p || p.sex == null || p.weight_kg == null || p.height_cm == null || p.birth_year == null) return null;
    const bmr = bmrMifflin(p.sex, p.weight_kg, p.height_cm, age(p.birth_year));
    const tdee = Math.round(bmr * (ACTIVITY_FACTORS[p.activity_level || 'moderate'] || 1.55) * 10) / 10;
    const target = Math.round(tdee + (GOAL_DELTA[goalType || 'koru'] || 0));
    return { bmr, tdee, target_kcal: target, target_low: target - 100, target_high: target + 100 };
  }

  // ---------- Seed ----------
  const STORE_KEY = 'fk.store.v2';

  // canonical id atlası (kara liste / malzeme eşleştirme taklidi)
  const CANON = [
    'yer_fistigi', 'karides', 'laktoz', 'tavuk', 'bulgur', 'pilav', 'yogurt', 'somon', 'mercimek',
    'patates', 'sogan', 'domates', 'biber', 'yumurta', 'zeytinyagi', 'tereyagi', 'kinoa', 'avokado', 'muz', 'yulaf', 'findik', 'salatalik',
  ].reduce((m, slug, i) => (m[slug] = i + 1, m), {});
  const slugName = { yer_fistigi: 'Yer fıstığı', karides: 'Karides', laktoz: 'Laktoz', tavuk: 'Tavuk', somon: 'Somon' };

  function mealItem(raw_name, qty, unit, kcal, p, c, f, fib, conf) {
    return { raw_name, quantity: qty, unit, canonical_id: null, kcal, protein_g: p, carb_g: c, fat_g: f, fiber_g: fib, confidence: conf == null ? 0.9 : conf };
  }

  function seed() {
    const t = todayStr();
    const d1 = new Date(); d1.setDate(d1.getDate() - 1); const yest = d1.toISOString().slice(0, 10);
    return {
      profile: { id: 1, name: 'Elif Demir', sex: 'kadin', birth_year: 1994, height_cm: 168, weight_kg: 72, activity_level: 'moderate', locale: 'tr' },
      goal: { id: 1, goal_type: 'kilo_ver', target_kcal: null, target_protein_g: null, active: true },
      // hedef sihirbazı sonuçları (ÖNERİ: backend UserPreference olarak saklanabilir)
      plan: { start_weight: 72, target_weight: 65, weeks: 14, pace: 0.5, days_per_week: 4, training_days: ['Pzt', 'Sal', 'Per', 'Cmt'] },
      blacklist: [
        { canonical_id: CANON.yer_fistigi, slug: 'yer_fistigi', name_tr: 'Yer fıstığı' },
        { canonical_id: CANON.karides, slug: 'karides', name_tr: 'Karides' },
        { canonical_id: CANON.laktoz, slug: 'laktoz', name_tr: 'Laktoz' },
      ],
      meals: {
        [t]: [
          { id: 101, eaten_at: isoAt(t, 8, 20), meal_type: 'kahvalti', raw_text: 'Yulaf ezmesi, 1 muz, bir avuç fındık', total_kcal: 420, photo_path: 'uploads/oat.jpg', items: [
            mealItem('Yulaf ezmesi', 60, 'gram', 228, 8, 40, 4, 6),
            mealItem('Muz', 1, 'adet', 95, 1, 24, 0, 3),
            mealItem('Fındık', 20, 'gram', 97, 5, 2, 9, 1.5),
          ] },
          { id: 102, eaten_at: isoAt(t, 13, 5), meal_type: 'ogle', raw_text: 'Tavuklu bulgur pilavı, 1 kase cacık', total_kcal: 610, photo_path: null, items: [
            mealItem('Izgara tavuk göğsü', 150, 'gram', 248, 46, 0, 5, 0),
            mealItem('Bulgur pilavı', 1, 'kase', 280, 8, 52, 5, 7),
            mealItem('Cacık', 1, 'kase', 82, 5, 8, 3, 0.5),
          ] },
          { id: 103, eaten_at: isoAt(t, 16, 40), meal_type: 'ara', raw_text: 'Protein shake', total_kcal: 180, photo_path: null, items: [
            mealItem('Whey protein', 1, 'ölçek', 120, 25, 3, 2, 0),
            mealItem('Süt (yağsız)', 200, 'ml', 60, 6, 9, 0, 0),
          ] },
        ],
        [yest]: [
          { id: 90, eaten_at: isoAt(yest, 9, 0), meal_type: 'kahvalti', raw_text: 'Menemen, 2 dilim tam buğday ekmek', total_kcal: 380, photo_path: 'uploads/menemen.jpg', items: [
            mealItem('Menemen (2 yumurta)', 1, 'porsiyon', 240, 16, 8, 16, 2),
            mealItem('Tam buğday ekmek', 2, 'dilim', 140, 6, 26, 2, 4),
          ] },
        ],
      },
      workoutLogs: { [t]: [{ id: 1, template_slug: 'bench-press', name_tr: 'Bench Press (Göğüs Presi)', sets: 4, reps: 10, minutes: 25, done: true }] },
      recId: 500,
    };
  }
  function getStore() { let s = LS.get(STORE_KEY, null); if (!s) { s = seed(); LS.set(STORE_KEY, s); } return s; }
  function saveStore(s) { LS.set(STORE_KEY, s); }

  function mealMacros(meal) {
    return (meal.items || []).reduce((a, it) => ({
      kcal: a.kcal + (it.kcal || 0), protein_g: a.protein_g + (it.protein_g || 0),
      carb_g: a.carb_g + (it.carb_g || 0), fat_g: a.fat_g + (it.fat_g || 0), fiber_g: a.fiber_g + (it.fiber_g || 0),
    }), { kcal: 0, protein_g: 0, carb_g: 0, fat_g: 0, fiber_g: 0 });
  }

  // ---------- Tarifler (RecipeRead birebir) ----------
  const RECIPES = [
    {
      id: 1, slug: 'firinda-kofteli-patates', title_tr: 'Fırında Köfteli Patates', servings: 4, region: 'İç Anadolu', total_kcal: 2160, adaptable: true,
      image_url: null, cook_minutes: 50, difficulty: 'orta',
      macros_per_serving: { kcal: 540, protein_g: 32, carb_g: 48, fat_g: 22, fiber_g: 6 },
      ingredients: [
        { raw_name: 'Dana kıyma', quantity: 250, unit: 'gram', optional: false, status: 'ok' },
        { raw_name: 'Patates', quantity: 3, unit: 'adet', optional: false, status: 'ok' },
        { raw_name: 'Soğan', quantity: 1, unit: 'adet', optional: false, status: 'ok' },
        { raw_name: 'Yoğurt sosu', quantity: 1, unit: 'kase', optional: true, status: 'substituted', substitute: 'Laktozsuz yoğurt' },
        { raw_name: 'Yer fıstığı serpme', quantity: 2, unit: 'yemek kaşığı', optional: true, status: 'removed' },
        { raw_name: 'Kekik, karabiber', optional: false, status: 'ok' },
      ],
      steps: ['Kıymayı rendelenmiş soğan ve baharatlarla yoğurup 15 dk dinlendir.', 'Ceviz büyüklüğünde köfteler yap.', 'Patatesleri yarım ay dilimle, tepsiye yağlayıp diz.', 'Köfteleri aralara yerleştir, üzerine zeytinyağı gezdir.', '200°C fırında 35 dk pişir.', 'Servis öncesi laktozsuz yoğurt sosu gezdir.'],
      tags: ['protein', 'firin', 'aksam'], notes: ['Kara listendeki “yer fıstığı” çıkarıldı.', 'Laktoz nedeniyle yoğurt → laktozsuz yoğurt ile değiştirildi.'],
    },
    {
      id: 2, slug: 'mercimek-koftesi', title_tr: 'Mercimek Köftesi', servings: 6, region: 'Akdeniz', total_kcal: 1920, adaptable: true,
      image_url: null, cook_minutes: 35, difficulty: 'kolay',
      macros_per_serving: { kcal: 320, protein_g: 14, carb_g: 52, fat_g: 6, fiber_g: 11 },
      ingredients: [
        { raw_name: 'Kırmızı mercimek', quantity: 1, unit: 'su bardağı', optional: false, status: 'ok' },
        { raw_name: 'İnce bulgur', quantity: 1, unit: 'su bardağı', optional: false, status: 'ok' },
        { raw_name: 'Domates salçası', quantity: 1, unit: 'yemek kaşığı', optional: false, status: 'ok' },
        { raw_name: 'Yeşil soğan, maydanoz', optional: true, status: 'ok' },
        { raw_name: 'Zeytinyağı', quantity: 3, unit: 'yemek kaşığı', optional: false, status: 'ok' },
      ],
      steps: ['Mercimeği 2 su bardağı suyla haşla.', 'Ocaktan alıp bulguru ekle, kapağı kapat 15 dk dinlendir.', 'Soğan ve salçayı zeytinyağında kavurup harca ekle.', 'Yeşillikleri doğra, yoğur ve köfte şekli ver.', 'Marul yaprağında, limonla servis et.'],
      tags: ['vegan', 'yuksek_lif', 'protein'], notes: ['Vegan ve yüksek lifli.'],
    },
    {
      id: 3, slug: 'izgara-somon-kinoa', title_tr: 'Izgara Somon & Kinoa', servings: 2, region: 'Modern', total_kcal: 960, adaptable: true,
      image_url: null, cook_minutes: 25, difficulty: 'kolay',
      macros_per_serving: { kcal: 480, protein_g: 38, carb_g: 30, fat_g: 22, fiber_g: 5 },
      ingredients: [
        { raw_name: 'Somon fileto', quantity: 360, unit: 'gram', optional: false, status: 'ok' },
        { raw_name: 'Kinoa', quantity: 1, unit: 'su bardağı', optional: false, status: 'ok' },
        { raw_name: 'Limon, dereotu', optional: false, status: 'ok' },
        { raw_name: 'Karides garnitür', quantity: 100, unit: 'gram', optional: true, status: 'removed' },
        { raw_name: 'Avokado', quantity: 1, unit: 'adet', optional: true, status: 'ok' },
      ],
      steps: ['Kinoayı bol suda 15 dk haşla, süz.', 'Somonu tuz, limon ve dereotuyla marine et.', 'Izgarada her yüzü 3-4 dk pişir.', 'Avokado ve kinoayla tabakla.'],
      tags: ['protein', 'omega3', 'aksam'], notes: ['Kara listendeki “karides” çıkarıldı.'],
    },
    {
      id: 4, slug: 'sebzeli-bulgur-pilavi', title_tr: 'Sebzeli Bulgur Pilavı', servings: 4, region: 'Güneydoğu', total_kcal: 1440, adaptable: true,
      image_url: null, cook_minutes: 30, difficulty: 'kolay',
      macros_per_serving: { kcal: 360, protein_g: 9, carb_g: 62, fat_g: 8, fiber_g: 9 },
      ingredients: [
        { raw_name: 'Pilavlık bulgur', quantity: 1.5, unit: 'su bardağı', optional: false, status: 'ok' },
        { raw_name: 'Biber, domates, soğan', optional: false, status: 'ok' },
        { raw_name: 'Tereyağı', quantity: 1, unit: 'yemek kaşığı', optional: true, status: 'substituted', substitute: 'Zeytinyağı' },
        { raw_name: 'Et suyu', quantity: 3, unit: 'su bardağı', optional: false, status: 'ok' },
      ],
      steps: ['Sebzeleri küp doğrayıp kavur.', 'Bulguru ekle, 2 dk çevir.', 'Sıcak et suyunu ekle, kısık ateşte pişir.', '10 dk demlenmeye bırak.'],
      tags: ['vejetaryen', 'yuksek_lif'], notes: ['Tereyağı zeytinyağıyla değiştirildi.'],
    },
    {
      id: 5, slug: 'firin-tavuk-sebze', title_tr: 'Fırın Tavuk & Sebze', servings: 3, region: 'Modern', total_kcal: 1260, adaptable: true,
      image_url: null, cook_minutes: 40, difficulty: 'kolay',
      macros_per_serving: { kcal: 420, protein_g: 40, carb_g: 28, fat_g: 16, fiber_g: 7 },
      ingredients: [
        { raw_name: 'Tavuk but', quantity: 500, unit: 'gram', optional: false, status: 'ok' },
        { raw_name: 'Brokoli, havuç, kabak', optional: false, status: 'ok' },
        { raw_name: 'Zeytinyağı', quantity: 2, unit: 'yemek kaşığı', optional: false, status: 'ok' },
        { raw_name: 'Sarımsak, kekik, pul biber', optional: true, status: 'ok' },
      ],
      steps: ['Tavuğu baharat ve zeytinyağıyla marine et.', 'Sebzeleri iri doğra, tepsiye diz.', 'Tavukları üzerine yerleştir.', '200°C fırında 35-40 dk pişir.'],
      tags: ['protein', 'firin', 'aksam', 'dusuk_karb'], notes: ['Yüksek protein, düşük karbonhidrat.'],
    },
    {
      id: 6, slug: 'yulafli-pankek', title_tr: 'Yulaflı Pankek', servings: 2, region: 'Kahvaltı', total_kcal: 640, adaptable: true,
      image_url: null, cook_minutes: 15, difficulty: 'kolay',
      macros_per_serving: { kcal: 320, protein_g: 22, carb_g: 38, fat_g: 8, fiber_g: 5 },
      ingredients: [
        { raw_name: 'Yulaf ezmesi', quantity: 1, unit: 'su bardağı', optional: false, status: 'ok' },
        { raw_name: 'Yumurta', quantity: 2, unit: 'adet', optional: false, status: 'ok' },
        { raw_name: 'Muz', quantity: 1, unit: 'adet', optional: false, status: 'ok' },
        { raw_name: 'Tarçın', optional: true, status: 'ok' },
      ],
      steps: ['Tüm malzemeleri blenderdan geçir.', 'Yapışmaz tavada az yağla pişir.', 'Üzerine taze meyve ile servis et.'],
      tags: ['protein', 'kahvalti', 'pratik'], notes: ['Antrenman öncesi/sonrası iyi seçenek.'],
    },
    {
      id: 7, slug: 'zeytinyagli-taze-fasulye', title_tr: 'Zeytinyağlı Taze Fasulye', servings: 4, region: 'Ege', total_kcal: 720, adaptable: true,
      image_url: null, cook_minutes: 35, difficulty: 'kolay',
      macros_per_serving: { kcal: 180, protein_g: 5, carb_g: 18, fat_g: 10, fiber_g: 8 },
      ingredients: [
        { raw_name: 'Taze fasulye', quantity: 500, unit: 'gram', optional: false, status: 'ok' },
        { raw_name: 'Soğan, domates', optional: false, status: 'ok' },
        { raw_name: 'Zeytinyağı', quantity: 4, unit: 'yemek kaşığı', optional: false, status: 'ok' },
      ],
      steps: ['Soğanı zeytinyağında kavur.', 'Fasulye ve domatesi ekle.', 'Az suyla kısık ateşte 30 dk pişir.', 'Soğuk servis et.'],
      tags: ['vegan', 'yuksek_lif', 'zeytinyagli'], notes: ['Lif açısından zengin, vegan.'],
    },
  ];

  // ---------- Egzersiz kataloğu (free-exercise-db tarzı, WorkoutTemplate) ----------
  const EXERCISES = [
    { id: 1, slug: 'bench-press', name_tr: 'Bench Press (Göğüs Presi)', primary_muscle: 'gogus', level: 'intermediate', equipment: 'halter', category: 'kuvvet', secondary: ['triceps', 'omuz'] },
    { id: 2, slug: 'incline-dumbbell-press', name_tr: 'Eğimli Dambıl Press', primary_muscle: 'gogus', level: 'intermediate', equipment: 'dambıl', category: 'kuvvet', secondary: ['omuz'] },
    { id: 3, slug: 'pull-up', name_tr: 'Barfiks', primary_muscle: 'sirt', level: 'expert', equipment: 'vücut ağırlığı', category: 'kuvvet', secondary: ['biceps'] },
    { id: 4, slug: 'lat-pulldown', name_tr: 'Lat Çekiş', primary_muscle: 'sirt', level: 'beginner', equipment: 'makine', category: 'kuvvet', secondary: ['biceps'] },
    { id: 5, slug: 'overhead-press', name_tr: 'Omuz Press', primary_muscle: 'omuz', level: 'intermediate', equipment: 'halter', category: 'kuvvet', secondary: ['triceps'] },
    { id: 6, slug: 'squat', name_tr: 'Squat (Çömelme)', primary_muscle: 'bacak', level: 'intermediate', equipment: 'halter', category: 'kuvvet', secondary: ['kalça'] },
    { id: 7, slug: 'romanian-deadlift', name_tr: 'Romanian Deadlift (Ölü Kaldırış)', primary_muscle: 'bacak', level: 'intermediate', equipment: 'halter', category: 'kuvvet', secondary: ['sirt', 'kalça'] },
    { id: 8, slug: 'plank', name_tr: 'Plank (Tahta Duruşu)', primary_muscle: 'karin', level: 'beginner', equipment: 'vücut ağırlığı', category: 'kuvvet', secondary: ['bel'] },
    { id: 9, slug: 'bicycle-crunch', name_tr: 'Bisiklet Mekiği', primary_muscle: 'karin', level: 'beginner', equipment: 'vücut ağırlığı', category: 'kuvvet', secondary: [] },
    { id: 10, slug: 'treadmill-run', name_tr: 'Koşu Bandı', primary_muscle: 'kardiyo', level: 'beginner', equipment: 'makine', category: 'kardiyo', secondary: [] },
    { id: 11, slug: 'hiit-intervals', name_tr: 'HIIT (Aralıklı Yüksek Tempo)', primary_muscle: 'kardiyo', level: 'intermediate', equipment: 'vücut ağırlığı', category: 'kardiyo', secondary: [] },
    { id: 12, slug: 'walking', name_tr: 'Tempolu Yürüyüş', primary_muscle: 'kardiyo', level: 'beginner', equipment: 'yok', category: 'kardiyo', secondary: [] },
    { id: 13, slug: 'dumbbell-curl', name_tr: 'Dambıl Biceps Curl', primary_muscle: 'kol', level: 'beginner', equipment: 'dambıl', category: 'kuvvet', secondary: [] },
    { id: 14, slug: 'tricep-pushdown', name_tr: 'Triceps Pushdown (Arka Kol İtişi)', primary_muscle: 'kol', level: 'beginner', equipment: 'makine', category: 'kuvvet', secondary: [] },
    { id: 15, slug: 'leg-press', name_tr: 'Leg Press (Bacak Presi)', primary_muscle: 'bacak', level: 'beginner', equipment: 'makine', category: 'kuvvet', secondary: ['kalca'] },
    { id: 16, slug: 'dips', name_tr: 'Dips (Paralel)', primary_muscle: 'gogus', level: 'intermediate', equipment: 'vücut ağırlığı', category: 'kuvvet', secondary: ['kol', 'omuz'] },
    { id: 17, slug: 'dumbbell-shoulder-press', name_tr: 'Dambıl Omuz Press', primary_muscle: 'omuz', level: 'beginner', equipment: 'dambıl', category: 'kuvvet', secondary: ['kol'] },
    { id: 18, slug: 'leg-curl', name_tr: 'Leg Curl (Arka Bacak Bükme)', primary_muscle: 'bacak', level: 'beginner', equipment: 'makine', category: 'kuvvet', secondary: ['kalca'] },
    { id: 19, slug: 'seated-row', name_tr: 'Oturarak Kürek', primary_muscle: 'sirt', level: 'beginner', equipment: 'makine', category: 'kuvvet', secondary: ['kol'] },
    { id: 20, slug: 'chest-fly', name_tr: 'Pec Deck (Göğüs Sıkıştırma)', primary_muscle: 'gogus', level: 'beginner', equipment: 'makine', category: 'kuvvet', secondary: ['omuz'] },
    { id: 21, slug: 'hip-thrust', name_tr: 'Hip Thrust (Kalça İtişi)', primary_muscle: 'kalca', level: 'intermediate', equipment: 'halter', category: 'kuvvet', secondary: ['bacak'] },
    { id: 22, slug: 'rowing-machine', name_tr: 'Kürek Makinesi', primary_muscle: 'kardiyo', level: 'beginner', equipment: 'makine', category: 'kardiyo', secondary: ['sirt'] },
    { id: 23, slug: 'jump-rope', name_tr: 'İp Atlama', primary_muscle: 'kardiyo', level: 'beginner', equipment: 'yok', category: 'kardiyo', secondary: ['bacak'] },
    { id: 24, slug: 'goblet-squat', name_tr: 'Goblet Squat (Önden Çömelme)', primary_muscle: 'bacak', level: 'beginner', equipment: 'dambıl', category: 'kuvvet', secondary: ['kalca'] },
  ];
  // Ekipman tipi: makine | serbest (halter/dambıl) | vücut (vücut ağırlığı/yok)
  const EQ_TYPE = (eq) => /makine/.test(eq) ? 'makine' : /halter|dambıl/.test(eq) ? 'serbest' : 'vücut';
  const EQ_TYPE_LABEL = { makine: 'Makine', serbest: 'Serbest ağırlık', 'vücut': 'Vücut ağırlığı' };

  // Form ipuçları (her hareket) + makine kullanım tarifi (yalnız makineler)
  const INSTR = {
    'bench-press': ['Sırt üstü uzan, gözler bar hizasında.', 'Kavrama omuzdan biraz geniş, bilekler dik.', 'Barı göğse kontrollü indir, kürek kemiklerini sık, patlayıcı it.'],
    'incline-dumbbell-press': ['Sehpayı 30-45° eğ.', 'Dambılları göğüs üst hizasına indir.', 'Dirsekleri 45° açıyla tut, yukarıda sıkıştır.'],
    'overhead-press': ['Bar omuz önünde, karın sıkı.', 'Başın üzerine dik it, kaburgaları açma.', 'Kontrollü indir.'],
    'pull-up': ['Bara omuzdan geniş asıl.', 'Kürekleri aşağı-geri çekerek çeneyi barın üstüne taşı.', 'Kontrollü in, tam aç.'],
    'dumbbell-curl': ['Dirsekler gövdeye sabit.', 'Dambılı sıkışana kadar kaldır, sallanma.', 'Negatifi yavaş indir.'],
    'squat': ['Bar üst sırtta, ayaklar omuz genişliği.', 'Kalçayı geri-aşağı, dizler parmak yönünde.', 'Uyluk paralelin altına in, topuktan it.'],
    'romanian-deadlift': ['Hafif diz bükük, bar bacağa yakın.', 'Kalçayı geri it, sırt nötr.', 'Hamstringde gerilim hissedince yukarı kalk.'],
    'hip-thrust': ['Sırt üst kısmı bench’e dayalı, bar kalçada.', 'Topuktan iterek kalçayı yukarı kilitle.', 'Üstte gluteyi 1 sn sık.'],
    'plank': ['Dirsekler omuz altında.', 'Gövde baştan topuğa düz, karın+kalça sıkı.', 'Beli çökertme.'],
    'bicycle-crunch': ['Sırt üstü, eller şakakta.', 'Karşı dirsek-diz buluştur, dönüşü karından yap.', 'Kontrollü ve yavaş.'],
    'dips': ['Paralel barda dirsekleri 90°ye bük.', 'Hafif öne eğil (göğüs) ya da dik dur (triceps).', 'Patlayıcı yukarı it.'],
    'goblet-squat': ['Dambılı göğüs önünde tut.', 'Dik gövde ile çömel.', 'Topuktan kalk.'],
    'jump-rope': ['Bilekten çevir, sıçramalar kısa.', 'Ayak ucunda kal.'],
    'walking': ['Tempolu, kol salınımı serbest.', 'Hafif nefes nefese kalacak hızda.'],
    'hiit-intervals': ['30 sn maksimal efor + 30 sn dinlen.', '6-10 tur tekrarla.'],
  };
  const MACHINE_HOWTO = {
    'lat-pulldown': 'Koltuğu otur, diz pedini uyluklara sıkıştır. Barı omuzdan geniş kavra; gövdeyi hafif geriye yaslayıp barı göğüs üstüne, dirsekleri yanlara çekerek indir. Kontrollü olarak yukarı bırak, kollar tam açılsın.',
    'leg-press': 'Sırtını ve kalçanı mindere tam yasla. Ayaklar platformda omuz genişliğinde, ortada. Emniyet kollarını aç, ağırlığı dizler ~90° olana dek indir; topuktan iterek kalk ama dizleri tam kilitleme.',
    'leg-curl': 'Yüzüstü/oturarak makineye yerleş; ped aşil üstüne gelsin. Topukları kalçaya doğru kıvırarak hamstringi sık, kontrollü geri bırak. Beli kaldırma.',
    'seated-row': 'Göğsü pede daya, dizler hafif bükük. Tutamağı çek; kürekleri geri-aşağı sıkıştır, dirsekleri gövdeye yakın tut. Kontrollü uzat, omuzları öne bırak.',
    'chest-fly': 'Koltuğu kollar omuz hizasında olacak şekilde ayarla. Dirsekler hafif bükük; kolları önde kavis çizerek birleştir, göğsü sıkıştır. Yavaşça aç.',
    'tricep-pushdown': 'Makaraya yüksek tut. Dirsekleri gövdeye sabitle; barı/ipi aşağı, kollar tam düzelene dek it. Sadece ön kol hareket etsin, kontrollü geri bırak.',
    'rowing-machine': 'Ayakları kayışa sabitle. Sıra: bacakla it → gövdeyi hafif geri yasla → kolla çek. Geri dönüşte ters sıra. Sırtı yuvarlama.',
    'treadmill-run': 'Hızı kademeli artır, gerekiyorsa %1-2 eğim ver. Bandın ortasında, dik gövdeyle koş; tutamağa asılma. Acil durdurma klipsini tak.',
  };
  const DEFAULT_INSTR = (e) => [`${e.name_tr} hareketini kontrollü ve tam hareket açıklığıyla yap.`, 'Nefesi efor anında ver, sırtı nötr tut.'];

  function enrich(e) {
    return { ...e, equipment_type: EQ_TYPE(e.equipment), instructions: INSTR[e.slug] || DEFAULT_INSTR(e), machine_howto: MACHINE_HOWTO[e.slug] || null };
  }
  const exBySlug = (slug) => { const e = EXERCISES.find((x) => x.slug === slug); return e ? enrich(e) : null; };

  // Tipe göre alternatifler (aynı birincil kas, farklı/aynı ekipman tipleri gruplu)
  function altsByType(slug) {
    const base = EXERCISES.find((e) => e.slug === slug); if (!base) return {};
    const g = {};
    EXERCISES.filter((e) => e.slug !== slug && e.primary_muscle === base.primary_muscle).forEach((e) => { const t = EQ_TYPE(e.equipment); (g[t] = g[t] || []).push({ slug: e.slug, name_tr: e.name_tr, equipment: e.equipment }); });
    return g;
  }
  function pickRowAlt(slug) {
    const g = altsByType(slug); const base = EXERCISES.find((e) => e.slug === slug); if (!base) return null;
    const bt = EQ_TYPE(base.equipment);
    const order = bt === 'makine' ? ['serbest', 'vücut', 'makine'] : bt === 'serbest' ? ['makine', 'vücut', 'serbest'] : ['makine', 'serbest', 'vücut'];
    for (const t of order) { if (g[t] && g[t].length) return { ...g[t][0], equipment_type: t }; }
    return null;
  }

  // Kuvvet seans havuzları (gün-bağımsız). Her seansa kapanış kardiyosu eklenir.
  const STRENGTH_POOLS = {
    kas_yap: [
      { title: 'İtiş — Göğüs / Omuz / Triceps', ex: [ { slug: 'bench-press', sets: 4, reps: '8-10', rest: 90 }, { slug: 'incline-dumbbell-press', sets: 3, reps: '10-12', rest: 75 }, { slug: 'overhead-press', sets: 3, reps: '8-10', rest: 90 }, { slug: 'tricep-pushdown', sets: 3, reps: '12-15', rest: 60 } ] },
      { title: 'Çekiş — Sırt / Biceps', ex: [ { slug: 'pull-up', sets: 4, reps: '6-10', rest: 90 }, { slug: 'seated-row', sets: 3, reps: '10-12', rest: 75 }, { slug: 'lat-pulldown', sets: 3, reps: '10-12', rest: 75 }, { slug: 'dumbbell-curl', sets: 3, reps: '12', rest: 60 } ] },
      { title: 'Bacak / Kalça', ex: [ { slug: 'squat', sets: 4, reps: '6-8', rest: 120 }, { slug: 'romanian-deadlift', sets: 3, reps: '8-10', rest: 100 }, { slug: 'leg-press', sets: 3, reps: '10-12', rest: 90 }, { slug: 'hip-thrust', sets: 3, reps: '10-12', rest: 75 } ] },
      { title: 'Üst vücut', ex: [ { slug: 'incline-dumbbell-press', sets: 3, reps: '10', rest: 75 }, { slug: 'seated-row', sets: 3, reps: '10', rest: 75 }, { slug: 'dumbbell-shoulder-press', sets: 3, reps: '12', rest: 60 }, { slug: 'dumbbell-curl', sets: 3, reps: '12', rest: 45 } ] },
      { title: 'Tam vücut + Karın', ex: [ { slug: 'goblet-squat', sets: 3, reps: '12', rest: 75 }, { slug: 'bench-press', sets: 3, reps: '10', rest: 75 }, { slug: 'lat-pulldown', sets: 3, reps: '12', rest: 75 }, { slug: 'plank', sets: 3, reps: '45 sn', rest: 45 }, { slug: 'bicycle-crunch', sets: 3, reps: '20', rest: 40 } ] },
    ],
    kilo_ver: [
      { title: 'Tam vücut A', ex: [ { slug: 'goblet-squat', sets: 3, reps: '12', rest: 60 }, { slug: 'bench-press', sets: 3, reps: '10', rest: 60 }, { slug: 'lat-pulldown', sets: 3, reps: '12', rest: 60 }, { slug: 'plank', sets: 3, reps: '40 sn', rest: 40 } ] },
      { title: 'Tam vücut B', ex: [ { slug: 'leg-press', sets: 3, reps: '12', rest: 60 }, { slug: 'dumbbell-shoulder-press', sets: 3, reps: '12', rest: 60 }, { slug: 'seated-row', sets: 3, reps: '12', rest: 60 }, { slug: 'bicycle-crunch', sets: 3, reps: '20', rest: 40 } ] },
      { title: 'Alt vücut + Kalça', ex: [ { slug: 'squat', sets: 3, reps: '10', rest: 90 }, { slug: 'romanian-deadlift', sets: 3, reps: '10', rest: 75 }, { slug: 'hip-thrust', sets: 3, reps: '12', rest: 60 }, { slug: 'leg-curl', sets: 3, reps: '12', rest: 60 } ] },
      { title: 'Üst vücut', ex: [ { slug: 'incline-dumbbell-press', sets: 3, reps: '10', rest: 60 }, { slug: 'lat-pulldown', sets: 3, reps: '12', rest: 60 }, { slug: 'overhead-press', sets: 3, reps: '10', rest: 60 }, { slug: 'tricep-pushdown', sets: 3, reps: '12', rest: 45 } ] },
    ],
    koru: [
      { title: 'Tam vücut A', ex: [ { slug: 'squat', sets: 3, reps: '10', rest: 90 }, { slug: 'bench-press', sets: 3, reps: '10', rest: 75 }, { slug: 'lat-pulldown', sets: 3, reps: '12', rest: 75 }, { slug: 'plank', sets: 3, reps: '40 sn', rest: 40 } ] },
      { title: 'Tam vücut B', ex: [ { slug: 'leg-press', sets: 3, reps: '12', rest: 75 }, { slug: 'dumbbell-shoulder-press', sets: 3, reps: '12', rest: 60 }, { slug: 'seated-row', sets: 3, reps: '12', rest: 60 }, { slug: 'dumbbell-curl', sets: 3, reps: '12', rest: 45 } ] },
      { title: 'Tam vücut C', ex: [ { slug: 'romanian-deadlift', sets: 3, reps: '10', rest: 75 }, { slug: 'dips', sets: 3, reps: '10', rest: 60 }, { slug: 'pull-up', sets: 3, reps: '8', rest: 75 }, { slug: 'bicycle-crunch', sets: 3, reps: '20', rest: 40 } ] },
    ],
  };
  const CARDIO_FINISH = { kilo_ver: '20 dk', kas_yap: '10 dk', koru: '15 dk' };
  const DEFAULT_DAYS = { 2: ['Pzt', 'Per'], 3: ['Pzt', 'Çar', 'Cum'], 4: ['Pzt', 'Sal', 'Per', 'Cmt'], 5: ['Pzt', 'Sal', 'Çar', 'Cum', 'Cmt'], 6: ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt'] };

  function resolveExercise(e, level, isFinisher) {
    const base = exBySlug(e.slug) || { name_tr: e.slug, equipment: '-', equipment_type: 'vücut', primary_muscle: null, secondary: [], category: 'kuvvet', instructions: [], machine_howto: null };
    let sets = e.sets;
    if (base.category === 'kuvvet' && !isFinisher) { if (level === 'beginner') sets = Math.max(2, e.sets - 1); else if (level === 'expert') sets = e.sets + 1; }
    return {
      slug: e.slug, name_tr: base.name_tr, equipment: base.equipment, equipment_type: base.equipment_type,
      category: base.category, primary_muscle: base.primary_muscle, secondary: base.secondary || [],
      instructions: base.instructions, machine_howto: base.machine_howto,
      sets, reps: e.reps, rest: e.rest, finisher: !!isFinisher,
      alternative: pickRowAlt(e.slug), alternatives_by_type: altsByType(e.slug),
    };
  }

  function dayWorked(exercises) {
    const prim = new Set(), sec = new Set();
    exercises.forEach((x) => { if (x.primary_muscle) prim.add(x.primary_muscle); (x.secondary || []).forEach((m) => sec.add(m)); });
    return { primary: [...prim], secondary: [...sec].filter((m) => !prim.has(m)) };
  }

  function buildPlan(goalType, level, daysPerWeek, trainingDays) {
    const pool = STRENGTH_POOLS[goalType] || STRENGTH_POOLS.koru;
    const N = Math.max(1, Math.min(6, daysPerWeek || 4));
    const td = (trainingDays && trainingDays.length === N) ? trainingDays : (DEFAULT_DAYS[N] || DEFAULT_DAYS[4]);
    const finishReps = CARDIO_FINISH[goalType] || '15 dk';
    const days = [];
    for (let i = 0; i < N; i++) {
      const sess = pool[i % pool.length];
      const strength = sess.ex.map((e) => resolveExercise(e, level, false));
      const cardio = resolveExercise({ slug: 'treadmill-run', sets: 1, reps: finishReps, rest: 0 }, level, true);
      const exercises = [...strength, cardio];
      const sMin = Math.round(strength.reduce((a, x) => a + x.sets * 2.2, 0)) + 8;
      const cMin = parseInt(finishReps) || 12;
      days.push({ day: td[i] || DEFAULT_DAYS[4][i], title: sess.title, kind: 'kuvvet+kardiyo', minutes: sMin + cMin, exercises, worked: dayWorked(strength) });
    }
    const weekly = days.reduce((a, d) => a + d.minutes, 0);
    const focus = { kas_yap: 'kuvvet (split)', kilo_ver: 'kardiyo + kuvvet', koru: 'karışık' }[goalType] || 'karışık';
    return { goal_type: goalType, level, days_per_week: N, training_days: td, focus, weekly_minutes: weekly,
      warmup: '5-10 dk hafif kardiyo + dinamik esneme ile ısın.', structure_note: 'Her seans: önce ağırlık antrenmanı, sonra kapanış kardiyosu.', days, note: WHO_NOTE };
  }
  const MET = { kuvvet: 5, kardiyo: 8 };

  const WORKOUT_BY_GOAL = {
    kilo_ver: { focus: 'kardiyo + kuvvet', weekly_minutes: 200, days: [
      { day: 'Pzt', title: '40 dk tempolu yürüyüş', kind: 'kardiyo', minutes: 40 },
      { day: 'Çar', title: 'Tam vücut kuvvet', kind: 'kuvvet', minutes: 50 },
      { day: 'Cum', title: '40 dk kardiyo', kind: 'kardiyo', minutes: 40 },
      { day: 'Cmt', title: 'Kuvvet (üst vücut)', kind: 'kuvvet', minutes: 45 },
    ] },
    kas_yap: { focus: 'kuvvet (split)', weekly_minutes: 180, days: [
      { day: 'Pzt', title: 'İtiş — Göğüs/Omuz/Triceps', kind: 'kuvvet', minutes: 50 },
      { day: 'Sal', title: 'Çekiş — Sırt/Biceps', kind: 'kuvvet', minutes: 50 },
      { day: 'Per', title: 'Bacak', kind: 'kuvvet', minutes: 55 },
      { day: 'Cmt', title: 'Tam vücut + karın', kind: 'kuvvet', minutes: 45 },
    ] },
    koru: { focus: 'karışık', weekly_minutes: 150, days: [
      { day: 'Pzt', title: '30 dk kardiyo', kind: 'kardiyo', minutes: 30 },
      { day: 'Çar', title: 'Kuvvet (tam vücut)', kind: 'kuvvet', minutes: 45 },
      { day: 'Cum', title: '30 dk kardiyo', kind: 'kardiyo', minutes: 30 },
    ] },
  };
  const WHO_NOTE = 'Haftada en az 150 dk orta veya 75 dk yüksek şiddet + 2 gün kuvvet (WHO).';

  // ---------- Kurallı NL parser (AI fallback) ----------
  function ruleParse(text) {
    const t = (text || '').toLowerCase();
    const db = [
      [/pilav/, mealItem('Pilav', 1, 'kase', 280, 6, 56, 4, 2)],
      [/bulgur/, mealItem('Bulgur', 1, 'kase', 250, 8, 48, 4, 7)],
      [/makarna/, mealItem('Makarna', 1, 'kase', 320, 11, 60, 3, 3)],
      [/ekmek|simit/, mealItem('Ekmek', 2, 'dilim', 140, 5, 26, 2, 2)],
      [/tavuk/, mealItem('Tavuk göğsü', 150, 'gram', 248, 46, 0, 6, 0)],
      [/köfte|kofte/, mealItem('Köfte', 4, 'adet', 300, 24, 4, 20, 0)],
      [/somon|balık|balik/, mealItem('Somon', 150, 'gram', 280, 30, 0, 18, 0)],
      [/yumurta|menemen|omlet/, mealItem('Yumurta', 2, 'adet', 150, 12, 2, 10, 0)],
      [/ayran/, mealItem('Ayran', 1, 'bardak', 60, 3, 5, 3, 0)],
      [/yoğurt|yogurt|cacık|cacik/, mealItem('Yoğurt', 1, 'kase', 90, 6, 8, 3, 0)],
      [/salata/, mealItem('Mevsim salata', 1, 'porsiyon', 70, 2, 9, 3, 4)],
      [/çorba|corba|mercimek/, mealItem('Mercimek çorbası', 1, 'kase', 150, 8, 22, 3, 5)],
      [/muz/, mealItem('Muz', 1, 'adet', 95, 1, 24, 0, 3)],
      [/elma/, mealItem('Elma', 1, 'adet', 80, 0, 21, 0, 4)],
    ];
    const items = [];
    db.forEach(([re, it]) => { if (re.test(t)) items.push({ ...it, confidence: 0.62 }); });
    if (!items.length) items.push(mealItem(text || 'Öğün', 1, 'porsiyon', 300, 12, 38, 9, 3, 0.4));
    return items;
  }

  function guessMealType() { const h = new Date().getHours(); return h < 11 ? 'kahvalti' : h < 15 ? 'ogle' : h < 18 ? 'ara' : 'aksam'; }
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const delay = () => wait(340 + Math.random() * 360);

  function recipeExcludeApply(r, excludeNames) {
    if (!excludeNames.length) return r;
    return { ...r, ingredients: r.ingredients.map((i) => excludeNames.some((e) => i.raw_name.toLowerCase().includes(e)) ? { ...i, status: 'removed' } : i) };
  }

  // ---------- MOCK ROUTER ----------
  async function mockHandle(method, path, query, body) {
    await delay();
    const s = getStore();
    const date = (query && query.date) || todayStr();

    // -- summary --
    if (path === '/api/summary') {
      const list = s.meals[date] || [];
      const agg = list.reduce((a, m) => { const mm = mealMacros(m); return { kcal: a.kcal + mm.kcal, p: a.p + mm.protein_g, c: a.c + mm.carb_g, f: a.f + mm.fat_g, fib: a.fib + mm.fiber_g, items: a.items + (m.items || []).length }; }, { kcal: 0, p: 0, c: 0, f: 0, fib: 0, items: 0 });
      return { day: date, intake_kcal: Math.round(agg.kcal), protein_g: Math.round(agg.p), carb_g: Math.round(agg.c), fat_g: Math.round(agg.f), fiber_g: Math.round(agg.fib), meal_count: list.length, item_count: agg.items, active_kcal: null, net_kcal: null };
    }

    // -- recommendations --
    if (path === '/api/recommendations') {
      const energy = computeEnergy(s.profile, s.goal.goal_type);
      const list = s.meals[date] || [];
      const intake = list.reduce((a, m) => a + mealMacros(m).kcal, 0);
      const intakeP = list.reduce((a, m) => a + mealMacros(m).protein_g, 0);
      const target_kcal = (s.goal.target_kcal) || (energy ? energy.target_kcal : null);
      const remaining = target_kcal != null ? Math.round((target_kcal - intake) * 10) / 10 : null;
      let protein_target = s.goal.target_protein_g;
      if (protein_target == null && s.profile.weight_kg) protein_target = Math.round(s.profile.weight_kg * DEFAULT_PROTEIN_PER_KG * 10) / 10;
      const protein_remaining = protein_target != null ? Math.round((protein_target - intakeP) * 10) / 10 : null;

      const blockedNames = s.blacklist.map((b) => b.name_tr.toLowerCase());
      let recs = RECIPES.filter((r) => !blockedNames.some((b) => r.ingredients.some((i) => i.raw_name.toLowerCase().includes(b))));
      if (protein_remaining != null && protein_remaining > 20) recs.sort((a, b) => (a.tags.includes('protein') ? 0 : 1) - (b.tags.includes('protein') ? 0 : 1));
      const meal_suggestions = recs.slice(0, 3);

      const w = WORKOUT_BY_GOAL[s.goal.goal_type] || WORKOUT_BY_GOAL.koru;
      const notes = [];
      if (target_kcal == null) notes.push('Kalori hedefi hesaplanamadı; profil ve hedefini doldur.');
      if (remaining != null && remaining > 0) notes.push(`Bugün ~${Math.round(remaining)} kcal daha alabilirsin.`);
      else if (remaining != null && remaining < 0) notes.push(`Hedefi ~${Math.round(Math.abs(remaining))} kcal aştın.`);
      if (protein_remaining != null && protein_remaining > 0) notes.push(`~${Math.round(protein_remaining)} g protein açığın var.`);

      return {
        id: s.recId, day: date,
        energy: energy ? { bmr: energy.bmr, tdee: energy.tdee, target_kcal, intake_kcal: Math.round(intake), remaining_kcal: remaining, protein_target_g: protein_target, protein_intake_g: Math.round(intakeP), protein_remaining_g: protein_remaining }
          : { bmr: null, tdee: null, target_kcal, intake_kcal: Math.round(intake), remaining_kcal: remaining, protein_target_g: protein_target, protein_intake_g: Math.round(intakeP), protein_remaining_g: protein_remaining },
        meal_suggestions, workout: { focus: w.focus, weekly_minutes: w.weekly_minutes, days: w.days, note: WHO_NOTE }, notes,
      };
    }

    // -- meals --
    if (path === '/api/meals' && method === 'GET') return (s.meals[date] || []).slice().sort((a, b) => a.eaten_at < b.eaten_at ? 1 : -1);
    if (path === '/api/meals' && method === 'POST') {
      let items = (body.items && body.items.length) ? body.items : ruleParse(body.raw_text);
      const total = Math.round(items.reduce((a, i) => a + (i.kcal || 0), 0)) || null;
      const meal = { id: Date.now(), eaten_at: isoAt(date, new Date().getHours(), new Date().getMinutes()), meal_type: body.meal_type || guessMealType(), raw_text: body.raw_text || (items[0] && items[0].raw_name) || 'Öğün', total_kcal: total, photo_path: null, items };
      s.meals[date] = [...(s.meals[date] || []), meal]; saveStore(s); return meal;
    }
    if (path === '/api/meals/by-barcode') {
      const grams = Number(body.grams) || 100; const per = { kcal: 1.6, p: 0.09, c: 0.18, f: 0.05, fib: 0.02 };
      const item = mealItem('Barkod ürünü ' + body.barcode, grams, 'gram', Math.round(per.kcal * grams), Math.round(per.p * grams), Math.round(per.c * grams), Math.round(per.f * grams), Math.round(per.fib * grams), 1.0);
      const meal = { id: Date.now(), eaten_at: isoAt(date, new Date().getHours(), new Date().getMinutes()), meal_type: body.meal_type || guessMealType(), raw_text: `[barkod ${body.barcode}]`, total_kcal: item.kcal, photo_path: null, items: [item] };
      s.meals[date] = [...(s.meals[date] || []), meal]; saveStore(s); return meal;
    }
    if (path === '/api/meals/photo') {
      const items = body.items && body.items.length ? body.items : (body.raw_text ? ruleParse(body.raw_text) : [mealItem('Fotoğraftan öğün', 1, 'porsiyon', 430, 22, 40, 18, 4, 0.5)]);
      const total = Math.round(items.reduce((a, i) => a + (i.kcal || 0), 0)) || null;
      const meal = { id: Date.now(), eaten_at: isoAt(date, new Date().getHours(), new Date().getMinutes()), meal_type: body.meal_type || guessMealType(), raw_text: body.raw_text || 'Fotoğraftan öğün', total_kcal: total, photo_path: 'uploads/' + Date.now() + '.jpg', items };
      s.meals[date] = [...(s.meals[date] || []), meal]; saveStore(s); return meal;
    }
    // PUT/DELETE meals (backend: meals.py)
    if (path.startsWith('/api/meals/') && method === 'PUT') {
      const id = Number(path.split('/').pop());
      Object.keys(s.meals).forEach((k) => { s.meals[k] = s.meals[k].map((m) => m.id === id ? { ...m, ...body, total_kcal: Math.round((body.items || m.items).reduce((a, i) => a + (i.kcal || 0), 0)) || null } : m); });
      saveStore(s); let found = null; Object.values(s.meals).forEach((arr) => arr.forEach((m) => { if (m.id === id) found = m; })); return found;
    }
    if (path.startsWith('/api/meals/') && method === 'DELETE') {
      const id = Number(path.split('/').pop());
      Object.keys(s.meals).forEach((k) => { s.meals[k] = s.meals[k].filter((m) => m.id !== id); }); saveStore(s); return { ok: true };
    }

    // -- recipes -- (kara liste / istenmeyen malzeme içeren tarifler GİZLENİR + uyarı)
    if (path === '/api/recipes') {
      const q = (query.q || '').toLowerCase();
      const exclude = [].concat(query.exclude || []).join(',').toLowerCase().split(',').map((x) => x.trim()).filter(Boolean);
      const blNames = s.blacklist.map((b) => b.name_tr.toLowerCase());
      const cand = RECIPES.filter((r) => !q || r.title_tr.toLowerCase().includes(q) || (r.region || '').toLowerCase().includes(q) || r.tags.some((t) => t.includes(q)));
      const items = [], hidden = [];
      cand.forEach((r) => {
        const names = r.ingredients.map((i) => i.raw_name.toLowerCase());
        const blHit = blNames.find((b) => names.some((n) => n.includes(b)));
        const exHit = exclude.find((b) => names.some((n) => n.includes(b)));
        if (blHit) hidden.push({ title_tr: r.title_tr, reason: cap(blHit), kind: 'blacklist' });
        else if (exHit) hidden.push({ title_tr: r.title_tr, reason: cap(exHit), kind: 'exclude' });
        else items.push(r);
      });
      const off = parseInt(query.offset) || 0;
      const lim = parseInt(query.limit) || 24;
      return { items: items.slice(off, off + lim), hidden, total: items.length };
    }
    if (path === '/api/recipes/cook-with') {
      const have = [].concat(query.have || []).join(',').toLowerCase().split(',').map((x) => x.trim()).filter(Boolean);
      if (!have.length) return { items: [], hidden: [] };
      const exclude = [].concat(query.exclude || []).join(',').toLowerCase().split(',').map((x) => x.trim()).filter(Boolean);
      const blNames = s.blacklist.map((b) => b.name_tr.toLowerCase());
      const items = [], hidden = [];
      RECIPES.forEach((r) => {
        const names = r.ingredients.map((i) => i.raw_name.toLowerCase());
        const blHit = blNames.find((b) => names.some((n) => n.includes(b)));
        const exHit = exclude.find((b) => names.some((n) => n.includes(b)));
        if (blHit || exHit) { hidden.push({ title_tr: r.title_tr, reason: cap(blHit || exHit), kind: blHit ? 'blacklist' : 'exclude' }); return; }
        const match = have.filter((h) => names.some((n) => n.includes(h))).length;
        if (match > 0) items.push({ ...r, match, total_have: have.length });
      });
      items.sort((a, b) => b.match - a.match);
      return { items, hidden };
    }

    // -- blacklist --
    if (path === '/api/blacklist' && method === 'GET') return s.blacklist;
    if (path === '/api/blacklist' && method === 'POST') {
      const slug = body.name.toLowerCase().replace(/\s+/g, '_').replace(/[^\w]/g, ''); const item = { canonical_id: Date.now(), slug, name_tr: body.name };
      s.blacklist = [...s.blacklist, item]; saveStore(s); return item;
    }
    if (path.startsWith('/api/blacklist/') && method === 'DELETE') {
      const id = Number(path.split('/').pop()); s.blacklist = s.blacklist.filter((b) => b.canonical_id !== id); saveStore(s); return { ok: true };
    }

    // -- profile / goal --
    if (path === '/api/profile' && method === 'GET') return s.profile;
    if (path === '/api/profile' && method === 'PUT') { s.profile = { ...s.profile, ...body }; saveStore(s); return s.profile; }
    if (path === '/api/goal' && method === 'GET') { if (!s.goal) throw new Error('Aktif hedef yok.'); return s.goal; }
    if (path === '/api/goal' && method === 'PUT') { s.goal = { ...s.goal, ...body, active: true, id: (s.goal && s.goal.id) || 1 }; saveStore(s); return s.goal; }
    // hedef planı (kilo sihirbazı) — backend: profile.py /goal/plan (UserPreference)
    if (path === '/api/goal/plan' && method === 'PUT') { s.plan = { ...s.plan, ...body }; saveStore(s); return s.plan; }
    if (path === '/api/goal/plan' && method === 'GET') return s.plan || null;

    // -- meal plans --
    if (path === '/api/meal-plans/preview') {
      const entries = []; let offset = 0;
      (body.text || '').split('\n').forEach((line) => {
        const h = line.match(/^#{1,3}\s*(?:Gün|Gun)\s*(\d+)/i);
        const li = line.match(/^\s*[-*]\s*([^:]+):\s*(.+)/);
        if (h) offset = parseInt(h[1], 10);
        else if (line.match(/^#{1,3}\s+/)) offset = entries.length ? entries[entries.length - 1].day_offset + 1 : 0;
        else if (li) { const mt = { 'kahvaltı': 'kahvalti', 'kahvalti': 'kahvalti', 'öğle': 'ogle', 'ogle': 'ogle', 'akşam': 'aksam', 'aksam': 'aksam', 'ara': 'ara', 'ara öğün': 'ara' }[li[1].trim().toLowerCase()] || 'ogle'; entries.push({ day_offset: offset, meal_type: mt, raw_text: li[2].trim() }); }
      });
      return { entries };
    }
    if (path === '/api/meal-plans/apply') {
      const prev = await mockHandle('POST', '/api/meal-plans/preview', null, body);
      const base = body.base_date || todayStr(); const created = [];
      prev.entries.forEach((e) => {
        const d = new Date(base + 'T00:00:00'); d.setDate(d.getDate() + e.day_offset); const key = d.toISOString().slice(0, 10);
        const items = ruleParse(e.raw_text); const total = Math.round(items.reduce((a, i) => a + (i.kcal || 0), 0)) || null;
        const id = Date.now() + Math.floor(Math.random() * 1000); created.push(id);
        const meal = { id, eaten_at: isoAt(key, 12, 0), meal_type: e.meal_type, raw_text: e.raw_text, total_kcal: total, photo_path: null, items };
        s.meals[key] = [...(s.meals[key] || []), meal];
      });
      saveStore(s); return { base_date: base, created_meal_ids: created, entries: prev.entries };
    }

    // -- ÖNERİ: workouts --
    if (path === '/api/workout-plan') {
      const goalType = (query && query.goal) || s.goal.goal_type || 'koru';
      const level = (query && query.level) || (s.profile.activity_level === 'sedentary' ? 'beginner' : 'intermediate');
      const dpw = (query && Number(query.days_per_week)) || (s.plan && s.plan.days_per_week) || 4;
      const td = (query && query.training_days) ? [].concat(query.training_days) : (s.plan && s.plan.training_days) || null;
      return buildPlan(goalType, level, dpw, td);
    }
    if (path === '/api/workouts') {
      const { muscle, level, equipment, equipment_type, q } = query || {};
      return EXERCISES.filter((e) => (!muscle || e.primary_muscle === muscle) && (!level || e.level === level) && (!equipment || e.equipment === equipment) && (!equipment_type || EQ_TYPE(e.equipment) === equipment_type) && (!q || e.name_tr.toLowerCase().includes(q.toLowerCase()))).map(enrich);
    }
    if (path === '/api/workout-logs' && method === 'GET') return s.workoutLogs[date] || [];
    if (path === '/api/workout-logs' && method === 'POST') {
      const ex = EXERCISES.find((e) => e.slug === body.template_slug);
      const minutes = body.minutes || 30; const met = MET[ex ? ex.category : 'kuvvet'] || 5;
      const burned = Math.round((met * 3.5 * (s.profile.weight_kg || 70) / 200) * minutes);
      const item = { id: Date.now(), template_slug: body.template_slug, name_tr: ex ? ex.name_tr : body.template_slug, sets: body.sets || null, reps: body.reps || null, minutes, kcal: burned, done: true };
      s.workoutLogs[date] = [...(s.workoutLogs[date] || []), item]; saveStore(s); return item;
    }
    if (path.startsWith('/api/workout-logs/') && method === 'DELETE') {
      const id = Number(path.split('/').pop()); Object.keys(s.workoutLogs).forEach((k) => { s.workoutLogs[k] = s.workoutLogs[k].filter((w) => w.id !== id); }); saveStore(s); return { ok: true };
    }

    throw new Error('Bilinmeyen uç nokta: ' + method + ' ' + path);
  }

  function buildQuery(q) {
    if (!q) return '';
    const parts = [];
    Object.entries(q).forEach(([k, v]) => { if (v == null || v === '') return; if (Array.isArray(v)) v.forEach((x) => parts.push(k + '=' + encodeURIComponent(x))); else parts.push(k + '=' + encodeURIComponent(v)); });
    return parts.length ? '?' + parts.join('&') : '';
  }
  async function request(method, path, { query, body } = {}) {
    const s = getSettings();
    if (s.live && s.baseUrl) {
      const res = await fetch(s.baseUrl.replace(/\/$/, '') + path + buildQuery(query), { method, headers: { 'Content-Type': 'application/json', ...(s.token ? { Authorization: 'Bearer ' + s.token } : {}) }, body: body ? JSON.stringify(body) : undefined });
      if (!res.ok) throw new Error('Sunucu hatası (' + res.status + ')');
      if (res.status === 204) return { ok: true };
      return res.json();
    }
    return mockHandle(method, path, query, body);
  }

  window.API = {
    getSettings, setSettings, todayStr, computeEnergy, ruleParse, EXERCISES: EXERCISES.map(enrich), EQ_TYPE_LABEL,
    resetDemo() { localStorage.removeItem(STORE_KEY); },
    summary: (date) => request('GET', '/api/summary', { query: { date } }),
    recommendations: (date) => request('GET', '/api/recommendations', { query: { date } }),
    meals: (date) => request('GET', '/api/meals', { query: { date } }),
    addMeal: (payload, date) => request('POST', '/api/meals', { query: { date }, body: payload }),
    addMealBarcode: (barcode, grams, meal_type, date) => request('POST', '/api/meals/by-barcode', { query: { date }, body: { barcode, grams, meal_type } }),
    addMealPhoto: (payload, date) => request('POST', '/api/meals/photo', { query: { date }, body: payload }),
    updateMeal: (id, payload) => request('PUT', '/api/meals/' + id, { body: payload }),
    deleteMeal: (id) => request('DELETE', '/api/meals/' + id),
    recipes: (q, exclude, offset, limit, live) => request('GET', '/api/recipes', { query: { q, exclude, offset, limit, live: live ? 'true' : undefined } }).then((r) => Array.isArray(r) ? { items: r, hidden: [] } : r),
    cookWith: (have, exclude) => request('GET', '/api/recipes/cook-with', { query: { have, exclude } }).then((r) => Array.isArray(r) ? { items: r, hidden: [] } : r),
    blacklist: () => request('GET', '/api/blacklist'),
    addBlacklist: (name) => request('POST', '/api/blacklist', { body: { name } }),
    deleteBlacklist: (canonicalId) => request('DELETE', '/api/blacklist/' + canonicalId),
    profile: () => request('GET', '/api/profile'),
    saveProfile: (p) => request('PUT', '/api/profile', { body: p }),
    goal: () => request('GET', '/api/goal'),
    saveGoal: (g) => request('PUT', '/api/goal', { body: g }),
    getPlan: () => request('GET', '/api/goal/plan'),
    savePlan: (p) => request('PUT', '/api/goal/plan', { body: p }),
    previewPlan: (text) => request('POST', '/api/meal-plans/preview', { body: { text } }),
    applyPlan: (text, base_date) => request('POST', '/api/meal-plans/apply', { body: { text, base_date } }),
    workouts: (q) => request('GET', '/api/workouts', { query: q || {} }),
    workoutPlan: (goal, level, daysPerWeek, trainingDays) => request('GET', '/api/workout-plan', { query: { goal, level, days_per_week: daysPerWeek, training_days: trainingDays } }),
    workoutLogs: (date) => request('GET', '/api/workout-logs', { query: { date } }),
    addWorkoutLog: (payload, date) => request('POST', '/api/workout-logs', { query: { date }, body: payload }),
    deleteWorkoutLog: (id) => request('DELETE', '/api/workout-logs/' + id),
  };
})();
