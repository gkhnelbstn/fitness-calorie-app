// screens-recipes.jsx — TARİFLER (detaylı: porsiyon/makro, etiket, not, cook-with)
const { useState: useStateR, useEffect: useEffectR } = React;
const RECIPES_PAGE = 24;

function ChipInput({ items, setItems, placeholder, color }) {
  const [val, setVal] = useStateR('');
  const add = () => { const v = val.trim(); if (v && !items.includes(v)) setItems([...items, v]); setVal(''); };
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl bordered surface-2 px-2.5 py-2 min-h-[44px]">
      {items.map((it) => <Chip key={it} color={color} onRemove={() => setItems(items.filter((x) => x !== it))}>{it}</Chip>)}
      <input value={val} onChange={(e) => setVal(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add(); } if (e.key === 'Backspace' && !val && items.length) setItems(items.slice(0, -1)); }} placeholder={items.length ? '' : placeholder} className="fr flex-1 min-w-[120px] bg-transparent px-1.5 h-8 text-sm outline-none" />
    </div>
  );
}
window.ChipInput = ChipInput;

function IngredientRow({ ing }) {
  const qty = ing.quantity != null ? `${ing.quantity}${ing.unit ? ' ' + ing.unit : ''} ` : '';
  if (ing.status === 'removed') return <li className="flex items-center gap-2 text-sm"><Icon name="x" size={13} style={{ color: 'var(--c-carb)' }} /><span className="line-through" style={{ color: 'var(--c-carb)' }}>{qty}{ing.raw_name}</span><span className="text-xs text-muted">çıkarıldı</span></li>;
  if (ing.status === 'substituted') return <li className="flex items-center gap-2 text-sm flex-wrap" style={{ color: 'var(--c-prot)' }}><Icon name="refresh" size={13} /><span className="font-medium">{qty}{ing.raw_name}</span><span>→ {ing.substitute}</span></li>;
  return <li className="flex items-center gap-2 text-sm"><span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ background: 'var(--accent)' }} /><span>{qty}{ing.raw_name}</span>{ing.optional && <span className="text-xs text-muted">(opsiyonel)</span>}</li>;
}

