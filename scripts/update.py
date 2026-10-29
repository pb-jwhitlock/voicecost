#!/usr/bin/env python3
"""VoiceCost daily update.

  python scripts/update.py              # fetch all pages, extract, snapshot, diff
  python scripts/update.py --offline    # re-extract from today's (or --date) raw pages, no network

Outputs:
  data/raw/<DATE>/...           raw page text + rendered HTML (kept forever -> history)
  data/snapshots/<DATE>.json    extracted, normalized prices
  data/latest.json              copy of newest snapshot
  data/changes/<DATE>.json      diff vs previous snapshot
  data/changelog.json           all diffs, newest first
"""
import argparse, asyncio, datetime as dt, glob, gzip, json, os, re, shutil, sys
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vendors as VC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
NORM_UNIT = {"agent": "USD/min", "stt": "USD/min", "tts": "USD/1M chars"}


def get_fx(rawdir):
    path = os.path.join(rawdir, "_fx.json")
    if os.path.exists(path):
        return json.load(open(path))
    fx = {"EUR_USD": None, "source": "https://api.frankfurter.app (ECB reference rates)", "date": None}
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=EUR&to=USD", timeout=20)
        j = r.json()
        fx["EUR_USD"], fx["date"] = j["rates"]["USD"], j["date"]
    except Exception as e:
        fx["error"] = str(e)[:200]
    json.dump(fx, open(path, "w"), indent=2)
    return fx


def extract(rawdir, date, fx, fetch_log):
    rows = []
    texts = {}
    for pid in VC.PAGES:
        p, pz = os.path.join(rawdir, pid + ".txt"), os.path.join(rawdir, pid + ".txt.gz")
        ok = fetch_log.get(pid, {}).get("ok", os.path.exists(p) or os.path.exists(pz))
        texts[pid] = None
        if ok and os.path.exists(p):
            texts[pid] = open(p).read()
        elif ok and os.path.exists(pz):
            texts[pid] = gzip.open(pz, "rt").read()
    for v in VC.V:
        for it in v["items"]:
            url = v["pages"][it["page"]]
            row = dict(vendor_id=v["id"], vendor=v["name"], category=it["category"],
                       product=it["product"], tier=it["tier"], headline=it["headline"],
                       source_url=url, checked=date, native_unit=it["unit"],
                       currency=it["currency"], norm_unit=NORM_UNIT[it["category"]],
                       price_native=None, price_native_high=None, price=None, price_high=None,
                       status="unknown", reason=None, evidence=None, note=it["note"],
                       scope=it.get("scope"))
            if v["status"] == "discontinued":
                row["status"] = "discontinued"
                row["reason"] = "Vendor appears discontinued"
                rows.append(row); continue
            t = texts.get(it["page"])
            if t is None:
                err = fetch_log.get(it["page"], {}).get("error") or "page could not be read"
                row["reason"] = f"Page fetch failed: {err}"
                rows.append(row); continue
            m = re.search(it["pattern"], t)
            if not m:
                row["reason"] = "Price not found on page (layout changed or not published)"
                rows.append(row); continue
            s, e = m.span()
            row["evidence"] = t[max(0, s - 40): e + 20].strip()
            num = lambda g: float(m.group(g).replace(",", ""))
            row["price_native"] = num(it["group"])
            if it["high_group"]:
                row["price_native_high"] = num(it["high_group"])
            if it["compute"]:
                norm, norm_hi = it["compute"](m), None
            elif it["factor"] is None:
                row["status"] = "no_rate"
                row["reason"] = "Published price is not a per-unit rate"
                rows.append(row); continue
            else:
                norm = row["price_native"] * it["factor"]
                norm_hi = row["price_native_high"] * it["factor"] if row["price_native_high"] is not None else None
            if it["currency"] == "EUR":
                if not fx.get("EUR_USD"):
                    row["reason"] = "No EUR->USD rate available"
                    rows.append(row); continue
                norm *= fx["EUR_USD"]
                norm_hi = norm_hi * fx["EUR_USD"] if norm_hi is not None else None
                row["fx"] = {"EUR_USD": fx["EUR_USD"], "date": fx["date"]}
            row["price"] = round(norm, 6)
            row["price_high"] = round(norm_hi, 6) if norm_hi is not None else None
            row["status"] = "verified"
            rows.append(row)

    def presets(spec):
        out = []
        for label, pid, pat in spec:
            t = texts.get(pid)
            m = re.search(pat, t) if t else None
            if m:
                out.append({"label": label, "price": float(m.group(1)), "source_url": VC.PAGES[pid]})
        return out

    vend = [dict(id=v["id"], name=v["name"], site=v["site"], categories=v["categories"],
                 note=v["note"], status=v["status"], pages=v["pages"]) for v in VC.V]
    return {"date": date, "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "fx": fx, "vendors": vend, "rows": rows,
            "llm_presets": presets(VC.LLM_PRESETS), "telephony_presets": presets(VC.TELEPHONY_PRESETS),
            "fetch": {k: {kk: vv for kk, vv in r.items() if kk in ("url", "ok", "status", "error", "final_url")}
                      for k, r in fetch_log.items()}}


