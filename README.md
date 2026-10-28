# VoiceCost

Daily-updated price tracker for voice AI: agent platforms, speech-to-text, text-to-speech.

## Commands
    ./vc daily       # fetch all pricing pages -> extract -> dated snapshot -> diff -> rebuild site
    ./vc update      # just the data step
    ./vc reextract   # re-run extraction on today's saved raw pages (after editing a rule)
    ./vc build       # just rebuild site/ from data/latest.json
    ./vc serve       # serve site/ on http://127.0.0.1:8787
    ./vc screens     # full-page screenshots into screens/

Cron example (06:00 daily): `0 6 * * * /workspace/voicecost/vc daily >> /workspace/voicecost/daily.log 2>&1`

## Layout
- `scripts/vendors.py`   vendors, pricing URLs and one regex rule per price. Edit here to add vendors.
- `scripts/fetch.py`     headless Chrome fetch; saves the DOM text (incl. hidden tabs) + rendered HTML.
- `scripts/update.py`    extraction, normalization (USD/min, USD/1M chars; EUR via ECB rate), snapshots, diffs.
- `scripts/build.py`     static site generator -> `site/` (plain HTML/CSS/JS, host anywhere).
- `data/raw/<date>/`     raw page snapshots (history evidence).
- `data/snapshots/<date>.json`, `data/latest.json`, `data/changes/<date>.json`, `data/changelog.json`.
- `affiliates.json`      affiliate URL placeholders (empty = official site link).

## Rules
- A price is only "verified" when its rule matches the live page; the matched text is stored as `evidence`.
- If a page fails or a rule stops matching, the row becomes `unknown` (never a guessed number) and the
  update prints a status change so the rule can be fixed.
- Set `VOICECOST_URL` before building to put the real domain in canonical tags and the sitemap.

## Deploy (GitHub Pages)
1. Create the empty public repo `pb-jwhitlock/voicecost` (no README).
2. Push: `git remote add origin https://github.com/pb-jwhitlock/voicecost.git && git push -u origin main`
3. Repo Settings → Pages → Build and deployment → Source: **GitHub Actions**.
4. Actions → "Daily price update + deploy" → Run workflow (it then runs daily at 10:00 UTC,
   commits the new snapshot to `data/`, and deploys `site/` with actions/deploy-pages).
Live URL: https://voicecost.net/ (custom domain; once it is set in Pages, GitHub redirects the old https://pb-jwhitlock.github.io/voicecost/ here)
