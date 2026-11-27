#!/usr/bin/env python3
"""Genera le versioni tradotte di ospitalk.it e aggiorna le parti comuni.

Uso, dalla radice del repository:  python3 _i18n/build.py

- Le pagine italiane restano scritte a mano (fanno fede): lo script vi aggiunge
  solo hreflang, selettore della lingua e lo script del menu, in modo idempotente.
- Le pagine /xx/index.html e /xx/{case-vacanza,bnb,affittacamere}/index.html sono
  GENERATE da _i18n/strings/xx.py: per cambiarle si modificano le stringhe e si
  rilancia lo script, non l'HTML.
- Le pagine legali tradotte (/en, /es, /pt, /de, /fr) sono scritte a mano nel
  <main>; lo script ne rigenera soltanto testata e piè di pagina.
La cartella _i18n non viene pubblicata da GitHub Pages (inizia con "_").
"""
import html
import importlib.util
import json
import pathlib
import re
from string import Template

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://ospitalk.it"
WA = "https://wa.me/393277485039?text=ATTIVA%20OSPITALK"
LOGIN = "https://app.ospitalk.it/accounts/login/"

# codice cartella, hreflang/lang, nome nativo, og:locale, inLanguage, sigla nel selettore
LANGS = [
    ("it", "it", "Italiano", "it_IT", "it-IT", "IT"),
    ("en", "en", "English", "en_GB", "en-GB", "EN"),
    ("de", "de", "Deutsch", "de_DE", "de-DE", "DE"),
    ("fr", "fr", "Français", "fr_FR", "fr-FR", "FR"),
    ("es", "es", "Español", "es_ES", "es-ES", "ES"),
    ("pt", "pt", "Português", "pt_PT", "pt-PT", "PT"),
    ("nl", "nl", "Nederlands", "nl_NL", "nl-NL", "NL"),
    ("pl", "pl", "Polski", "pl_PL", "pl-PL", "PL"),
    ("zh", "zh-Hans", "中文", "zh_CN", "zh-Hans", "中文"),
    ("ja", "ja", "日本語", "ja_JP", "ja-JP", "日本語"),
    ("ru", "ru", "Русский", "ru_RU", "ru-RU", "RU"),
]
CODES = [l[0] for l in LANGS]
INFO = {l[0]: l for l in LANGS}
PAGES = ["", "case-vacanza/", "bnb/", "affittacamere/"]
LEGAL = ["termini.html", "privacy.html", "dpa.html"]
LEGAL_LANGS = ["it", "en", "de", "fr", "es", "pt"]
# Lingue senza font web (sottoinsieme latin-1): tutto in font di sistema, niente preload.
SYSTEM_FONT_LANGS = {"pl", "ru"}
LANG_WORD = {"it": "Lingua", "en": "Language", "de": "Sprache", "fr": "Langue", "es": "Idioma",
             "pt": "Idioma", "nl": "Taal", "pl": "Język", "zh": "语言", "ja": "言語", "ru": "Язык"}

LOGO_SVG = ('<svg class="logo-mark" viewBox="0 0 100 132" aria-hidden="true"><circle cx="50" cy="19" r="13" '
            'fill="none" stroke="#9A7A3F" stroke-width="9"/><path d="M50 33C27 33 15 48 15 72c0 23 14 37 30 '
            '40l27 16-8-21c13-7 21-19 21-35 0-24-12-39-35-39z" fill="#1F5A45"/><circle cx="50" cy="65" r="10" '
            'fill="#E3B54C"/><path d="M44.5 69h11l2.5 23h-16z" fill="#E3B54C"/></svg>')
PLACARD_STRING = ('<svg class="placard-string" viewBox="0 0 100 50" preserveAspectRatio="none"><path d="M0 50 50 4 '
                  '100 50" fill="none" stroke="#1B2420" stroke-width="1.5" vector-effect="non-scaling-stroke"/>'
                  '<circle cx="50" cy="4" r="4" fill="#8E3A22"/></svg>')


def prefix(lang):
    return "/" if lang == "it" else f"/{lang}/"


