// analytics.js — Google Analytics 4 (gtag) + Consent Mode v2.
// VITE_GA_MEASUREMENT_ID boşsa hiçbir şey yüklenmez (dev/mock build temiz kalır).
// PII gönderilmez (email/kullanıcı adı event parametrelerine girmez).

const GA_ID = import.meta.env.VITE_GA_MEASUREMENT_ID || '';
const CONSENT_KEY = 'fk.consent'; // 'granted' | 'denied'

function gtag() {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(arguments);
}

function loadGa() {
  if (!GA_ID || document.getElementById('ga-gtag')) return;
  const s = document.createElement('script');
  s.id = 'ga-gtag';
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);

  // Consent Mode v2: varsayılan reddedilmiş; kullanıcı onayıyla güncellenir.
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: localStorage.getItem(CONSENT_KEY) === 'granted' ? 'granted' : 'denied',
  });
  gtag('js', new Date());
  // SPA: sayfa görüntülemeleri manuel gönderilir (route değişiminde).
  gtag('config', GA_ID, { send_page_view: false });
}

function setConsent(granted) {
  localStorage.setItem(CONSENT_KEY, granted ? 'granted' : 'denied');
  if (GA_ID) gtag('consent', 'update', { analytics_storage: granted ? 'granted' : 'denied' });
}

function trackPageView(route) {
  if (!GA_ID) return;
  gtag('event', 'page_view', { page_path: '/' + route, page_title: route });
}

function trackEvent(name, params) {
  if (!GA_ID) return;
  gtag('event', name, params || {});
}

loadGa();

window.analytics = {
  enabled: !!GA_ID,
  consentAsked: () => localStorage.getItem(CONSENT_KEY) != null,
  setConsent,
  trackPageView,
  trackEvent,
};
