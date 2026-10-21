"""Fetch pricing pages with headless Chrome and save dated raw snapshots.

Saves, per page:  data/raw/<DATE>/<page_id>.txt     (all DOM text incl. hidden tabs, whitespace collapsed)
                  data/raw/<DATE>/<page_id>.html.gz (rendered HTML)
                  data/raw/<DATE>/_fetch_log.json  (status per page)
"""
import asyncio, gzip, json, os, re, sys, time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/129.0 Safari/537.36")
CHROME = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")


def dom_text(html):
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript", "svg", "template"]):
        t.decompose()
    txt = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", txt)


async def fetch_one(browser, pid, url, outdir, sem, log):
    async with sem:
        ctx = await browser.new_context(user_agent=UA, locale="en-US",
                                        viewport={"width": 1366, "height": 900})
        page = await ctx.new_page()
        rec = {"url": url, "ok": False, "status": None, "error": None, "final_url": None}
        for attempt in range(2):
            try:
                r = await page.goto(url, timeout=45000, wait_until="domcontentloaded")
                rec["status"] = r.status if r else None
                try:
                    await page.wait_for_load_state("networkidle", timeout=12000)
                except Exception:
                    pass
                await page.wait_for_timeout(2500)
                html = await page.content()
                rec["final_url"] = page.url
                txt = dom_text(html)
                with open(os.path.join(outdir, pid + ".txt"), "w") as f:
                    f.write(txt)
                with gzip.open(os.path.join(outdir, pid + ".txt.gz"), "wt") as f:  # committed to git
                    f.write(txt)
                with gzip.open(os.path.join(outdir, pid + ".html.gz"), "wt") as f:
                    f.write(html)
                rec["ok"] = bool(rec["status"] and rec["status"] < 400 and len(txt) > 200)
                rec["chars"] = len(txt)
                rec["error"] = None
                break
            except Exception as e:
                rec["error"] = str(e).splitlines()[0][:200]
                await page.wait_for_timeout(2000)
        log[pid] = rec
        print(f"  {'ok ' if rec['ok'] else 'ERR'} {pid:<22} {rec['status']} {rec.get('chars','')} {rec['error'] or ''}")
        await ctx.close()


async def fetch_all(pages, outdir):
    os.makedirs(outdir, exist_ok=True)
    log = {}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=CHROME, headless=True)
        sem = asyncio.Semaphore(6)
        await asyncio.gather(*[fetch_one(browser, pid, url, outdir, sem, log)
                               for pid, url in pages.items()])
        await browser.close()
    with open(os.path.join(outdir, "_fetch_log.json"), "w") as f:
        json.dump({"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "pages": log}, f, indent=2)
    return log
