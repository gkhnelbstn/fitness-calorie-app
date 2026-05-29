"""Egzersiz kataloğu + antrenman planı kurgusu (frontend mock.jsx portu).

Saf veri + mantık (DB yok). Routers bunu kullanır. Türkçe kas/ekipman değerleri
frontend kas haritası ve filtreleriyle birebir uyumlu.
"""

from __future__ import annotations

from typing import Any

WHO_NOTE = "Haftada en az 150 dk orta veya 75 dk yüksek şiddet + 2 gün kuvvet (WHO)."
MET = {"kuvvet": 5, "kardiyo": 8}

# (slug, name_tr, primary_muscle, level, equipment, category, secondary)
EXERCISES: list[dict[str, Any]] = [
    {
        "id": 1,
        "slug": "bench-press",
        "name_tr": "Bench Press",
        "primary_muscle": "gogus",
        "level": "intermediate",
        "equipment": "halter",
        "category": "kuvvet",
        "secondary": ["triceps", "omuz"],
    },
    {
        "id": 2,
        "slug": "incline-dumbbell-press",
        "name_tr": "Eğimli Dambıl Press",
        "primary_muscle": "gogus",
        "level": "intermediate",
        "equipment": "dambıl",
        "category": "kuvvet",
        "secondary": ["omuz"],
    },
    {
        "id": 3,
        "slug": "pull-up",
        "name_tr": "Barfiks",
        "primary_muscle": "sirt",
        "level": "expert",
        "equipment": "vücut ağırlığı",
        "category": "kuvvet",
        "secondary": ["biceps"],
    },
    {
        "id": 4,
        "slug": "lat-pulldown",
        "name_tr": "Lat Çekiş",
        "primary_muscle": "sirt",
        "level": "beginner",
        "equipment": "makine",
        "category": "kuvvet",
        "secondary": ["biceps"],
    },
    {
        "id": 5,
        "slug": "overhead-press",
        "name_tr": "Omuz Press",
        "primary_muscle": "omuz",
        "level": "intermediate",
        "equipment": "halter",
        "category": "kuvvet",
        "secondary": ["triceps"],
    },
    {
        "id": 6,
        "slug": "squat",
        "name_tr": "Squat",
        "primary_muscle": "bacak",
        "level": "intermediate",
        "equipment": "halter",
        "category": "kuvvet",
        "secondary": ["kalca"],
    },
    {
        "id": 7,
        "slug": "romanian-deadlift",
        "name_tr": "Romanian Deadlift",
        "primary_muscle": "bacak",
        "level": "intermediate",
        "equipment": "halter",
        "category": "kuvvet",
        "secondary": ["sirt", "kalca"],
    },
    {
        "id": 8,
        "slug": "plank",
        "name_tr": "Plank",
        "primary_muscle": "karin",
        "level": "beginner",
        "equipment": "vücut ağırlığı",
        "category": "kuvvet",
        "secondary": ["bel"],
    },
    {
        "id": 9,
        "slug": "bicycle-crunch",
        "name_tr": "Bisiklet Mekiği",
        "primary_muscle": "karin",
        "level": "beginner",
        "equipment": "vücut ağırlığı",
        "category": "kuvvet",
        "secondary": [],
    },
    {
        "id": 10,
        "slug": "treadmill-run",
        "name_tr": "Koşu Bandı",
        "primary_muscle": "kardiyo",
        "level": "beginner",
        "equipment": "makine",
        "category": "kardiyo",
        "secondary": [],
    },
    {
        "id": 11,
        "slug": "hiit-intervals",
        "name_tr": "HIIT İnterval",
        "primary_muscle": "kardiyo",
        "level": "intermediate",
        "equipment": "vücut ağırlığı",
        "category": "kardiyo",
        "secondary": [],
    },
    {
        "id": 12,
        "slug": "walking",
        "name_tr": "Tempolu Yürüyüş",
        "primary_muscle": "kardiyo",
        "level": "beginner",
        "equipment": "yok",
        "category": "kardiyo",
        "secondary": [],
    },
    {
        "id": 13,
        "slug": "dumbbell-curl",
        "name_tr": "Dambıl Biceps Curl",
        "primary_muscle": "kol",
        "level": "beginner",
        "equipment": "dambıl",
        "category": "kuvvet",
        "secondary": [],
    },
    {
        "id": 14,
        "slug": "tricep-pushdown",
        "name_tr": "Triceps Pushdown",
        "primary_muscle": "kol",
        "level": "beginner",
        "equipment": "makine",
        "category": "kuvvet",
        "secondary": [],
    },
    {
        "id": 15,
        "slug": "leg-press",
        "name_tr": "Leg Press",
        "primary_muscle": "bacak",
        "level": "beginner",
        "equipment": "makine",
        "category": "kuvvet",
        "secondary": ["kalca"],
    },
    {
        "id": 16,
        "slug": "dips",
        "name_tr": "Dips (Paralel)",
        "primary_muscle": "gogus",
        "level": "intermediate",
        "equipment": "vücut ağırlığı",
        "category": "kuvvet",
        "secondary": ["kol", "omuz"],
    },
    {
        "id": 17,
        "slug": "dumbbell-shoulder-press",
        "name_tr": "Dambıl Omuz Press",
        "primary_muscle": "omuz",
        "level": "beginner",
        "equipment": "dambıl",
        "category": "kuvvet",
        "secondary": ["kol"],
    },
    {
        "id": 18,
        "slug": "leg-curl",
        "name_tr": "Leg Curl",
        "primary_muscle": "bacak",
        "level": "beginner",
        "equipment": "makine",
        "category": "kuvvet",
        "secondary": ["kalca"],
    },
    {
        "id": 19,
        "slug": "seated-row",
        "name_tr": "Oturarak Kürek",
        "primary_muscle": "sirt",
        "level": "beginner",
        "equipment": "makine",
        "category": "kuvvet",
        "secondary": ["kol"],
    },
    {
        "id": 20,
        "slug": "chest-fly",
        "name_tr": "Pec Deck (Fly)",
        "primary_muscle": "gogus",
        "level": "beginner",
        "equipment": "makine",
        "category": "kuvvet",
        "secondary": ["omuz"],
    },
    {
        "id": 21,
        "slug": "hip-thrust",
        "name_tr": "Hip Thrust",
        "primary_muscle": "kalca",
        "level": "intermediate",
        "equipment": "halter",
        "category": "kuvvet",
        "secondary": ["bacak"],
    },
    {
        "id": 22,
        "slug": "rowing-machine",
        "name_tr": "Kürek Makinesi",
        "primary_muscle": "kardiyo",
        "level": "beginner",
        "equipment": "makine",
        "category": "kardiyo",
        "secondary": ["sirt"],
    },
    {
        "id": 23,
        "slug": "jump-rope",
        "name_tr": "İp Atlama",
        "primary_muscle": "kardiyo",
        "level": "beginner",
        "equipment": "yok",
        "category": "kardiyo",
        "secondary": ["bacak"],
    },
    {
        "id": 24,
        "slug": "goblet-squat",
        "name_tr": "Goblet Squat",
        "primary_muscle": "bacak",
        "level": "beginner",
        "equipment": "dambıl",
        "category": "kuvvet",
        "secondary": ["kalca"],
    },
]