def path(lang, page):
    return prefix(lang) + page


def url(lang, page):
    return BASE + path(lang, page)


def plain(s):
    """Testo HTML -> testo semplice per JSON-LD."""
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def ico(name):
    return f'<svg class="ico" aria-hidden="true"><use href="/icons.svg#i-{name}"/></svg>'


def load_strings(lang):
    spec = importlib.util.spec_from_file_location(f"s_{lang}", ROOT / "_i18n" / "strings" / f"{lang}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.T


# ---------------------------------------------------------------- parti comuni

def switcher(lang, page):
    """Selettore lingua: <details> nativo, usabile da tastiera anche senza JS."""
    items = []
    for code, hl, name, *_ in LANGS:
        if page in PAGES or (page in LEGAL and code in LEGAL_LANGS):
            target = path(code, page)
        else:
            target = path(code, "")
        cur = ' aria-current="true"' if code == lang else ""
        items.append(f'<li><a href="{target}" hreflang="{hl}" lang="{hl}"{cur}>{name}</a></li>')
    i = INFO[lang]
    return (f'<details class="lang-switch"><summary aria-label="{LANG_WORD[lang]}: {i[2]}">{ico("globe")}'
            f'<span>{i[5]}</span></summary><ul>{"".join(items)}</ul></details>')


def hreflang_links(page):
    out = [f'<link rel="alternate" hreflang="{hl}" href="{url(code, page)}">' for code, hl, *_ in LANGS]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{url("it", page)}">')
    return "\n".join(out)


def nav(lang, T, page):
    home = "" if page == "" else prefix(lang)
    def cur(p):
        return ' aria-current="page"' if p == page else ""
    return (f'<nav aria-label="{T["nav_label"]}"><a class="nav-y" href="{home}#come-funziona">{T["nav_how"]}</a>'
            f'<a class="nav-x" href="{path(lang, "case-vacanza/")}"{cur("case-vacanza/")}>{T["nav_cv"]}</a>'
            f'<a class="nav-x" href="{path(lang, "bnb/")}"{cur("bnb/")}>{T["nav_bnb"]}</a>'
            f'<a class="nav-x" href="{path(lang, "affittacamere/")}"{cur("affittacamere/")}>{T["nav_aff"]}</a>'
            f'<a class="nav-x" href="{home}#prezzi">{T["nav_prices"]}</a>'
            f'<a class="nav-x" href="{home}#faq">{T["nav_faq"]}</a>'
            f'<a class="nav-x" href="{LOGIN}">{T["nav_login"]}</a>'
            f'<a class="nav-cta" href="{WA}">{T["cta"]}</a></nav>')


def header(lang, T, page):
    return (f'<header class="site-head"><div class="wrap"><a class="logo" href="{prefix(lang)}" '
            f'aria-label="{T["logo_aria"]}">{LOGO_SVG}Ospitalk</a>{nav(lang, T, page)}{switcher(lang, page)}'
            f'</div></header>')


def legal_href(lang, page):
    """Pagina legale nella lingua, oppure la versione inglese con l'indicazione English."""
    if lang in LEGAL_LANGS:
        return path(lang, page), ""
    return path("en", page), ' <span lang="en">(English)</span>'


def footer(lang, T):
    p = prefix(lang)
    it_note = ' <span lang="it">(Italiano)</span>'
    links = []
    for key, page in (("privacy", "privacy.html"), ("cookie", None), ("terms", "termini.html")):
        if page:
            href, note = legal_href(lang, page)
            links.append(f'<a href="{href}">{T["legal_" + key]}</a>{note}')
        else:
            links.append(f'<a href="/cookie.html">{T["legal_cookie"]}</a>{it_note}')
    dpa_href, dpa_note = legal_href(lang, "dpa.html")
    return (f'<footer class="site-foot"><div class="wrap"><div><strong>Ospitalk</strong> {T["foot_service"]}<br>'
            f'Via Giuseppe Garibaldi 23, 95010 Santa Venerina (CT), {T["italy"]} · {T["vat"]} IT05047840870<br>'
            f'{T["register"]}</div>'
            f'<nav class="foot-nav" aria-label="{T["foot_nav_label"]}"><a href="{p}case-vacanza/">{T["nav_cv"]}</a>'
            f'<a href="{p}bnb/">{T["nav_bnb"]}</a><a href="{p}affittacamere/">{T["nav_aff"]}</a>'
            f'<a href="{p}#prezzi">{T["nav_prices"]}</a><a href="{p}#faq">{T["faq_long"]}</a>'
            f'<a href="{LOGIN}">{T["nav_login"]}</a><a href="/" hreflang="it" lang="it">Italiano</a></nav>'
            f'<div class="footer-links"><a href="mailto:info@ospitalk.it">info@ospitalk.it</a><br>'
            f'{" · ".join(links)}<br><a href="{dpa_href}">{T["legal_dpa"]}</a>{dpa_note} · '
            f'<a href="/sub-responsabili.html">{T["legal_sub"]}</a>{it_note}<br>'
            f'<button type="button" class="link-btn" data-cookie-prefs>{T["cookie_prefs"]}</button><br>'
            f'{T["servizi_note"]}</div></div></footer>')


def head(lang, T, page, title, desc, og_title, og_desc, tw_desc, ld):
    i = INFO[lang]
    if lang in SYSTEM_FONT_LANGS:
        fonts = '<link rel="stylesheet" href="/style.css">'
    else:
        fonts = ('<link rel="preload" href="/fonts/AtkinsonNext.woff2" as="font" type="font/woff2" crossorigin>'
                 '<link rel="preload" href="/fonts/Newsreader.woff2" as="font" type="font/woff2" crossorigin>'
                 '<link rel="stylesheet" href="/fonts/fonts.css"><link rel="stylesheet" href="/style.css">')
    u = url(lang, page)
    return f"""<!DOCTYPE html>
<html lang="{i[1]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="/consent.js"></script>
<script src="/lang-menu.js" defer></script>
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{u}">
{hreflang_links(page)}
<meta property="og:type" content="website"><meta property="og:locale" content="{i[3]}"><meta property="og:site_name" content="Ospitalk">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:url" content="{u}"><meta property="og:image" content="https://ospitalk.it/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{T["og_alt"]}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{og_title}"><meta name="twitter:description" content="{tw_desc}"><meta name="twitter:image" content="https://ospitalk.it/og-image.png"><meta name="twitter:image:alt" content="{T["og_alt"]}">
<meta name="theme-color" content="#F6F0E4">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{fonts}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
{header(lang, T, page)}
"""


def fill(s, lang):
    """Segnaposto nei testi: {home} {cin} {terms} {prices} {faq}."""
    terms, _ = legal_href(lang, "termini.html")
    return (s.replace("{home}", prefix(lang)).replace("{cin}", "/guida-cin/").replace("{terms}", terms)
            .replace("{prices}", prefix(lang) + "#prezzi").replace("{faq}", prefix(lang) + "#faq"))


def btn(T):
    return f'<a class="btn" href="{WA}">{ico("chat")}{T["cta"]}</a>'


def qr(T):
    return (f'<figure class="bigtag-qr"><img src="/qr-attiva.svg" width="168" height="168" loading="lazy" '
            f'decoding="async" alt="{T["qr_alt"]}"><figcaption>{T["qr_cap"]}</figcaption></figure>')


ORG = {
    "@type": "Organization",
    "@id": "https://ospitalk.it/#organization",
    "name": "Ospitalk",
    "legalName": "RGM S.r.l.",
    "url": "https://ospitalk.it/",
    "logo": "https://ospitalk.it/apple-touch-icon.png",
    "email": "info@ospitalk.it",
    "telephone": "+39 327 748 5039",
    "vatID": "IT05047840870",
    "contactPoint": {"@type": "ContactPoint", "telephone": "+39 327 748 5039",
                     "contactType": "customer service", "availableLanguage": ["Italian", "English"]},
    "address": {"@type": "PostalAddress", "streetAddress": "Via Giuseppe Garibaldi 23", "postalCode": "95010",
                "addressLocality": "Santa Venerina", "addressRegion": "CT", "addressCountry": "IT"},
}


def price_spec(price, unit=False):
    spec = {"@type": "UnitPriceSpecification" if unit else "PriceSpecification", "price": price,
            "priceCurrency": "EUR", "valueAddedTaxIncluded": True}
    if unit:
        spec["unitCode"] = "MON"
    return spec


# ---------------------------------------------------------------- home

def home(lang, T):
    i = INFO[lang]
    u = url(lang, "")
    L = T["ld"]
    offers = []
    for (name, desc), price, unit in zip(L["offers"], ["0", "99", "149", "19.90"], [False, False, False, True]):
        offers.append({"@type": "Offer", "name": name, "price": price, "priceCurrency": "EUR", "description": desc,
                       "url": u + "#prezzi", "priceSpecification": price_spec(price, unit)})
    ld = {"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "WebPage", "@id": u + "#webpage", "url": u, "name": plain(T["title"]),
         "description": plain(T["desc"]), "isPartOf": {"@id": "https://ospitalk.it/#website"},
         "about": {"@id": u + "#software"}, "publisher": {"@id": "https://ospitalk.it/#organization"},
         "inLanguage": i[4]},
        {"@type": "SoftwareApplication", "@id": u + "#software", "name": "Ospitalk", "url": u,
         "applicationCategory": "BusinessApplication", "applicationSubCategory": L["subcat"],
         "operatingSystem": "Web", "publisher": {"@id": "https://ospitalk.it/#organization"},
         "description": L["desc"], "inLanguage": i[4], "areaServed": "IT", "featureList": L["features"],
         "offers": offers},
        {"@type": "FAQPage", "@id": u + "#faq", "inLanguage": i[4], "mainEntity": [
            {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(fill(a, lang))}}
            for q, a in T["faq"]]},
    ]}
    f = lambda s: fill(s, lang)
    ledger = "".join(f'\n    <li><q>{q}</q><p>{p}</p><span class="stamp{cls}">{st}</span></li>'
                     for (q, p, st), cls in zip(T["ledger"], [" stamp-green", "", " stamp-ink"]))
    steps = "".join(f'\n        <li class="step"><h3>{h}</h3><p>{p}</p></li>' for h, p in T["steps"])
    icons = ["chat", "mic", "handoff", "save", "globe", "key", "door", "cloche"]
    feats = "".join(f'\n    <div class="feature">{ico(n)}<h3>{h}</h3><p>{p}</p></div>'
                    for n, (h, p) in zip(icons, T["features"]))
    keys = "".join(f'\n    <article class="keytag"><h3>{h}</h3><p>{p}</p><p><a class="text-link" href="{path(lang, pg)}">{a}</a></p></article>'
                   for pg, (h, p, a) in zip(PAGES[1:], T["keyrack"]))
    P = T["prices"]
    welcome_li = "".join(f'\n      <li>{ico("check")}{x}</li>' for x in T["welcome_li"])
    faq = "".join(f'\n    <details><summary>{q}</summary><p>{f(a)}</p></details>' for q, a in T["faq"])
    body = f"""<main>
  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <h1><span class="kicker">{T["kicker"]}</span>{T["h1"]}<em>{T["h1_em"]}</em></h1>
        <p class="lead">{T["lead"]}</p>
        {btn(T)}
        <p class="hero-note">{T["hero_note"]}<br><strong>{T["trial"]}</strong><br>{T["offer"]}</p>
      </div>
      <figure class="scene">
        <div class="placard" aria-hidden="true">
          {PLACARD_STRING}
          <span class="placard-name">Casa Limoni</span>
          <svg class="placard-qr"><use href="/icons.svg#i-qrdeco"/></svg>
          <span class="placard-text">{T["placard_text"]}</span>
        </div>
        <ol class="trail" aria-label="{T["trail_label"]}">
          <li class="msg msg-guest"><span class="who">{T["who_guest_en"]}</span><span lang="en">Hi! What's the Wi-Fi password?</span></li>
          <li class="msg msg-auto"><span class="who">{T["who_auto"]}</span><span lang="en">Network “CasaLimoni”, password limoni2026. Enjoy your stay!</span> <span class="stamp">{T["stamp_sent"]}</span></li>
          <li class="msg msg-guest"><span class="who">{T["who_guest_de"]}</span><span lang="de">Können wir das Gepäck schon um 10 Uhr abgeben?</span></li>
          <li class="msg msg-relay">{ico("handoff")}{T["relay"]}</li>
          <li class="msg msg-host"><span class="who">{T["who_host"]}</span>{T["host_msg"]} <span class="stamp stamp-green">{T["stamp_saved"]}</span></li>
        </ol>
        <figcaption>{T["scene_cap"]}</figcaption>
      </figure>
    </div>
  </section>

  <section class="band"><div class="wrap"><div class="sec-head"><p class="eyebrow">{T["e1"]}</p><h2>{T["h2_1"]}</h2></div><ol class="ledger">{ledger}
  </ol></div></section>

  <section id="come-funziona"><div class="wrap how">
    <div>
      <p class="eyebrow">{T["nav_how"]}</p><h2>{T["h2_2"]}</h2><p class="lead">{T["lead_2"]}</p>
      <div class="voice" aria-hidden="true"><span class="voice-play"></span><svg class="ico" viewBox="0 0 120 28" preserveAspectRatio="none"><use href="/icons.svg#i-wave"/></svg><span class="voice-time">0:42</span></div>
      <p class="voice-cap">{T["voice_cap"]}</p>
    </div>
    <div class="receipt">
      <p class="receipt-head">{T["receipt_head"]}</p>
      <ol class="steps">{steps}
      </ol>
      <p class="receipt-foot">{T["receipt_foot"]}</p>
    </div>
  </div></section>

  <section class="band"><div class="wrap"><div class="sec-head"><p class="eyebrow">{T["e3"]}</p><h2>{T["h2_3"]}</h2></div><div class="features">{feats}
  </div></div></section>

  <section><div class="wrap"><div class="sec-head"><p class="eyebrow">{T["e4"]}</p><h2>{T["h2_4"]}</h2><p class="lead">{T["lead_4"]}</p></div><div class="keyrack">{keys}
  </div></div></section>

  <section id="prezzi"><div class="wrap"><div class="sec-head"><p class="eyebrow">{T["nav_prices"]}</p><h2>{P["h2"]}</h2><p class="lead"><strong>{T["offer"]}</strong> {P["lead"]}</p></div>
    <div class="prices prices-3">
      <article class="price price-hl"><span class="label">{P["launch_label"]}</span><h3>{P["season"]}</h3><p class="amount">€99</p><p>{P["season_p"]}</p></article>
      <article class="price"><h3>{P["annual"]}</h3><p class="amount">€149</p><p>{P["annual_p"]}</p></article>
      <article class="price"><h3>{P["monthly"]}</h3><p class="amount">€19,90<span>{P["per_month"]}</span></p><p>{P["monthly_p"]}</p></article>
    </div>
    <p class="price-note">{f(P["note"])}</p>
  </div></section>

  <section class="welcome-sec"><div class="wrap welcome">
    <div class="welcome-card"><span class="label">{T["w_label"]}</span><h2>{T["w_h2"]}</h2><p>{T["w_p"]}</p><p>{btn(T)}</p></div>
    <ul>{welcome_li}
    </ul>
  </div></section>

  <section class="band" id="faq"><div class="wrap"><p class="eyebrow">{T["faq_long"]}</p><h2>{T["h2_faq"]}</h2><div class="faq">{faq}
  </div></div></section>

  <section class="final-cta"><div class="wrap"><div class="bigtag">
    <div><p class="eyebrow">{T["e_start"]}</p><h2>{T["h2_final"]}</h2><p class="lead">{T["lead_final"]}</p>{btn(T)}<p class="bigtag-number">WhatsApp +39 327 748 5039</p></div>
    {qr(T)}
  </div></div></section>
</main>
"""
    return head(lang, T, "", T["title"], T["desc"], T["title"], T["desc"], T["desc"], ld) + body + footer(lang, T) + "\n</body>\n</html>\n"


