"""Render issue-001.md to Beehiiv-pasteable inline-styled HTML. Needs `pip install markdown`."""
import re, sys, markdown
src = sys.argv[1] if len(sys.argv) > 1 else "issue-001.md"
s = re.sub(r'<!--.*?-->\n*', '', open(src).read(), flags=re.S)
h = markdown.markdown(s, extensions=['tables'])
F = "font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;"
TD = '<td style="border-bottom:1px solid #e2e8f0;padding:8px 6px;color:#0f172a">'
for a, b in [('<h1>', f'<h1 style="{F}font-size:24px;line-height:1.25;color:#0f172a;margin:0 0 16px">'),
             ('<h2>', f'<h2 style="{F}font-size:19px;color:#0f172a;margin:28px 0 10px">'),
             ('<p>', f'<p style="{F}font-size:16px;line-height:1.55;color:#334155;margin:0 0 14px">'),
             ('<li>', f'<li style="{F}font-size:16px;line-height:1.55;color:#334155;margin:0 0 8px">'),
             ('<table>', f'<table style="{F}border-collapse:collapse;width:100%;font-size:14px;margin:6px 0 14px">'),
             ('<th>', '<th style="text-align:left;border-bottom:2px solid #e2e8f0;padding:8px 6px;color:#64748b;font-size:12px;text-transform:uppercase">'),
             ('<td>', TD), ('<a href=', '<a style="color:#4f46e5" href=')]:
    h = h.replace(a, b)
num = TD[:-2] + ';text-align:right;white-space:nowrap">'
h = h.replace(TD + '$', num + '$').replace(TD + '<strong>$', num + '<strong>$')
for a in ['vapi.ai/?aff', 'try.elevenlabs.io']:
    h = re.sub(r'(<a style="color:#4f46e5" href="https://' + re.escape(a) + r'[^"]*")', r'\1 rel="sponsored noopener"', h)
out = src.replace('.md', '.html')
open(out, 'w').write(f'<!-- VoiceCost issue #1. Paste into Beehiiv (HTML block). Snapshot 2026-10-21. -->\n<div style="max-width:620px;margin:0 auto;padding:8px 4px">\n{h}\n</div>\n')
print("wrote", out)
