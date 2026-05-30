// modals.jsx — Öğün ekle (AI) · Öğün düzenle · Hedef sihirbazı · Yemek planı (Excel) · Ayarlar
const { useState: useStateMo, useEffect: useEffMo } = React;

const MEAL_TYPES = [
  { value: 'kahvalti', label: 'Kahvaltı' }, { value: 'ogle', label: 'Öğle' },
  { value: 'ara', label: 'Ara öğün' }, { value: 'aksam', label: 'Akşam' },
];

function MealTypePicker({ value, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      <button onClick={() => onChange('')} className={cx('fr rounded-full px-3.5 py-2 text-sm font-semibold bordered transition', !value ? 'shadow-soft' : 'surface-2 text-muted')} style={!value ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>Otomatik</button>
      {MEAL_TYPES.map((m) => <button key={m.value} onClick={() => onChange(m.value)} className={cx('fr rounded-full px-3.5 py-2 text-sm font-semibold bordered transition', value === m.value ? 'shadow-soft' : 'surface-2 text-muted')} style={value === m.value ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>{m.label}</button>)}
    </div>
  );
}

// Öğün kalem editörü — Add (AI sonucu) + Edit ortak
function ItemEditor({ items, setItems }) {
  const upd = (i, k, v) => setItems(items.map((it, idx) => idx === i ? { ...it, [k]: k === 'raw_name' || k === 'unit' ? v : (v === '' ? 0 : +v) } : it));
  const rm = (i) => setItems(items.filter((_, idx) => idx !== i));
  const add = () => setItems([...items, { raw_name: '', quantity: 1, unit: 'porsiyon', kcal: 0, protein_g: 0, carb_g: 0, fat_g: 0, fiber_g: 0, confidence: 1 }]);
  const tot = items.reduce((a, it) => ({ kcal: a.kcal + (+it.kcal || 0), p: a.p + (+it.protein_g || 0), c: a.c + (+it.carb_g || 0), f: a.f + (+it.fat_g || 0) }), { kcal: 0, p: 0, c: 0, f: 0 });
  return (
    <div className="flex flex-col gap-2">
      {items.map((it, i) => (
        <div key={i} className="rounded-xl bordered surface-2 p-2.5 flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <input value={it.raw_name} onChange={(e) => upd(i, 'raw_name', e.target.value)} placeholder="Kalem adı" className="fr flex-1 bg-transparent font-semibold text-sm outline-none min-w-0" />
            {it.confidence != null && it.confidence < 0.7 && <Badge tone="amber" className="shrink-0">tahmini</Badge>}
            <button onClick={() => rm(i)} className="fr text-muted hover:text-[var(--c-fat)] shrink-0"><Icon name="x" size={15} /></button>
          </div>
          <div className="grid grid-cols-4 gap-1.5">
            {[['kcal', 'kcal', 'var(--c-kcal)'], ['protein_g', 'P', 'var(--c-prot)'], ['carb_g', 'K', 'var(--c-carb)'], ['fat_g', 'Y', 'var(--c-fat)']].map(([k, lab, col]) => (
              <label key={k} className="flex flex-col gap-0.5">
                <span className="text-[10px] font-semibold" style={{ color: col }}>{lab}</span>
                <input type="number" value={it[k] ?? 0} onChange={(e) => upd(i, k, e.target.value)} className="fr w-full rounded-lg surface px-2 h-8 text-sm tnum outline-none bordered" />
              </label>
            ))}
          </div>
        </div>
      ))}
      <button onClick={add} className="fr self-start text-sm font-semibold inline-flex items-center gap-1.5" style={{ color: 'var(--accent-text)' }}><Icon name="plus" size={15} />Kalem ekle</button>
      <div className="flex items-center justify-between rounded-xl px-3.5 py-2.5 mt-1" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}>
        <span className="text-sm font-semibold">Toplam</span>
        <span className="text-sm font-display font-semibold tnum">{Math.round(tot.kcal)} kcal · P{Math.round(tot.p)} K{Math.round(tot.c)} Y{Math.round(tot.f)}</span>
      </div>
    </div>
  );
}

// ---------------- ÖĞÜN EKLE ----------------
function AddMealModal({ open, onClose, date, onAdded, toast, methodStyle = 'tabs' }) {
  const [tab, setTab] = useStateMo('dogal');
  const [mealType, setMealType] = useStateMo('');
  const [nl, setNl] = useStateMo('');
  const [items, setItems] = useStateMo(null);
  const [analyzing, setAnalyzing] = useStateMo(false);
  const [source, setSource] = useStateMo(null);
  const [barcode, setBarcode] = useStateMo('');
  const [grams, setGrams] = useStateMo('');
  const [photoName, setPhotoName] = useStateMo('');
  const [photoDesc, setPhotoDesc] = useStateMo('');
  const [busy, setBusy] = useStateMo(false);

  const reset = () => { setTab('dogal'); setMealType(''); setNl(''); setItems(null); setSource(null); setBarcode(''); setGrams(''); setPhotoName(''); setPhotoDesc(''); };
  const close = () => { reset(); onClose(); };

  const analyze = async () => { if (nl.trim().length < 2) return; setAnalyzing(true); try { const r = await aiParseMeal(nl); setItems(r.items); setSource(r.source); } finally { setAnalyzing(false); } };

  const submit = async () => {
    setBusy(true);
    try {
      let meal;
      if (tab === 'dogal') meal = await API.addMeal({ raw_text: nl, meal_type: mealType || undefined, items }, date);
      else if (tab === 'barkod') meal = await API.addMealBarcode(barcode, grams || 100, mealType || undefined, date);
      else meal = await API.addMealPhoto({ raw_text: photoDesc, meal_type: mealType || undefined }, date);
      toast(`Eklendi: ${Math.round(meal.total_kcal || 0)} kcal`); onAdded(meal); close();
    } catch (e) { toast('Eklenemedi: ' + e.message, 'error'); } finally { setBusy(false); }
  };

  const canSubmit = tab === 'dogal' ? (items && items.length) : tab === 'barkod' ? barcode.trim().length > 3 : !!photoName;
  const aiBadge = window.aiAvailable ? { l: 'AI', tone: 'accent' } : { l: 'kurallı', tone: 'neutral' };

  return (
    <Modal open={open} onClose={close} title="Öğün ekle" size="md"
      footer={<><Button variant="ghost" onClick={close}>Vazgeç</Button><Button icon="plus" onClick={submit} disabled={!canSubmit || busy}>{busy ? 'Ekleniyor…' : 'Öğünü ekle'}</Button></>}>
      <div className="flex flex-col gap-4 pb-2">
        {methodStyle === 'tiles' ? (
          <div className="grid grid-cols-3 gap-2.5">
            {[{ value: 'dogal', label: 'Doğal dil', icon: 'sparkles', desc: 'AI analiz' }, { value: 'barkod', label: 'Barkod', icon: 'barcode', desc: 'Okut + gram' }, { value: 'foto', label: 'Fotoğraf', icon: 'camera', desc: 'Tabağı çek' }].map((m) => (
              <button key={m.value} onClick={() => setTab(m.value)} className={cx('fr flex flex-col items-center gap-1.5 rounded-2xl bordered px-2 py-4 transition', tab === m.value ? 'shadow-soft' : 'surface-2 text-muted hover:text-[var(--text)]')} style={tab === m.value ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>
                <Icon name={m.icon} size={24} /><span className="font-display font-semibold text-sm">{m.label}</span><span className="text-[11px] opacity-80">{m.desc}</span>
              </button>
            ))}
          </div>
        ) : <Segmented value={tab} onChange={setTab} options={[{ value: 'dogal', label: 'Doğal dil', icon: 'sparkles' }, { value: 'barkod', label: 'Barkod', icon: 'barcode' }, { value: 'foto', label: 'Fotoğraf', icon: 'camera' }]} />}

        {tab === 'dogal' && (
          <div className="anim-fade flex flex-col gap-3">
            <Field label="Ne yedin?" hint="Serbestçe yaz; yapay zekâ kalemlere ve makrolara ayırsın.">
              <Textarea rows={3} value={nl} onChange={(e) => { setNl(e.target.value); setItems(null); }} placeholder="örn. 1 kase pilav, 1 ayran, 200g ızgara tavuk" autoFocus />
            </Field>
            {!items && (
              <div className="flex items-center gap-2 flex-wrap">
                <Button variant="soft" icon="sparkles" onClick={analyze} disabled={nl.trim().length < 2 || analyzing}>{analyzing ? 'Analiz ediliyor…' : 'AI ile analiz et'}</Button>
                {['1 kase pilav, 1 ayran', '2 yumurta menemen', 'mercimek çorbası, 2 dilim ekmek'].map((s) => <button key={s} onClick={() => { setNl(s); setItems(null); }} className="fr text-xs rounded-full surface-2 bordered px-3 py-1.5 text-muted hover:text-[var(--text)]">{s}</button>)}
              </div>
            )}
            {analyzing && <div className="flex flex-col gap-2">{[0, 1].map((i) => <Skel key={i} style={{ height: 84, borderRadius: 12 }} />)}</div>}
            {items && (
              <div className="anim-fade flex flex-col gap-2">
                <div className="flex items-center gap-2 text-sm"><Badge tone={aiBadge.tone}><Icon name="sparkles" size={12} />{source === 'ai' ? 'AI analizi' : 'Kurallı analiz'}</Badge><span className="text-muted text-xs">Değerleri düzenleyebilirsin</span><button onClick={() => setItems(null)} className="fr ml-auto text-xs font-semibold text-muted hover:text-[var(--text)]">Yeniden analiz</button></div>
                <ItemEditor items={items} setItems={setItems} />
              </div>
            )}
          </div>
        )}

        {tab === 'barkod' && (
          <div className="anim-fade grid grid-cols-3 gap-3">
            <Field label="Barkod no" className="col-span-2"><div className="relative"><span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted"><Icon name="scan" size={18} /></span><Input value={barcode} onChange={(e) => setBarcode(e.target.value)} placeholder="869…" className="pl-11" inputMode="numeric" autoFocus /></div></Field>
            <Field label="Miktar (g)"><Input type="number" value={grams} onChange={(e) => setGrams(e.target.value)} placeholder="100" /></Field>
            <p className="col-span-3 flex items-center gap-1.5 text-xs text-muted"><Icon name="info" size={13} />Besin değeri Open Food Facts'ten çekilir.</p>
          </div>
        )}

        {tab === 'foto' && (
          <div className="anim-fade flex flex-col gap-3">
            <label className="fr cursor-pointer rounded-2xl bordered surface-2 border-dashed flex flex-col items-center justify-center gap-2 py-8 hover:bg-[var(--surface)] transition" style={{ borderWidth: 2 }}>
              <input type="file" accept="image/*" className="hidden" onChange={(e) => setPhotoName(e.target.files?.[0]?.name || '')} />
              {photoName ? <><span className="grid place-items-center h-12 w-12 rounded-xl" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}><Icon name="check" size={22} /></span><span className="font-semibold text-sm">{photoName}</span><span className="text-xs text-muted">Değiştirmek için tıkla</span></>
                : <><span className="grid place-items-center h-12 w-12 rounded-xl surface text-muted"><Icon name="camera" size={22} /></span><span className="font-semibold text-sm">Fotoğraf yükle</span><span className="text-xs text-muted">Tabağının fotoğrafını sürükle ya da seç</span></>}
            </label>
            <Field label="Açıklama (opsiyonel)" hint="Ne olduğunu yazarsan değerler daha doğru tahmin edilir."><Input value={photoDesc} onChange={(e) => setPhotoDesc(e.target.value)} placeholder="örn. tavuklu salata, az yağlı" /></Field>
          </div>
        )}

        <Field label="Öğün tipi (opsiyonel)"><MealTypePicker value={mealType} onChange={setMealType} /></Field>
        <p className="flex items-center gap-1.5 text-xs text-muted"><Icon name="info" size={13} />Değerler yaklaşıktır, tıbbi tavsiye değildir.</p>
      </div>
    </Modal>
  );
}
window.AddMealModal = AddMealModal;

// ---------------- ÖĞÜN DÜZENLE ----------------
function EditMealModal({ open, onClose, meal, onSaved, toast }) {
  const [items, setItems] = useStateMo([]);
  const [mealType, setMealType] = useStateMo('');
  const [busy, setBusy] = useStateMo(false);
  useEffMo(() => { if (open && meal) { setItems(meal.items || []); setMealType(meal.meal_type || ''); } }, [open, meal]);
  if (!meal) return null;
  const save = async () => { setBusy(true); try { await API.updateMeal(meal.id, { items, meal_type: mealType || meal.meal_type, raw_text: meal.raw_text }); toast('Öğün güncellendi'); onSaved(); onClose(); } catch (e) { toast('Güncellenemedi', 'error'); } finally { setBusy(false); } };
  return (
    <Modal open={open} onClose={onClose} title="Öğünü düzenle" size="md" footer={<><Button variant="ghost" onClick={onClose}>Vazgeç</Button><Button icon="check" onClick={save} disabled={busy}>{busy ? 'Kaydediliyor…' : 'Kaydet'}</Button></>}>
      <div className="flex flex-col gap-4 pb-2">
        <div className="rounded-xl surface-2 px-3.5 py-2.5 text-sm"><span className="text-muted">Öğün: </span><span className="font-semibold">{meal.raw_text}</span></div>
        <Field label="Öğün tipi"><MealTypePicker value={mealType} onChange={setMealType} /></Field>
        <Field label="Kalemler"><ItemEditor items={items} setItems={setItems} /></Field>
      </div>
    </Modal>
  );
}
window.EditMealModal = EditMealModal;

// ---------------- HEDEF SİHİRBAZI ----------------
function GoalWizardModal({ open, onClose, toast, onApplied }) {
  const [step, setStep] = useStateMo(0);
  const [profile, setProfile] = useStateMo(null);
  const [start, setStart] = useStateMo(72);
  const [target, setTarget] = useStateMo(65);
  const [pace, setPace] = useStateMo(0.5);
  const [busy, setBusy] = useStateMo(false);

  useEffMo(() => { if (open) { setStep(0); API.profile().then((p) => { setProfile(p); if (p.weight_kg) setStart(p.weight_kg); }); } }, [open]);

  const delta = Math.round((target - start) * 10) / 10; // hedef - mevcut
  const losing = delta < -0.2, gaining = delta > 0.2;
  const goalType = losing ? 'kilo_ver' : gaining ? 'kas_yap' : 'koru';
  const weeks = Math.abs(delta) > 0 ? Math.ceil(Math.abs(delta) / pace) : 0;
  const energy = profile ? API.computeEnergy({ ...profile, weight_kg: start }, goalType) : null;
  const dailyAdjust = Math.round(pace * 7700 / 7); // kcal/gün
  const targetKcal = energy ? (losing ? energy.tdee - dailyAdjust : gaining ? energy.tdee + Math.min(dailyAdjust, 400) : energy.tdee) : null;
  const aggressive = losing && (dailyAdjust > 900 || (energy && targetKcal < energy.bmr));
  const targetDate = weeks ? (() => { const d = new Date(); d.setDate(d.getDate() + weeks * 7); return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' }); })() : null;

  const apply = async () => {
    setBusy(true);
    try {
      await API.saveProfile({ weight_kg: start });
      await API.saveGoal({ goal_type: goalType, target_kcal: targetKcal != null ? Math.round(targetKcal) : null, target_protein_g: profile && profile.weight_kg ? Math.round(start * 1.6) : null });
      // Plan tercihi yardımcı veridir; kaydı başarısız olsa da hedef ayarlandı sayılır.
      try { await API.savePlan({ start_weight: start, target_weight: target, weeks, pace }); } catch {}
      toast('Hedef ayarlandı'); onApplied && onApplied(); onClose();
    } catch { toast('Kaydedilemedi', 'error'); } finally { setBusy(false); }
  };

  const steps = ['Kilo', 'Tempo', 'Plan'];
  return (
    <Modal open={open} onClose={onClose} title="Hedef sihirbazı" size="md"
      footer={step < 2
        ? <><Button variant="ghost" onClick={onClose}>Vazgeç</Button><Button icon="chevronR" onClick={() => setStep(step + 1)}>Devam</Button></>
        : <><Button variant="ghost" onClick={() => setStep(1)}>Geri</Button><Button icon="check" onClick={apply} disabled={busy}>{busy ? 'Uygulanıyor…' : 'Hedefi uygula'}</Button></>}>
      <div className="flex flex-col gap-5 pb-2">
        {/* adım göstergesi */}
        <div className="flex items-center gap-2">
          {steps.map((s, i) => <React.Fragment key={s}><div className={cx('flex items-center gap-2', i <= step ? '' : 'opacity-40')}><span className="grid place-items-center h-7 w-7 rounded-full font-display font-semibold text-xs" style={{ background: i <= step ? 'var(--accent)' : 'var(--surface-2)', color: i <= step ? '#fff' : 'var(--text-muted)' }}>{i + 1}</span><span className="text-sm font-semibold">{s}</span></div>{i < 2 && <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />}</React.Fragment>)}
        </div>

        {step === 0 && (
          <div className="anim-fade flex flex-col gap-4">
            <p className="text-sm text-muted">Şu anki ve ulaşmak istediğin kiloyu gir.</p>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Mevcut kilo (kg)"><div className="flex"><Stepper value={start} onChange={setStart} min={35} max={250} step={0.5} suffix="kg" /></div></Field>
              <Field label="Hedef kilo (kg)"><div className="flex"><Stepper value={target} onChange={setTarget} min={35} max={250} step={0.5} suffix="kg" /></div></Field>
            </div>
            <div className="rounded-xl surface-2 px-4 py-3 text-sm flex items-center gap-2">
              <Icon name={losing ? 'arrowDown' : gaining ? 'flame' : 'check'} size={16} style={{ color: 'var(--accent-text)' }} />
              {Math.abs(delta) < 0.2 ? 'Kiloyu korumak istiyorsun.' : <>Toplam <b className="font-display">{Math.abs(delta)} kg</b> {losing ? 'vereceksin' : 'alacaksın'}.</>}
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="anim-fade flex flex-col gap-4">
            <p className="text-sm text-muted">Haftalık tempo. Sağlıklı aralık: 0.25–0.75 kg/hafta.</p>
            <div className="grid grid-cols-4 gap-2">
              {[0.25, 0.5, 0.75, 1].map((p) => <button key={p} onClick={() => setPace(p)} className={cx('fr rounded-xl h-14 flex flex-col items-center justify-center font-display font-semibold transition bordered', pace === p ? 'shadow-soft' : 'surface-2 text-muted')} style={pace === p ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>{p}<span className="text-[10px] font-medium opacity-70">kg/hf</span></button>)}
            </div>
            <div className="rounded-xl surface-2 px-4 py-3.5 flex flex-col gap-1.5 text-sm">
              <div className="flex justify-between"><span className="text-muted">Tahmini süre</span><b className="font-display tnum">{weeks ? weeks + ' hafta' : '—'}</b></div>
              {targetDate && <div className="flex justify-between"><span className="text-muted">Hedef tarih</span><b className="font-display">{targetDate}</b></div>}
              <div className="flex justify-between"><span className="text-muted">Günlük {losing ? 'açık' : gaining ? 'fazla' : 'denge'}</span><b className="font-display tnum">{Math.abs(delta) < 0.2 ? '0' : '~' + dailyAdjust} kcal</b></div>
            </div>
            {pace >= 1 && losing && <div className="flex items-start gap-2 text-xs rounded-xl px-3.5 py-2.5" style={{ background: 'color-mix(in srgb, var(--c-carb) 12%, var(--surface))', color: 'var(--text)' }}><Icon name="alert" size={14} style={{ color: 'var(--c-carb)' }} className="mt-0.5 shrink-0" />1 kg/hafta hızlı bir tempo; kas kaybı riski için 0.5–0.75 önerilir.</div>}
          </div>
        )}

        {step === 2 && (
          <div className="anim-fade flex flex-col gap-4">
            {!energy && <ErrorBanner message="Hesap için profilde cinsiyet, kilo, boy ve doğum yılı dolu olmalı." />}
            <div className="grid grid-cols-2 gap-3">
              {[{ l: 'TDEE', v: energy && Math.round(energy.tdee), s: 'kcal/gün' }, { l: 'Hedef kalori', v: targetKcal != null ? Math.round(targetKcal) : null, s: 'kcal/gün', hi: true }].map((b) => (
                <Card key={b.l} className="p-4" style={b.hi ? { background: 'var(--accent-soft)' } : undefined}>
                  <div className="text-xs text-muted font-medium">{b.l}</div>
                  <div className="font-display font-bold text-2xl tnum" style={b.hi ? { color: 'var(--accent-text)' } : undefined}>{b.v != null ? b.v : '—'}</div>
                  <div className="text-xs text-muted">{b.s}</div>
                </Card>
              ))}
            </div>
            <div className="rounded-xl surface-2 px-4 py-3.5 flex flex-col gap-2 text-sm">
              <div className="flex justify-between"><span className="text-muted">Hedef türü</span><Badge tone="accent">{{ kilo_ver: 'Kilo verme', kas_yap: 'Kas kazanımı', koru: 'Koruma' }[goalType]}</Badge></div>
              <div className="flex justify-between"><span className="text-muted">Haftalık değişim</span><b className="font-display tnum">{Math.abs(delta) < 0.2 ? '0' : '~' + pace + ' kg'}</b></div>
              <div className="flex justify-between"><span className="text-muted">Protein hedefi</span><b className="font-display tnum">{Math.round(start * 1.6)} g/gün</b></div>
            </div>
            {aggressive && <div className="flex items-start gap-2 text-xs rounded-xl px-3.5 py-2.5" style={{ background: 'color-mix(in srgb, var(--c-fat) 12%, var(--surface))', color: 'var(--text)' }}><Icon name="alert" size={14} style={{ color: 'var(--c-fat)' }} className="mt-0.5 shrink-0" />Hedef kalori BMR'nin altına iniyor olabilir. Daha yavaş bir tempo seçmen önerilir.</div>}
            <p className="flex items-center gap-1.5 text-xs text-muted"><Icon name="info" size={13} />Bu hesap yaklaşıktır ve tıbbi tavsiye değildir.</p>
          </div>
        )}
      </div>
    </Modal>
  );
}
window.GoalWizardModal = GoalWizardModal;

// ---------------- AYARLAR ----------------
function SettingsModal({ open, onClose, toast, onChanged }) {
  const [s, setS] = useStateMo(API.getSettings());
  useEffMo(() => { if (open) setS(API.getSettings()); }, [open]);
  const save = () => { API.setSettings(s); toast(s.live ? 'Canlı backend açık' : 'Mock veri modu'); onChanged && onChanged(); onClose(); };
  return (
    <Modal open={open} onClose={onClose} title="Ayarlar" size="md" footer={<><Button variant="ghost" onClick={onClose}>Kapat</Button><Button icon="check" onClick={save}>Kaydet</Button></>}>
      <div className="flex flex-col gap-4 pb-2">
        <Card className="p-4 flex items-center gap-3" style={{ background: 'var(--surface-2)' }}>
          <span className="grid place-items-center h-10 w-10 rounded-xl shrink-0" style={{ background: s.live ? 'var(--accent-soft)' : 'var(--surface)', color: s.live ? 'var(--accent-text)' : 'var(--text-muted)' }}><Icon name={s.live ? 'leaf' : 'inbox'} size={18} /></span>
          <div className="flex-1 min-w-0"><div className="font-semibold text-sm">Canlı backend</div><div className="text-xs text-muted">{s.live ? 'Gerçek FastAPI sunucusuna bağlanılıyor' : 'Örnek (mock) veri kullanılıyor'}</div></div>
          <Toggle value={s.live} onChange={(v) => setS({ ...s, live: v })} />
        </Card>
        <Field label="Backend URL" hint="FastAPI temel adresi."><Input value={s.baseUrl} onChange={(e) => setS({ ...s, baseUrl: e.target.value })} placeholder="http://localhost:8000" /></Field>
        <Field label="Token" hint="Tüm isteklere Authorization: Bearer <token> olarak eklenir."><Input type="password" value={s.token} onChange={(e) => setS({ ...s, token: e.target.value })} placeholder="••••••••" /></Field>
        <button onClick={() => { API.resetDemo(); toast('Örnek veri sıfırlandı'); onChanged && onChanged(); onClose(); }} className="fr self-start text-sm font-semibold inline-flex items-center gap-1.5 text-muted hover:text-[var(--c-fat)]"><Icon name="refresh" size={15} />Örnek veriyi sıfırla</button>
      </div>
    </Modal>
  );
}
window.SettingsModal = SettingsModal;

// ---------------- YEMEK PLANI (markdown + Excel) ----------------
const PLAN_SAMPLE = `# Gün 0
- Kahvaltı: yulaf, muz, bir avuç fındık
- Öğle: tavuklu bulgur, cacık
- Akşam: fırın somon, mevsim salata

# Gün 1
- Kahvaltı: menemen, 2 dilim tam buğday ekmek
- Öğle: mercimek çorbası, ızgara köfte`;

function planToText(rows) {
  // Excel satırları → "# Gün N / - Öğün: yemek" metni
  const byDay = {};
  rows.forEach((r) => {
    const day = r.gun ?? r['gün'] ?? r.day ?? r.Gün ?? r.Gun ?? 0;
    const meal = r.ogun ?? r['öğün'] ?? r.meal ?? r['Öğün'] ?? r.Ogun ?? 'Öğle';
    const food = r.yemek ?? r.food ?? r.Yemek ?? r['içerik'] ?? r.aciklama ?? '';
    if (!food) return;
    const d = Number(String(day).replace(/[^\d]/g, '')) || 0;
    (byDay[d] = byDay[d] || []).push(`- ${meal}: ${food}`);
  });
  return Object.keys(byDay).sort((a, b) => a - b).map((d) => `# Gün ${d}\n${byDay[d].join('\n')}`).join('\n\n');
}

function MealPlanModal({ open, onClose, toast, onApplied }) {
  const [mode, setMode] = useStateMo('md');
  const [md, setMd] = useStateMo('');
  const [preview, setPreview] = useStateMo(null);
  const [busy, setBusy] = useStateMo(false);
  const [fileName, setFileName] = useStateMo('');

  useEffMo(() => { if (open) { setMode('md'); setMd(''); setPreview(null); setFileName(''); } }, [open]);

  const onExcel = async (file) => {
    if (!file) return; setFileName(file.name);
    try {
      const buf = await file.arrayBuffer();
      const wb = window.XLSX.read(buf, { type: 'array' });
      const rows = window.XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { defval: '' });
      const norm = rows.map((r) => { const o = {}; Object.keys(r).forEach((k) => o[k.toString().trim().toLowerCase()] = r[k]); return o; });
      const text = planToText(norm);
      setMd(text); if (!text) toast('Excel okundu ama satır bulunamadı', 'error'); else toast(`${rows.length} satır okundu`);
    } catch (e) { toast('Excel okunamadı', 'error'); }
  };

  const doPreview = async () => { setBusy(true); try { setPreview(await API.previewPlan(md)); } catch { toast('Önizlenemedi', 'error'); } finally { setBusy(false); } };
  const doApply = async () => { setBusy(true); try { const r = await API.applyPlan(md); toast(`Plan uygulandı (${r.created_meal_ids.length} öğün)`); onApplied && onApplied(); onClose(); } catch { toast('Uygulanamadı', 'error'); } finally { setBusy(false); } };

  const dayLabel = (off) => off === 0 ? 'Bugün' : `+${off} gün`;
  const grouped = preview ? preview.entries.reduce((m, e) => ((m[e.day_offset] = m[e.day_offset] || []).push(e), m), {}) : {};

  return (
    <Modal open={open} onClose={onClose} title="Yemek planı yükle" size="lg"
      footer={preview
        ? <><Button variant="ghost" onClick={() => setPreview(null)}>Geri</Button><Button icon="check" onClick={doApply} disabled={busy}>{busy ? 'Uygulanıyor…' : 'Planı uygula'}</Button></>
        : <><Button variant="ghost" onClick={onClose}>Vazgeç</Button><Button icon="search" onClick={doPreview} disabled={busy || md.trim().length < 5}>{busy ? 'Hazırlanıyor…' : 'Önizle'}</Button></>}>
      <div className="flex flex-col gap-3 pb-2">
        {!preview ? (
          <>
            <div className="max-w-xs"><Segmented value={mode} onChange={setMode} options={[{ value: 'md', label: 'Markdown', icon: 'text' }, { value: 'excel', label: 'Excel', icon: 'upload' }]} /></div>
            {mode === 'excel' && (
              <label className="fr cursor-pointer rounded-2xl bordered surface-2 border-dashed flex flex-col items-center justify-center gap-2 py-6 hover:bg-[var(--surface)] transition" style={{ borderWidth: 2 }}>
                <input type="file" accept=".xlsx,.xls,.csv" className="hidden" onChange={(e) => onExcel(e.target.files?.[0])} />
                <span className="grid place-items-center h-11 w-11 rounded-xl surface text-muted"><Icon name="upload" size={20} /></span>
                <span className="font-semibold text-sm">{fileName || 'Excel (.xlsx) yükle'}</span>
                <span className="text-xs text-muted">Sütunlar: Gün · Öğün · Yemek</span>
              </label>
            )}
            <Field label={mode === 'excel' ? 'Dönüştürülen plan (düzenleyebilirsin)' : 'Markdown plan'} hint="“# Gün 0” başlıkları günü, “- Öğün: yemek” satırları öğünü belirtir.">
              <Textarea rows={9} value={md} onChange={(e) => setMd(e.target.value)} placeholder={PLAN_SAMPLE} className="font-mono text-sm" />
            </Field>
            {mode === 'md' && <button onClick={() => setMd(PLAN_SAMPLE)} className="fr self-start text-xs rounded-full surface-2 bordered px-3 py-1.5 text-muted hover:text-[var(--text)]">Örnek planı doldur</button>}
          </>
        ) : (
          <div className="anim-fade flex flex-col gap-3">
            <div className="flex items-center gap-2 text-sm"><Badge tone="accent">{Object.keys(grouped).length} gün</Badge><Badge>{preview.entries.length} öğün</Badge></div>
            {preview.entries.length === 0 ? <EmptyState icon="inbox" title="Plan okunamadı" hint="Başlık ve madde biçimini kontrol et." />
              : Object.keys(grouped).sort((a, b) => a - b).map((off) => (
                <Card key={off} className="p-4">
                  <div className="font-display font-semibold mb-2 flex items-center gap-2"><Icon name="calendar" size={15} className="text-accent-text" />{dayLabel(+off)}</div>
                  <ul className="flex flex-col gap-1.5">{grouped[off].map((e, j) => <li key={j} className="flex items-center gap-2 text-sm"><MealTypeBadge type={e.meal_type} /><span>{e.raw_text}</span></li>)}</ul>
                </Card>
              ))}
          </div>
        )}
      </div>
    </Modal>
  );
}
window.MealPlanModal = MealPlanModal;
