// screens-workout.jsx — ANTRENMAN (detaylı seans + amaç/deneyim + kas haritası + log)
const { useState: useStateW } = React;

const MUSCLES = [
  { v: 'gogus', l: 'Göğüs' }, { v: 'sirt', l: 'Sırt' }, { v: 'omuz', l: 'Omuz' },
  { v: 'bacak', l: 'Bacak' }, { v: 'karin', l: 'Karın' }, { v: 'kol', l: 'Kol' }, { v: 'kardiyo', l: 'Kardiyo' },
];
const LEVELS = { beginner: 'Başlangıç', intermediate: 'Orta', expert: 'İleri' };
const GOALS = [{ v: 'kilo_ver', l: 'Kilo ver' }, { v: 'kas_yap', l: 'Kas yap' }, { v: 'koru', l: 'Koru' }];
const WDAYS = ['Paz', 'Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt'];
const mLabel = (k) => (window.MUSCLE_LABELS && window.MUSCLE_LABELS[k]) || k;

// Hareket detay + loglama (kas haritalı + alternatifler + makine tarifi)
function ExerciseModal({ open, onClose, exercise, onSaved, toast }) {
  const [cur, setCur] = useStateW(exercise);
  const [sets, setSets] = useStateW(4);
  const [reps, setReps] = useStateW(10);
  const [minutes, setMinutes] = useStateW(30);
  const [busy, setBusy] = useStateW(false);
  React.useEffect(() => { if (open && exercise) setCur(exercise); }, [open, exercise]);
  React.useEffect(() => { if (cur) { const cardio = cur.category === 'kardiyo'; setSets(cardio ? 1 : (typeof cur.sets === 'number' ? cur.sets : 4)); setReps(cardio ? 1 : (parseInt(cur.reps) || 10)); setMinutes(cur.minutes || (cardio ? 30 : 25)); } }, [cur]);
  if (!cur) return null;
  const cardio = cur.category === 'kardiyo';
  const catalog = (window.API.EXERCISES || []);
  const base = catalog.find((e) => e.slug === cur.slug) || cur;
  // alternatifleri ekipman tipine göre grupla
  const groups = {};
  catalog.filter((e) => e.slug !== cur.slug && e.primary_muscle === base.primary_muscle).forEach((e) => { (groups[e.equipment_type] = groups[e.equipment_type] || []).push(e); });
  const TYPE_ORDER = ['makine', 'serbest', 'vücut'];
  const howto = base.machine_howto;
  const instr = base.instructions || cur.instructions || [];
  const save = async () => { setBusy(true); try { const r = await onSaved({ template_slug: cur.slug, sets: cardio ? null : sets, reps: cardio ? null : reps, minutes }); toast(`Loglandı: ~${r.kcal} kcal yakıldı`); onClose(); } catch { toast('Loglanamadı', 'error'); } finally { setBusy(false); } };
  const switchTo = (e) => setCur({ ...e });
  return (
    <Modal open={open} onClose={onClose} title={cur.name_tr} size="lg" footer={<><Button variant="ghost" onClick={onClose}>Kapat</Button><Button icon="check" onClick={save} disabled={busy}>{busy ? 'Kaydediliyor…' : 'Antrenmana ekle'}</Button></>}>
      <div className="flex flex-col gap-4 pb-2">
        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <div className="shrink-0 rounded-2xl surface-2 bordered p-2"><MuscleMap primary={[base.primary_muscle]} secondary={base.secondary} size={150} /></div>
          <div className="flex-1 flex flex-col gap-2.5 w-full">
            <div className="flex items-center gap-1.5 flex-wrap"><Badge tone="accent"><Icon name="dumbbell" size={12} />{base.equipment}</Badge><Badge>{(window.API.EQ_TYPE_LABEL && window.API.EQ_TYPE_LABEL[base.equipment_type]) || base.equipment_type}</Badge>{base.level && <Badge>{LEVELS[base.level] || base.level}</Badge>}</div>
            <div>
              <div className="text-xs text-muted font-semibold mb-1">Çalışan kaslar</div>
              <div className="flex gap-1.5 flex-wrap">
                <Chip color="var(--accent)">{mLabel(base.primary_muscle)}</Chip>
                {(base.secondary || []).map((m) => <span key={m} className="inline-flex items-center gap-1.5 rounded-full surface-2 bordered px-3 py-1.5 text-sm text-muted"><span className="h-2 w-2 rounded-full" style={{ background: 'color-mix(in srgb, var(--accent) 45%, var(--surface-2))' }} />{mLabel(m)}</span>)}
              </div>
            </div>
          </div>
        </div>

        {/* Nasıl yapılır */}
        {instr.length > 0 && (
          <div className="rounded-xl surface-2 p-3.5">
            <div className="text-sm font-semibold mb-2 flex items-center gap-1.5"><Icon name="info" size={15} className="text-accent-text" />Nasıl yapılır</div>
            <ol className="flex flex-col gap-1.5">{instr.map((s, i) => <li key={i} className="flex gap-2 text-sm"><span className="text-muted tnum">{i + 1}.</span><span className="leading-snug">{s}</span></li>)}</ol>
          </div>
        )}

        {/* Makine kullanım tarifi */}
        {howto && (
          <div className="rounded-xl px-3.5 py-3 flex items-start gap-2.5" style={{ background: 'color-mix(in srgb, var(--accent) 9%, var(--surface))', border: '1px solid color-mix(in srgb, var(--accent) 24%, transparent)' }}>
            <span className="grid place-items-center h-8 w-8 rounded-lg shrink-0" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}><Icon name="settings" size={16} /></span>
            <div><div className="text-sm font-semibold">Makine nasıl kullanılır</div><p className="text-sm text-muted leading-relaxed mt-0.5">{howto}</p></div>
          </div>
        )}

        {/* Alternatifler — tipe göre */}
        {TYPE_ORDER.some((t) => groups[t] && groups[t].length) && (
          <div className="flex flex-col gap-2">
            <div className="text-sm font-semibold">Alternatif hareketler</div>
            {TYPE_ORDER.filter((t) => groups[t] && groups[t].length).map((t) => (
              <div key={t} className="flex items-start gap-2">
                <span className="text-xs font-semibold text-muted w-28 shrink-0 pt-1.5">{(window.API.EQ_TYPE_LABEL && window.API.EQ_TYPE_LABEL[t]) || t}</span>
                <div className="flex flex-wrap gap-1.5">{groups[t].map((e) => <button key={e.slug} onClick={() => switchTo(e)} className="fr inline-flex items-center gap-1.5 rounded-full surface-2 bordered px-3 py-1.5 text-sm hover:bg-[var(--surface)] transition"><Icon name="refresh" size={12} />{e.name_tr}</button>)}</div>
              </div>
            ))}
          </div>
        )}

        <div className="h-px" style={{ background: 'var(--border)' }} />
        <div className="text-sm font-semibold">Bu hareketi logla</div>
        {!cardio && <div className="grid grid-cols-2 gap-4"><Field label="Set"><Stepper value={sets} onChange={setSets} min={1} max={12} /></Field><Field label="Tekrar"><Stepper value={reps} onChange={setReps} min={1} max={50} /></Field></div>}
        <Field label="Süre (dakika)"><Stepper value={minutes} onChange={setMinutes} min={1} max={180} step={5} suffix="dk" /></Field>
        <p className="flex items-center gap-1.5 text-xs text-muted"><Icon name="info" size={13} />Yakılan kalori kiloya ve MET değerine göre tahmin edilir.</p>
      </div>
    </Modal>
  );
}

