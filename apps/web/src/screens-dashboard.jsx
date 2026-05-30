// screens-dashboard.jsx — ÖZET
function MealTypeBadge({ type }) {
  const map = { kahvalti: { label: 'Kahvaltı', tone: 'amber' }, ogle: { label: 'Öğle', tone: 'accent' }, aksam: { label: 'Akşam', tone: 'blue' }, ara: { label: 'Ara öğün', tone: 'rose' } };
  const m = map[type] || { label: type || 'Öğün', tone: 'neutral' };
  return <Badge tone={m.tone}>{m.label}</Badge>;
}
window.MealTypeBadge = MealTypeBadge;

function DateNav({ date, onChange }) {
  const shift = (d) => { const n = new Date(date + 'T00:00:00'); n.setDate(n.getDate() + d); onChange(n.toISOString().slice(0, 10)); };
  const isToday = date === API.todayStr();
  const dt = new Date(date + 'T00:00:00');
  const label = dt.toLocaleDateString('tr-TR', { weekday: 'long', day: 'numeric', month: 'long' });
  return (
    <div className="inline-flex items-center gap-1 surface bordered rounded-xl p-1 shadow-soft">
      <button onClick={() => shift(-1)} className="fr grid h-9 w-9 place-items-center rounded-lg text-muted hover:bg-[var(--surface-2)]"><Icon name="chevronL" size={18} /></button>
      <div className="flex items-center gap-2 px-2 min-w-[170px] justify-center"><Icon name="calendar" size={16} className="text-accent-text" /><span className="font-semibold text-sm capitalize">{isToday ? 'Bugün' : label}</span></div>
      <button onClick={() => shift(1)} disabled={isToday} className="fr grid h-9 w-9 place-items-center rounded-lg text-muted hover:bg-[var(--surface-2)] disabled:opacity-30"><Icon name="chevronR" size={18} /></button>
    </div>
  );
}
window.DateNav = DateNav;

function MacroStatCard({ label, value, max, color, unit, layout, icon }) {
  const pct = Math.round(max ? Math.min(100, (value / max) * 100) : 0);
  if (layout === 'rings') {
    return (
      <Card className="p-4 flex flex-col items-center gap-2">
        <Ring value={value} max={max || 1} color={color} size={92} stroke={9}>
          <div className="font-display font-semibold text-lg tnum leading-none">{Math.round(value)}</div>
          <div className="text-[10px] text-muted">{max ? '/ ' + max + unit : unit}</div>
        </Ring>
        <div className="text-sm font-semibold">{label}</div>
      </Card>
    );
  }
  return (
    <Card className="p-4 flex flex-col gap-2.5">
      <div className="flex items-center justify-between"><span className="text-sm font-semibold text-muted">{label}</span><span className="h-2.5 w-2.5 rounded-full" style={{ background: color }} /></div>
      <div className="flex items-baseline gap-1"><span className="font-display font-semibold text-2xl tnum">{Math.round(value)}</span><span className="text-sm text-muted">{max ? '/ ' + max : ''}{unit}</span></div>
      <ProgressBar value={value} max={max || 1} color={color} />
      <div className="text-xs text-muted tnum">{max ? '%' + pct + ' tamam' : 'hedef yok'}</div>
    </Card>
  );
}

