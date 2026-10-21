#!/usr/bin/env python3
"""Build the VoiceCost static site from data/ into site/ (plain HTML/CSS/JS)."""
import datetime as dt, glob, html, itertools, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, OUT, ASSETS = os.path.join(ROOT, "data"), os.path.join(ROOT, "site"), os.path.join(ROOT, "assets")
SITE_URL = os.environ.get("VOICECOST_URL", "https://voicecost.example")  # placeholder domain
SITE = "VoiceCost"
CAT = {"agent": "Voice agent platforms", "stt": "Speech-to-text", "tts": "Text-to-speech"}
CAT_SHORT = {"agent": "Voice agents", "stt": "STT", "tts": "TTS"}
UNIT = {"agent": "per minute", "stt": "per minute", "tts": "per 1M characters"}
SCOPE_LABEL = {"platform": "Platform fee only", "all-in": "All-in", "bundled": "Bundled models"}
e = lambda s: html.escape(str(s), quote=True)

snap = json.load(open(os.path.join(DATA, "latest.json")))
snaps = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(DATA, "snapshots", "*.json")))]
changelog = json.load(open(os.path.join(DATA, "changelog.json"))) if os.path.exists(os.path.join(DATA, "changelog.json")) else []
aff = json.load(open(os.path.join(ROOT, "affiliates.json")))
CFG = json.load(open(os.path.join(ROOT, "site.json")))

def utm(url, placement):
    return f"{url}{'&' if '?' in url else '?'}utm_source=voicecost&utm_medium=referral&utm_campaign={placement}"

def author_link():
    li = (CFG.get("author_linkedin") or "").strip()
    return f'<a href="{e(li)}" target="_blank" rel="noopener me">{e(CFG["author_name"])}</a>' if li else e(CFG["author_name"])

def agency_cta(placement):
    return f"""<aside class="card cta-soft"><p><b>Pricing this out for your business?</b> Get a free AI assessment from {e(CFG['agency_name'])}. We build AI and voice agents for small and medium-sized businesses.</p>
<a class="btn" href="{e(utm(CFG['agency_cta_url'], placement))}" target="_blank" rel="noopener">Get a free AI assessment</a></aside>"""
ROWS = snap["rows"]
VEND = {v["id"]: v for v in snap["vendors"]}
ORDER = [v["id"] for v in snap["vendors"]]
DATE = snap["date"]
D = dt.date.fromisoformat(DATE)
DATE_H = D.strftime("%b %-d, %Y")
MONTH = D.strftime("%b %Y")

def key(r): return f'{r["vendor_id"]}|{r["category"]}|{r["product"]}'
HIST = {}
for s in snaps:
    for r in s["rows"]:
        HIST.setdefault(key(r), []).append((s["date"], r["price"], r.get("price_high"), r["status"]))
CHG = {c["key"]: c for c in snap.get("changes", []) if c["type"] in ("price", "status")}

def fmt(p, cat):
    if p is None: return None
    if cat == "tts":
        return f"${p:,.2f}" if p < 100 else f"${p:,.0f}"
    if p >= 1: return f"${p:,.2f}"
    s = f"{p:.4f}".rstrip("0")
    if len(s.split(".")[1]) < 2: s = f"{p:.2f}"
    return "$" + s

def price_html(r):
    if r["status"] == "verified":
        s = fmt(r["price"], r["category"])
        if r.get("price_high"): s += "–" + fmt(r["price_high"], r["category"])
        return s
    if r["status"] == "no_rate":
        return f'<span class="unk" title="{e(r["reason"])}">No per-min rate</span>'
    return f'<span class="unk" title="{e(r["reason"] or "")}">Unknown</span>'

def native_html(r):
    if r["price_native"] is None: return "—"
    u = r["native_unit"]
    if u == "plan $/credits":
        return e(r["product"].split("(")[-1].rstrip(")"))
    cur = "€" if r["currency"] == "EUR" else "$"
    n = r["price_native"]
    s = f"{cur}{n:,.4f}".rstrip("0").rstrip(".") if n < 1 else f"{cur}{n:,.2f}".replace(".00", "")
    if r.get("price_native_high"): s += f"–{cur}{r['price_native_high']:g}"
    return e(s + " " + u.replace("$", "").replace("€", "").strip())

def best(vid, cat):
    """Cheapest verified headline-ish row for a vendor/category (prefer headline)."""
    rs = [r for r in ROWS if r["vendor_id"] == vid and r["category"] == cat]
    ver = [r for r in rs if r["status"] == "verified"]
    head = [r for r in ver if r["headline"]]
    return (head or ver or rs or [None])[0]

def cheapest(vid, cat):
    ver = [r for r in ROWS if r["vendor_id"] == vid and r["category"] == cat and r["status"] == "verified"]
    return min(ver, key=lambda r: r["price"]) if ver else None

def affurl(vid): return (aff.get(vid) or "").strip()

def outlink(vid):
    a = affurl(vid)
    url = a or VEND[vid]["site"]
    rel = "sponsored noopener" if a else "noopener"
    verb = "Try" if a else "Visit"
    return f'<a class="btn" href="{e(url)}" rel="{rel}" target="_blank" data-affiliate-slot="{e(vid)}"{" data-aff=\"1\"" if a else ""}>{verb} {e(VEND[vid]["name"])} →</a>'

def aff_note(vids, prefix):
    if not any(affurl(v) for v in vids): return ""
    return f'<span class="small muted aff-note">Affiliate link · <a href="{prefix}about.html">disclosure</a></span>'

