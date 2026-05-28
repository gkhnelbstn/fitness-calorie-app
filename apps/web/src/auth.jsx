// auth.jsx — Basit kullanıcı sistemi (prototip): Google + e-posta/şifre giriş kapısı.
// NOT: Gerçek Google OAuth + backend oturumu önerilir; burada localStorage tabanlı mock oturum.
const { useState: useAuthState } = React;

const AUTH_KEY = 'fk.auth';

function useAuth() {
  const [user, setUser] = useAuthState(() => { try { return JSON.parse(localStorage.getItem(AUTH_KEY) || 'null'); } catch { return null; } });
  const login = (u) => { const full = { ...u, initial: (u.name || u.email || '?').trim()[0].toUpperCase() }; localStorage.setItem(AUTH_KEY, JSON.stringify(full)); setUser(full); };
  const logout = () => { localStorage.removeItem(AUTH_KEY); setUser(null); };
  return [user, login, logout];
}
window.useAuth = useAuth;

// Google markası — marka glifi değil, Google paletinde nötr halka
function GoogleMark({ size = 18 }) {
  const segs = [['#EA4335', '0 25'], ['#FBBC05', '25 25'], ['#34A853', '50 25'], ['#4285F4', '75 25']];
  return (
    <svg width={size} height={size} viewBox="0 0 36 36" aria-hidden="true">
      {segs.map(([c, dash], i) => <circle key={i} cx="18" cy="18" r="13" fill="none" stroke={c} strokeWidth="6" strokeDasharray={`${(dash.split(' ')[1] / 100) * 81.7} 81.7`} strokeDashoffset={-(dash.split(' ')[0] / 100) * 81.7} transform="rotate(-90 18 18)" />)}
      <circle cx="18" cy="18" r="6" fill="var(--surface)" />
    </svg>
  );
}

const SAMPLE_ACCOUNTS = [
  { name: 'Elif Demir', email: 'elif.demir@gmail.com' },
  { name: 'Mehmet Yılmaz', email: 'mehmet.yilmaz@gmail.com' },
];

function AuthScreen({ onAuthed }) {
  const [view, setView] = useAuthState('main'); // main | google | email
  const [email, setEmail] = useAuthState('');
  const [pass, setPass] = useAuthState('');
  const [err, setErr] = useAuthState('');

  const emailLogin = () => {
    if (!/.+@.+\..+/.test(email)) { setErr('Geçerli bir e-posta gir.'); return; }
    if (pass.length < 4) { setErr('Şifre en az 4 karakter olmalı.'); return; }
    onAuthed({ name: email.split('@')[0].replace(/[._]/g, ' '), email, provider: 'email' });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-5" style={{ background: 'var(--bg)' }}>
      <div className="w-full max-w-sm flex flex-col items-center anim-pop">
        <div className="flex items-center gap-2.5 mb-7">
          <span className="grid place-items-center h-11 w-11 rounded-2xl text-white" style={{ background: 'var(--accent)' }}><Icon name="leaf" size={24} /></span>
          <div className="leading-none"><div className="font-display font-bold text-xl tracking-tight">FitKoç</div><div className="text-xs text-muted mt-0.5">Beslenme & Fitness Koçu</div></div>
        </div>

        <Card className="w-full p-6 sm:p-7 flex flex-col gap-4">
          {view === 'main' && (
            <div className="anim-fade flex flex-col gap-4">
              <div className="text-center"><h1 className="font-display font-bold text-xl">Hoş geldin</h1><p className="text-muted text-sm mt-1">Hesabına giriş yap veya kaydol.</p></div>
              <button onClick={() => setView('google')} className="fr flex items-center justify-center gap-3 h-12 rounded-xl bordered surface font-semibold hover:bg-[var(--surface-2)] transition"><GoogleMark />Google ile devam et</button>
              <div className="flex items-center gap-3 text-xs text-muted"><div className="flex-1 h-px" style={{ background: 'var(--border)' }} />veya<div className="flex-1 h-px" style={{ background: 'var(--border)' }} /></div>
              <button onClick={() => setView('email')} className="fr flex items-center justify-center gap-2 h-12 rounded-xl font-semibold text-white transition hover:brightness-105" style={{ background: 'var(--accent)' }}><Icon name="meals" size={18} />E-posta ile giriş</button>
              <button onClick={() => onAuthed({ name: 'Misafir', email: 'misafir@fitkoc.app', provider: 'guest' })} className="fr text-sm font-semibold text-muted hover:text-[var(--text)]">Misafir olarak dene</button>
            </div>
          )}

          {view === 'google' && (
            <div className="anim-fade flex flex-col gap-3">
              <div className="flex items-center gap-2 mb-1"><button onClick={() => setView('main')} className="fr grid h-8 w-8 place-items-center rounded-lg text-muted hover:bg-[var(--surface-2)]"><Icon name="chevronL" size={18} /></button><div className="flex items-center gap-2"><GoogleMark size={16} /><span className="font-display font-semibold">Hesap seç</span></div></div>
              {SAMPLE_ACCOUNTS.map((a) => (
                <button key={a.email} onClick={() => onAuthed({ ...a, provider: 'google' })} className="fr flex items-center gap-3 rounded-xl bordered surface-2 px-3.5 py-3 text-left hover:bg-[var(--surface)] transition">
                  <span className="grid place-items-center h-9 w-9 rounded-full text-white font-display font-semibold shrink-0" style={{ background: 'var(--accent)' }}>{a.name[0]}</span>
                  <div className="min-w-0"><div className="text-sm font-semibold truncate">{a.name}</div><div className="text-xs text-muted truncate">{a.email}</div></div>
                </button>
              ))}
              <button onClick={() => setView('email')} className="fr flex items-center gap-3 rounded-xl bordered px-3.5 py-3 text-left text-muted hover:bg-[var(--surface-2)] transition"><span className="grid place-items-center h-9 w-9 rounded-full bordered shrink-0"><Icon name="plus" size={16} /></span><span className="text-sm font-semibold">Başka hesap kullan</span></button>
              <p className="text-[11px] text-muted text-center mt-1">Prototip: gerçek Google OAuth yerine örnek hesaplar.</p>
            </div>
          )}

          {view === 'email' && (
            <div className="anim-fade flex flex-col gap-3">
              <div className="flex items-center gap-2 mb-1"><button onClick={() => setView('main')} className="fr grid h-8 w-8 place-items-center rounded-lg text-muted hover:bg-[var(--surface-2)]"><Icon name="chevronL" size={18} /></button><span className="font-display font-semibold">E-posta ile giriş</span></div>
              <Field label="E-posta"><Input type="email" value={email} onChange={(e) => { setEmail(e.target.value); setErr(''); }} placeholder="ornek@mail.com" autoFocus /></Field>
              <Field label="Şifre"><Input type="password" value={pass} onChange={(e) => { setPass(e.target.value); setErr(''); }} placeholder="••••••••" onKeyDown={(e) => e.key === 'Enter' && emailLogin()} /></Field>
              {err && <div className="text-xs font-medium" style={{ color: 'var(--c-fat)' }}>{err}</div>}
              <Button size="lg" icon="check" onClick={emailLogin} className="mt-1">Giriş yap</Button>
              <p className="text-[11px] text-muted text-center">Hesabın yok mu? Bu e-posta ile otomatik oluşturulur.</p>
            </div>
          )}
        </Card>
        <p className="text-[11px] text-muted mt-5 text-center max-w-xs text-balance">Devam ederek bunun bir tasarım prototipi olduğunu kabul edersin. Veriler cihazında saklanır.</p>
      </div>
    </div>
  );
}
window.AuthScreen = AuthScreen;