EQ_TYPE_LABEL = {"makine": "Makine", "serbest": "Serbest ağırlık", "vücut": "Vücut ağırlığı"}


def eq_type(eq: str) -> str:
    if "makine" in eq:
        return "makine"
    if "halter" in eq or "dambıl" in eq:
        return "serbest"
    return "vücut"


INSTR: dict[str, list[str]] = {
    "bench-press": [
        "Sırt üstü uzan, gözler bar hizasında.",
        "Kavrama omuzdan biraz geniş, bilekler dik.",
        "Barı göğse kontrollü indir, kürek kemiklerini sık, patlayıcı it.",
    ],
    "incline-dumbbell-press": [
        "Sehpayı 30-45° eğ.",
        "Dambılları göğüs üst hizasına indir.",
        "Dirsekleri 45° açıyla tut, yukarıda sıkıştır.",
    ],
    "overhead-press": [
        "Bar omuz önünde, karın sıkı.",
        "Başın üzerine dik it, kaburgaları açma.",
        "Kontrollü indir.",
    ],
    "pull-up": [
        "Bara omuzdan geniş asıl.",
        "Kürekleri aşağı-geri çekerek çeneyi barın üstüne taşı.",
        "Kontrollü in, tam aç.",
    ],
    "dumbbell-curl": [
        "Dirsekler gövdeye sabit.",
        "Dambılı sıkışana kadar kaldır, sallanma.",
        "Negatifi yavaş indir.",
    ],
    "squat": [
        "Bar üst sırtta, ayaklar omuz genişliği.",
        "Kalçayı geri-aşağı, dizler parmak yönünde.",
        "Uyluk paralelin altına in, topuktan it.",
    ],
    "romanian-deadlift": [
        "Hafif diz bükük, bar bacağa yakın.",
        "Kalçayı geri it, sırt nötr.",
        "Hamstringde gerilim hissedince yukarı kalk.",
    ],
    "hip-thrust": [
        "Sırt üst kısmı bench’e dayalı, bar kalçada.",
        "Topuktan iterek kalçayı yukarı kilitle.",
        "Üstte gluteyi 1 sn sık.",
    ],
    "plank": [
        "Dirsekler omuz altında.",
        "Gövde baştan topuğa düz, karın+kalça sıkı.",
        "Beli çökertme.",
    ],
    "bicycle-crunch": [
        "Sırt üstü, eller şakakta.",
        "Karşı dirsek-diz buluştur, dönüşü karından yap.",
        "Kontrollü ve yavaş.",
    ],
    "dips": [
        "Paralel barda dirsekleri 90°ye bük.",
        "Hafif öne eğil (göğüs) ya da dik dur (triceps).",
        "Patlayıcı yukarı it.",
    ],
    "goblet-squat": ["Dambılı göğüs önünde tut.", "Dik gövde ile çömel.", "Topuktan kalk."],
    "jump-rope": ["Bilekten çevir, sıçramalar kısa.", "Ayak ucunda kal."],
    "walking": ["Tempolu, kol salınımı serbest.", "Hafif nefes nefese kalacak hızda."],
    "hiit-intervals": ["30 sn maksimal efor + 30 sn dinlen.", "6-10 tur tekrarla."],
}