def visit_link(vid):
    a = affurl(vid)
    if a:
        return f'<a class="visit" href="{e(a)}" rel="sponsored noopener" target="_blank" title="Affiliate link" data-aff="1">Try {e(VEND[vid]["name"])} ↗</a>'
    return f'<a class="visit" href="{e(VEND[vid]["site"])}" rel="noopener" target="_blank">Visit site ↗</a>'

def slug_pair(a, b): return f"{a}-vs-{b}"

# ------------------------------------------------------------------ layout
def page(path, title, desc, body, prefix, canonical, jsonld=None, extra_head=""):
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    doc = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/{canonical}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE_URL}/{canonical}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%234f46e5'/%3E%3Cpath d='M9 20v-8M14 24V8M19 20v-8M24 17v-2' stroke='white' stroke-width='2.6' stroke-linecap='round'/%3E%3C/svg%3E">
{ld}{extra_head}
</head><body>
<header class="top"><div class="wrap nav">
<a class="logo" href="{prefix}index.html"><span class="mark"></span>{SITE}</a>
<nav><a href="{prefix}start-here.html">Start here</a><a href="{prefix}index.html#agents">Agents</a><a href="{prefix}index.html#stt">STT</a><a href="{prefix}index.html#tts">TTS</a><a href="{prefix}index.html#calculator">Calculator</a><a href="{prefix}compare/index.html">Compare</a><a href="{prefix}changes.html">Changes</a></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">
{newsletter()}
<p class="small">Prices are read automatically from each vendor's public pricing page and normalized to USD. Last updated <b>{DATE_H}</b>. Always confirm on the vendor's site before buying. Some outbound links are affiliate links; that never changes the numbers. <a href="{prefix}methodology.html">How we collect prices</a> · <a href="{prefix}about.html">About &amp; disclosures</a> · <a href="{prefix}data/latest.json">Raw data (JSON)</a></p>
<p class="small">Built by {author_link()} · <a href="{e(utm(CFG['agency_url'], 'footer'))}" target="_blank" rel="noopener">{e(CFG['agency_name'])}</a> · © {D.year} {SITE}</p>
</div></footer>
<script src="{prefix}assets/app.js" defer></script>
</body></html>"""
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(doc)
    SITEMAP.append(canonical)

NEWSLETTER_URL = "https://voicecost.beehiiv.com/subscribe"

def newsletter():
    return f"""<section class="news" id="newsletter"><div>
<h3>Get the weekly voice AI price changes. Free.</h3><p>One short email a week with what changed in voice agent, speech-to-text and text-to-speech pricing. Unsubscribe anytime.</p></div>
<a class="btn nl-btn" href="{NEWSLETTER_URL}" target="_blank" rel="noopener">Subscribe free →</a></section>"""

def stamp():
    return f'<p class="stamp"><span class="dot"></span>Last updated <time datetime="{DATE}">{DATE_H}</time> · prices checked daily</p>'

def table(cat, rows, prefix, show_vendor=True, tid=None):
    head = ("<th data-sort='text'>Vendor</th>" if show_vendor else "") + \
        "<th data-sort='text'>Product / tier</th>" + \
        (f"<th data-sort='text' class='hide-s'>Scope</th>" if cat == "agent" else "") + \
        f"<th data-sort='num' class='num'><span class='hide-s'>Price {UNIT[cat]}</span><span class='show-s'>{'$/1M chars' if cat == 'tts' else '$/min'}</span></th>" + \
        ("<th data-sort='num' class='num hide-s'>Per hour</th>" if cat == "stt" else "") + \
        "<th class='hide-s'>As listed</th><th class='hide-s'>Source</th>"
    body = []
    for r in rows:
        sv = r["price"] if r["status"] == "verified" else 1e9
        c = CHG.get(key(r))
        badge = ""
        if c and c["type"] == "price":
            up = c["new"] > c["old"]
            badge = f' <span class="chg {"up" if up else "down"}" title="was {fmt(c["old"], cat)}">{"▲" if up else "▼"}{abs(c["pct"] or 0):.0f}%</span>'
        tds = []
        if show_vendor:
            tds.append(f'<td data-v="{e(r["vendor"])}"><a href="{prefix}vendors/{r["vendor_id"]}.html">{e(r["vendor"])}</a><br>{visit_link(r["vendor_id"])}</td>')
        tds.append(f'<td>{e(r["product"])}' + (f' <span class="tier">{e(r["tier"])}</span>' if r.get("tier") else "") +
                   (f'<div class="show-s"><span class="scope s-{e(r.get("scope") or "na")}">{e(SCOPE_LABEL.get(r.get("scope"), ""))}</span></div>' if cat == "agent" and r.get("scope") else "") +
                   (f'<div class="note">{e(r["note"])}</div>' if r.get("note") else "") + "</td>")
        if cat == "agent":
            tds.append(f'<td class="hide-s"><span class="scope s-{e(r.get("scope") or "na")}">{e(SCOPE_LABEL.get(r.get("scope"), "—"))}</span></td>')
        tds.append(f'<td class="num" data-v="{sv}"><b>{price_html(r)}</b>{badge}</td>')
        if cat == "stt":
            ph = f'${r["price"]*60:.2f}' if r["status"] == "verified" else "—"
            tds.append(f'<td class="num hide-s" data-v="{sv}">{ph}</td>')
        tds.append(f'<td class="hide-s small">{native_html(r)}</td>')
        tds.append(f'<td class="hide-s small"><a href="{e(r["source_url"])}" rel="nofollow noopener" target="_blank">source</a><br><span class="muted">{e(r["checked"])}</span></td>')
        cls = "" if r["status"] == "verified" else ' class="is-unk"'
        hd = ' data-head="1"' if r.get("headline") else ""
        body.append(f"<tr{cls}{hd}>" + "".join(tds) + "</tr>")
    foot = ""
    if show_vendor:
        names = sorted({VEND[r["vendor_id"]]["name"] for r in rows if affurl(r["vendor_id"])})
        if names:
            foot = f'<p class="small muted aff-note">"Try" links for {" and ".join(names)} are affiliate links. Source links go to official pricing pages. <a href="{prefix}about.html">Disclosure</a></p>'
    return f'<div class="tbl"><table class="sortable" {f"id={tid!r}" if tid else ""}><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>{foot}'

def sorted_rows(rows):
    return sorted(rows, key=lambda r: (r["status"] != "verified", r["price"] if r["price"] is not None else 0))

# ------------------------------------------------------------------ calculator data
def calc_data():
    opt = lambda r: {"id": key(r), "vid": r["vendor_id"], "label": f'{r["vendor"]} · {r["product"]}', "price": r["price"],
                     "high": r.get("price_high"), "src": r["source_url"], "scope": r.get("scope")}
    ver = [r for r in ROWS if r["status"] == "verified"]
    return {
        "stt": [opt(r) for r in sorted(ver, key=lambda r: r["price"]) if r["category"] == "stt"],
        "tts": [opt(r) for r in sorted(ver, key=lambda r: r["price"]) if r["category"] == "tts"],
        "platform": [opt(r) for r in ver if r["category"] == "agent" and r.get("scope") == "platform"],
        "agent": [opt(r) for r in sorted(ver, key=lambda r: r["price"]) if r["category"] == "agent" and r.get("scope") != "platform"],
        "llm": snap.get("llm_presets", []), "tel": snap.get("telephony_presets", []), "date": DATE,
        "aff": {v: {"name": VEND[v]["name"], "url": affurl(v)} for v in ORDER if affurl(v)},
    }

DEFAULT_PRESET = {"stt": "deepgram|stt|Nova-3 Monolingual (streaming, current price)",
                  "tts": "cartesia|tts|Sonic (Startup plan, $49 / 1.25M credits)"}

def calculator(preset=None, prefix=""):
    data = calc_data()
    ids = {o["id"] for k in ("stt", "tts", "platform", "agent") for o in data[k]}
    pre = {k: v for k, v in DEFAULT_PRESET.items() if v in ids}
    pre.update(preset or {})
    pre = json.dumps(pre)
    return f"""<section class="card calc" id="calculator">
