// app.jsx — Kabuk: sol nav + üst bar + tema + routing + toast + modallar + Tweaks
const { useState: useS, useEffect: useE } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "green",
  "surfaceTone": "fresh",
  "macroStyle": "bars",
  "addMealStyle": "tabs"
}/*EDITMODE-END*/;

const ACCENTS = {
  green: { l: ['#16a34a', '#dcfce7', '#166534'], d: ['#34d27b', '#14361f', '#6ee7a3'] },
  teal:  { l: ['#0d9488', '#ccfbf1', '#115e59'], d: ['#2dd4bf', '#0c332f', '#5eead4'] },
  lime:  { l: ['#65a30d', '#ecfccb', '#3f6212'], d: ['#a3e635', '#1f2e0a', '#bef264'] },
  ocean: { l: ['#0891b2', '#cffafe', '#155e75'], d: ['#22d3ee', '#08323b', '#67e8f4'] },
};
const TONES = {
  fresh:   { l: ['#f6f8f6', '#ffffff', '#f1f5f2', '#e7ebe8', '#18211c', '#5d6b62'], d: ['#0e1411', '#161e19', '#1d2722', '#283530', '#e7ede9', '#93a39a'] },
  neutral: { l: ['#f5f6f7', '#ffffff', '#f1f2f4', '#e6e8eb', '#1a1d21', '#626a73'], d: ['#0f1113', '#181b1e', '#212528', '#2c3136', '#e8eaed', '#949aa1'] },
  warm:    { l: ['#f8f6f2', '#fffdf9', '#f2efe9', '#eae4d9', '#211e19', '#6d655a'], d: ['#14110d', '#1d1a15', '#252118', '#332e23', '#ece7df', '#a39a8a'] },
};
function applyTheme(tw, dark) {
  const a = ACCENTS[tw.accent] || ACCENTS.green;
  const t = TONES[tw.surfaceTone] || TONES.fresh;
  const css = `:root{--accent:${a.l[0]};--accent-soft:${a.l[1]};--accent-text:${a.l[2]};--c-kcal:${a.l[0]};--bg:${t.l[0]};--surface:${t.l[1]};--surface-2:${t.l[2]};--border:${t.l[3]};--text:${t.l[4]};--text-muted:${t.l[5]};color-scheme:light;}
.dark{--accent:${a.d[0]};--accent-soft:${a.d[1]};--accent-text:${a.d[2]};--c-kcal:${a.d[0]};--bg:${t.d[0]};--surface:${t.d[1]};--surface-2:${t.d[2]};--border:${t.d[3]};--text:${t.d[4]};--text-muted:${t.d[5]};color-scheme:dark;}`;
  let el = document.getElementById('theme-vars');
  if (!el) { el = document.createElement('style'); el.id = 'theme-vars'; document.head.appendChild(el); }
  el.textContent = css;
  document.documentElement.classList.toggle('dark', dark);
}

const NAV = [
  { id: 'ozet', label: 'Özet', icon: 'dashboard' },
  { id: 'yemekler', label: 'Yemekler', icon: 'meals' },
  { id: 'antrenman', label: 'Antrenman', icon: 'dumbbell' },
  { id: 'karaliste', label: 'Kara Liste', icon: 'blacklist' },
  { id: 'profil', label: 'Profil', icon: 'profile' },
];

function useToast() {
  const [items, setItems] = useS([]);
  const toast = (msg, type = 'ok') => { const id = Date.now() + Math.random(); setItems((x) => [...x, { id, msg, type }]); setTimeout(() => setItems((x) => x.filter((i) => i.id !== id)), 2600); };
  const node = (
    <div className="fixed z-[60] bottom-24 sm:bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 pointer-events-none">
      {items.map((i) => (
        <div key={i.id} className="anim-pop pointer-events-auto flex items-center gap-2.5 rounded-full pl-3.5 pr-4 py-2.5 shadow-softlg surface bordered text-sm font-semibold">
          <span className="grid place-items-center h-5 w-5 rounded-full text-white shrink-0" style={{ background: i.type === 'error' ? '#e0568b' : 'var(--accent)' }}><Icon name={i.type === 'error' ? 'x' : 'check'} size={13} stroke={3} /></span>{i.msg}
        </div>
      ))}
    </div>
  );
  return [toast, node];
}