# ---------------------------------------------------------------- pagine per tipo di struttura

VERTICAL_ICONS = {"case-vacanza/": ["wifi", "bin", "pin", "suitcase"], "bnb/": ["clock", "bed", "cup", "map"],
                  "affittacamere/": ["door", "linen", "moon", "handoff"]}


def vertical(lang, T, page):
    V = T["v"][page]
    i = INFO[lang]
    u = url(lang, page)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": u + "#webpage", "url": u, "name": V["ld_name"], "description": V["ld_desc"],
         "about": {"@id": url(lang, "") + "#software"}, "isPartOf": {"@id": "https://ospitalk.it/#website"},
         "publisher": {"@id": "https://ospitalk.it/#organization"}, "inLanguage": i[4]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Ospitalk", "item": url(lang, "")},
            {"@type": "ListItem", "position": 2, "name": plain(V["crumb"]), "item": u}]},
    ]}
    f = lambda s: fill(s, lang)
    cards = "".join(f'\n    <article class="card"><h3>{h}</h3><p>{p}</p></article>' for h, p in V["cards"])
    feats = "".join(f'\n    <div class="feature">{ico(n)}<h3>{h}</h3><p>{p}</p></div>'
                    for n, (h, p) in zip(VERTICAL_ICONS[page], V["features"]))
    s3 = "".join(f"<p>{f(x)}</p>" for x in V["s3_ps"])
    s4 = "".join(f"<p>{f(x)}</p>" for x in V["s4_ps"])
    related = "".join(f'<a href="{path(lang, pg)}">{T["rel"][pg]}</a>' for pg in PAGES[1:] if pg != page)
    related += f'<a href="{prefix(lang)}">{T["back_home"]}</a>'
    body = f"""<main>
  <section class="vertical-hero"><div class="wrap"><div><nav class="breadcrumb" aria-label="{T["crumb_label"]}"><ol><li><a href="{prefix(lang)}">Home</a></li><li aria-current="page">{V["crumb"]}</li></ol></nav><span class="badge">{V["badge"]}</span><h1>{V["h1"]}</h1><p class="lead">{V["lead"]}</p>{btn(T)}<p class="hero-note">{V["note"]}<br><strong>{T["trial"]}</strong><br>{T["offer"]}</p></div><div class="placard" aria-hidden="true">{PLACARD_STRING}<span class="placard-name">{V["placard"]}</span><svg class="placard-qr"><use href="/icons.svg#i-qrdeco"/></svg><span class="placard-text">{T["placard_text"]}</span></div></div></section>
  <section class="band"><div class="wrap"><span class="eyebrow">{V["e1"]}</span><h2>{V["h2_1"]}</h2><p class="lead">{V["lead_1"]}</p><div class="cards">{cards}
  </div></div></section>
  <section><div class="wrap"><span class="eyebrow">{V["e2"]}</span><h2>{V["h2_2"]}</h2><div class="features">{feats}
  </div></div></section>
  <section class="band"><div class="wrap narrow"><span class="eyebrow">{V["e3"]}</span><h2>{V["h2_3"]}</h2>{s3}</div></section>
  <section><div class="wrap narrow"><span class="eyebrow">{T["e_privacy"]}</span><h2>{V["h2_4"]}</h2>{s4}<p>{f(T["v_cin"])}</p><p>{V["prices_p"]} {T["v_prices_tail"]} <a class="text-link" href="{prefix(lang)}#prezzi">{T["prices_link"]}</a></p></div></section>
  <section class="final-cta"><div class="wrap"><div class="bigtag"><div><p class="eyebrow">{T["e_start"]}</p><h2>{V["cta_h2"]}</h2><p class="lead">{V["cta_lead"]}</p>{btn(T)}<div class="related" aria-label="{T["related_label"]}">{related}</div></div>{qr(T)}</div></div></section>
</main>
"""
    return (head(lang, T, page, V["title"], V["desc"], V["title"], V["og_desc"], V["tw_desc"], ld)
            + body + footer(lang, T) + "\n</body>\n</html>\n")


