/* Consenso cookie di Ospitalk: Google Consent Mode v2 + banner fatto in casa.
   Va incluso nel <head> di ogni pagina, prima di qualsiasi altro script Google.
   Google Analytics si carica solo dopo "Accetta" (Linee guida Garante 10/06/2021). */
(function () {
  // Per attivare Analytics basta inserire qui l'ID di misurazione GA4 (es. 'G-XXXXXXXXXX'):
  // tutte le pagine includono già questo file come primo script del <head>.
  // Vuoto = Analytics spento (il banner resta, la scelta viene ricordata).
  // Nella proprietà GA4 impostare la conservazione dati a 14 mesi (come scritto in privacy.html)
  // e lasciare disattivati Google Signals e personalizzazione annunci.
  var GA_ID = 'G-9PR0LBHKKP';
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

  // Testi del banner nella lingua della pagina (<html lang>); italiano se la lingua non è prevista.
  // La cookie policy esiste solo in italiano: le altre lingue la indicano tra parentesi.
  // "prefs" deve coincidere con il testo del pulsante "Preferenze cookie" nel piè di pagina.
  var TEXTS = {
    it: { close: 'Chiudi senza accettare', title: 'Cookie su questo sito', text: 'Usiamo strumenti tecnici necessari al sito e, solo con il tuo consenso, Google Analytics per contare le visite in forma aggregata. Se chiudi il riquadro con la X è come rifiutare. Puoi cambiare idea quando vuoi da “Preferenze cookie” in fondo alla pagina.', policy: 'Cookie policy', reject: 'Rifiuta', accept: 'Accetta' },
    en: { close: 'Close without accepting', title: 'Cookies on this site', text: 'We use technical tools the site needs and, only with your consent, Google Analytics to count visits in aggregate form. Closing this box with the X counts as refusing. You can change your mind at any time from “Cookie preferences” at the bottom of the page.', policy: 'Cookie policy', reject: 'Reject', accept: 'Accept' },
    de: { close: 'Schließen, ohne zuzustimmen', title: 'Cookies auf dieser Website', text: 'Wir verwenden technisch notwendige Werkzeuge und, nur mit Ihrer Einwilligung, Google Analytics, um Besuche in zusammengefasster Form zu zählen. Wenn Sie das Fenster mit dem X schließen, gilt das als Ablehnung. Sie können Ihre Entscheidung jederzeit unter „Cookie-Einstellungen“ unten auf der Seite ändern.', policy: 'Cookie-Richtlinie', reject: 'Ablehnen', accept: 'Akzeptieren' },
    fr: { close: 'Fermer sans accepter', title: 'Cookies sur ce site', text: 'Nous utilisons des outils techniques nécessaires au site et, uniquement avec votre accord, Google Analytics pour compter les visites de façon agrégée. Fermer cette fenêtre avec la croix équivaut à refuser. Vous pouvez changer d’avis à tout moment via « Préférences cookies » en bas de page.', policy: 'Politique cookies', reject: 'Refuser', accept: 'Accepter' },
    es: { close: 'Cerrar sin aceptar', title: 'Cookies en este sitio', text: 'Usamos herramientas técnicas necesarias para el sitio y, solo con tu consentimiento, Google Analytics para contar las visitas de forma agregada. Cerrar este aviso con la X equivale a rechazar. Puedes cambiar de opinión cuando quieras desde «Preferencias de cookies», al final de la página.', policy: 'Política de cookies', reject: 'Rechazar', accept: 'Aceptar' },
    pt: { close: 'Fechar sem aceitar', title: 'Cookies neste site', text: 'Utilizamos ferramentas técnicas necessárias ao site e, apenas com o seu consentimento, o Google Analytics para contar as visitas de forma agregada. Fechar este aviso com o X equivale a recusar. Pode mudar de ideias quando quiser em «Preferências de cookies», no fundo da página.', policy: 'Política de cookies', reject: 'Recusar', accept: 'Aceitar' },
    nl: { close: 'Sluiten zonder te accepteren', title: 'Cookies op deze website', text: 'We gebruiken technische hulpmiddelen die de site nodig heeft en, alleen met jouw toestemming, Google Analytics om bezoeken in geaggregeerde vorm te tellen. Sluit je dit venster met het kruisje, dan geldt dat als weigeren. Je kunt je keuze altijd wijzigen via ‘Cookievoorkeuren’ onderaan de pagina.', policy: 'Cookiebeleid', reject: 'Weigeren', accept: 'Accepteren' },
    pl: { close: 'Zamknij bez akceptacji', title: 'Pliki cookie na tej stronie', text: 'Używamy narzędzi technicznych niezbędnych do działania strony, a wyłącznie za Twoją zgodą – Google Analytics do liczenia odwiedzin w formie zbiorczej. Zamknięcie okna krzyżykiem oznacza odmowę. Zdanie możesz zmienić w każdej chwili w „Ustawieniach cookie” na dole strony.', policy: 'Polityka cookie', reject: 'Odrzuć', accept: 'Akceptuj' },
    zh: { close: '关闭且不同意', title: '本网站的 Cookie', text: '我们使用网站运行所必需的技术工具；仅在您同意后，才会使用 Google Analytics 以汇总方式统计访问量。点击 X 关闭此窗口即视为拒绝。您可以随时通过页面底部的“Cookie 偏好设置”更改选择。', policy: 'Cookie 政策', reject: '拒绝', accept: '同意' },
    ja: { close: '同意せずに閉じる', title: 'このサイトのCookieについて', text: 'サイトの動作に必要な技術的ツールを使用しています。また、同意いただいた場合に限り、Google Analytics で訪問数を集計します。×で閉じた場合は拒否したものとみなします。ページ下部の「Cookie設定」からいつでも変更できます。', policy: 'Cookieポリシー', reject: '拒否する', accept: '同意する' },
    ru: { close: 'Закрыть без согласия', title: 'Файлы cookie на этом сайте', text: 'Мы используем технические инструменты, необходимые для работы сайта, и — только с вашего согласия — Google Analytics для подсчёта посещений в обобщённом виде. Если закрыть это окно крестиком, это будет означать отказ. Изменить выбор можно в любой момент через «Настройки cookie» внизу страницы.', policy: 'Политика cookie', reject: 'Отклонить', accept: 'Принять' }
  };
  function texts() {
    var lang = (document.documentElement.lang || 'it').toLowerCase().split('-')[0];
    return { lang: TEXTS[lang] ? lang : 'it', t: TEXTS[lang] || TEXTS.it };
  }

  function openBanner() {
    if (banner) return;
    var L = texts(), t = L.t;
    var policy = '<a href="/cookie.html">' + t.policy + '</a>' + (L.lang === 'it' ? '' : ' <span lang="it">(Italiano)</span>');
    banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-labelledby', 'cookie-title');
    banner.setAttribute('aria-describedby', 'cookie-text');
    banner.innerHTML =
      '<button type="button" class="cookie-x" data-cookie="reject" aria-label="' + t.close + '">&times;</button>' +
      '<p class="cookie-title" id="cookie-title">' + t.title + '</p>' +
      '<p id="cookie-text">' + t.text + ' ' + policy + '</p>' +
      '<div class="cookie-actions">' +
      '<button type="button" class="cookie-btn" data-cookie="reject">' + t.reject + '</button>' +
      '<button type="button" class="cookie-btn" data-cookie="accept">' + t.accept + '</button>' +
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