MACHINE_HOWTO: dict[str, str] = {
    "lat-pulldown": "Koltuğu otur, diz pedini uyluklara sıkıştır. Barı omuzdan geniş kavra; gövdeyi hafif geriye yaslayıp barı göğüs üstüne, dirsekleri yanlara çekerek indir. Kontrollü olarak yukarı bırak, kollar tam açılsın.",
    "leg-press": "Sırtını ve kalçanı mindere tam yasla. Ayaklar platformda omuz genişliğinde, ortada. Emniyet kollarını aç, ağırlığı dizler ~90° olana dek indir; topuktan iterek kalk ama dizleri tam kilitleme.",
    "leg-curl": "Yüzüstü/oturarak makineye yerleş; ped aşil üstüne gelsin. Topukları kalçaya doğru kıvırarak hamstringi sık, kontrollü geri bırak. Beli kaldırma.",
    "seated-row": "Göğsü pede daya, dizler hafif bükük. Tutamağı çek; kürekleri geri-aşağı sıkıştır, dirsekleri gövdeye yakın tut. Kontrollü uzat, omuzları öne bırak.",
    "chest-fly": "Koltuğu kollar omuz hizasında olacak şekilde ayarla. Dirsekler hafif bükük; kolları önde kavis çizerek birleştir, göğsü sıkıştır. Yavaşça aç.",
    "tricep-pushdown": "Makaraya yüksek tut. Dirsekleri gövdeye sabitle; barı/ipi aşağı, kollar tam düzelene dek it. Sadece ön kol hareket etsin, kontrollü geri bırak.",
    "rowing-machine": "Ayakları kayışa sabitle. Sıra: bacakla it → gövdeyi hafif geri yasla → kolla çek. Geri dönüşte ters sıra. Sırtı yuvarlama.",
    "treadmill-run": "Hızı kademeli artır, gerekiyorsa %1-2 eğim ver. Bandın ortasında, dik gövdeyle koş; tutamağa asılma. Acil durdurma klipsini tak.",
}