# ---------------------------------------------------------------- pagine esistenti

HEADER_RE = re.compile(r'<header class="site-head">.*?</header>', re.S)
FOOTER_RE = re.compile(r'<footer class="site-foot">.*?</footer>', re.S)
SWITCH_RE = re.compile(r'<details class="lang-switch">.*?</details>', re.S)
ALT_RE = re.compile(r'\n<link rel="alternate" hreflang="[^"]+" href="[^"]+">')


def add_menu_script(s):
    if "/lang-menu.js" not in s:
        s = s.replace('<script src="/consent.js"></script>',
                      '<script src="/consent.js"></script>\n<script src="/lang-menu.js" defer></script>', 1)
    return s


def patch_italian(rel, page, with_hreflang):
    p = ROOT / rel
    s = p.read_text()
    s = add_menu_script(s)
    s = SWITCH_RE.sub("", s)
    s = re.sub(r"(</nav>)(\s*</div>\s*</header>)", lambda m: m.group(1) + switcher("it", page) + m.group(2), s, count=1)
    if with_hreflang:
        s = ALT_RE.sub("", s)
        s = re.sub(r'(<link rel="canonical" href="[^"]+">)', lambda m: m.group(1) + "\n" + hreflang_links(page), s, count=1)
    p.write_text(s)