function ExerciseRow({ ex, idx, onOpen }) {
  const [alt, setAlt] = useStateW(false);
  const cur = alt && ex.alternative ? { ...ex.alternative, primary_muscle: ex.primary_muscle, secondary: ex.secondary, category: ex.category } : ex;
  return (
    <div className="flex items-center gap-3 rounded-xl surface-2 px-3 py-2.5">
      <span className="grid place-items-center h-7 w-7 rounded-lg shrink-0 font-display font-semibold text-xs" style={{ background: 'var(--surface)', color: 'var(--accent-text)' }}>{idx + 1}</span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <button onClick={() => onOpen(cur)} className="fr text-sm font-semibold hover:underline truncate text-left">{cur.name_tr}</button>
          <span className="inline-flex items-center gap-1 text-[11px] text-muted"><Icon name="dumbbell" size={11} />{cur.equipment}</span>
          {ex.finisher && <span className="text-[10px] font-semibold rounded-full px-1.5 py-0.5" style={{ background: 'color-mix(in srgb, var(--c-fat) 14%, transparent)', color: 'var(--c-fat)' }}>Kapanış kardiyosu</span>}
        </div>
        <div className="flex items-center gap-2 mt-0.5 flex-wrap">
          <span className="text-xs font-semibold tnum" style={{ color: 'var(--accent-text)' }}>{ex.category === 'kardiyo' ? ex.reps : `${ex.sets} × ${ex.reps}`}</span>
          {ex.rest > 0 && <span className="text-[11px] text-muted">· {ex.rest}sn dinlenme</span>}
          <span className="text-[11px] rounded-full px-1.5 py-0.5" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}>{mLabel(cur.primary_muscle)}</span>
        </div>
        {ex.alternative && <button onClick={() => setAlt(!alt)} className="fr text-[11px] text-muted hover:text-[var(--accent-text)] inline-flex items-center gap-1 mt-1"><Icon name="refresh" size={11} />{alt ? `Asıl: ${ex.name_tr}` : `Alternatif: ${ex.alternative.name_tr}`}</button>}
      </div>
      <button onClick={() => onOpen(cur)} className="fr shrink-0 grid h-8 w-8 place-items-center rounded-lg text-muted hover:text-[var(--accent-text)] hover:bg-[var(--surface)]"><Icon name="chevronR" size={16} /></button>
    </div>
  );
}

