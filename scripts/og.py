"""1200x630 social share cards (og:image) rendered with Pillow. Colors match assets/style.css."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG, INK, MUT, LINE, BRAND, BRAND2 = "#f7f8fb", "#0f172a", "#64748b", "#e5e7eb", "#4f46e5", "#eef2ff"
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Inter.ttf")
_cache = {}

def font(size, weight="Regular"):
    k = (size, weight)
    if k not in _cache:
        f = ImageFont.truetype(FONT, size)
        try: f.set_variation_by_name(weight)
        except Exception: pass
        _cache[k] = f
    return _cache[k]

def _mark(size):
    """Rounded gradient square (#4f46e5 -> #06b6d4) with the favicon's white bars."""
    s = size * 4  # supersample
    g = Image.new("RGB", (s, s))
    a, b = (0x4f, 0x46, 0xe5), (0x06, 0xb6, 0xd4)
    px = g.load()
    for y in range(s):
        for x in range(s):
            t = (x + y) / (2 * s - 2)
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 7 / 32), fill=255)
    d = ImageDraw.Draw(g)
    u = s / 32; w = int(2.6 * u)
    for x, y0, y1 in [(9, 12, 20), (14, 8, 24), (19, 12, 20), (24, 15, 17)]:
        d.line([(x * u, y0 * u), (x * u, y1 * u)], fill="white", width=w)
        for yy in (y0, y1):
            d.ellipse([x * u - w / 2, yy * u - w / 2, x * u + w / 2, yy * u + w / 2], fill="white")
    out = Image.new("RGBA", (s, s)); out.paste(g, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)

_MARKS = {}
def mark(size):
    if size not in _MARKS: _MARKS[size] = _mark(size)
    return _MARKS[size]

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def fit(d, text, weight, sizes, maxw, maxlines):
    for sz in sizes:
        f = font(sz, weight); ls = wrap(d, text, f, maxw)
        if len(ls) <= maxlines and all(d.textlength(l, font=f) <= maxw for l in ls): return f, ls
    f = font(sizes[-1], weight); ls = wrap(d, text, f, maxw)[:maxlines]
    return f, ls

def _base():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=BRAND)
    return im, d

def _footer(d, url, left="Checked daily from official pricing pages"):
    d.line([(72, H - 92), (W - 72, H - 92)], fill=LINE, width=2)
    d.text((72, H - 66), left, font=font(26, "Medium"), fill=MUT)
    d.text((W - 72, H - 66), url, font=font(26, "Medium"), fill=BRAND, anchor="ra")

def _save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)

def site_card(path, url):
    im, d = _base()
    m = mark(132); im.paste(m, (72, 150), m)
    d.text((232, 150 + 66), "VoiceCost", font=font(124, "ExtraBold"), fill=INK, anchor="lm")
    f, ls = fit(d, "The real price per minute for voice AI, checked daily", "SemiBold", [56, 52, 48], W - 144, 2)
    y = 340
    for l in ls:
        d.text((72, y), l, font=f, fill="#334155"); y += int(f.size * 1.25)
    _footer(d, url, "Voice agents · Speech-to-text · Text-to-speech")
    _save(im, path)

def page_card(path, title, kicker, lines, url):
    """title: big text. kicker: small label above it. lines: list of real-price strings (may be empty)."""
    im, d = _base()
    m = mark(56); im.paste(m, (72, 60), m)
    d.text((142, 60 + 28), "VoiceCost", font=font(40, "ExtraBold"), fill=INK, anchor="lm")
    d.text((W - 72, 60 + 28), kicker.upper(), font=font(24, "SemiBold"), fill=MUT, anchor="rm")
    lines = [l for l in lines if l][:3]
    sz = 38 if len(lines) == 1 else 32 if len(lines) == 2 else 28
    bh = len(lines) * int(sz * 1.45) + 36 if lines else 0
    limit = H - 116  # keep clear of the footer rule
    for tsz in (92, 84, 76, 68, 60, 54, 48):
        f, ls = fit(d, title, "ExtraBold", [tsz], W - 144, 2)
        if 168 + len(ls) * int(tsz * 1.18) + 22 + bh <= limit: break
    y = 168
    for l in ls:
        d.text((72, y), l, font=f, fill=INK); y += int(f.size * 1.18)
    y += 22
    if lines:
        pf = font(sz, "SemiBold")
        d.rounded_rectangle([72, y, W - 72, y + bh], radius=18, fill=BRAND2)
        ty = y + 18
        for l in lines:
            while d.textlength(l, font=pf) > W - 192 and pf.size > 20: pf = font(pf.size - 2, "SemiBold")
            d.text((96, ty), l, font=pf, fill="#3730a3"); ty += int(sz * 1.45)
    _footer(d, url)
    _save(im, path)
