// muscle-map.jsx — Şematik ön/arka vücut; çalışan kas gruplarını vurgular.
// highlight: ['gogus','sirt','omuz','kol','karin','bacak','kalca','kardiyo']
(function () {
  const HI = 'var(--accent)';
  const HI2 = 'color-mix(in srgb, var(--accent) 45%, var(--surface-2))';
  const BASE = 'var(--surface-2)';
  const LINE = 'var(--border)';

  function R(props, on) { return <rect {...props} fill={on} stroke={LINE} strokeWidth="1" />; }
  function E(props, on) { return <ellipse {...props} fill={on} stroke={LINE} strokeWidth="1" />; }

  // her view için kas bölgeleri: key -> shape üretici
  function FrontFigure({ has, sec }) {
    const c = (k) => (has(k) ? HI : sec(k) ? HI2 : BASE);
    return (
      <svg viewBox="0 0 100 220" width="100%" height="100%" aria-hidden="true">
        {/* yapısal (nötr) */}
        <circle cx="50" cy="16" r="12" fill={BASE} stroke={LINE} />
        <rect x="44" y="27" width="12" height="7" rx="2" fill={BASE} stroke={LINE} />
        <rect x="19" y="80" width="11" height="30" rx="5" fill={BASE} stroke={LINE} />
        <rect x="70" y="80" width="11" height="30" rx="5" fill={BASE} stroke={LINE} />
        <rect x="37" y="150" width="12" height="50" rx="5" fill={BASE} stroke={LINE} />
        <rect x="51" y="150" width="12" height="50" rx="5" fill={BASE} stroke={LINE} />
        {/* omuz */}
        {E({ cx: 30, cy: 45, rx: 11, ry: 8 }, c('omuz'))}
        {E({ cx: 70, cy: 45, rx: 11, ry: 8 }, c('omuz'))}
        {/* kol (biceps) */}
        {R({ x: 21, y: 49, width: 11, height: 32, rx: 5 }, c('kol'))}
        {R({ x: 68, y: 49, width: 11, height: 32, rx: 5 }, c('kol'))}
        {/* göğüs */}
        {R({ x: 34, y: 40, width: 15, height: 18, rx: 5 }, c('gogus'))}
        {R({ x: 51, y: 40, width: 15, height: 18, rx: 5 }, c('gogus'))}
        {/* karın */}
        {R({ x: 40, y: 59, width: 20, height: 30, rx: 5 }, c('karin'))}
        {/* pelvis */}
        <rect x="38" y="89" width="24" height="12" rx="5" fill={BASE} stroke={LINE} />
        {/* bacak (quadriceps) */}
        {R({ x: 37, y: 100, width: 12, height: 50, rx: 6 }, c('bacak'))}
        {R({ x: 51, y: 100, width: 12, height: 50, rx: 6 }, c('bacak'))}
      </svg>
    );
  }

  function BackFigure({ has, sec }) {
    const c = (k) => (has(k) ? HI : sec(k) ? HI2 : BASE);
    return (
      <svg viewBox="0 0 100 220" width="100%" height="100%" aria-hidden="true">
        <circle cx="50" cy="16" r="12" fill={BASE} stroke={LINE} />
        <rect x="44" y="27" width="12" height="7" rx="2" fill={BASE} stroke={LINE} />
        <rect x="19" y="80" width="11" height="30" rx="5" fill={BASE} stroke={LINE} />
        <rect x="70" y="80" width="11" height="30" rx="5" fill={BASE} stroke={LINE} />
        <rect x="37" y="152" width="12" height="48" rx="5" fill={BASE} stroke={LINE} />
        <rect x="51" y="152" width="12" height="48" rx="5" fill={BASE} stroke={LINE} />
        {/* omuz arka */}
        {E({ cx: 30, cy: 45, rx: 11, ry: 8 }, c('omuz'))}
        {E({ cx: 70, cy: 45, rx: 11, ry: 8 }, c('omuz'))}
        {/* kol (triceps) */}
        {R({ x: 21, y: 49, width: 11, height: 32, rx: 5 }, c('kol'))}
        {R({ x: 68, y: 49, width: 11, height: 32, rx: 5 }, c('kol'))}
        {/* sırt */}
        {R({ x: 35, y: 40, width: 30, height: 30, rx: 6 }, c('sirt'))}
        {/* kalça */}
        {R({ x: 38, y: 88, width: 24, height: 16, rx: 6 }, c('kalca'))}
        {/* bacak (hamstring) */}
        {R({ x: 37, y: 104, width: 12, height: 48, rx: 6 }, c('bacak'))}
        {R({ x: 51, y: 104, width: 12, height: 48, rx: 6 }, c('bacak'))}
      </svg>
    );
  }

  const FRONT_KEYS = new Set(['omuz', 'gogus', 'kol', 'karin', 'bacak', 'kardiyo']);
  const BACK_KEYS = new Set(['omuz', 'sirt', 'kol', 'kalca', 'bacak', 'kardiyo']);

  function MuscleMap({ primary = [], secondary = [], size = 120, showBack = true }) {
    const prim = new Set([].concat(primary));
    const seco = new Set([].concat(secondary));
    if (prim.has('kardiyo')) { prim.delete('kardiyo'); ['omuz', 'gogus', 'kol', 'karin', 'bacak', 'sirt', 'kalca'].forEach((k) => prim.add(k)); }
    const has = (k) => prim.has(k);
    const sec = (k) => seco.has(k) && !prim.has(k);
    return (
      <div className="flex items-end justify-center gap-1" style={{ height: size }}>
        <div style={{ height: size, aspectRatio: '100/220' }}><FrontFigure has={has} sec={sec} /></div>
        {showBack && <div style={{ height: size, aspectRatio: '100/220' }}><BackFigure has={has} sec={sec} /></div>}
      </div>
    );
  }

  window.MuscleMap = MuscleMap;
  window.MUSCLE_LABELS = { gogus: 'Göğüs', sirt: 'Sırt', omuz: 'Omuz', kol: 'Kol', karin: 'Karın', bacak: 'Bacak', kalca: 'Kalça', kardiyo: 'Tüm vücut', biceps: 'Biceps', triceps: 'Triceps', 'kalça': 'Kalça', bel: 'Bel' };
})();