function Logo() {
  return (
    <div className="flex items-center gap-2.5">
      <span className="grid place-items-center h-9 w-9 rounded-xl text-white shrink-0" style={{ background: 'var(--accent)' }}><Icon name="leaf" size={20} /></span>
      <div className="leading-none"><div className="font-display font-bold text-[15px] tracking-tight">FitKoç</div><div className="text-[11px] text-muted">Beslenme & Fitness</div></div>
    </div>
  );
}

function Sidebar({ route, setRoute }) {
  return (
    <aside className="hidden md:flex flex-col w-60 shrink-0 surface bordered border-t-0 border-b-0 border-l-0 h-screen sticky top-0 p-4 gap-1">
      <div className="px-2 py-2 mb-3"><Logo /></div>
      {NAV.map((n) => {
        const active = route === n.id;
        return (
          <button key={n.id} onClick={() => setRoute(n.id)} className={cx('fr flex items-center gap-3 rounded-xl px-3 h-11 font-semibold text-[15px] transition', active ? 'shadow-soft' : 'text-muted hover:text-[var(--text)] hover:bg-[var(--surface-2)]')} style={active ? { background: 'var(--accent-soft)', color: 'var(--accent-text)' } : undefined}>
            <Icon name={n.icon} size={20} stroke={active ? 2.4 : 2} />{n.label}
          </button>
        );
      })}
      <div className="mt-auto rounded-xl surface-2 p-3.5 text-xs text-muted leading-relaxed"><span className="font-semibold" style={{ color: 'var(--accent-text)' }}>İpucu:</span> Öğünü doğal dille yaz — AI kalemlere ve makrolara ayırsın.</div>
    </aside>
  );
}