function MacroGrid({ intake, targets, layout }) {
  const items = [
    { k: 'kcal', label: 'Kalori', color: 'var(--c-kcal)', unit: '', v: intake.intake_kcal, m: targets.kcal },
    { k: 'prot', label: 'Protein', color: 'var(--c-prot)', unit: 'g', v: intake.protein_g, m: targets.protein },
    { k: 'carb', label: 'Karbonhidrat', color: 'var(--c-carb)', unit: 'g', v: intake.carb_g, m: targets.carb },
    { k: 'fat', label: 'Yağ', color: 'var(--c-fat)', unit: 'g', v: intake.fat_g, m: targets.fat },
  ];
  if (layout === 'hero') {
    const macros = items.slice(1);
    return (
      <div className="grid lg:grid-cols-[300px_1fr] gap-3 sm:gap-4">
        <Card className="p-5 flex flex-col items-center justify-center gap-3">
          <Ring value={intake.intake_kcal} max={targets.kcal || 1} color="var(--c-kcal)" size={172} stroke={16}>
            <div className="font-display font-bold text-3xl tnum leading-none">{Math.round(intake.intake_kcal)}</div>
            <div className="text-xs text-muted mt-1">{targets.kcal ? '/ ' + targets.kcal + ' kcal' : 'kcal'}</div>
            {targets.kcal != null && <div className="text-[11px] font-semibold mt-1.5" style={{ color: 'var(--accent-text)' }}>{Math.max(0, targets.kcal - intake.intake_kcal)} kcal kaldı</div>}
          </Ring>
          <div className="text-sm font-semibold">Günlük kalori</div>
        </Card>
        <Card className="p-5 flex flex-col justify-center gap-4">
          {macros.map((it) => {
            const pct = Math.round(it.m ? Math.min(100, (it.v / it.m) * 100) : 0);
            return (
              <div key={it.k} className="flex flex-col gap-1.5">
                <div className="flex items-baseline justify-between">
                  <span className="text-sm font-semibold inline-flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full" style={{ background: it.color }} />{it.label}</span>
                  <span className="text-sm tnum"><b className="font-display">{Math.round(it.v)}</b><span className="text-muted"> {it.m ? '/ ' + it.m + it.unit + ' · %' + pct : it.unit}</span></span>
                </div>
                <ProgressBar value={it.v} max={it.m || 1} color={it.color} height={10} />
              </div>
            );
          })}
        </Card>
      </div>
    );
  }
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      {items.map((it) => <MacroStatCard key={it.k} label={it.label} value={it.v} max={it.m} color={it.color} unit={it.unit} layout={layout} />)}
    </div>
  );
}

// Enerji + kalori açığı kartı
function EnergyCard({ energy, plan, onOpenWizard }) {
  const hasTarget = energy && energy.target_kcal != null;
  const deficit = energy && energy.tdee != null && energy.target_kcal != null ? Math.round(energy.tdee - energy.target_kcal) : null;
  const weeklyKg = deficit != null ? Math.round((Math.abs(deficit) * 7 / 7700) * 100) / 100 : null;
  const dir = deficit > 0 ? 'açık' : deficit < 0 ? 'fazla' : 'denge';
  return (
    <Card className="p-5 sm:p-6 flex flex-col gap-5">
      <div className="flex items-center gap-2.5">
        <span className="grid place-items-center h-9 w-9 rounded-xl" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}><Icon name="activity" size={18} /></span>
        <h3 className="font-display font-semibold text-lg">Enerji dengesi</h3>
        <button onClick={onOpenWizard} className="fr ml-auto text-sm font-semibold inline-flex items-center gap-1.5" style={{ color: 'var(--accent-text)' }}><Icon name="target" size={15} />Hedefi düzenle</button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {[{ l: 'BMR', v: energy && energy.bmr, s: 'kcal' }, { l: 'TDEE', v: energy && energy.tdee, s: 'kcal' }, { l: 'Hedef', v: hasTarget ? energy.target_kcal : null, s: 'kcal' }, { l: 'Kalan', v: energy && energy.remaining_kcal, s: 'kcal', hi: true }].map((b) => (
          <div key={b.l} className="rounded-xl surface-2 px-3.5 py-3" style={b.hi ? { background: 'var(--accent-soft)' } : undefined}>
            <div className="text-xs text-muted font-medium">{b.l}</div>
            <div className="font-display font-semibold text-xl tnum" style={b.hi ? { color: 'var(--accent-text)' } : undefined}>{b.v != null ? Math.round(b.v) : '—'}<span className="text-xs font-medium text-muted ml-1">{b.v != null ? b.s : ''}</span></div>
          </div>
        ))}
      </div>

      {deficit != null && deficit !== 0 ? (
        <div className="flex items-start gap-3 rounded-xl px-4 py-3.5" style={{ background: 'color-mix(in srgb, var(--accent) 8%, var(--surface))', border: '1px solid color-mix(in srgb, var(--accent) 26%, transparent)' }}>
          <span className="grid place-items-center h-9 w-9 rounded-lg shrink-0" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}><Icon name={deficit > 0 ? 'arrowDown' : 'flame'} size={18} /></span>
          <div className="text-sm leading-relaxed">
            <b className="font-display">Günlük ~{Math.abs(deficit)} kcal {dir}.</b> Bu tempoda haftada yaklaşık <b style={{ color: 'var(--accent-text)' }}>{weeklyKg} kg</b> {deficit > 0 ? 'verirsin' : 'alırsın'}.
            {plan && plan.target_weight ? ` Hedef: ${plan.target_weight} kg.` : ''} {Math.abs(deficit) > 900 ? ' Açık çok yüksek; sürdürülebilirlik için 500-750 kcal önerilir.' : ''}
          </div>
        </div>
      ) : !hasTarget ? (
        <button onClick={onOpenWizard} className="fr flex items-center gap-3 rounded-xl px-4 py-3.5 text-left hover:brightness-95 transition" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}>
          <Icon name="sparkles" size={20} /><div className="text-sm font-semibold flex-1">Hedefini belirle — ne kadar sürede kaç kilo? Kalori hedefini senin için hesaplayalım.</div><Icon name="chevronR" size={18} />
        </button>
      ) : null}
    </Card>
  );
}