function RecipeCard({ recipe, defaultOpen }) {
  const [open, setOpen] = useStateR(defaultOpen || false);
  const mps = recipe.macros_per_serving || (recipe.total_kcal && recipe.servings ? { kcal: Math.round(recipe.total_kcal / recipe.servings) } : null);
  return (
    <Card className="overflow-hidden flex flex-col">
      <div className="flex gap-4 p-4 sm:p-5">
        {recipe.image_url
          ? <img src={recipe.image_url} alt={recipe.title_tr} loading="lazy" className="h-24 w-24 sm:h-28 sm:w-28 shrink-0 rounded-xl object-cover bordered" onError={(e) => { e.target.style.display = 'none'; }} />
          : <ImgPlaceholder className="h-24 w-24 sm:h-28 sm:w-28 shrink-0" label="tarif" />}
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-display font-semibold text-lg leading-tight">{recipe.title_tr}</h3>
            {recipe.match != null && <Badge tone="accent">{recipe.match}/{recipe.total_have} eşleşme</Badge>}
          </div>
          <div className="flex items-center gap-x-3 gap-y-1 mt-1.5 text-xs text-muted flex-wrap">
            {recipe.region && <span className="inline-flex items-center gap-1"><Icon name="leaf" size={13} />{recipe.region}</span>}
            {recipe.cook_minutes && <span className="inline-flex items-center gap-1"><Icon name="clock" size={13} />{recipe.cook_minutes} dk</span>}
            {recipe.servings && <span className="inline-flex items-center gap-1"><Icon name="utensils" size={13} />{recipe.servings} porsiyon</span>}
            {recipe.difficulty && <span className="capitalize">{recipe.difficulty}</span>}
          </div>
          {mps && (
            <div className="flex items-center gap-3 mt-2.5 text-xs tnum">
              <span className="font-semibold" style={{ color: 'var(--c-kcal)' }}>{mps.kcal} kcal</span>
              {mps.protein_g != null && <span style={{ color: 'var(--c-prot)' }}>P {mps.protein_g}g</span>}
              {mps.carb_g != null && <span style={{ color: 'var(--c-carb)' }}>K {mps.carb_g}g</span>}
              {mps.fat_g != null && <span style={{ color: 'var(--c-fat)' }}>Y {mps.fat_g}g</span>}
              {mps.fiber_g != null && <span className="text-muted">Lif {mps.fiber_g}g</span>}
              <span className="text-muted">/ porsiyon</span>
            </div>
          )}
          {recipe.tags && recipe.tags.length > 0 && <div className="flex gap-1.5 flex-wrap mt-2.5">{recipe.tags.map((t) => <span key={t} className="text-[11px] rounded-full surface-2 bordered px-2 py-0.5 text-muted">#{t}</span>)}</div>}
        </div>
      </div>

      <div className="px-4 sm:px-5 pb-1">
        <div className="text-xs font-semibold text-muted mb-1.5">Malzemeler</div>
        <ul className="flex flex-col gap-1">{recipe.ingredients.map((ing, i) => <IngredientRow key={i} ing={ing} />)}</ul>
      </div>

      {recipe.notes && recipe.notes.length > 0 && (
        <div className="mx-4 sm:mx-5 mt-3 rounded-xl px-3.5 py-2.5 flex flex-col gap-1" style={{ background: 'color-mix(in srgb, var(--accent) 8%, var(--surface))', border: '1px solid color-mix(in srgb, var(--accent) 22%, transparent)' }}>
          {recipe.notes.map((n, i) => <div key={i} className="flex items-start gap-2 text-xs"><Icon name="info" size={13} className="mt-0.5 shrink-0" style={{ color: 'var(--accent-text)' }} /><span>{n}</span></div>)}
        </div>
      )}

      <button onClick={() => setOpen(!open)} className="fr flex items-center justify-between px-4 sm:px-5 py-3 mt-3 bordered border-l-0 border-r-0 border-b-0 text-sm font-semibold hover:bg-[var(--surface-2)] transition">
        <span className="inline-flex items-center gap-2"><Icon name="recipes" size={15} className="text-accent-text" />Hazırlanışı ({recipe.steps.length} adım)</span>
        <span className={cx('transition-transform', open && 'rotate-180')}><Icon name="chevronD" size={18} /></span>
      </button>
      {open && <ol className="flex flex-col gap-2.5 px-4 sm:px-5 py-4 anim-fade surface-2">{recipe.steps.map((s, i) => <li key={i} className="flex gap-3 text-sm"><span className="grid place-items-center h-6 w-6 shrink-0 rounded-full font-display font-semibold text-xs" style={{ background: 'var(--accent-soft)', color: 'var(--accent-text)' }}>{i + 1}</span><span className="leading-relaxed pt-0.5">{s}</span></li>)}</ol>}
    </Card>
  );
}

function RecipesScreen({ demoState }) {
  const [tab, setTab] = useStateR('ara');
  const [q, setQ] = useStateR('');
  const [exclude, setExclude] = useStateR([]);
  const [have, setHave] = useStateR(['bulgur', 'soğan']);
  const [webSearch, setWebSearch] = useStateR(false);

  // "Tarif ara" sekmesi sayfalı (load-more). Filtre değişince sıfırlanır.
  const [sItems, setSItems] = useStateR([]);
  const [sHidden, setSHidden] = useStateR([]);
  const [sOffset, setSOffset] = useStateR(0);
  const [sHasMore, setSHasMore] = useStateR(false);
  const [sLoading, setSLoading] = useStateR(false);
  const [sError, setSError] = useStateR(null);

  const fetchRecipes = async (off, reset) => {
    setSLoading(true);
    setSError(null);
    try {
      // Canlı arama yalnız ilk sayfada (off=0) — sonraki sayfalar yerelden.
      const r = await API.recipes(q, exclude, off, RECIPES_PAGE, webSearch && off === 0);
      const newItems = r.items || [];
      setSItems(reset ? newItems : (prev) => [...prev, ...newItems]);
      setSHidden(r.hidden || []);
      setSHasMore(newItems.length === RECIPES_PAGE);
      setSOffset(off + newItems.length);
    } catch (e) {
      setSError(String((e && e.message) || e));
    } finally {
      setSLoading(false);
    }
  };

  useEffectR(() => {
    if (tab === 'ara') fetchRecipes(0, true);
    // eslint-disable-next-line
  }, [q, exclude.join(','), tab, webSearch]);

  const cook = useResource(() => API.cookWith(have, exclude), [have.join(','), exclude.join(',')]);

  let loading, error, list, hidden, hasMore;
  if (tab === 'ara') {
    loading = demoState === 'loading' || (sLoading && sItems.length === 0);
    error = demoState === 'error' ? 'Tarifler getirilemedi.' : sError;
    list = demoState === 'empty' ? [] : sItems;
    hidden = demoState === 'empty' ? [] : sHidden;
    hasMore = sHasMore && demoState !== 'empty';
  } else {
    loading = demoState === 'loading' || cook.loading;
    error = demoState === 'error' ? 'Tarifler getirilemedi.' : cook.error;
    const data = demoState === 'empty' ? { items: [], hidden: [] } : (cook.data || { items: [], hidden: [] });
    list = data.items || [];
    hidden = data.hidden || [];
    hasMore = false;
  }
  const blHidden = hidden.filter((h) => h.kind === 'blacklist');
  const exHidden = hidden.filter((h) => h.kind === 'exclude');
  const retry = () => { if (tab === 'ara') fetchRecipes(0, true); else cook.reload(); };

  return (
    <div className="flex flex-col gap-5">
      <header><h1 className="font-display font-bold text-2xl sm:text-[28px] leading-tight">Tarifler</h1><p className="text-muted text-sm mt-0.5">Kara listendeki malzemeyi içeren tarifler otomatik gizlenir.</p></header>

      <div className="max-w-md"><Segmented value={tab} onChange={setTab} options={[{ value: 'ara', label: 'Tarif ara', icon: 'search' }, { value: 'pisir', label: 'Şununla pişer', icon: 'leaf' }]} /></div>

      <div className="flex flex-col gap-3">
        {tab === 'ara'
          ? <div className="flex flex-col gap-2">
              <div className="relative"><span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted"><Icon name="search" size={18} /></span><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tarif, bölge ya da etiket ara… (ör. köfte, vegan)" className="pl-11" /></div>
              <label className="flex items-center gap-2 text-sm text-muted cursor-pointer select-none">
                <input type="checkbox" checked={webSearch} onChange={(e) => setWebSearch(e.target.checked)} className="accent-[var(--accent)] h-4 w-4" />
                Web'de ara (TheMealDB) — sonuçlar Türkçeye çevrilip kaydedilir
              </label>
            </div>
          : <Field label="Elimdeki malzemeler" hint="Enter ile ekle. En çok eşleşen tarifler üstte."><ChipInput items={have} setItems={setHave} placeholder="malzeme yaz…" color="var(--accent)" /></Field>}
        <Field label="İstenmeyen malzeme" hint="Kara listenle birlikte bu malzemeleri içeren tarifler gizlenir.">
          <ChipInput items={exclude} setItems={setExclude} placeholder="ör. yer fıstığı, laktoz…" color="var(--c-carb)" />
        </Field>
      </div>

      {error ? <ErrorBanner message={error} onRetry={retry} />
        : loading ? <div className="flex flex-col gap-3">{[0, 1].map((i) => <Skel key={i} style={{ height: 240, borderRadius: 16 }} />)}</div>
        : (
          <>
            {/* Kara liste / istenmeyen uyarısı */}
            {(blHidden.length > 0 || exHidden.length > 0) && (
              <div className="flex items-start gap-3 rounded-2xl px-4 py-3.5 anim-fade" style={{ background: 'color-mix(in srgb, var(--c-carb) 11%, var(--surface))', border: '1px solid color-mix(in srgb, var(--c-carb) 32%, transparent)' }}>
                <span className="grid place-items-center h-9 w-9 rounded-lg shrink-0" style={{ background: 'color-mix(in srgb, var(--c-carb) 18%, transparent)', color: 'var(--c-carb)' }}><Icon name="blacklist" size={18} /></span>
                <div className="text-sm leading-relaxed flex-1">
                  <b className="font-display">{hidden.length} tarif gizlendi.</b> Bu tarifler kara listendeki / istenmeyen malzemeleri içerdiği için listelenmedi:
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {hidden.map((h, i) => <span key={i} className="inline-flex items-center gap-1.5 rounded-full surface px-2.5 py-1 text-xs"><span className="line-through opacity-70">{h.title_tr}</span><span className="text-[11px] font-semibold" style={{ color: h.kind === 'blacklist' ? 'var(--c-fat)' : 'var(--c-carb)' }}>{h.reason}</span></span>)}
                  </div>
                </div>
              </div>
            )}
            {list.length === 0
              ? <Card className="p-2"><EmptyState icon="recipes" title={hidden.length ? 'Uygun tarif kalmadı' : (tab === 'ara' ? 'Tarif bulunamadı' : 'Eşleşen tarif yok')} hint={hidden.length ? 'Tüm sonuçlar kara liste/istenmeyen malzeme nedeniyle gizlendi.' : (tab === 'ara' ? 'Farklı bir arama dene.' : 'Elindeki malzemeleri ekleyince uygun tarifleri göstereceğiz.')} /></Card>
              : <>
                  <div className="grid gap-4 lg:grid-cols-2">{list.map((r, i) => <RecipeCard key={r.id != null ? r.id : (r.slug || i)} recipe={r} defaultOpen={list.length === 1} />)}</div>
                  {hasMore && (
                    <button onClick={() => fetchRecipes(sOffset, false)} disabled={sLoading} className="fr mx-auto mt-4 inline-flex items-center gap-2 rounded-xl bordered surface px-5 py-3 text-sm font-semibold hover:bg-[var(--surface-2)] disabled:opacity-60">
                      {sLoading ? 'Yükleniyor…' : 'Daha fazla tarif'}<Icon name="chevronD" size={16} />
                    </button>
                  )}
                </>}
          </>
        )}
    </div>
  );
}
window.RecipesScreen = RecipesScreen;
