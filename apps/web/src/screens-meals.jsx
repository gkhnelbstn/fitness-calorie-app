// screens-meals.jsx — YEMEKLER (items tabanlı, foto, düzenle/sil)
const { useState: useStateMl } = React;

function macrosOf(meal) {
  return (meal.items || []).reduce((a, it) => ({ kcal: a.kcal + (it.kcal || 0), p: a.p + (it.protein_g || 0), c: a.c + (it.carb_g || 0), f: a.f + (it.fat_g || 0), fib: a.fib + (it.fiber_g || 0) }), { kcal: 0, p: 0, c: 0, f: 0, fib: 0 });
}
window.macrosOf = macrosOf;

function timeOf(iso) { try { return new Date(iso).toTimeString().slice(0, 5); } catch { return ''; } }

function MealCard({ meal, onDelete, onEdit }) {
  const [open, setOpen] = useStateMl(false);
  const [confirm, setConfirm] = useStateMl(false);
  const m = macrosOf(meal);
  return (
    <Card className="overflow-hidden">
      <div className="p-3.5 flex items-center gap-3.5 group">
        {meal.photo_path
          ? <ImgPlaceholder className="h-14 w-14 shrink-0" label="foto" round="rounded-xl" />
          : <span className="grid place-items-center h-14 w-14 shrink-0 rounded-xl surface-2" style={{ color: 'var(--accent-text)' }}><Icon name="utensils" size={22} /></span>}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap"><MealTypeBadge type={meal.meal_type} />{meal.eaten_at && <span className="text-xs text-muted inline-flex items-center gap-1"><Icon name="clock" size={12} />{timeOf(meal.eaten_at)}</span>}</div>
          <h3 className="font-semibold mt-1 truncate">{meal.raw_text}</h3>
          <div className="flex items-center gap-3 mt-0.5 text-xs text-muted tnum">
            <span style={{ color: 'var(--c-prot)' }}>P {Math.round(m.p)}g</span>
            <span style={{ color: 'var(--c-carb)' }}>K {Math.round(m.c)}g</span>
            <span style={{ color: 'var(--c-fat)' }}>Y {Math.round(m.f)}g</span>
            {(meal.items || []).length > 0 && <button onClick={() => setOpen(!open)} className="fr inline-flex items-center gap-0.5 hover:text-[var(--text)]">{meal.items.length} kalem<Icon name="chevronD" size={12} className={cx('transition-transform', open && 'rotate-180')} /></button>}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <div className="font-display font-semibold tnum text-lg inline-flex items-baseline gap-1" style={{ color: 'var(--c-kcal)' }}>{Math.round(meal.total_kcal || m.kcal)}<span className="text-xs text-muted font-medium">kcal</span></div>
          <div className="flex items-center gap-1 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition">
            <button onClick={() => onEdit(meal)} className="fr text-muted hover:text-[var(--accent-text)] grid h-8 w-8 place-items-center rounded-lg hover:bg-[var(--surface-2)]"><Icon name="edit" size={16} /></button>
            <button onClick={() => setConfirm(true)} className="fr text-muted hover:text-[var(--c-fat)] grid h-8 w-8 place-items-center rounded-lg hover:bg-[var(--surface-2)]"><Icon name="trash" size={16} /></button>
          </div>
        </div>
      </div>
      {open && (meal.items || []).length > 0 && (
        <ul className="surface-2 px-4 py-3 anim-fade flex flex-col gap-2 bordered border-l-0 border-r-0 border-b-0">
          {meal.items.map((it, i) => (
            <li key={i} className="flex items-center justify-between gap-3 text-sm">
              <span className="flex items-center gap-2 min-w-0"><span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ background: 'var(--accent)' }} /><span className="truncate">{it.raw_name}</span>{it.quantity != null && <span className="text-xs text-muted shrink-0">{it.quantity} {it.unit || ''}</span>}{it.confidence != null && it.confidence < 0.7 && <Badge tone="amber" className="shrink-0">tahmini</Badge>}</span>
              <span className="text-xs text-muted tnum shrink-0">{Math.round(it.kcal || 0)} kcal</span>
            </li>
          ))}
        </ul>
      )}
      {confirm && (
        <div className="surface-2 px-4 py-3 anim-fade flex items-center justify-between gap-3 bordered border-l-0 border-r-0 border-b-0">
          <span className="text-sm font-medium">Bu öğünü silmek istiyor musun?</span>
          <div className="flex gap-2"><Button size="sm" variant="ghost" onClick={() => setConfirm(false)}>Vazgeç</Button><Button size="sm" variant="danger" icon="trash" onClick={() => { setConfirm(false); onDelete(meal); }}>Sil</Button></div>
        </div>
      )}
    </Card>
  );
}

function MealsSkeleton() { return <div className="flex flex-col gap-3">{[0, 1, 2, 3].map((i) => <Skel key={i} style={{ height: 86, borderRadius: 16 }} />)}</div>; }

function MealsScreen({ date, setDate, demoState, onAddMeal, onEditMeal, refreshKey }) {
  const meals = useResource(() => API.meals(date), [date, refreshKey]);
  const loading = demoState === 'loading' || meals.loading;
  const error = demoState === 'error' ? 'Öğünler yüklenemedi.' : meals.error;
  const list = demoState === 'empty' ? [] : (meals.data || []);

  const del = async (meal) => { meals.setData(list.filter((m) => m.id !== meal.id)); try { await API.deleteMeal(meal.id); } catch { meals.reload(); } };
  const totalKcal = list.reduce((a, m) => a + (m.total_kcal || macrosOf(m).kcal), 0);
  const order = ['kahvalti', 'ogle', 'ara', 'aksam'];
  const groups = order.map((t) => ({ t, items: list.filter((m) => m.meal_type === t) })).filter((g) => g.items.length);
  const other = list.filter((m) => !order.includes(m.meal_type));
  if (other.length) groups.push({ t: 'diger', items: other });

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div><h1 className="font-display font-bold text-2xl sm:text-[28px] leading-tight">Yemekler</h1><p className="text-muted text-sm mt-0.5">{!loading && !error ? `${list.length} öğün • ${Math.round(totalKcal)} kcal` : 'Seçili günün öğünleri.'}</p></div>
        <div className="flex items-center gap-2"><DateNav date={date} onChange={setDate} /><Button icon="plus" onClick={onAddMeal} className="hidden sm:inline-flex">Öğün ekle</Button></div>
      </header>

      {error ? <ErrorBanner message={error} onRetry={meals.reload} />
        : loading ? <MealsSkeleton />
        : list.length === 0 ? <Card className="p-2"><EmptyState icon="utensils" title="Henüz öğün eklenmemiş" hint="Doğal dille yaz (AI analiz etsin), barkod okut ya da fotoğraf yükle." action={<Button icon="plus" onClick={onAddMeal}>İlk öğünü ekle</Button>} /></Card>
        : (
          <div className="flex flex-col gap-6">
            {groups.map((g) => (
              <section key={g.t} className="flex flex-col gap-3">
                <div className="flex items-center gap-2 px-1">{g.t === 'diger' ? <Badge>Diğer</Badge> : <MealTypeBadge type={g.t} />}<span className="text-xs text-muted tnum">{Math.round(g.items.reduce((a, m) => a + (m.total_kcal || macrosOf(m).kcal), 0))} kcal</span></div>
                <div className="flex flex-col gap-3">{g.items.map((m) => <MealCard key={m.id} meal={m} onDelete={del} onEdit={onEditMeal} />)}</div>
              </section>
            ))}
          </div>
        )}
    </div>
  );
}
window.MealsScreen = MealsScreen;
