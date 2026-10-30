/* Consenso cookie di Ospitalk: Google Consent Mode v2 + banner fatto in casa.
   Va incluso nel <head> di ogni pagina, prima di qualsiasi altro script Google.
   Google Analytics si carica solo dopo "Accetta" (Linee guida Garante 10/06/2021). */
(function () {
  var GA_ID = ''; // ID di misurazione GA4 (es. 'G-XXXXXXXXXX'); vuoto = Analytics spento
  var KEY = 'ospitalk-consent';
  var MAX_AGE = 182 * 24 * 60 * 60 * 1000; // 6 mesi, poi il banner si ripropone
  var memory = null; // ripiego se localStorage non è disponibile

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    functionality_storage: 'denied',
    personalization_storage: 'denied',
    security_storage: 'denied'
  });

  function read() {
    var raw = null;
    try { raw = window.localStorage.getItem(KEY); } catch (e) { raw = memory; }
    if (!raw) return null;
    try {
      var c = JSON.parse(raw);
      if (typeof c.analytics !== 'boolean' || !(Date.now() - c.ts < MAX_AGE)) return null;
      return c;
    } catch (e) { return null; }
  }

  function save(analytics) {
    var raw = JSON.stringify({ v: 1, analytics: analytics, ts: Date.now() });
    memory = raw;
    try { window.localStorage.setItem(KEY, raw); } catch (e) { /* resta valida per questa visita */ }
  }

  var loaded = false;
  function loadAnalytics() {
    if (loaded || !GA_ID) return;
    loaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', GA_ID, {
      cookie_expires: 13 * 30 * 24 * 60 * 60,
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
  }

  function dropAnalyticsCookies() {
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (name === '_ga' || name.indexOf('_ga_') === 0) {
        var host = location.hostname;
        document.cookie = name + '=; Max-Age=0; path=/';
        document.cookie = name + '=; Max-Age=0; path=/; domain=' + host;
        document.cookie = name + '=; Max-Age=0; path=/; domain=.' + host.replace(/^www\./, '');
      }
    });
  }

  function apply(analytics) {
    gtag('consent', 'update', { analytics_storage: analytics ? 'granted' : 'denied' });
    if (analytics) loadAnalytics(); else dropAnalyticsCookies();
  }

  var banner = null;
  function closeBanner() {
    if (banner) { banner.remove(); banner = null; }
  }

  function choose(analytics) {
    save(analytics);
    apply(analytics);
    closeBanner();
  }

  function openBanner() {
    if (banner) return;
    banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-labelledby', 'cookie-title');
    banner.setAttribute('aria-describedby', 'cookie-text');
    banner.innerHTML =
      '<button type="button" class="cookie-x" data-cookie="reject" aria-label="Chiudi senza accettare">&times;</button>' +
      '<p class="cookie-title" id="cookie-title">Cookie su questo sito</p>' +
      '<p id="cookie-text">Usiamo strumenti tecnici necessari al sito e, solo con il tuo consenso, ' +
      'Google Analytics per contare le visite in forma aggregata. Se chiudi il riquadro con la X è come rifiutare. ' +
      'Puoi cambiare idea quando vuoi da “Preferenze cookie” in fondo alla pagina. ' +
      '<a href="/cookie.html">Cookie policy</a></p>' +
      '<div class="cookie-actions">' +
      '<button type="button" class="cookie-btn" data-cookie="reject">Rifiuta</button>' +
      '<button type="button" class="cookie-btn" data-cookie="accept">Accetta</button>' +
      '</div>';
    document.body.appendChild(banner);
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-cookie], [data-cookie-prefs]');
    if (!t) return;
    if (t.hasAttribute('data-cookie-prefs')) { e.preventDefault(); openBanner(); return; }
    choose(t.getAttribute('data-cookie') === 'accept');
  });

  var current = read();
  if (current) apply(current.analytics);

  function start() { if (!read()) openBanner(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
