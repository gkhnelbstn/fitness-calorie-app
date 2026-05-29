// screens-misc.jsx — KARA LİSTE + PROFİL
const { useState: useStateM } = React;

function BlacklistScreen({ demoState }) {
  const bl = useResource(() => API.blacklist(), []);
  const [val, setVal] = useStateM('');
  const loading = demoState === 'loading' || bl.loading;
  const error = demoState === 'error' ? 'Kara liste yüklenemedi.' : bl.error;
  const list = demoState === 'empty' ? [] : (bl.data || []);

  const add = async () => {
    const name = val.trim(); if (!name) return; setVal('');
    bl.setData([...list, { canonical_id: 'tmp' + Date.now(), slug: '', name_tr: name }]);
    try { await API.addBlacklist(name); bl.reload(); } catch { bl.reload(); }
  };
  const del = async (item) => { bl.setData(list.filter((b) => b.canonical_id !== item.canonical_id)); try { await API.deleteBlacklist(item.canonical_id); } catch { bl.reload(); } };

  return (
    <div className="flex flex-col gap-5 max-w-2xl">
      <header><h1 className="font-display font-bold text-2xl sm:text-[28px] leading-tight">Kara Liste</h1><p className="text-muted text-sm mt-0.5">Bu malzemeler tarif önerilerinden çıkarılır veya ikame edilir.</p></header>
      <Card className="p-2 flex items-center gap-2">
        <Input value={val} onChange={(e) => setVal(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && add()} placeholder="Malzeme ekle… (ör. yer fıstığı)" className="border-0 surface" />
        <Button icon="plus" onClick={add} disabled={!val.trim()} className="shrink-0">Ekle</Button>
      </Card>
      {error ? <ErrorBanner message={error} onRetry={bl.reload} />
        : loading ? <div className="grid sm:grid-cols-2 gap-3">{[0, 1, 2].map((i) => <Skel key={i} style={{ height: 60, borderRadius: 16 }} />)}</div>
        : list.length === 0 ? <Card className="p-2"><EmptyState icon="blacklist" title="Kara liste boş" hint="Sevmediğin ya da alerjin olan malzemeleri ekle; tariflerde otomatik çıkaralım." /></Card>
        : <div className="grid sm:grid-cols-2 gap-3">{list.map((b) => (
            <Card key={b.canonical_id} className="p-3.5 flex items-center gap-3 group">
              <span className="grid place-items-center h-10 w-10 rounded-xl shrink-0" style={{ background: 'color-mix(in srgb, var(--c-fat) 14%, transparent)', color: 'var(--c-fat)' }}><Icon name="blacklist" size={18} /></span>
              <span className="font-semibold flex-1 truncate">{b.name_tr}</span>
              <button onClick={() => del(b)} className="fr opacity-0 group-hover:opacity-100 transition text-muted hover:text-[var(--c-fat)] grid h-8 w-8 place-items-center rounded-lg hover:bg-[var(--surface-2)]"><Icon name="trash" size={16} /></button>
            </Card>
          ))}</div>}
    </div>
  );
}
window.BlacklistScreen = BlacklistScreen;

const ACTIVITY_OPTS = [
  { v: 'sedentary', l: 'Hareketsiz', d: 'Masa başı, az hareket' },
  { v: 'light', l: 'Az hareketli', d: 'Haftada 1-2 antrenman' },
  { v: 'moderate', l: 'Orta düzey', d: 'Haftada 3-5 antrenman' },
  { v: 'active', l: 'Çok hareketli', d: 'Haftada 6-7 antrenman' },
  { v: 'very_active', l: 'Atlet', d: 'Günde 2 antrenman / fiziksel iş' },
];

function bmiInfo(w, h) {
  if (!w || !h) return null;
  const bmi = Math.round((w / Math.pow(h / 100, 2)) * 10) / 10;
  const cat = bmi < 18.5 ? { l: 'Zayıf', c: 'var(--c-prot)' } : bmi < 25 ? { l: 'Normal', c: 'var(--accent)' } : bmi < 30 ? { l: 'Fazla kilolu', c: 'var(--c-carb)' } : { l: 'Obez', c: 'var(--c-fat)' };
  return { bmi, ...cat };
}

function ProfileScreen({ demoState, toast, onOpenWizard, refreshKey }) {
  const prof = useResource(() => API.profile(), [refreshKey]);
  const goalR = useResource(() => API.goal().catch(() => null), [refreshKey]);
  const [form, setForm] = useStateM(null);
  const [goal, setGoal] = useStateM(null);
  const [saving, setSaving] = useStateM(false);

  React.useEffect(() => { if (prof.data) setForm(prof.data); }, [prof.data]);
  React.useEffect(() => { setGoal(goalR.data || { goal_type: 'koru', target_kcal: null, target_protein_g: null }); }, [goalR.data]);

  const loading = demoState === 'loading' || prof.loading || goalR.loading || !form || !goal;
  const error = demoState === 'error' ? 'Profil yüklenemedi.' : prof.error;

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const setG = (k, v) => setGoal((g) => ({ ...g, [k]: v }));
  const save = async () => { setSaving(true); try { await API.saveProfile(form); await API.saveGoal(goal); toast('Profil kaydedildi'); } catch { toast('Kaydedilemedi', 'error'); } finally { setSaving(false); } };

  const energy = form ? API.computeEnergy(form, goal && goal.goal_type) : null;
  const bmi = form ? bmiInfo(form.weight_kg, form.height_cm) : null;

  return (
    <div className="flex flex-col gap-5 max-w-3xl">
      <header><h1 className="font-display font-bold text-2xl sm:text-[28px] leading-tight">Profil</h1><p className="text-muted text-sm mt-0.5">Bilgilerin BMR/TDEE ve hedef hesaplarında kullanılır.</p></header>

      {error ? <ErrorBanner message={error} onRetry={() => { prof.reload(); goalR.reload(); }} />
        : loading ? <Skel style={{ height: 520, borderRadius: 16 }} />
        : (
          <>
            {/* Canlı enerji önizleme */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[{ l: 'BMR', v: energy && energy.bmr, s: 'kcal' }, { l: 'TDEE', v: energy && energy.tdee, s: 'kcal' }, { l: 'Hedef kcal', v: energy && energy.target_kcal, s: 'kcal', hi: true }, { l: 'BMI', v: bmi && bmi.bmi, s: bmi ? bmi.l : '', col: bmi && bmi.c }].map((b) => (
                <Card key={b.l} className="p-4">
                  <div className="text-xs text-muted font-medium">{b.l}</div>
                  <div className="font-display font-semibold text-2xl tnum mt-0.5" style={{ color: b.hi ? 'var(--accent-text)' : (b.col || 'var(--text)') }}>{b.v != null ? b.v : '—'}</div>
                  <div className="text-xs text-muted">{b.s}</div>
                </Card>
              ))}
            </div>

            <Card className="p-5 sm:p-6 flex flex-col gap-4">
              <h3 className="font-display font-semibold text-lg flex items-center gap-2"><Icon name="profile" size={18} className="text-accent-text" />Kişisel bilgiler</h3>
              <div className="grid sm:grid-cols-2 gap-4">
                <Field label="İsim"><Input value={form.name || ''} onChange={(e) => set('name', e.target.value)} /></Field>
                <Field label="Cinsiyet"><Select value={form.sex || ''} onChange={(e) => set('sex', e.target.value)}><option value="kadin">Kadın</option><option value="erkek">Erkek</option></Select></Field>
                <Field label="Doğum yılı"><Input type="number" value={form.birth_year || ''} onChange={(e) => set('birth_year', +e.target.value)} /></Field>
                <Field label="Aktivite düzeyi"><Select value={form.activity_level || 'moderate'} onChange={(e) => set('activity_level', e.target.value)}>{ACTIVITY_OPTS.map((o) => <option key={o.v} value={o.v}>{o.l} — {o.d}</option>)}</Select></Field>
                <Field label="Boy (cm)"><Input type="number" value={form.height_cm || ''} onChange={(e) => set('height_cm', +e.target.value)} /></Field>
                <Field label="Kilo (kg)"><Input type="number" value={form.weight_kg || ''} onChange={(e) => set('weight_kg', +e.target.value)} /></Field>
              </div>
            </Card>

            <Card className="p-5 sm:p-6 flex flex-col gap-4">
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-display font-semibold text-lg flex items-center gap-2"><Icon name="target" size={18} className="text-accent-text" />Hedef</h3>
                <Button size="sm" variant="soft" icon="sparkles" onClick={onOpenWizard}>Hedef sihirbazı</Button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                {[{ v: 'kilo_ver', l: 'Kilo ver', s: '−500 kcal' }, { v: 'koru', l: 'Koru', s: 'denge' }, { v: 'kas_yap', l: 'Kas yap', s: '+300 kcal' }].map((o) => (
                  <button key={o.v} onClick={() => setG('goal_type', o.v)} className={cx('fr rounded-xl h-16 flex flex-col items-center justify-center gap-0.5 font-display font-semibold transition bordered', goal.goal_type === o.v ? 'shadow-soft' : 'surface-2 text-muted hover:text-[var(--text)]')} style={goal.goal_type === o.v ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>
                    {o.l}<span className="text-xs font-medium opacity-70">{o.s}</span>
                  </button>
                ))}
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <Field label="Hedef kalori (kcal)" hint="Boş bırakılırsa otomatik hesaplanır."><Input type="number" value={goal.target_kcal || ''} onChange={(e) => setG('target_kcal', e.target.value ? +e.target.value : null)} placeholder={energy ? 'otomatik: ' + energy.target_kcal : 'otomatik'} /></Field>
                <Field label="Hedef protein (g)" hint="Boş bırakılırsa kilo × 1.6 g."><Input type="number" value={goal.target_protein_g || ''} onChange={(e) => setG('target_protein_g', e.target.value ? +e.target.value : null)} placeholder={form.weight_kg ? 'otomatik: ' + Math.round(form.weight_kg * 1.6) : 'otomatik'} /></Field>
              </div>
            </Card>

            <div className="flex justify-end sticky bottom-4 sm:static"><Button size="lg" icon={saving ? null : 'check'} onClick={save} disabled={saving} className="w-full sm:w-auto shadow-softlg">{saving ? 'Kaydediliyor…' : 'Kaydet'}</Button></div>
          </>
        )}
    </div>
  );
}
window.ProfileScreen = ProfileScreen;