<h2>Cost-per-call calculator</h2>
<p class="muted">Estimate what one call really costs. Prices come from today's table; LLM and telephony presets are per-minute rates published by Retell and Vapi. Everything is editable.</p>
<div class="tabs" role="tablist"><button type="button" class="tab on" data-mode="diy">Build your own stack</button><button type="button" class="tab" data-mode="all">All-in agent platform</button></div>
<div class="calc-grid">
<div class="fields">
<label>Minutes per call <input type="number" id="c-min" value="5" min="0" step="0.5"></label>
<label>Calls per month <input type="number" id="c-calls" value="1000" min="0" step="100"></label>
<div class="diy">
<label>Speech-to-text <select id="c-stt"></select></label>
<label>LLM ($/min) <select id="c-llm"></select></label>
<label class="custom" id="c-llm-cw">Custom LLM $/min <input type="number" id="c-llm-c" value="0.01" step="0.001" min="0"></label>
<label>Orchestration platform <select id="c-plat"></select></label>
<label>Text-to-speech <select id="c-tts"></select></label>
<div class="two"><label>Agent talk share % <input type="number" id="c-share" value="50" min="0" max="100"></label>
<label>Chars per spoken min <input type="number" id="c-cpm" value="800" min="0" step="50"></label></div>
<p class="small muted">Cartesia's pricing page puts one minute of speech at 750–800 characters; Rime says about 1,000. The talk share is your own guess at how much of each call the agent is speaking.</p>
</div>
<div class="all" hidden>
<label>Agent platform <select id="c-agent"></select></label>
<label class="chk"><input type="checkbox" id="c-agent-llm"> Add LLM cost (for platforms that bill the model separately)</label>
<label>LLM ($/min) <select id="c-llm2"></select></label>
</div>
<label>Telephony <select id="c-tel"></select></label>
</div>
<div class="result" aria-live="polite">
<div class="big"><span id="r-call">$0.00</span><small>per call</small></div>
<div class="kpis"><div><b id="r-min">$0.000</b><small>per minute</small></div><div><b id="r-month">$0</b><small>per month</small></div></div>
<div id="r-bars" class="bars"></div>
<p class="small muted" id="r-note"></p>
<p class="small r-try" id="r-try" hidden data-disc="{prefix}about.html"></p>
</div></div>
<script>window.VC_CALC={json.dumps(data)};window.VC_PRESET={pre};</script>
</section>"""

# ------------------------------------------------------------------ pages
SITEMAP = []

def build_index():
    ver = [r for r in ROWS if r["status"] == "verified"]
    def low(cat, pred=lambda r: True):
        c = [r for r in ver if r["category"] == cat and pred(r)]
        return min(c, key=lambda r: r["price"]) if c else None
    cards = []
    for cat, label, pred in [("stt", "Cheapest speech-to-text", lambda r: True),
                             ("tts", "Cheapest text-to-speech", lambda r: True),
                             ("agent", "Cheapest all-in / bundled agent", lambda r: r.get("scope") != "platform")]:
        r = low(cat, pred)
        if r:
            cards.append(f'<a class="kcard" href="vendors/{r["vendor_id"]}.html"><small>{label}</small><b>{fmt(r["price"], cat)}</b><span>{UNIT[cat]} · {e(r["vendor"])} {e(r["product"])}</span></a>')
    n_v = len({r["vendor_id"] for r in ver})
    n_unk = len([r for r in ROWS if r["status"] != "verified"])
    sections = []
    for cat, anchor in [("agent", "agents"), ("stt", "stt"), ("tts", "tts")]:
        rows = sorted_rows([r for r in ROWS if r["category"] == cat])
        intro = {
            "agent": "Per-minute pricing for voice agent platforms. Watch the scope: some charge a platform fee and pass speech and LLM costs through, others quote one all-in rate.",
            "stt": "Per-minute rates for transcription APIs, streaming and batch. Hourly prices are converted to per-minute.",
            "tts": "Price per 1 million characters of generated speech. Plan-based prices are divided by the characters each plan includes.",
        }[cat]
        sections.append(f'<section id="{anchor}" class="card"><div class="sec-h"><h2>{CAT[cat]}</h2><label class="toggle"><input type="checkbox" class="only-head" checked> Main products only</label></div><p class="muted">{intro} Click a column to sort.</p>{table(cat, rows, "", tid="t-"+cat)}</section>')
    pop_links = "".join(f'<a class="chip" href="compare/{slug_pair(a, b)}.html">{e(VEND[a]["name"])} vs {e(VEND[b]["name"])}</a>' for a, b in POPULAR_OK)
    body = f"""<section class="hero"><h1>Voice AI pricing, checked every day</h1>
