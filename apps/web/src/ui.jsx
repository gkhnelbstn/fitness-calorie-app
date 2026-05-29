// ui.jsx — Yeniden kullanılabilir UI parçaları. window'a export edilir.
const { useState, useEffect, useRef, useCallback } = React;

function cx(...a) { return a.filter(Boolean).join(' '); }

// ---- Veri kancası ----
function useResource(fn, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const reload = useCallback(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    Promise.resolve().then(fn).then((data) => { if (alive) setState({ data, loading: false, error: null }); })
      .catch((e) => { if (alive) setState({ data: null, loading: false, error: e.message || 'Bir hata oluştu' }); });
    return () => { alive = false; };
  }, deps); // eslint-disable-line
  useEffect(() => { const c = reload(); return c; }, [reload]);
  return { ...state, reload, setData: (d) => setState((s) => ({ ...s, data: d })) };
}

// ---- Kart ----
function Card({ className = '', children, style, onClick, hover }) {
  return (
    <div onClick={onClick}
      className={cx('surface bordered rounded-2xl shadow-soft', hover && 'transition hover:shadow-softlg hover:-translate-y-0.5 cursor-pointer', className)}
      style={style}>
      {children}
    </div>
  );
}

// ---- Buton ----
function Button({ variant = 'primary', size = 'md', icon, children, className = '', ...rest }) {
  const sizes = { sm: 'h-9 px-3 text-sm gap-1.5', md: 'h-11 px-4 text-[15px] gap-2', lg: 'h-12 px-5 text-base gap-2', icon: 'h-10 w-10' };
  const variants = {
    primary: 'text-white shadow-soft hover:brightness-105 active:brightness-95',
    soft: 'text-accent-text hover:brightness-95',
    ghost: 'text-muted hover:bg-[var(--surface-2)]',
    outline: 'bordered text-[var(--text)] hover:bg-[var(--surface-2)]',
    danger: 'text-white hover:brightness-105',
  };
  const bg = variant === 'primary' ? { background: 'var(--accent)' }
    : variant === 'soft' ? { background: 'var(--accent-soft)' }
    : variant === 'danger' ? { background: '#e0568b' } : undefined;
  return (
    <button {...rest} style={{ ...bg, ...(rest.style || {}) }}
      className={cx('fr inline-flex items-center justify-center rounded-xl font-semibold font-display transition disabled:opacity-50 disabled:pointer-events-none', sizes[size], variants[variant], className)}>
      {icon && <Icon name={icon} size={size === 'sm' ? 16 : 18} />}
      {children}
    </button>
  );
}

// ---- Rozet / Chip ----
function Badge({ children, tone = 'neutral', className = '' }) {
  const tones = {
    neutral: 'surface-2 text-muted',
    accent: 'text-accent-text',
    blue: 'text-[var(--c-prot)]', amber: 'text-[var(--c-carb)]', rose: 'text-[var(--c-fat)]',
  };
  const bg = tone === 'accent' ? { background: 'var(--accent-soft)' }
    : tone === 'blue' ? { background: 'color-mix(in srgb, var(--c-prot) 14%, transparent)' }
    : tone === 'amber' ? { background: 'color-mix(in srgb, var(--c-carb) 16%, transparent)' }
    : tone === 'rose' ? { background: 'color-mix(in srgb, var(--c-fat) 14%, transparent)' } : undefined;
  return <span style={bg} className={cx('inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold', tones[tone], className)}>{children}</span>;
}

function Chip({ children, onRemove, color, className = '' }) {
  return (
    <span className={cx('inline-flex items-center gap-1.5 rounded-full surface-2 bordered px-3 py-1.5 text-sm font-medium', className)}>
      {color && <span className="h-2 w-2 rounded-full" style={{ background: color }} />}
      {children}
      {onRemove && (
        <button onClick={onRemove} className="fr ml-0.5 -mr-1 grid h-5 w-5 place-items-center rounded-full text-muted hover:text-[var(--c-fat)] hover:bg-[var(--surface)]">
          <Icon name="x" size={13} />
        </button>
      )}
    </span>
  );
}

// ---- Progress: bar + ring ----
function ProgressBar({ value, max, color, className = '', height = 8 }) {
  const pct = Math.min(100, max ? (value / max) * 100 : 0);
  return (
    <div className={cx('w-full rounded-full overflow-hidden', className)} style={{ height, background: 'var(--surface-2)' }}>
      <div className="h-full rounded-full transition-all duration-700" style={{ width: pct + '%', background: color || 'var(--accent)' }} />
    </div>
  );
}

