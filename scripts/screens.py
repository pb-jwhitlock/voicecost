"""Full-page screenshots of the locally served site."""
import asyncio, os, sys
from playwright.async_api import async_playwright
BASE = os.environ.get("VC_BASE", "http://127.0.0.1:8787")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screens")
SHOTS = [("home.png", "/index.html", 1280), ("compare-vapi-vs-retell.png", "/compare/vapi-vs-retell.html", 1280),
         ("home-mobile.png", "/index.html", 390), ("start-here.png", "/start-here.html", 1280), ("start-here-mobile.png", "/start-here.html", 390), ("compare-deepgram-vs-assemblyai.png", "/compare/deepgram-vs-assemblyai.html", 1280)]
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True)
        for name, path, w in SHOTS:
            p = await b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1 if w > 500 else 2)
            errs = []
            p.on("pageerror", lambda ex: errs.append(str(ex)))
            await p.goto(BASE + path, wait_until="networkidle")
            await p.wait_for_timeout(400)
            await p.screenshot(path=os.path.join(OUT, name), full_page=True)
            print(name, "JS errors:" if errs else "ok", errs or "")
            await p.close()
        await b.close()
asyncio.run(main())