<p class="lead">Compare per-minute prices for AI phone agents, speech-to-text and text-to-speech across {n_v} vendors, with price history and a calculator for what a call really costs.</p>
<p class="lead"><b>The real price per minute, checked daily, with receipts.</b> New here? <a href="start-here.html">Start here →</a></p>
{stamp()}<div class="kcards">{''.join(cards)}</div></section>
{calculator()}
{agency_cta('calculator')}
{''.join(sections)}
<section class="card"><h2>Popular comparisons</h2><div class="chips">{pop_links}</div><p><a href="compare/index.html">All comparisons →</a></p></section>
<p class="small muted">{n_unk} price rows are marked <span class="unk">Unknown</span> because the vendor's page couldn't be read or doesn't publish that price. We never guess.</p>"""
    title = f"Voice AI Pricing Tracker ({MONTH}): Agents, STT & TTS Cost per Minute | {SITE}"
    desc = f"Daily-updated prices for Vapi, Retell, Bland, ElevenLabs, Deepgram, AssemblyAI, Cartesia and more. Cost per minute, per 1M characters, price history and a cost-per-call calculator. Updated {DATE_H}."
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": SITE_URL + "/", "dateModified": DATE}
    page("index.html", title, desc, body, "", "", ld)

def history_block(r):
    h = HIST.get(key(r), [])
    pts = [(d, p) for d, p, _, st in h if st == "verified" and p is not None]
    if len(pts) < 2:
        return f'<span class="muted small">Tracking since {e(h[0][0] if h else DATE)}</span>'
    ps = [p for _, p in pts]; lo, hi = min(ps), max(ps)
    w, hgt = 120, 28
    xy = [(i * w / (len(ps) - 1), hgt - 3 - ((p - lo) / (hi - lo) * (hgt - 6) if hi > lo else (hgt - 6) / 2)) for i, p in enumerate(ps)]
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    return f'<svg class="spark" width="{w}" height="{hgt}" viewBox="0 0 {w} {hgt}"><polyline points="{path}" fill="none" stroke="currentColor" stroke-width="2"/></svg><span class="muted small"> {len(pts)} checks since {pts[0][0]}</span>'

def build_vendor(vid):
    v = VEND[vid]
    vr = [r for r in ROWS if r["vendor_id"] == vid]
    cats = [c for c in ("agent", "stt", "tts") if any(r["category"] == c for r in vr)]
    parts = []
    for c in cats:
        rows = sorted_rows([r for r in vr if r["category"] == c])
        parts.append(f'<section class="card"><h2>{CAT[c]}</h2>{table(c, rows, "../", show_vendor=False)}</section>')
    hist_rows = "".join(f'<tr><td>{e(r["product"])} <span class="tag">{CAT_SHORT[r["category"]]}</span></td><td class="num">{price_html(r)}</td><td>{history_block(r)}</td></tr>' for r in vr)
    comps = [p for p in ALL_PAIRS if vid in p]
    comp_links = "".join(f'<a class="chip" href="../compare/{slug_pair(a, b)}.html">{e(VEND[a]["name"])} vs {e(VEND[b]["name"])}</a>' for a, b in comps[:24])
    ver = [r for r in vr if r["status"] == "verified"]
    summ = []
    for c in cats:
        r = cheapest(vid, c)
        if r: summ.append(f"{CAT_SHORT[c]} from {fmt(r['price'], c)} {UNIT[c]}")
    summary = "; ".join(summ) if summ else "no verified prices right now"
    status = '<p class="warn">This service appears to be discontinued.</p>' if v["status"] == "discontinued" else ""
    note = f'<p class="note-box">{e(v["note"])}</p>' if v.get("note") else ""
    srcs = "".join(f'<li><a href="{e(u)}" rel="nofollow noopener" target="_blank">{e(u)}</a> {"✓" if snap["fetch"].get(pid, {}).get("ok") else "<span class=unk>could not be read</span>"}</li>' for pid, u in v["pages"].items())
    body = f"""<nav class="crumbs"><a href="../index.html">Home</a> › Vendors › {e(v["name"])}</nav>
<section class="hero sm"><h1>{e(v["name"])} pricing</h1><p class="lead">{e(summary[0].upper() + summary[1:])}.</p>{stamp()}{status}{note}
<div class="cta">{outlink(vid)}{aff_note([vid], "../")}</div></section>
{''.join(parts)}
<section class="card"><h2>Price history</h2><div class="tbl"><table><thead><tr><th>Product</th><th class="num">Today</th><th>History</th></tr></thead><tbody>{hist_rows}</tbody></table></div></section>
<section class="card"><h2>Compare {e(v["name"])}</h2><div class="chips">{comp_links or '<span class="muted">No comparisons yet.</span>'}</div></section>
<section class="card"><h2>Sources</h2><ul class="src">{srcs}</ul></section>"""
    title = f"{v['name']} Pricing ({MONTH}): Cost per Minute & Price History | {SITE}"
    desc = f"{v['name']} pricing checked {DATE_H}: {summary}. Every tier, normalized units, price history and source links."
    page(f"vendors/{vid}.html", title, desc, body, "../", f"vendors/{vid}.html")