function Ring({ value, max, color, size = 64, stroke = 7, children }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.min(1, max ? value / max : 0);
  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--surface-2)" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color || 'var(--accent)'} strokeWidth={stroke}
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - pct)} style={{ transition: 'stroke-dashoffset .8s cubic-bezier(.22,1,.36,1)' }} />
      </svg>
      <div className="absolute inset-0 grid place-items-center text-center">{children}</div>
    </div>
  );
}

// Makro istatistiği — düzene göre bar veya ring
function MacroStat({ label, value, max, color, unit, layout = 'bar' }) {
  const pct = Math.round(max ? Math.min(100, (value / max) * 100) : 0);
  if (layout === 'ring') {
    return (
      <Card className="p-4 flex flex-col items-center gap-2">
        <Ring value={value} max={max} color={color} size={92} stroke={9}>
          <div className="font-display font-semibold text-lg tnum leading-none">{Math.round(value)}</div>
          <div className="text-[10px] text-muted">/ {max}{unit}</div>
        </Ring>
        <div className="text-sm font-semibold">{label}</div>
      </Card>
    );
  }
  return (
    <Card className="p-4 flex flex-col gap-2.5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-muted">{label}</span>
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: color }} />
      </div>
      <div className="flex items-baseline gap-1">
        <span className="font-display font-semibold text-2xl tnum">{Math.round(value)}</span>
        <span className="text-sm text-muted">/ {max}{unit}</span>
      </div>
      <ProgressBar value={value} max={max} color={color} />
      <div className="text-xs text-muted tnum">%{pct} tamam</div>
    </Card>
  );
}

// ---- Skeleton ----
function Skel({ className = '', style }) { return <div className={cx('skel', className)} style={style} />; }

// ---- Boş durum ----
function EmptyState({ icon = 'inbox', title, hint, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-14 px-6">
      <div className="grid place-items-center h-16 w-16 rounded-2xl surface-2 text-muted mb-4"><Icon name={icon} size={28} /></div>
      <h3 className="font-display font-semibold text-lg">{title}</h3>
      {hint && <p className="text-muted text-sm mt-1 max-w-xs text-balance">{hint}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

// ---- Hata banner ----
function ErrorBanner({ message, onRetry }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl px-4 py-3.5 text-sm anim-fade"
      style={{ background: 'color-mix(in srgb, #e0568b 12%, var(--surface))', border: '1px solid color-mix(in srgb, #e0568b 35%, transparent)', color: 'var(--text)' }}>
      <span style={{ color: '#e0568b' }}><Icon name="alert" size={18} /></span>
      <span className="flex-1 font-medium">{message}</span>
      {onRetry && <button onClick={onRetry} className="fr font-semibold inline-flex items-center gap-1.5" style={{ color: '#e0568b' }}><Icon name="refresh" size={15} />Tekrar dene</button>}
    </div>
  );
}

// ---- Modal (masaüstü ortada, mobil bottom-sheet) ----
function Modal({ open, onClose, title, children, footer, size = 'md', mobileSheet = true }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow; document.body.style.overflow = 'hidden';
    return () => { document.removeEventListener('keydown', onKey); document.body.style.overflow = prev; };
  }, [open]);
  if (!open) return null;
  const max = { sm: 'sm:max-w-md', md: 'sm:max-w-xl', lg: 'sm:max-w-2xl' }[size];
  return (
    <div className="fixed inset-0 z-50 flex sm:items-center sm:justify-center items-end" >
      <div className="absolute inset-0 bg-black/45 backdrop-blur-sm anim-fade" onClick={onClose} />
      <div className={cx('surface relative w-full bordered shadow-softlg flex flex-col max-h-[92vh] sm:max-h-[88vh]',
        max, mobileSheet ? 'rounded-t-3xl sm:rounded-3xl anim-sheet sm:anim-pop' : 'rounded-3xl anim-pop')}>
        <div className="flex items-center justify-between px-5 sm:px-6 pt-5 pb-3 shrink-0">
          <h2 className="font-display font-semibold text-lg sm:text-xl">{title}</h2>
          <button onClick={onClose} className="fr grid h-9 w-9 place-items-center rounded-full text-muted hover:bg-[var(--surface-2)]"><Icon name="x" size={18} /></button>
        </div>
        <div className="overflow-y-auto px-5 sm:px-6 pb-2 flex-1">{children}</div>
        {footer && <div className="px-5 sm:px-6 py-4 bordered border-l-0 border-r-0 border-b-0 shrink-0 flex gap-2 justify-end" style={{ background: 'var(--surface)' }}>{footer}</div>}
      </div>
    </div>
  );
}

