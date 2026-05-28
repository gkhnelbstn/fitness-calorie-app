// ai.jsx — Doğal dil öğün analizi.
// Backend mantığını yansıtır: LLM yalnızca NORMALİZE eder; değer yoksa kurallı parser'a düşülür.
// window.claude.complete varsa onu kullanır (prototip içi), yoksa API.ruleParse fallback.
(function () {
  const SYS = `Sen bir Türkçe beslenme asistanısın. Kullanıcının serbest metinle yazdığı öğünü
yapılandırılmış besin kalemlerine ayır. SADECE geçerli JSON dizisi döndür, başka hiçbir şey yazma.
Her kalem: {"raw_name": "...", "quantity": sayı, "unit": "adet|gram|kase|porsiyon|bardak|dilim|ml|ölçek",
"kcal": sayı, "protein_g": sayı, "carb_g": sayı, "fat_g": sayı, "fiber_g": sayı, "confidence": 0-1 arası}.
Türkiye porsiyonlarına ve yaygın yemeklere göre makul tahmin yap. Değerler yaklaşık olsun.`;

  function extractJson(text) {
    if (!text) return null;
    let t = text.trim().replace(/^```(json)?/i, '').replace(/```$/i, '').trim();
    const start = t.indexOf('['); const end = t.lastIndexOf(']');
    if (start === -1 || end === -1) return null;
    try { return JSON.parse(t.slice(start, end + 1)); } catch { return null; }
  }

  async function aiParseMeal(text) {
    const clean = (text || '').trim();
    if (!clean) return { items: [], source: 'empty' };
    if (window.claude && typeof window.claude.complete === 'function') {
      try {
        const out = await window.claude.complete(`${SYS}\n\nÖğün metni: "${clean}"\n\nJSON:`);
        const arr = extractJson(out);
        if (Array.isArray(arr) && arr.length) {
          const items = arr.map((i) => ({
            raw_name: String(i.raw_name || 'Kalem'),
            quantity: i.quantity != null ? Number(i.quantity) : null,
            unit: i.unit || null, canonical_id: null,
            kcal: Math.round(Number(i.kcal) || 0),
            protein_g: Math.round(Number(i.protein_g) || 0),
            carb_g: Math.round(Number(i.carb_g) || 0),
            fat_g: Math.round(Number(i.fat_g) || 0),
            fiber_g: Math.round(Number(i.fiber_g) || 0),
            confidence: i.confidence != null ? Number(i.confidence) : 0.8,
          }));
          return { items, source: 'ai' };
        }
      } catch (e) { /* sessizce fallback */ }
    }
    // Fallback — kurallı parser
    await new Promise((r) => setTimeout(r, 450));
    return { items: window.API.ruleParse(clean), source: 'rule' };
  }

  window.aiParseMeal = aiParseMeal;
  window.aiAvailable = !!(window.claude && typeof window.claude.complete === 'function');
})();