def shared_cats(a, b):
    out = []
    for c in ("agent", "stt", "tts"):
        if cheapest(a, c) and cheapest(b, c): out.append(c)
    return out

def build_pair(a, b):
    A, B = VEND[a], VEND[b]
    cats = shared_cats(a, b)
    secs, faq, desc_bits = [], [], []
    for c in cats:
        ra, rb = cheapest(a, c), cheapest(b, c)
        rows = sorted_rows([r for r in ROWS if r["vendor_id"] in (a, b) and r["category"] == c])
        cheaper, other = (ra, rb) if ra["price"] <= rb["price"] else (rb, ra)
        diff = (other["price"] - cheaper["price"]) / other["price"] * 100 if other["price"] else 0
        verdict = (f"<b>{e(cheaper['vendor'])}</b> has the lower listed {CAT_SHORT[c]} price: {fmt(cheaper['price'], c)} {UNIT[c]} "
                   f"({e(cheaper['product'])}) vs {fmt(other['price'], c)} for {e(other['vendor'])} ({e(other['product'])}), about {diff:.0f}% less.") if diff >= 0.5 else \
                  f"Both list the same lowest {CAT_SHORT[c]} price: {fmt(ra['price'], c)} {UNIT[c]}."
        caveat = ""
        if c == "agent":
            sa, sb = ra.get("scope"), rb.get("scope")
            if sa != sb:
                caveat = f'<p class="warn">Not apples to apples: {e(A["name"])}\'s rate is <b>{e(SCOPE_LABEL.get(sa, "?").lower())}</b> while {e(B["name"])}\'s is <b>{e(SCOPE_LABEL.get(sb, "?").lower())}</b>. Use the calculator below to add speech, LLM and telephony costs.</p>'
        if c in ("agent", "stt"):
            ex = "".join(f"<tr><td>{m:,} min</td><td class='num'>${ra['price']*m:,.2f}</td><td class='num'>${rb['price']*m:,.2f}</td></tr>" for m in (1000, 10000, 100000))
            unit_lbl = "minutes"
        else:
            ex = "".join(f"<tr><td>{m:,}M chars</td><td class='num'>${ra['price']*m:,.2f}</td><td class='num'>${rb['price']*m:,.2f}</td></tr>" for m in (1, 10, 100))
            unit_lbl = "characters"
        secs.append(f"""<section class="card"><h2>{CAT[c]}: {e(A['name'])} vs {e(B['name'])}</h2><p class="verdict">{verdict}</p>{caveat}
{table(c, rows, "../")}
<h3>What it costs at volume (lowest listed rate)</h3><div class="tbl"><table><thead><tr><th>{unit_lbl.title()}</th><th class="num">{e(A['name'])}</th><th class="num">{e(B['name'])}</th></tr></thead><tbody>{ex}</tbody></table></div></section>""")
        faq.append((f"Is {A['name']} or {B['name']} cheaper for {CAT[c].lower()}?",
                    html.unescape(verdict.replace("<b>", "").replace("</b>", "")) + f" Prices checked {DATE_H}."))
        desc_bits.append(f"{CAT_SHORT[c]}: {A['name']} from {fmt(ra['price'], c)} vs {B['name']} from {fmt(rb['price'], c)}")
    preset = {}
    if "agent" in cats:
        ra, rb = cheapest(a, "agent"), cheapest(b, "agent")
        for r in (ra, rb):
            if r.get("scope") != "platform": preset = {"mode": "all", "agent": key(r)}; break
        else: preset = {"mode": "diy", "plat": key(ra)}
    elif "stt" in cats: preset = {"mode": "diy", "stt": key(cheapest(a, "stt"))}
    elif "tts" in cats: preset = {"mode": "diy", "tts": key(cheapest(a, "tts"))}
    what = " & ".join(CAT_SHORT[c] for c in cats)
    title = f"{A['name']} vs {B['name']} Pricing ({MONTH}): {what} Cost Compared | {SITE}"
    desc = f"{A['name']} vs {B['name']}, prices checked {DATE_H}. " + "; ".join(desc_bits) + ". Side-by-side tiers, volume costs and a call cost calculator."
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faq]}
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(t)}</p></details>" for q, t in faq)
    body = f"""<nav class="crumbs"><a href="../index.html">Home</a> › <a href="index.html">Compare</a> › {e(A['name'])} vs {e(B['name'])}</nav>
<section class="hero sm"><h1>{e(A['name'])} vs {e(B['name'])} pricing</h1>
<p class="lead">{e('; '.join(desc_bits))}.</p>{stamp()}
<div class="cta">{outlink(a)}{outlink(b)}{aff_note([a, b], "../")}</div></section>
{''.join(secs)}
{calculator(preset, "../")}
<section class="card"><h2>FAQ</h2>{faq_html}
<details><summary>How often are these prices updated?</summary><p>Every day. A script reads each vendor's public pricing page, extracts the listed rates and keeps a dated copy, so price changes show up in the history.</p></details></section>
<p><a href="../vendors/{a}.html">All {e(A['name'])} prices</a> · <a href="../vendors/{b}.html">All {e(B['name'])} prices</a></p>"""
    page(f"compare/{slug_pair(a, b)}.html", title, desc, body, "../", f"compare/{slug_pair(a, b)}.html", ld)