function DayCard({ d, isToday, onOpen, warmup }) {
  const [open, setOpen] = useStateW(isToday);
  return (
    <Card className="overflow-hidden" style={isToday ? { boxShadow: 'inset 0 0 0 1.5px var(--accent), var(--tw-shadow,0 0 0 0)' } : undefined}>
      <button onClick={() => setOpen(!open)} className="fr w-full flex items-center gap-3 p-3.5 text-left hover:bg-[var(--surface-2)] transition">
        <span className="grid place-items-center h-10 w-10 rounded-xl shrink-0 font-display font-semibold text-sm" style={{ background: isToday ? 'var(--accent)' : 'var(--surface-2)', color: isToday ? '#fff' : 'var(--text-muted)' }}>{d.day}</span>
        <div className="min-w-0 flex-1"><div className="font-semibold truncate">{d.title}</div><div className="text-xs text-muted capitalize">{d.kind} · {d.exercises.length} hareket · ~{d.minutes} dk</div></div>
        {isToday && <Badge tone="accent">Bugün</Badge>}
        <Icon name="chevronD" size={18} className={cx('text-muted transition-transform shrink-0', open && 'rotate-180')} />
      </button>
      {open && (
        <div className="px-3.5 pb-3.5 anim-fade flex flex-col gap-3">
          {d.worked && (d.worked.primary.length > 0) && (
            <div className="flex items-center gap-3 rounded-xl surface-2 px-3 py-2.5">
              <div className="shrink-0"><MuscleMap primary={d.worked.primary} secondary={d.worked.secondary} size={72} /></div>
              <div className="min-w-0">
                <div className="text-xs font-semibold text-muted mb-1">Bu gün çalışan bölgeler</div>
                <div className="flex flex-wrap gap-1.5">
                  {d.worked.primary.map((m) => <Badge key={m} tone="accent">{mLabel(m)}</Badge>)}
                  {d.worked.secondary.map((m) => <span key={m} className="text-xs rounded-full surface bordered px-2 py-0.5 text-muted">{mLabel(m)}</span>)}
                </div>
              </div>
            </div>
          )}
          {warmup && <div className="flex items-start gap-2 text-xs text-muted px-1"><Icon name="flame" size={13} className="mt-0.5 shrink-0" style={{ color: 'var(--c-carb)' }} />{warmup}</div>}
          {d.exercises.map((ex, i) => <ExerciseRow key={i} ex={ex} idx={i} onOpen={onOpen} />)}
        </div>
      )}
    </Card>
  );
}