function RecCard({ rec, onGoWorkout, onGoRecipes }) {
  const w = rec.workout;
  const servBySlug = Object.fromEntries((rec.serving_suggestions || []).map((s) => [s.recipe_slug, s]));
  return (
    <Card className="p-5 sm:p-6 flex flex-col gap-5">
      <div className="flex items-center gap-2.5"><span className="grid place-items-center h-9 w-9 rounded-xl" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}><Icon name="sparkles" size={18} /></span><h3 className="font-display font-semibold text-lg">Günün önerisi</h3></div>

      <div className="grid sm:grid-cols-2 gap-5">
        <div className="flex flex-col gap-2.5">
          <div className="flex items-center gap-2 text-sm font-semibold"><Icon name="utensils" size={16} className="text-accent-text" />Sana uygun öğünler</div>
          <div className="flex flex-col gap-2">
            {rec.meal_suggestions.slice(0, 3).map((r) => {
              const sv = servBySlug[r.slug];
              const perKcal = r.macros_per_serving ? r.macros_per_serving.kcal : (r.total_kcal ? Math.round(r.total_kcal / (r.servings || 1)) : null);
              return (
                <button key={r.id} onClick={onGoRecipes} className="fr flex items-center gap-3 rounded-xl surface-2 px-3 py-2.5 text-left hover:bg-[var(--surface)] transition">
                  {r.image_url ? <img src={r.image_url} alt="" loading="lazy" className="h-10 w-10 shrink-0 rounded-lg object-cover" onError={(e) => { e.target.style.display = 'none'; }} /> : <ImgPlaceholder className="h-10 w-10 shrink-0" label="" round="rounded-lg" />}
                  <div className="min-w-0 flex-1"><div className="text-sm font-semibold truncate">{r.title_tr}</div><div className="text-xs text-muted">{sv ? `≈ ${(+sv.recommended_servings).toLocaleString('tr')} porsiyon` : r.region}</div></div>
                  <div className="text-xs font-semibold tnum shrink-0 text-right" style={{ color: 'var(--c-kcal)' }}>{perKcal != null ? `${perKcal} kcal` : '—'}<div className="text-[10px] text-muted font-normal">/porsiyon</div></div>
                </button>
              );
            })}
          </div>
        </div>
        <div className="flex flex-col gap-2.5">
          <div className="flex items-center gap-2 text-sm font-semibold"><Icon name="dumbbell" size={16} className="text-accent-text" />Antrenman odağı</div>
          <button onClick={onGoWorkout} className="fr rounded-xl surface-2 px-4 py-3.5 text-left hover:bg-[var(--surface)] transition flex flex-col gap-1">
            <div className="flex items-center justify-between"><span className="font-display font-semibold capitalize">{w.focus}</span><Badge tone="accent">{w.weekly_minutes} dk/hafta</Badge></div>
            <div className="text-xs text-muted">{w.days.length} antrenman günü · detay için dokun</div>
          </button>
          {rec.notes.length > 0 && (
            <ul className="flex flex-col gap-1.5 mt-1">
              {rec.notes.slice(0, 3).map((n, i) => <li key={i} className="flex items-start gap-2 text-sm text-muted"><span className="mt-1.5 h-1.5 w-1.5 rounded-full shrink-0" style={{ background: 'var(--accent)' }} />{n}</li>)}
            </ul>
          )}
        </div>
      </div>
    </Card>
  );
}