def build_compare_index():
    groups = {}
    for a, b in ALL_PAIRS:
        for c in shared_cats(a, b):
            groups.setdefault(c, []).append((a, b))
    secs = "".join(f'<section class="card"><h2>{CAT[c]}</h2><div class="chips">' +
                   "".join(f'<a class="chip" href="{slug_pair(a, b)}.html">{e(VEND[a]["name"])} vs {e(VEND[b]["name"])}</a>' for a, b in ps) +
                   "</div></section>" for c, ps in groups.items())
    page("compare/index.html", f"Voice AI Pricing Comparisons ({MONTH}) | {SITE}",
         f"Side-by-side price comparisons of {len(ALL_PAIRS)} voice AI vendor pairs: agents, speech-to-text and text-to-speech. Updated {DATE_H}.",
         f'<section class="hero sm"><h1>Compare voice AI prices</h1>{stamp()}</section>{secs}', "../", "compare/index.html")

def build_changes():
    items = []
    for day in changelog:
        lis = []
        for c in day["changes"]:
            vid, cat, prod = c["key"].split("|", 2)
            name = VEND.get(vid, {}).get("name", vid)
            if c["type"] == "price":
                lis.append(f"<li><b>{e(name)}</b> {e(prod)}: {fmt(c['old'], cat)} → {fmt(c['new'], cat)} ({c['pct']:+.1f}%)</li>")
            elif c["type"] == "status":
                lis.append(f"<li><b>{e(name)}</b> {e(prod)}: status {e(c['old'])} → {e(c['new'])}</li>")
            else:
                lis.append(f"<li><b>{e(name)}</b> {e(prod)}: {e(c['type'].replace('_', ' '))}</li>")
        items.append(f"<section class='card'><h2>{e(day['date'])}</h2><p class='muted small'>vs {e(day['vs'])}</p><ul>{''.join(lis)}</ul></section>")
    body = f'<section class="hero sm"><h1>Voice AI price changes</h1><p class="lead">Every change our daily check has detected, newest first.</p>{stamp()}</section>' + \
        ("".join(items) or f'<section class="card"><p>No price changes detected yet. Tracking started {e(snaps[0]["date"] if snaps else DATE)}; changes appear here as soon as a vendor edits its pricing page.</p></section>')
    page("changes.html", f"Voice AI Price Changes Log | {SITE}", f"A dated log of price changes at voice AI vendors, detected by daily checks. Updated {DATE_H}.", body, "", "changes.html")

def build_about():
    unk = "".join(f"<li><b>{e(r['vendor'])}</b> · {e(r['product'])}: {e(r['reason'])}</li>" for r in ROWS if r["status"] != "verified")
    body = f"""<section class="hero sm"><h1>How VoiceCost collects prices</h1>{stamp()}</section>
<section class="card prose"><p>Every day a script opens each vendor's public pricing page in a headless browser, saves a dated copy of the page, and pulls out the listed prices with rules written for that page. Prices are converted to comparable units:</p>
<ul><li><b>Voice agents and speech-to-text:</b> US dollars per minute. Hourly prices are divided by 60.</li>
<li><b>Text-to-speech:</b> US dollars per 1 million characters. For plans that include credits, we divide the plan price by the included credits, where the vendor says 1 credit = 1 character.</li>
<li><b>Euro prices</b> are converted at the European Central Bank reference rate for that day ({snap['fx'].get('EUR_USD')} USD per EUR on {e(snap['fx'].get('date'))}).</li></ul>
<p>If a page can't be read, or a rule stops matching because the vendor changed the page, that price shows as <span class="unk">Unknown</span>. We never fill in a number by hand. Listed prices are before volume discounts, taxes and promotions unless noted.</p>
<h3>Currently unknown</h3><ul>{unk}</ul>
<h3>Disclosures</h3><p>Some outbound links (currently ElevenLabs and Vapi) are affiliate links, and VoiceCost's builder runs a company that sells voice agent setup services. Neither affects the prices shown or how rows are sorted. <a href="about.html">More on the About page</a>.</p></section>"""
    page("methodology.html", f"Methodology: How Voice AI Prices Are Collected | {SITE}", "How VoiceCost reads vendor pricing pages daily, normalizes units and handles unknown prices.", body, "", "methodology.html")

# ------------------------------------------------------------------ guide
def _row(k):
    for r in ROWS:
        if key(r) == k and r["status"] == "verified": return r
    return None

def _preset(lst, label):
    return next((p for p in snap.get(lst, []) if p["label"] == label), None)

def example_stack():
    """Worked example built from today's verified data. Returns None if any piece is missing."""
    plat = _row("vapi|agent|Vapi hosting fee (platform only)")
    stt = _row("deepgram|stt|Nova-3 Monolingual (streaming, current price)")
    tts = _row("elevenlabs|tts|Flash / Turbo")
    llm = _preset("llm_presets", "GPT 4.1 mini (via Retell list)")
    tel = _preset("telephony_presets", "Twilio inbound (via Vapi list)")
    if not all([plat, stt, tts, llm, tel]): return None
    share, cpm, mins = 0.5, 800, 5
    tts_min = tts["price"] / 1e6 * cpm * share
    parts = [("Platform fee", "Vapi hosting", plat["price"], plat["source_url"]),
             ("Speech-to-text", "Deepgram Nova-3 streaming", stt["price"], stt["source_url"]),
             ("LLM", "GPT 4.1 mini (per-minute rate from Retell's list)", llm["price"], llm["source_url"]),
             ("Text-to-speech", f"ElevenLabs Flash / Turbo (${tts['price']:.0f}/1M chars × {int(cpm*share)} chars/min)", tts_min, tts["source_url"]),
             ("Telephony", "Twilio inbound (rate from Vapi's list)", tel["price"], tel["source_url"])]
    total = sum(p[2] for p in parts)
    return {"parts": parts, "total": total, "mins": mins, "share": share, "cpm": cpm, "plat": plat["price"]}