// ---- Form alanları ----
function Field({ label, hint, children, className = '' }) {
  return (
    <label className={cx('flex flex-col gap-1.5', className)}>
      {label && <span className="text-sm font-semibold">{label}</span>}
      {children}
      {hint && <span className="text-xs text-muted">{hint}</span>}
    </label>
  );
}
const inputCls = 'fr w-full rounded-xl bordered surface-2 px-3.5 h-11 text-[15px] placeholder:text-[color:var(--text-muted)] focus:bg-[var(--surface)]';
function Input(props) { return <input {...props} className={cx(inputCls, props.className)} />; }
function Textarea(props) { return <textarea {...props} className={cx(inputCls, 'h-auto py-3 leading-relaxed resize-none', props.className)} />; }
function Select({ children, ...props }) {
  return (
    <div className="relative">
      <select {...props} className={cx(inputCls, 'appearance-none pr-9 cursor-pointer', props.className)}>{children}</select>
      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-muted"><Icon name="chevronD" size={16} /></span>
    </div>
  );
}

// ---- Tabs (segment) ----
function Segmented({ value, onChange, options }) {
  return (
    <div className="inline-flex p-1 rounded-xl surface-2 bordered gap-1 w-full">
      {options.map((o) => (
        <button key={o.value} onClick={() => onChange(o.value)}
          className={cx('fr flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg px-3 h-9 text-sm font-semibold font-display transition',
            value === o.value ? 'surface shadow-soft' : 'text-muted hover:text-[var(--text)]')}
          style={value === o.value ? { color: 'var(--accent-text)' } : undefined}>
          {o.icon && <Icon name={o.icon} size={16} />}<span className="truncate">{o.label}</span>
        </button>
      ))}
    </div>
  );
}

// ---- Görsel placeholder (çizgili) ----
function ImgPlaceholder({ className = '', label = 'görsel', round = 'rounded-xl' }) {
  return (
    <div className={cx('relative overflow-hidden grid place-items-center', round, className)}
      style={{ background: 'repeating-linear-gradient(45deg, var(--surface-2), var(--surface-2) 9px, var(--border) 9px, var(--border) 10px)' }}>
      <span className="text-[10px] uppercase tracking-wider text-muted font-mono px-1.5 py-0.5 rounded" style={{ background: 'color-mix(in srgb, var(--surface) 70%, transparent)' }}>{label}</span>
    </div>
  );
}

// ---- Sayı stepper ----
function Stepper({ value, onChange, min = 0, max = 999, step = 1, suffix }) {
  const set = (v) => onChange(Math.max(min, Math.min(max, Math.round(v * 100) / 100)));
  return (
    <div className="inline-flex items-center rounded-xl bordered surface-2 h-11 overflow-hidden">
      <button onClick={() => set(value - step)} className="fr grid h-11 w-11 place-items-center text-muted hover:bg-[var(--surface)]"><Icon name="minus" size={16} /></button>
      <div className="min-w-[58px] text-center font-display font-semibold tnum">{value}{suffix && <span className="text-xs text-muted ml-0.5">{suffix}</span>}</div>
      <button onClick={() => set(value + step)} className="fr grid h-11 w-11 place-items-center text-muted hover:bg-[var(--surface)]"><Icon name="plus" size={16} /></button>
    </div>
  );
}

// ---- Toggle ----
function Toggle({ value, onChange }) {
  return (
    <button onClick={() => onChange(!value)} className="fr relative h-7 w-12 rounded-full transition shrink-0" style={{ background: value ? 'var(--accent)' : 'var(--border)' }}>
      <span className="absolute top-1 h-5 w-5 rounded-full bg-white shadow transition-all" style={{ left: value ? 26 : 4 }} />
    </button>
  );
}

// ---- Hedeflerden makro türetme (carb/fat/fiber backend'de yok → client türetir) ----
function deriveTargets(energy) {
  const kcal = energy && energy.target_kcal ? energy.target_kcal : null;
  const protein = energy && energy.protein_target_g ? Math.round(energy.protein_target_g) : (kcal ? Math.round(kcal * 0.3 / 4) : null);
  const carb = kcal ? Math.round(kcal * 0.45 / 4) : null;
  const fat = kcal ? Math.round(kcal * 0.27 / 9) : null;
  const fiber = kcal ? Math.round(kcal / 1000 * 14) : 30;
  return { kcal, protein, carb, fat, fiber };
}

Object.assign(window, {
  cx, useResource, Card, Button, Badge, Chip, ProgressBar, Ring, MacroStat,
  Skel, EmptyState, ErrorBanner, Modal, Field, Input, Textarea, Select, Segmented, ImgPlaceholder,
  Stepper, Toggle, deriveTargets,
});