_BY_SLUG = {e["slug"]: e for e in EXERCISES}


def _default_instr(e: dict) -> list[str]:
    return [
        f"{e['name_tr']} hareketini kontrollü ve tam hareket açıklığıyla yap.",
        "Nefesi efor anında ver, sırtı nötr tut.",
    ]


def enrich(e: dict) -> dict[str, Any]:
    return {
        **e,
        "equipment_type": eq_type(e["equipment"]),
        "instructions": INSTR.get(e["slug"], _default_instr(e)),
        "machine_howto": MACHINE_HOWTO.get(e["slug"]),
    }


def filter_exercises(
    *,
    muscle: str | None = None,
    level: str | None = None,
    equipment: str | None = None,
    equipment_type: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    out = []
    for e in EXERCISES:
        if muscle and e["primary_muscle"] != muscle:
            continue
        if level and e["level"] != level:
            continue
        if equipment and e["equipment"] != equipment:
            continue
        if equipment_type and eq_type(e["equipment"]) != equipment_type:
            continue
        if q and q.lower() not in e["name_tr"].lower():
            continue
        out.append(enrich(e))
    return out


def exercise_category(slug: str) -> str:
    e = _BY_SLUG.get(slug)
    return e["category"] if e else "kuvvet"


def _alts_by_type(slug: str) -> dict[str, list[dict]]:
    base = _BY_SLUG.get(slug)
    if not base:
        return {}
    g: dict[str, list[dict]] = {}
    for e in EXERCISES:
        if e["slug"] == slug or e["primary_muscle"] != base["primary_muscle"]:
            continue
        t = eq_type(e["equipment"])
        g.setdefault(t, []).append(
            {"slug": e["slug"], "name_tr": e["name_tr"], "equipment": e["equipment"]}
        )
    return g


def _pick_row_alt(slug: str) -> dict | None:
    base = _BY_SLUG.get(slug)
    if not base:
        return None
    g = _alts_by_type(slug)
    bt = eq_type(base["equipment"])
    order = (
        ["serbest", "vücut", "makine"]
        if bt == "makine"
        else ["makine", "vücut", "serbest"]
        if bt == "serbest"
        else ["makine", "serbest", "vücut"]
    )
    for t in order:
        if g.get(t):
            return {**g[t][0], "equipment_type": t}
    return None


STRENGTH_POOLS: dict[str, list[dict]] = {
    "kas_yap": [
        {
            "title": "İtiş — Göğüs / Omuz / Triceps",
            "ex": [
                {"slug": "bench-press", "sets": 4, "reps": "8-10", "rest": 90},
                {"slug": "incline-dumbbell-press", "sets": 3, "reps": "10-12", "rest": 75},
                {"slug": "overhead-press", "sets": 3, "reps": "8-10", "rest": 90},
                {"slug": "tricep-pushdown", "sets": 3, "reps": "12-15", "rest": 60},
            ],
        },
        {
            "title": "Çekiş — Sırt / Biceps",
            "ex": [
                {"slug": "pull-up", "sets": 4, "reps": "6-10", "rest": 90},
                {"slug": "seated-row", "sets": 3, "reps": "10-12", "rest": 75},
                {"slug": "lat-pulldown", "sets": 3, "reps": "10-12", "rest": 75},
                {"slug": "dumbbell-curl", "sets": 3, "reps": "12", "rest": 60},
            ],
        },
        {
            "title": "Bacak / Kalça",
            "ex": [
                {"slug": "squat", "sets": 4, "reps": "6-8", "rest": 120},
                {"slug": "romanian-deadlift", "sets": 3, "reps": "8-10", "rest": 100},
                {"slug": "leg-press", "sets": 3, "reps": "10-12", "rest": 90},
                {"slug": "hip-thrust", "sets": 3, "reps": "10-12", "rest": 75},
            ],
        },
        {
            "title": "Üst vücut",
            "ex": [
                {"slug": "incline-dumbbell-press", "sets": 3, "reps": "10", "rest": 75},
                {"slug": "seated-row", "sets": 3, "reps": "10", "rest": 75},
                {"slug": "dumbbell-shoulder-press", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "dumbbell-curl", "sets": 3, "reps": "12", "rest": 45},
            ],
        },
        {
            "title": "Tam vücut + Karın",
            "ex": [
                {"slug": "goblet-squat", "sets": 3, "reps": "12", "rest": 75},
                {"slug": "bench-press", "sets": 3, "reps": "10", "rest": 75},
                {"slug": "lat-pulldown", "sets": 3, "reps": "12", "rest": 75},
                {"slug": "plank", "sets": 3, "reps": "45 sn", "rest": 45},
                {"slug": "bicycle-crunch", "sets": 3, "reps": "20", "rest": 40},
            ],
        },
    ],
    "kilo_ver": [
        {
            "title": "Tam vücut A",
            "ex": [
                {"slug": "goblet-squat", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "bench-press", "sets": 3, "reps": "10", "rest": 60},
                {"slug": "lat-pulldown", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "plank", "sets": 3, "reps": "40 sn", "rest": 40},
            ],
        },
        {
            "title": "Tam vücut B",
            "ex": [
                {"slug": "leg-press", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "dumbbell-shoulder-press", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "seated-row", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "bicycle-crunch", "sets": 3, "reps": "20", "rest": 40},
            ],
        },
        {
            "title": "Alt vücut + Kalça",
            "ex": [
                {"slug": "squat", "sets": 3, "reps": "10", "rest": 90},
                {"slug": "romanian-deadlift", "sets": 3, "reps": "10", "rest": 75},
                {"slug": "hip-thrust", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "leg-curl", "sets": 3, "reps": "12", "rest": 60},
            ],
        },
        {
            "title": "Üst vücut",
            "ex": [
                {"slug": "incline-dumbbell-press", "sets": 3, "reps": "10", "rest": 60},
                {"slug": "lat-pulldown", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "overhead-press", "sets": 3, "reps": "10", "rest": 60},
                {"slug": "tricep-pushdown", "sets": 3, "reps": "12", "rest": 45},
            ],
        },
    ],
    "koru": [
        {
            "title": "Tam vücut A",
            "ex": [
                {"slug": "squat", "sets": 3, "reps": "10", "rest": 90},
                {"slug": "bench-press", "sets": 3, "reps": "10", "rest": 75},
                {"slug": "lat-pulldown", "sets": 3, "reps": "12", "rest": 75},
                {"slug": "plank", "sets": 3, "reps": "40 sn", "rest": 40},
            ],
        },
        {
            "title": "Tam vücut B",
            "ex": [
                {"slug": "leg-press", "sets": 3, "reps": "12", "rest": 75},
                {"slug": "dumbbell-shoulder-press", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "seated-row", "sets": 3, "reps": "12", "rest": 60},
                {"slug": "dumbbell-curl", "sets": 3, "reps": "12", "rest": 45},
            ],
        },
        {
            "title": "Tam vücut C",
            "ex": [
                {"slug": "romanian-deadlift", "sets": 3, "reps": "10", "rest": 75},
                {"slug": "dips", "sets": 3, "reps": "10", "rest": 60},
                {"slug": "pull-up", "sets": 3, "reps": "8", "rest": 75},
                {"slug": "bicycle-crunch", "sets": 3, "reps": "20", "rest": 40},
            ],
        },
    ],
}
CARDIO_FINISH = {"kilo_ver": "20 dk", "kas_yap": "10 dk", "koru": "15 dk"}
DEFAULT_DAYS = {
    2: ["Pzt", "Per"],
    3: ["Pzt", "Çar", "Cum"],
    4: ["Pzt", "Sal", "Per", "Cmt"],
    5: ["Pzt", "Sal", "Çar", "Cum", "Cmt"],
    6: ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt"],
}
FOCUS = {"kas_yap": "kuvvet (split)", "kilo_ver": "kardiyo + kuvvet", "koru": "karışık"}


def _resolve_exercise(e: dict, level: str, is_finisher: bool) -> dict[str, Any]:
    base = _BY_SLUG.get(e["slug"])
    enriched = (
        enrich(base)
        if base
        else {
            "name_tr": e["slug"],
            "equipment": "-",
            "category": "kuvvet",
            "primary_muscle": None,
            "secondary": [],
            "instructions": [],
            "machine_howto": None,
        }
    )
    sets = e["sets"]
    if enriched["category"] == "kuvvet" and not is_finisher:
        if level == "beginner":
            sets = max(2, e["sets"] - 1)
        elif level == "expert":
            sets = e["sets"] + 1
    return {
        "slug": e["slug"],
        "name_tr": enriched["name_tr"],
        "equipment": enriched["equipment"],
        "equipment_type": eq_type(enriched["equipment"]) if base else "vücut",
        "category": enriched["category"],
        "primary_muscle": enriched.get("primary_muscle"),
        "secondary": enriched.get("secondary", []),
        "instructions": enriched.get("instructions", []),
        "machine_howto": enriched.get("machine_howto"),
        "sets": sets,
        "reps": e["reps"],
        "rest": e["rest"],
        "finisher": is_finisher,
        "alternative": _pick_row_alt(e["slug"]),
        "alternatives_by_type": _alts_by_type(e["slug"]),
    }


def _day_worked(exercises: list[dict]) -> dict[str, list[str]]:
    prim: list[str] = []
    sec: list[str] = []
    for x in exercises:
        if x.get("primary_muscle") and x["primary_muscle"] not in prim:
            prim.append(x["primary_muscle"])
        for m in x.get("secondary", []):
            if m not in sec:
                sec.append(m)
    return {"primary": prim, "secondary": [m for m in sec if m not in prim]}


def build_plan(
    goal_type: str,
    level: str,
    days_per_week: int,
    training_days: list[str] | None,
) -> dict[str, Any]:
    pool = STRENGTH_POOLS.get(goal_type, STRENGTH_POOLS["koru"])
    n = max(1, min(6, days_per_week or 4))
    td = (
        training_days
        if (training_days and len(training_days) == n)
        else DEFAULT_DAYS.get(n, DEFAULT_DAYS[4])
    )
    finish_reps = CARDIO_FINISH.get(goal_type, "15 dk")
    days = []
    for i in range(n):
        sess = pool[i % len(pool)]
        strength = [_resolve_exercise(e, level, False) for e in sess["ex"]]
        cardio = _resolve_exercise(
            {"slug": "treadmill-run", "sets": 1, "reps": finish_reps, "rest": 0}, level, True
        )
        exercises = [*strength, cardio]
        s_min = round(sum(x["sets"] * 2.2 for x in strength)) + 8
        try:
            c_min = int(finish_reps.split()[0])
        except (ValueError, IndexError):
            c_min = 12
        days.append(
            {
                "day": td[i] if i < len(td) else DEFAULT_DAYS[4][i % 4],
                "title": sess["title"],
                "kind": "kuvvet+kardiyo",
                "minutes": s_min + c_min,
                "exercises": exercises,
                "worked": _day_worked(strength),
            }
        )
    weekly = sum(d["minutes"] for d in days)
    return {
        "goal_type": goal_type,
        "level": level,
        "days_per_week": n,
        "training_days": td,
        "focus": FOCUS.get(goal_type, "karışık"),
        "weekly_minutes": weekly,
        "warmup": "5-10 dk hafif kardiyo + dinamik esneme ile ısın.",
        "structure_note": "Her seans: önce ağırlık antrenmanı, sonra kapanış kardiyosu.",
        "days": days,
        "note": WHO_NOTE,
    }


def burned_kcal(slug: str, minutes: int, weight_kg: float) -> int:
    met = MET.get(exercise_category(slug), 5)
    return round(met * 3.5 * weight_kg / 200 * minutes)