function BottomNav({ route, setRoute }) {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 surface bordered border-l-0 border-r-0 border-b-0 flex px-0.5 pb-[env(safe-area-inset-bottom)]">
      {NAV.map((n) => {
        const active = route === n.id;
        return (
          <button key={n.id} onClick={() => setRoute(n.id)} className="fr flex-1 flex flex-col items-center gap-0.5 py-2.5 min-w-0">
            <Icon name={n.icon} size={21} stroke={active ? 2.5 : 2} style={{ color: active ? 'var(--accent-text)' : 'var(--text-muted)' }} />
            <span className="text-[9.5px] font-semibold truncate max-w-full px-0.5" style={{ color: active ? 'var(--accent-text)' : 'var(--text-muted)' }}>{n.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

function TopBar({ dark, setDark, onSettings, onPlan, user, onLogout }) {
  return (
    <div className="sticky top-0 z-30 flex items-center justify-between gap-3 px-4 sm:px-6 lg:px-8 h-16 backdrop-blur bordered border-l-0 border-r-0 border-t-0" style={{ background: 'color-mix(in srgb, var(--surface) 82%, transparent)' }}>
      <div className="md:hidden"><Logo /></div>
      <div className="hidden md:block" />
      <div className="flex items-center gap-1.5">
        <button onClick={onPlan} title="Yemek planı yükle" className="fr grid h-10 w-10 place-items-center rounded-xl text-muted hover:bg-[var(--surface-2)]"><Icon name="upload" size={20} /></button>
        <button onClick={() => setDark(!dark)} title="Tema" className="fr grid h-10 w-10 place-items-center rounded-xl text-muted hover:bg-[var(--surface-2)]"><Icon name={dark ? 'sun' : 'moon'} size={20} /></button>
        <button onClick={onSettings} title="Ayarlar" className="fr grid h-10 w-10 place-items-center rounded-xl text-muted hover:bg-[var(--surface-2)]"><Icon name="settings" size={20} /></button>
        <div className="w-px h-6 mx-1" style={{ background: 'var(--border)' }} />
        {user && <UserMenu user={user} onLogout={onLogout} />}
      </div>
    </div>
  );
}

// Çerez/analitik onayı (Consent Mode v2) — yalnız GA aktifken ve henüz sorulmamışsa.
function ConsentBanner() {
  const [visible, setVisible] = useS(() => !!(window.analytics?.enabled && !window.analytics.consentAsked()));
  if (!visible) return null;
  const answer = (ok) => { window.analytics.setConsent(ok); setVisible(false); };
  return (
    <div className="fixed bottom-4 left-4 right-4 sm:left-auto sm:max-w-sm z-50 surface bordered rounded-2xl shadow-softlg p-4 anim-pop">
      <p className="text-sm">Deneyimi iyileştirmek için anonim kullanım istatistikleri toplayabilir miyiz? (Google Analytics)</p>
      <div className="flex gap-2 mt-3">
        <button onClick={() => answer(true)} className="fr flex-1 h-10 rounded-xl font-semibold text-white text-sm" style={{ background: 'var(--accent)' }}>Kabul et</button>
        <button onClick={() => answer(false)} className="fr flex-1 h-10 rounded-xl font-semibold text-sm bordered hover:bg-[var(--surface-2)]">Reddet</button>
      </div>
    </div>
  );
}

// Yemekler = Günlük (loglanan öğünler) + Tarifler (katalog/keşfet) tek sekmede.
function MealsHub({ date, setDate, demoState, onAddMeal, onEditMeal, refreshKey, toast, reloadAll, sub, setSub }) {
  const logRecipe = async (r) => {
    try {
      const mps = r.macros_per_serving || {};
      const kcal = mps.kcal
        || (r.total_kcal && r.servings ? Math.round(r.total_kcal / r.servings) : 0);
      await API.addMeal({ items: [{ raw_name: r.title_tr, quantity: 1, unit: 'porsiyon', kcal, protein_g: mps.protein_g || 0, carb_g: mps.carb_g || 0, fat_g: mps.fat_g || 0, confidence: 1 }] }, date);
      toast(`Öğüne eklendi: ${r.title_tr} (~${kcal} kcal)`);
      window.analytics?.trackEvent('recipe_logged', { recipe: r.slug || r.title_tr, kcal });
      reloadAll();
      setSub('gunluk');
    } catch (e) { toast('Eklenemedi: ' + (e.message || e), 'error'); }
  };
  return (
    <div className="flex flex-col gap-5">
      <div className="max-w-sm"><Segmented value={sub} onChange={setSub} options={[{ value: 'gunluk', label: 'Günlük', icon: 'meals' }, { value: 'tarifler', label: 'Tarifler', icon: 'recipes' }]} /></div>
      {sub === 'tarifler'
        ? <RecipesScreen key={'r' + refreshKey} demoState={demoState} onLog={logRecipe} />
        : <MealsScreen key={'m' + refreshKey + date} date={date} setDate={setDate} demoState={demoState} onAddMeal={onAddMeal} onEditMeal={onEditMeal} refreshKey={refreshKey} />}
    </div>
  );
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [user, login, logout, authLoading] = useAuth();
  const [route, setRoute] = useS(() => localStorage.getItem('fk.route') || 'ozet');
  const [date, setDate] = useS(API.todayStr());
  const [dark, setDark] = useS(() => { const v = localStorage.getItem('fk.dark'); return v == null ? window.matchMedia('(prefers-color-scheme: dark)').matches : v === '1'; });
  const [addOpen, setAddOpen] = useS(false);
  const [editMeal, setEditMeal] = useS(null);
  const [wizardOpen, setWizardOpen] = useS(false);
  const [setOpen, setSetOpen] = useS(false);
  const [planOpen, setPlanOpen] = useS(false);
  const [mealsSub, setMealsSub] = useS(() => localStorage.getItem('fk.mealsSub') || 'gunluk');
  const [refreshKey, setRefreshKey] = useS(0);
  const [toast, toastNode] = useToast();

  useE(() => { applyTheme(t, dark); }, [t.accent, t.surfaceTone, dark]);
  useE(() => { localStorage.setItem('fk.dark', dark ? '1' : '0'); }, [dark]);
  useE(() => { localStorage.setItem('fk.route', route); window.analytics?.trackPageView(route); }, [route]);
  useE(() => { localStorage.setItem('fk.mealsSub', mealsSub); }, [mealsSub]);

  const demoState = 'normal';
  const reloadAll = () => setRefreshKey((k) => k + 1);

  // Supabase oturumu async çözülürken login ekranı parlamasın.
  if (authLoading) {
    return (
      <div className="min-h-screen grid place-items-center" style={{ background: 'var(--bg)' }}>
        <span className="grid place-items-center h-12 w-12 rounded-2xl text-white anim-fade" style={{ background: 'var(--accent)' }}><Icon name="leaf" size={26} /></span>
      </div>
    );
  }
  if (!user) return <AuthScreen onAuthed={login} />;

  const screen = (() => {
    const k = refreshKey + date;
    switch (route) {
      case 'ozet': return <DashboardScreen key={'d' + k} date={date} setDate={setDate} demoState={demoState} ringLayout={t.macroStyle} onAddMeal={() => setAddOpen(true)} onOpenWizard={() => setWizardOpen(true)} onGoWorkout={() => setRoute('antrenman')} onGoRecipes={() => { setMealsSub('tarifler'); setRoute('yemekler'); }} />;
      case 'yemekler': return <MealsHub key={'m' + k} date={date} setDate={setDate} demoState={demoState} onAddMeal={() => setAddOpen(true)} onEditMeal={setEditMeal} refreshKey={refreshKey} toast={toast} reloadAll={reloadAll} sub={mealsSub} setSub={setMealsSub} />;
      case 'antrenman': return <WorkoutScreen key={'w' + k} date={date} setDate={setDate} demoState={demoState} toast={toast} />;
      case 'karaliste': return <BlacklistScreen key={'b' + refreshKey} demoState={demoState} />;
      case 'profil': return <ProfileScreen key={'p' + refreshKey} demoState={demoState} toast={toast} onOpenWizard={() => setWizardOpen(true)} refreshKey={refreshKey} />;
      default: return null;
    }
  })();

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--bg)' }}>
      <Sidebar route={route} setRoute={setRoute} />
      <div className="flex-1 min-w-0 flex flex-col">
        <TopBar dark={dark} setDark={setDark} onSettings={() => setSetOpen(true)} onPlan={() => setPlanOpen(true)} user={user} onLogout={logout} />
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6 pb-28 md:pb-10 max-w-5xl w-full mx-auto anim-fade" key={route}>{screen}</main>
      </div>

      <BottomNav route={route} setRoute={setRoute} />
      <button onClick={() => setAddOpen(true)} className="fr md:hidden fixed right-5 bottom-24 z-40 grid h-14 w-14 place-items-center rounded-full text-white shadow-softlg" style={{ background: 'var(--accent)' }}><Icon name="plus" size={26} stroke={2.5} /></button>

      <AddMealModal open={addOpen} onClose={() => setAddOpen(false)} date={date} methodStyle={t.addMealStyle} onAdded={reloadAll} toast={toast} />
      <EditMealModal open={!!editMeal} meal={editMeal} onClose={() => setEditMeal(null)} onSaved={reloadAll} toast={toast} />
      <GoalWizardModal open={wizardOpen} onClose={() => setWizardOpen(false)} toast={toast} onApplied={reloadAll} />
      <SettingsModal open={setOpen} onClose={() => setSetOpen(false)} toast={toast} onChanged={reloadAll} />
      <MealPlanModal open={planOpen} onClose={() => setPlanOpen(false)} toast={toast} onApplied={reloadAll} />

      {toastNode}
      <ConsentBanner />

      <TweaksPanel>
        <TweakSection label="Görsel stil" />
        <TweakColor label="Accent" value={{ green: '#16a34a', teal: '#0d9488', lime: '#65a30d', ocean: '#0891b2' }[t.accent]} options={['#16a34a', '#0d9488', '#65a30d', '#0891b2']} onChange={(v) => setTweak('accent', { '#16a34a': 'green', '#0d9488': 'teal', '#65a30d': 'lime', '#0891b2': 'ocean' }[v] || 'green')} />
        <TweakRadio label="Yüzey tonu" value={t.surfaceTone} options={['fresh', 'neutral', 'warm']} onChange={(v) => setTweak('surfaceTone', v)} />
        <TweakToggle label="Koyu tema" value={dark} onChange={setDark} />
        <TweakSection label="Özet düzeni" />
        <TweakRadio label="Makro gösterimi" value={t.macroStyle} options={['bars', 'rings', 'hero']} onChange={(v) => setTweak('macroStyle', v)} />
        <TweakSection label="Öğün ekleme" />
        <TweakRadio label="Yöntem seçimi" value={t.addMealStyle} options={['tabs', 'tiles']} onChange={(v) => setTweak('addMealStyle', v)} />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