def patch_legal(lang, page, T):
    p = ROOT / lang / page
    s = p.read_text()
    s = add_menu_script(s)
    s = HEADER_RE.sub(lambda m: header(lang, T, page), s, count=1)
    s = FOOTER_RE.sub(lambda m: footer(lang, T), s, count=1)
    s = s.replace('<body lang="it">', "<body>")
    s = s.replace('<p><a href="/">← Ospitalk</a></p>', f'<p><a href="/{lang}/">← Ospitalk</a></p>')
    p.write_text(s)


def sitemap():
    groups = PAGES
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    old = (ROOT / "sitemap.xml").read_text()
    for page in groups:
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{hl}" href="{url(code, page)}"/>' for code, hl, *_ in LANGS)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url("it", page)}"/>'
        for code in CODES:
            out.append(f"  <url>\n    <loc>{url(code, page)}</loc>\n    <lastmod>2026-11-20</lastmod>{alts}\n  </url>")
    for page in ("guida-cin/", "welcome-book-digitale/"):
        m = re.search(r"<loc>%s</loc>\s*<lastmod>([^<]+)</lastmod>" % re.escape(url("it", page)), old)
        lastmod = m.group(1) if m else "2026-11-20"
        out.append(f"  <url>\n    <loc>{url('it', page)}</loc>\n    <lastmod>{lastmod}</lastmod>\n  </url>")
    out.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(out))


def main():
    strings = {c: load_strings(c) for c in CODES
               if c != "it" and (ROOT / "_i18n" / "strings" / f"{c}.py").exists()}
    for lang, T in strings.items():
        (ROOT / lang).mkdir(exist_ok=True)
        (ROOT / lang / "index.html").write_text(home(lang, T))
        for page in PAGES[1:]:
            (ROOT / lang / page).mkdir(parents=True, exist_ok=True)
            (ROOT / lang / page / "index.html").write_text(vertical(lang, T, page))
        if lang in LEGAL_LANGS:
            for page in LEGAL:
                if (ROOT / lang / page).exists():
                    patch_legal(lang, page, T)
    for page in PAGES:
        patch_italian(page + "index.html" if page else "index.html", page, True)
    for rel, page in [("guida-cin/index.html", "guida-cin/"), ("welcome-book-digitale/index.html", "welcome-book-digitale/"),
                      ("cookie.html", "cookie.html"), ("sub-responsabili.html", "sub-responsabili.html"),
                      ("termini.html", "termini.html"), ("privacy.html", "privacy.html"), ("dpa.html", "dpa.html"),
                      ("404.html", "404.html")]:
        patch_italian(rel, page, False)
    sitemap()


if __name__ == "__main__":
    main()