def key(r):
    return f'{r["vendor_id"]}|{r["category"]}|{r["product"]}'


def diff(prev, cur):
    changes = []
    p = {key(r): r for r in prev["rows"]} if prev else {}
    c = {key(r): r for r in cur["rows"]}
    for k, r in c.items():
        o = p.get(k)
        if o is None:
            if prev: changes.append(dict(type="new_row", key=k, new=r["price"], status=r["status"]))
            continue
        if o["status"] != r["status"]:
            changes.append(dict(type="status", key=k, old=o["status"], new=r["status"],
                                old_price=o["price"], new_price=r["price"]))
        elif r["status"] == "verified" and (o["price"] != r["price"] or o.get("price_high") != r.get("price_high")):
            pct = (r["price"] - o["price"]) / o["price"] * 100 if o["price"] else None
            changes.append(dict(type="price", key=k, old=o["price"], new=r["price"],
                                old_high=o.get("price_high"), new_high=r.get("price_high"),
                                pct=round(pct, 1) if pct is not None else None))
    for k in p:
        if k not in c:
            changes.append(dict(type="removed_row", key=k))
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="don't fetch; re-extract existing raw pages")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()
    date = a.date
    rawdir = os.path.join(DATA, "raw", date)
    if a.offline:
        if not os.path.isdir(rawdir):
            sys.exit(f"no raw data for {date}")
        fetch_log = json.load(open(os.path.join(rawdir, "_fetch_log.json")))["pages"]
    else:
        import fetch
        print(f"Fetching {len(VC.PAGES)} pages -> {rawdir}")
        fetch_log = asyncio.run(fetch.fetch_all(VC.PAGES, rawdir))
    fx = get_fx(rawdir)
    snap = extract(rawdir, date, fx, fetch_log)

    os.makedirs(os.path.join(DATA, "snapshots"), exist_ok=True)
    os.makedirs(os.path.join(DATA, "changes"), exist_ok=True)
    prev_files = sorted(f for f in glob.glob(os.path.join(DATA, "snapshots", "*.json"))
                        if os.path.basename(f)[:10] < date)
    prev = json.load(open(prev_files[-1])) if prev_files else None
    changes = diff(prev, snap)
    snap["changes_vs"] = prev["date"] if prev else None
    snap["changes"] = changes

    json.dump(snap, open(os.path.join(DATA, "snapshots", f"{date}.json"), "w"), indent=1)
    shutil.copy(os.path.join(DATA, "snapshots", f"{date}.json"), os.path.join(DATA, "latest.json"))
    json.dump({"date": date, "vs": snap["changes_vs"], "changes": changes},
              open(os.path.join(DATA, "changes", f"{date}.json"), "w"), indent=1)
    # changelog: rebuild from change files
    log = []
    for f in sorted(glob.glob(os.path.join(DATA, "changes", "*.json")), reverse=True):
        j = json.load(open(f))
        if j["changes"]:
            log.append(j)
    json.dump(log, open(os.path.join(DATA, "changelog.json"), "w"), indent=1)

    rows = snap["rows"]
    ver = [r for r in rows if r["status"] == "verified"]
    print(f"\n{date}: {len(ver)}/{len(rows)} price rows verified across {len(VC.V)} vendors")
    for r in rows:
        if r["status"] != "verified":
            print(f"  [{r['status']}] {r['vendor']} / {r['product']}: {r['reason']}")
    if prev:
        print(f"\nChanges vs {prev['date']}: {len(changes)}")
        for c in changes:
            print("  CHANGE", json.dumps(c))
    else:
        print("\nNo previous snapshot - this is the baseline.")


if __name__ == "__main__":
    main()
