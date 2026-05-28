# Backend sözleşmesi — gkhnelbstn/fitness-calorie-app (services/api)

Frontend bunu birebir takip eder. Tüm isteklerde `Authorization: Bearer <token>`. Base: http://localhost:8000

## Profil / Hedef
- GET/PUT `/api/profile` → `{id, name, sex, birth_year, height_cm, weight_kg, activity_level, locale}`
  - sex: "erkek" | "kadin" (parser male set: erkek/male/m/e)
  - activity_level: **sedentary | light | moderate | active | very_active** (İngilizce!)
- GET/PUT `/api/goal` → `{id, goal_type, target_kcal?, target_protein_g?, active}`
  - goal_type: kilo_ver | koru | kas_yap
  - PUT goal: önceki aktif hedefi pasifleştirir.

## Enerji (services/energy.py)
- BMR Mifflin-St Jeor; TDEE = BMR × faktör (sedentary1.2/light1.375/moderate1.55/active1.725/very_active1.9)
- GOAL_DELTA: kilo_ver −500, koru 0, kas_yap +300; target band ±100
- DEFAULT_PROTEIN_PER_KG = 1.6

## Özet
- GET `/api/summary?date=YYYY-MM-DD` → `{day, intake_kcal, protein_g, carb_g, fat_g, meal_count, item_count, active_kcal?, net_kcal?}`
  - NOT: hedefler burada YOK. kcal/protein hedefi `/api/recommendations.energy`'den. carb/fat/fiber hedefi backend'de yok → client türetir (öneri).

## Öneriler
- GET `/api/recommendations?date=` → `{id, day, energy, meal_suggestions:[RecipeRead], workout, notes:[str]}`
  - energy: `{bmr,tdee,target_kcal,intake_kcal,remaining_kcal,protein_target_g,protein_intake_g,protein_remaining_g}`
  - workout: `{focus, weekly_minutes, days:[str], note}`
- POST `/api/recommendations/feedback` `{recommendation_id, action(accepted|rejected|edited), note?}`

## Yemekler
- MealRead: `{id, eaten_at(ISO datetime), meal_type, raw_text, total_kcal, items:[MealItem], photo_path?}`
- MealItem: `{raw_name, quantity?, unit?, canonical_id?, kcal?, protein_g?, carb_g?, fat_g?, confidence?}`
  - öğün adı = raw_text; makro öğün item'larının toplamı
- GET `/api/meals?date=`
- POST `/api/meals` `{raw_text?, meal_type?, items:[MealItem]}` (en az biri dolu). raw_text → LLM/kurallı parse → items
- POST `/api/meals/by-barcode` `{barcode, grams=100, meal_type?}` (Open Food Facts)
- POST `/api/meals/photo` multipart `{photo, raw_text?, meal_type?}` (foto saklanır, photo_path döner; AI tanıma yok—raw_text ile düzeltilir)
- ÖNERİ (backend'de yok, eklenecek): DELETE `/api/meals/{id}`, PUT `/api/meals/{id}`

## Tarifler
- RecipeRead: `{id, slug, title_tr, servings?, region?, total_kcal?, adaptable, ingredients:[IngredientLine], steps:[str], tags:[str], notes:[str]}`
- IngredientLine: `{raw_name, quantity?, unit?, canonical_id?, optional, status(ok|removed|substituted), substitute?}`
- GET `/api/recipes?q=&exclude=a&exclude=b` (exclude tekrarlı param)
- GET `/api/recipes/cook-with?have=&exclude=`
- Blacklist tarifleri otomatik filtreler.

## Kara liste
- BlacklistItem: `{canonical_id, slug, name_tr}`
- GET `/api/blacklist`; POST `{name}` → BlacklistItem; DELETE `/api/blacklist/{canonical_id}`

## Yemek planı
- POST `/api/meal-plans/preview` `{text}` → `{entries:[{day_offset, meal_type, raw_text}]}`
- POST `/api/meal-plans/apply` `{text, base_date?}` → `{base_date, created_meal_ids, entries}`
- Format: "# Gün 0" başlık (day_offset), "- Kahvaltı: ..." satır.
- ÖNERİ: Excel(.xlsx) → client'ta bu text formatına çevrilir, sonra preview/apply.

## Egzersiz (models var, router YOK — eklenecek)
- WorkoutTemplate: `{id, slug, name_tr, primary_muscle, level, equipment}` (free-exercise-db: level=beginner/intermediate/expert)
  - ÖNERİ ek alanlar: `equipment_type` (makine|serbest|vücut), `secondary:[muscle]`, `instructions:[str]`, `machine_howto:str?`
- ÖNERİ endpoint'ler:
  - GET `/api/workouts?muscle=&level=&equipment_type=&q=`
  - GET `/api/workout-plan?goal=&level=&days_per_week=&training_days=Pzt&training_days=Sal...`
    → `{goal_type, level, days_per_week, training_days:[], focus, weekly_minutes, warmup, structure_note, days:[{day, title, kind:'kuvvet+kardiyo', minutes, worked:{primary:[],secondary:[]}, exercises:[{slug,name_tr,equipment,equipment_type,sets,reps,rest,finisher,primary_muscle,secondary,instructions,machine_howto,alternatives_by_type:{makine:[],serbest:[],vücut:[]}}]}]}`
    - Her seans: kuvvet blok + kapanış kardiyosu (finisher=true). training_days kullanıcının seçtiği günler.
  - POST `/api/workout-logs` `{template_slug, sets?, reps?, minutes?}`; GET `?date=`; DELETE `/{id}`
- Antrenman tercihleri (gün sayısı/günler) UserPreference olarak saklanabilir (mock: goal/plan).

## Tarif filtresi (kara liste = SERT filtre)
- Kara listedeki ya da `exclude` malzemesini içeren tarifler **sonuçtan çıkarılır** (adapte edilmez).
- ÖNERİ dönüş: `{items: RecipeRead[], hidden: [{title_tr, reason, kind:'blacklist'|'exclude'}]}` — UI gizlenenleri uyarı olarak gösterir. (Backend şu an list[RecipeRead] döndürüyor; `hidden` listesi/`blocked` bayrağı eklenmeli.)

## Kimlik (prototip)
- Frontend Google + e-posta giriş kapısı (localStorage mock oturum). ÖNERİ: gerçek Google OAuth + backend oturum/JWT; `UserProfile.email` zaten var.

## Görseller
- meal.photo_path: backend upload_dir; serve `/uploads/...` (öneri statik mount).
- recipe görseli: TheMealDB adapter → raw_payload.strMealThumb olabilir (image_url alanı öneri).