function ExerciseCard({ ex, onOpen }) {
  return (
    <Card className="p-4 flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <div className="shrink-0 rounded-xl surface-2 p-1"><MuscleMap primary={[ex.primary_muscle]} secondary={ex.secondary} size={56} showBack={false} /></div>
        <div className="min-w-0 flex-1"><h3 className="font-display font-semibold leading-tight truncate">{ex.name_tr}</h3><div className="text-xs text-muted mt-0.5 capitalize">{ex.equipment}</div></div>
      </div>
      <div className="flex items-center gap-1.5 flex-wrap"><Badge tone="accent">{mLabel(ex.primary_muscle)}</Badge><Badge>{LEVELS[ex.level] || ex.level}</Badge></div>
      <Button size="sm" variant="soft" icon="chevronR" onClick={() => onOpen(ex)} className="w-full mt-auto">Detay & ekle</Button>
    </Card>
  );
}

function WorkoutScreen({ date, setDate, demoState, toast }) {
  const WEEK = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];
  const [goal, setGoal] = useStateW(() => localStorage.getItem('fk.wgoal') || '');
  const [level, setLevel] = useStateW(() => localStorage.getItem('fk.wlevel') || 'intermediate');
  const [trainDays, setTrainDays] = useStateW(null);
  const [muscle, setMuscle] = useStateW('');
  const [libLevel, setLibLevel] = useStateW('');
  const [q, setQ] = useStateW('');
  const [exModal, setExModal] = useStateW(null);
  const [logKey, setLogKey] = useStateW(0);

  const goalR = useResource(() => API.goal().catch(() => ({ goal_type: 'koru' })), []);
  const planPrefs = useResource(() => API.getPlan().catch(() => null), []);
  React.useEffect(() => { if (trainDays == null) setTrainDays((planPrefs.data && planPrefs.data.training_days) || ['Pzt', 'Sal', 'Per', 'Cmt']); }, [planPrefs.data]);

  const effGoal = goal || (goalR.data && goalR.data.goal_type) || 'koru';
  const td = trainDays || ['Pzt', 'Sal', 'Per', 'Cmt'];
  const dpw = td.length;
  const plan = useResource(() => API.workoutPlan(effGoal, level, dpw, td), [effGoal, level, td.join(','), dpw]);
  const exs = useResource(() => API.workouts({ muscle, level: libLevel, q }), [muscle, libLevel, q]);
  const logs = useResource(() => API.workoutLogs(date), [date, logKey]);

  React.useEffect(() => { if (goal) localStorage.setItem('fk.wgoal', goal); }, [goal]);
  React.useEffect(() => { localStorage.setItem('fk.wlevel', level); }, [level]);

  const toggleDay = (d) => {
    let next = td.includes(d) ? td.filter((x) => x !== d) : [...td, d];
    if (next.length < 1) return; if (next.length > 6) return;
    next = WEEK.filter((w) => next.includes(w));
    setTrainDays(next); API.savePlan({ training_days: next, days_per_week: next.length });
  };

  const loading = demoState === 'loading' || plan.loading || goalR.loading || trainDays == null;
  const error = demoState === 'error' ? 'Antrenman verisi yüklenemedi.' : plan.error;
  const todayAbbr = WEEK[(new Date(date + 'T00:00:00').getDay() + 6) % 7];
  const logList = demoState === 'empty' ? [] : (logs.data || []);
  const burned = logList.reduce((a, l) => a + (l.kcal || 0), 0);
  const doneMin = logList.reduce((a, l) => a + (l.minutes || 0), 0);

  const saveLog = async (payload) => { const r = await API.addWorkoutLog(payload, date); setLogKey((k) => k + 1); return r; };
  const delLog = async (l) => { logs.setData(logList.filter((x) => x.id !== l.id)); try { await API.deleteWorkoutLog(l.id); } catch { logs.reload(); } };

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div><h1 className="font-display font-bold text-2xl sm:text-[28px] leading-tight">Antrenman</h1><p className="text-muted text-sm mt-0.5">Seçtiğin günlere göre sıralı, set-tekrarlı plan; her seans ağırlık + kardiyo.</p></div>
        <DateNav date={date} onChange={setDate} />
      </header>

      {/* Amaç & deneyim & günler */}
      <Card className="p-4 flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex items-center gap-2 shrink-0 w-28"><Icon name="target" size={16} className="text-accent-text" /><span className="text-sm font-semibold">Amacın</span></div>
          <div className="flex-1"><Segmented value={effGoal} onChange={setGoal} options={GOALS.map((g) => ({ value: g.v, label: g.l }))} /></div>
          <Select value={level} onChange={(e) => setLevel(e.target.value)} className="sm:w-40 shrink-0">{Object.entries(LEVELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}</Select>
        </div>
        <div className="h-px" style={{ background: 'var(--border)' }} />
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex items-center gap-2 shrink-0 w-28"><Icon name="calendar" size={16} className="text-accent-text" /><span className="text-sm font-semibold">Antrenman günleri</span></div>
          <div className="flex-1 flex flex-wrap gap-1.5">
            {WEEK.map((d) => { const on = td.includes(d); return <button key={d} onClick={() => toggleDay(d)} className={cx('fr h-9 w-11 rounded-lg text-sm font-semibold bordered transition', on ? 'shadow-soft' : 'surface-2 text-muted hover:text-[var(--text)]')} style={on ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>{d}</button>; })}
          </div>
          <Badge tone="accent" className="shrink-0">Haftada {dpw} gün</Badge>
        </div>
      </Card>

      {error ? <ErrorBanner message={error} onRetry={plan.reload} />
        : loading ? <div className="flex flex-col gap-4"><Skel style={{ height: 90, borderRadius: 16 }} /><Skel style={{ height: 260, borderRadius: 16 }} /></div>
        : (
          <>
            <div className="grid lg:grid-cols-[1fr_300px] gap-4 items-start">
              <div className="flex flex-col gap-3">
                <div className="flex items-center gap-2 px-1 flex-wrap"><Icon name="dumbbell" size={16} className="text-accent-text" /><h3 className="font-display font-semibold text-lg">Haftalık plan</h3><Badge tone="accent" className="capitalize">{plan.data.focus}</Badge><span className="text-xs text-muted ml-auto">{plan.data.weekly_minutes} dk/hafta</span></div>
                <div className="flex items-start gap-2 text-xs text-muted px-1"><Icon name="info" size={13} className="mt-0.5 shrink-0" style={{ color: 'var(--accent-text)' }} />{plan.data.structure_note}</div>
                {plan.data.days.map((d, i) => <DayCard key={i} d={d} isToday={d.day === todayAbbr} onOpen={setExModal} warmup={plan.data.warmup} />)}
                <p className="flex items-start gap-2 text-xs text-muted px-1"><Icon name="info" size={13} className="mt-0.5 shrink-0" />{plan.data.note}</p>
              </div>
              <Card className="p-5 flex flex-col gap-4 lg:sticky lg:top-20">
                <h3 className="font-display font-semibold">Bugün</h3>
                <div className="grid grid-cols-2 gap-2.5">
                  <div className="rounded-xl surface-2 px-3.5 py-3"><div className="text-xs text-muted">Yakılan</div><div className="font-display font-semibold text-xl tnum" style={{ color: 'var(--c-fat)' }}>{Math.round(burned)}<span className="text-xs text-muted ml-1">kcal</span></div></div>
                  <div className="rounded-xl surface-2 px-3.5 py-3"><div className="text-xs text-muted">Süre</div><div className="font-display font-semibold text-xl tnum">{doneMin}<span className="text-xs text-muted ml-1">dk</span></div></div>
                </div>
                {logList.length === 0 ? <div className="text-sm text-muted text-center py-2">Bugün antrenman loglanmadı.</div>
                  : <ul className="flex flex-col gap-2">{logList.map((l) => (
                      <li key={l.id} className="flex items-center gap-2 rounded-lg surface-2 px-3 py-2 group"><Icon name="check" size={14} stroke={3} style={{ color: 'var(--accent-text)' }} /><span className="text-sm font-medium flex-1 truncate">{l.name_tr}</span><span className="text-xs text-muted tnum">{l.minutes}dk</span><button onClick={() => delLog(l)} className="fr opacity-0 group-hover:opacity-100 text-muted hover:text-[var(--c-fat)]"><Icon name="x" size={14} /></button></li>
                    ))}</ul>}
              </Card>
            </div>

            <section className="flex flex-col gap-3">
              <div className="flex items-center gap-2"><Icon name="filter" size={16} className="text-accent-text" /><h3 className="font-display font-semibold text-lg">Hareket kütüphanesi</h3></div>
              <div className="flex flex-col sm:flex-row gap-2.5">
                <div className="relative flex-1"><span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted"><Icon name="search" size={18} /></span><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Hareket ara…" className="pl-11" /></div>
                <Select value={libLevel} onChange={(e) => setLibLevel(e.target.value)} className="sm:w-44"><option value="">Tüm seviyeler</option>{Object.entries(LEVELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}</Select>
              </div>
              <div className="flex gap-2 flex-wrap">
                <button onClick={() => setMuscle('')} className={cx('fr rounded-full px-3.5 py-1.5 text-sm font-semibold bordered transition', !muscle ? 'shadow-soft' : 'surface-2 text-muted')} style={!muscle ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>Tümü</button>
                {MUSCLES.map((mm) => <button key={mm.v} onClick={() => setMuscle(mm.v)} className={cx('fr rounded-full px-3.5 py-1.5 text-sm font-semibold bordered transition', muscle === mm.v ? 'shadow-soft' : 'surface-2 text-muted')} style={muscle === mm.v ? { background: 'var(--accent-soft)', color: 'var(--accent-text)', borderColor: 'var(--accent)' } : undefined}>{mm.l}</button>)}
              </div>
              {exs.loading ? <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{[0, 1, 2].map((i) => <Skel key={i} style={{ height: 150, borderRadius: 16 }} />)}</div>
                : (exs.data || []).length === 0 ? <Card className="p-2"><EmptyState icon="dumbbell" title="Hareket bulunamadı" hint="Filtreleri değiştirip tekrar dene." /></Card>
                : <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{exs.data.map((ex) => <ExerciseCard key={ex.id} ex={ex} onOpen={setExModal} />)}</div>}
            </section>
          </>
        )}

      <ExerciseModal open={!!exModal} exercise={exModal} onClose={() => setExModal(null)} onSaved={saveLog} toast={toast} />
    </div>
  );
}
window.WorkoutScreen = WorkoutScreen;