def m4(x): return f"${x:.4f}"

def build_guide():
    n_v = len({r["vendor_id"] for r in ROWS if r["status"] == "verified"})
    first = snaps[0]["date"] if snaps else DATE
    first_h = dt.date.fromisoformat(first).strftime("%b %-d, %Y")
    ex = example_stack()
    if ex:
        rows = "".join(f'<tr><td>{e(a)}</td><td>{e(b)}</td><td class="num"><b>{m4(c)}</b></td><td class="small"><a href="{e(u)}" rel="nofollow noopener" target="_blank">source</a></td></tr>' for a, b, c, u in ex["parts"])
        exhtml = f"""<p><b>Example only</b>, using prices VoiceCost recorded on {DATE_H}. Assumptions: an inbound phone call, the agent speaks {int(ex['share']*100)}% of the time, and one spoken minute is about {ex['cpm']} characters (Cartesia's pricing page puts it at 750–800). Your stack and call pattern will differ.</p>
<div class="tbl"><table><thead><tr><th>Piece</th><th>Choice in this example</th><th class="num">$/min</th><th>Source</th></tr></thead><tbody>{rows}
<tr><td colspan="2"><b>Total per minute</b></td><td class="num"><b>{m4(ex['total'])}</b></td><td></td></tr></tbody></table></div>
<p>So the {m4(ex['plat']).rstrip('0')}/min platform fee is about {ex['plat']/ex['total']*100:.0f}% of what a minute actually costs here. A {ex['mins']}-minute call comes to about <b>${ex['total']*ex['mins']:.2f}</b>, not ${ex['plat']*ex['mins']:.2f}. The LLM rate is the per-minute figure Retell publishes for that model; Vapi passes model costs through at cost, so your actual LLM line may differ.</p>"""
    else:
        exhtml = "<p>The worked example is hidden today because one of its prices couldn't be verified. Use the calculator instead.</p>"
    vapi, el = (aff.get("vapi") or VEND["vapi"]["site"]), (aff.get("elevenlabs") or VEND["elevenlabs"]["site"])
    body = f"""<nav class="crumbs"><a href="index.html">Home</a> › Start here</nav>
<section class="hero sm"><h1>Start here: the real price per minute, checked daily, with receipts</h1>
<p class="lead">Many pricing roundups copy a vendor's headline price once and never touch it again. VoiceCost rechecks each tracked vendor's official pricing page every day, keeps a dated price history and a changes log, and helps you add up the all-in cost of a minute: platform fee, speech-to-text, LLM, text-to-speech and telephony.</p>
{stamp()}</section>
<section class="card prose"><h2>How to use VoiceCost</h2>
<ol>
<li><b>Price your call in the <a href="index.html#calculator">calculator</a>.</b> Pick a speech-to-text, LLM, platform, voice and phone line, or switch to "All-in agent platform". Enter your call length and monthly volume to get cost per call and per month.</li>
<li><b>Compare two vendors side by side.</b> Pages like <a href="compare/vapi-vs-retell.html">Vapi vs Retell</a> or <a href="compare/deepgram-vs-assemblyai.html">Deepgram vs AssemblyAI</a> line up each product's price. Browse them all on the <a href="compare/index.html">compare page</a>.</li>
<li><b>Check a vendor's page and price history.</b> Every vendor page (for example <a href="vendors/elevenlabs.html">ElevenLabs</a>) shows each product's price, the unit the vendor uses, a link to the source page, and a price-history line built from every daily check since tracking began on {first_h}.</li>
<li><b>Watch the <a href="changes.html">changes log</a>.</b> When a vendor edits a price, the change lands there with the old and new number and the date we spotted it.</li>
</ol>
<p class="small muted">Tip: in the agent table, watch the <b>Scope</b> column. "Platform fee only" means models and phone minutes cost extra. "Bundled" and "All-in" include more, but each vendor's note says what's left out.</p></section>
<section class="card prose"><h2>What a voice agent call really costs</h2>
<p>A voice agent stacks five meters, and each one runs every minute of the call:</p>
<ul><li><b>Platform fee</b>: the orchestration layer (for example <a href="{e(vapi)}" rel="sponsored noopener" target="_blank">Vapi</a>, Retell, LiveKit).</li>
<li><b>Speech-to-text</b>: turns the caller's voice into text.</li>
<li><b>LLM</b>: decides what to say.</li>
<li><b>Text-to-speech</b>: speaks the reply (for example <a href="{e(el)}" rel="sponsored noopener" target="_blank">ElevenLabs</a>). Billed by characters, so it depends on how much the agent talks.</li>
<li><b>Telephony</b>: the phone number and carrier minutes.</li></ul>
<p>Many platforms advertise only the first line. Here's what happens when you add the rest.</p>
{exhtml}
<p><a class="btn" href="index.html#calculator">Try your own numbers →</a></p></section>
<section class="card prose"><h2>What "checked daily" means</h2>
<p>A scheduled job reads {len(ORDER)} vendors' public pricing pages each morning. We currently have verified prices for {n_v} of them. If a page can't be read or doesn't publish a price, we show <span class="unk">Unknown</span> instead of guessing. Every price links to its source and the date it was checked. Full details are in <a href="methodology.html">how we collect prices</a>, and the raw numbers are in <a href="data/latest.json">JSON</a>.</p>
<p class="small muted">Disclosure: some links (currently ElevenLabs and Vapi) are affiliate links. We may earn a commission at no cost to you. It never changes the prices shown or how they're sorted.</p></section>
{agency_cta('start-here')}"""
    page("start-here.html", f"Start Here: Real Voice AI Cost per Minute, Checked Daily | {SITE}",
         "How to use VoiceCost: calculator, comparisons, vendor price history and changes log, plus what a voice agent call really costs once STT, LLM, TTS and telephony are added.",
         body, "", "start-here.html")