// Üst bardaki kullanıcı menüsü
function UserMenu({ user, onLogout }) {
  const [open, setOpen] = useAuthState(false);
  React.useEffect(() => { if (!open) return; const h = () => setOpen(false); document.addEventListener('click', h); return () => document.removeEventListener('click', h); }, [open]);
  return (
    <div className="relative" onClick={(e) => e.stopPropagation()}>
      <button onClick={() => setOpen(!open)} className="fr flex items-center gap-2 rounded-xl pl-1.5 pr-2.5 h-10 hover:bg-[var(--surface-2)] transition">
        <span className="grid place-items-center h-8 w-8 rounded-full text-white font-display font-semibold text-sm shrink-0" style={{ background: 'var(--accent)' }}>{user.initial}</span>
        <span className="hidden sm:block text-sm font-semibold max-w-[120px] truncate">{user.name}</span>
        <Icon name="chevronD" size={15} className="text-muted hidden sm:block" />
      </button>
      {open && (
        <div className="absolute right-0 top-12 z-50 w-60 surface bordered rounded-2xl shadow-softlg p-2 anim-pop">
          <div className="flex items-center gap-3 px-2.5 py-2.5">
            <span className="grid place-items-center h-10 w-10 rounded-full text-white font-display font-semibold shrink-0" style={{ background: 'var(--accent)' }}>{user.initial}</span>
            <div className="min-w-0"><div className="text-sm font-semibold truncate">{user.name}</div><div className="text-xs text-muted truncate">{user.email}</div></div>
          </div>
          {user.provider === 'google' && <div className="px-2.5 pb-1.5"><span className="inline-flex items-center gap-1.5 text-[11px] text-muted"><GoogleMark size={12} />Google ile bağlı</span></div>}
          <div className="h-px my-1" style={{ background: 'var(--border)' }} />
          <button onClick={onLogout} className="fr w-full flex items-center gap-2.5 rounded-xl px-2.5 py-2.5 text-sm font-semibold text-muted hover:bg-[var(--surface-2)] hover:text-[var(--c-fat)] transition"><Icon name="chevronL" size={16} />Çıkış yap</button>
        </div>
      )}
    </div>
  );
}
window.UserMenu = UserMenu;
