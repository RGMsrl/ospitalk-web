#!/usr/bin/env python3
"""Controlli prima della PR. Uso, dalla radice:  python3 _i18n/check.py
1. HTML ben formato (tag aperti/chiusi in ordine) e JSON-LD valido in ogni pagina;
2. ogni link interno (href/src che iniziano con /) porta a un file esistente, e le ancore #id esistono;
3. pagine con hreflang: 11 lingue + x-default, codici giusti, canonical verso sé stessa, reciprocità;
4. prezzi, numero, link WhatsApp, email e accesso identici in tutte le home (e nelle pagine per struttura);
5. ogni file di stringhe ha esattamente le stesse chiavi dell'inglese.
Esce con codice 1 se qualcosa non va."""
import html.parser
import importlib.util
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_i18n"))
import build  # noqa: E402

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SVG_SELF = {"use", "path", "circle", "rect", "line", "polyline", "polygon", "ellipse", "stop"}
errors = []


def err(msg):
    errors.append(msg)


class Checker(html.parser.HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.name, self.stack, self.ids, self.links, self.ld, self._in_ld = name, [], set(), [], [], False
        self.alternates, self.canonical, self.lang = [], None, None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            if a["id"] in self.ids:
                err(f"{self.name}: id duplicato {a['id']}")
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.links.append(a[k])
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.alternates.append((a["hreflang"], a["href"]))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._buf = True, []
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src"):
            if a.get(k):
                self.links.append(a[k])
        if tag not in VOID and tag not in SVG_SELF:
            err(f"{self.name}: <{tag}/> autochiuso non valido in HTML")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "script" and self._in_ld:
            self._in_ld = False
            self.ld.append("".join(self._buf))
        if not self.stack:
            err(f"{self.name}: </{tag}> senza apertura alla riga {self.getpos()[0]}")
            return
        open_tag, pos = self.stack.pop()
        if open_tag != tag:
            err(f"{self.name}: </{tag}> alla riga {self.getpos()[0]} chiude <{open_tag}> aperto alla riga {pos[0]}")

    def handle_data(self, data):
        if self._in_ld:
            self._buf.append(data)


def target_file(href_path):
    p = ROOT / href_path.lstrip("/")
    if href_path.endswith("/"):
        p = p / "index.html"
    return p


pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "_i18n" not in p.parts)
parsed = {}
for p in pages:
    rel = p.relative_to(ROOT).as_posix()
    c = Checker(rel)
    c.feed(p.read_text())
    c.close()
    if c.stack:
        err(f"{rel}: tag non chiusi {[t for t, _ in c.stack]}")
    for block in c.ld:
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            err(f"{rel}: JSON-LD non valido: {e}")
    parsed[rel] = c

# 2. link interni e ancore
n_links = 0
for rel, c in parsed.items():
    for href in c.links:
        if href.startswith("//") or not (href.startswith("/") or href.startswith("#")):
            continue
        n_links += 1
        path_part, _, frag = href.partition("#")
        path_part = path_part.split("?")[0]
        if path_part:
            f = target_file(path_part)
            if not f.exists():
                err(f"{rel}: link interno rotto {href}")
                continue
            target_rel = f.relative_to(ROOT).as_posix()
        else:
            target_rel = rel
        if frag and target_rel in parsed and frag not in parsed[target_rel].ids:
            err(f"{rel}: ancora #{frag} assente in {target_rel}")

# 3. hreflang
expected_codes = [l[1] for l in build.LANGS] + ["x-default"]
url_to_rel = {}
for rel in parsed:
    if rel.endswith("index.html"):
        url_to_rel[build.BASE + "/" + rel[: -len("index.html")]] = rel
n_hreflang = 0
for rel, c in parsed.items():
    if not c.alternates:
        continue
    n_hreflang += 1
    codes = [h for h, _ in c.alternates]
    if codes != expected_codes:
        err(f"{rel}: hreflang {codes} invece di {expected_codes}")
    self_url = build.BASE + "/" + rel[: -len("index.html")]
    if c.canonical != self_url:
        err(f"{rel}: canonical {c.canonical} invece di {self_url}")
    alt = dict(c.alternates)
    lang_code = c.lang
    if alt.get(lang_code) != self_url:
        err(f"{rel}: l'hreflang della propria lingua ({lang_code}) non punta a sé stessa")
    for code, u in c.alternates:
        other = url_to_rel.get(u)
        if not other:
            err(f"{rel}: alternate {code} {u} senza file")
            continue
        if dict(parsed[other].alternates) != alt:
            err(f"{rel}: hreflang non reciproco con {other}")
        if code != "x-default" and parsed[other].lang != code:
            err(f"{other}: lang={parsed[other].lang} ma è indicato come hreflang {code}")

# sitemap
sm = ET.parse(ROOT / "sitemap.xml")
locs = [e.text for e in sm.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
for u in locs:
    if u not in url_to_rel:
        err(f"sitemap: {u} senza file")
for u, rel in url_to_rel.items():
    if parsed[rel].alternates and u not in locs:
        err(f"sitemap: manca {u}")

# 4. dati che devono essere identici
MUST = ["€74,50", "€99", "€19,90", "+39 327 748 5039", "https://wa.me/393277485039?text=ATTIVA%20OSPITALK",
        "info@ospitalk.it", "https://app.ospitalk.it/accounts/login/", "RGM S.r.l.", "IT05047840870",
        "Via Giuseppe Garibaldi 23, 95010 Santa Venerina (CT)", "05047840870", "ATTIVA OSPITALK"]
facts = {}
for code in [l[0] for l in build.LANGS]:
    for page in build.PAGES:
        rel = build.path(code, page).lstrip("/") + "index.html"
        if rel not in parsed:
            err(f"manca la pagina {rel}")
            continue
        text = (ROOT / rel).read_text()
        must = MUST if page == "" else [m for m in MUST if m not in ("+39 327 748 5039",)]
        missing = [m for m in must if m not in text]
        if missing:
            err(f"{rel}: mancano {missing}")
        if page == "":
            # cifre del lancio: 100 strutture, 14 giorni, 150 risposte, 30 giorni
            nums = [n for n in ("100", "14", "150", "30", "2027", "2028") if n not in re.sub(r"<[^>]+>", " ", text)]
            if nums:
                err(f"{rel}: numeri mancanti {nums}")
            facts[code] = {m: text.count(m) for m in MUST}

# 5. chiavi delle stringhe
def keys(obj, prefix=""):
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            out |= {prefix + k} | keys(v, prefix + k + ".")
    elif isinstance(obj, (list, tuple)):
        out.add(prefix + f"len={len(obj)}")
        for i, v in enumerate(obj):
            out |= keys(v, prefix + f"{i}.")
    return out

en_keys = keys(build.load_strings("en"))
for f in sorted((ROOT / "_i18n" / "strings").glob("*.py")):
    k = keys(build.load_strings(f.stem))
    if k != en_keys:
        err(f"stringhe {f.stem}: mancano {sorted(en_keys - k)[:8]} in più {sorted(k - en_keys)[:8]}")

print(f"Pagine HTML controllate: {len(pages)} · link interni: {n_links} · pagine con hreflang: {n_hreflang} · URL in sitemap: {len(locs)}")
print("Occorrenze dei dati fissi per home:")
for code, d in facts.items():
    print(f"  {code}: " + ", ".join(f"{k.split('?')[0][-22:]}×{v}" for k, v in d.items()))
if errors:
    print(f"\n{len(errors)} PROBLEMI:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("\nTutto a posto.")