def build_about_page():
    links = [f'<a href="{e(utm(CFG["agency_url"], "about"))}" target="_blank" rel="noopener">{e(CFG["agency_name"])}</a>']
    if CFG.get("author_linkedin"):
        links.append(f'<a href="{e(CFG["author_linkedin"])}" target="_blank" rel="noopener me">LinkedIn</a>')
    if CFG.get("youtube_url"):
        links.append(f'<a href="{e(CFG["youtube_url"])}" target="_blank" rel="noopener">YouTube</a>')
    first = snaps[0]["date"] if snaps else DATE
    first_h = dt.date.fromisoformat(first).strftime("%b %-d, %Y")
    body = f"""<nav class="crumbs"><a href="index.html">Home</a> › About</nav>
<section class="hero sm"><h1>About VoiceCost</h1></section>
<section class="card prose"><h2>Who's behind it</h2>
<p>{e(CFG['author_name'])} runs {e(CFG['agency_name'])}, which builds AI and voice agents for small and medium-sized businesses.</p>
<p class="small">{' · '.join(links)}</p>
<h2>Why VoiceCost exists</h2>
<p>Voice AI pricing is hard to compare. Vendors use different units (per minute, per hour, per character, per credit), and a platform's headline per-minute fee often leaves out speech-to-text, the LLM, text-to-speech and the phone line. Many comparison posts copy a headline price once and never update it. VoiceCost rechecks each vendor's official pricing page every day, keeps a dated history and a changes log, and helps you add up what a call really costs. Daily tracking started on {first_h}.</p>
<h2>How prices are collected</h2>
<p>A scheduled job reads each tracked vendor's public pricing page, saves a dated copy, and extracts the listed prices. If a price can't be read, it shows as <span class="unk">Unknown</span>; nothing is filled in by hand. Details are on the <a href="methodology.html">methodology page</a>.</p>
<h2>Disclosures</h2>
<ul><li><b>Affiliate links.</b> Some outbound links (currently ElevenLabs and Vapi) are affiliate links. If you sign up through them, VoiceCost may earn a commission at no cost to you.</li>
<li><b>Services.</b> {e(CFG['author_name'])}'s company, {e(CFG['agency_name'])}, sells voice agent setup services.</li></ul>
<p>Comparisons are based only on published vendor prices. Neither affiliate relationships nor {e(CFG['agency_name'])}'s services influence the numbers, which vendors are listed, or how rows are sorted.</p></section>"""
    page("about.html", f"About VoiceCost and Disclosures | {SITE}", "Who builds VoiceCost, why it exists, how prices are collected, and affiliate and services disclosures.", body, "", "about.html")

# ------------------------------------------------------------------ pairs
POPULAR = [("vapi", "retell"), ("vapi", "bland"), ("retell", "bland"), ("vapi", "synthflow"), ("retell", "synthflow"),
           ("deepgram", "assemblyai"), ("deepgram", "openai"), ("assemblyai", "openai"), ("deepgram", "speechmatics"),
           ("deepgram", "gladia"), ("assemblyai", "speechmatics"), ("elevenlabs", "cartesia"), ("elevenlabs", "deepgram"),
           ("elevenlabs", "google"), ("cartesia", "rime"), ("elevenlabs", "fish"), ("google", "aws"), ("aws", "azure"),
           ("vapi", "livekit"), ("retell", "elevenlabs"), ("deepgram", "aws"), ("google", "azure")]

def main():
    global ALL_PAIRS, POPULAR_OK
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(ASSETS, os.path.join(OUT, "assets"))
    os.makedirs(os.path.join(OUT, "data"))
    shutil.copy(os.path.join(DATA, "latest.json"), os.path.join(OUT, "data", "latest.json"))
    # all vendor pairs (in tracker order) that share at least one category with verified prices
    ALL_PAIRS = [(a, b) for a, b in itertools.combinations(ORDER, 2) if shared_cats(a, b)]
    pairset = set(ALL_PAIRS)
    POPULAR_OK = [p for p in POPULAR if p in pairset]
    for a, b in ALL_PAIRS: build_pair(a, b)
    for vid in ORDER: build_vendor(vid)
    build_compare_index(); build_changes(); build_about(); build_about_page(); build_guide(); build_index()
    urls = "".join(f"<url><loc>{SITE_URL}/{u}</loc><lastmod>{DATE}</lastmod></url>" for u in SITEMAP)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    open(os.path.join(OUT, "404.html"), "w").write(f'<!doctype html><meta charset="utf-8"><title>Not found</title><p>Page not found. <a href="{SITE_URL}/index.html">VoiceCost home</a></p>')
    print(f"Built {len(SITEMAP)} pages ({len(ALL_PAIRS)} comparisons, {len(ORDER)} vendors) -> {OUT}")

if __name__ == "__main__":
    main()