function DashboardSkeleton({ layout }) {
  return (
    <div className="flex flex-col gap-4">
      <Skel style={{ height: 200, borderRadius: 16 }} />
      {layout === 'hero'
        ? <div className="grid lg:grid-cols-[300px_1fr] gap-4"><Skel style={{ height: 260, borderRadius: 16 }} /><Skel style={{ height: 260, borderRadius: 16 }} /></div>
        : <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">{[0, 1, 2, 3].map((i) => <Skel key={i} style={{ height: layout === 'rings' ? 168 : 132, borderRadius: 16 }} />)}</div>}
      <Skel style={{ height: 280, borderRadius: 16 }} />
    </div>
  );
}

function DashboardScreen({ date, setDate, demoState, ringLayout, onAddMeal, onOpenWizard, onGoWorkout, onGoRecipes }) {
  const sum = useResource(() => API.summary(date), [date]);
  const rec = useResource(() => API.recommendations(date), [date]);
  const plan = useResource(() => API.getPlan(), []);

  const loading = demoState === 'loading' || sum.loading || rec.loading;
  const error = demoState === 'error' ? 'Sunucuya ulaşılamadı. Bağlantını kontrol et.' : (sum.error || rec.error);
  const empty = demoState === 'empty';
  const targets = rec.data ? deriveTargets(rec.data.energy) : {};

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div><h1 className="font-display font-bold text-2xl sm:text-[28px] leading-tight">Özet</h1><p className="text-muted text-sm mt-0.5">Günlük beslenme ve antrenman takibin.</p></div>
        <div className="flex items-center gap-2"><DateNav date={date} onChange={setDate} /><Button icon="plus" onClick={onAddMeal} className="hidden sm:inline-flex">Öğün ekle</Button></div>
      </header>

      {error ? <ErrorBanner message={error} onRetry={() => { sum.reload(); rec.reload(); }} />
        : loading ? <DashboardSkeleton layout={ringLayout} />
        : empty ? <Card className="p-2"><EmptyState icon="utensils" title="Bu gün için kayıt yok" hint="Öğün ekleyerek günlük makro takibine başla." action={<Button icon="plus" onClick={onAddMeal}>Öğün ekle</Button>} /></Card>
        : (
          <>
            <EnergyCard energy={rec.data.energy} plan={plan.data} onOpenWizard={onOpenWizard} />
            <MacroGrid intake={sum.data} targets={targets} layout={ringLayout} />
            {/* Lif — backend summary'ye fiber_g eklenmesi önerilir */}
            <Card className="p-4 flex items-center gap-4">
              <span className="grid place-items-center h-11 w-11 rounded-xl shrink-0" style={{ background: 'color-mix(in srgb, var(--c-carb) 14%, transparent)', color: 'var(--c-carb)' }}><Icon name="leaf" size={20} /></span>
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between mb-1.5"><span className="text-sm font-semibold">Lif</span><span className="text-sm tnum"><b className="font-display">{sum.data.fiber_g || 0}</b><span className="text-muted"> / {targets.fiber}g</span></span></div>
                <ProgressBar value={sum.data.fiber_g || 0} max={targets.fiber} color="var(--c-carb)" />
              </div>
            </Card>
            <RecCard rec={rec.data} onGoWorkout={onGoWorkout} onGoRecipes={onGoRecipes} />
            <p className="flex items-center gap-1.5 text-xs text-muted px-1"><Icon name="info" size={13} />Kalori, makro ve hesaplamalar yaklaşıktır; tıbbi tavsiye değildir.</p>
          </>
        )}
    </div>
  );
}
window.DashboardScreen = DashboardScreen;
