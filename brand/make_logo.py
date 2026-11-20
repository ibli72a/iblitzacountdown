"""Generate the IBLITZA logo set as self-contained SVGs (lettering outlined, no fonts needed).

    pip install fonttools brotli && python3 brand/make_logo.py
"""
import math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = TTFont(os.path.join(HERE, 'barlow-semi-condensed-latin-800-italic.woff2'))
LIME, ORANGE, PINK, INK, GREEN = '#d3ee5f', '#ff9a0a', '#ff3ea5', '#1b1030', '#0fae4b'
SHEAR = 0.20  # extra slant on top of the font's own italic
SLANT = math.tan(math.radians(-FONT['post'].italicAngle)) + SHEAR


def wordmark(width, cx, baseline, text='IBLITZA', tracking=-0.005):
    """Outline `text` scaled to `width`, centred on cx. Returns (path, box, first-glyph box)."""
    gs, cmap, upm = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm
    names = [cmap[ord(c)] for c in text]
    adv = [gs[n].width for n in names]
    total = sum(adv) + tracking * upm * (len(text) - 1)
    s = width / total
    x0 = cx - width / 2
    pen, allb, first = SVGPathPen(gs, ntos=lambda v: f'{v:.2f}'), BoundsPen(gs), BoundsPen(gs)
    x = 0.0
    for i, (n, a) in enumerate(zip(names, adv)):
        t = (s, 0, SHEAR * s, -s, x0 + x * s, baseline)
        for p in (pen, allb) + ((first,) if i == 0 else ()):
            gs[n].draw(TransformPen(p, t))
        x += a + tracking * upm
    return pen.getCommands(), allb.bounds, first.bounds


def frond(x, y, L, a0, bend, notches=5):
    """One palm frond: a spine that leaves the hub at angle a0 (degrees from straight up,
    clockwise) and curls by `bend` degrees, so the tip droops. The upper edge is smooth,
    the lower edge is cut into leaflets."""
    n = 60
    spine, ang = [(x, y)], []
    px, py = x, y
    for k in range(1, n + 1):
        t = k / n
        th = math.radians(a0 + bend * t * t)
        px += math.sin(th) * L / n
        py -= math.cos(th) * L / n
        spine.append((px, py)); ang.append(th)
    ang.insert(0, math.radians(a0))
    side = 1 if bend >= 0 else -1          # which normal points "up/outside" of the curl
    upper, lower = [], []
    for k, ((sx, sy), th) in enumerate(zip(spine, ang)):
        t = k / n
        w = L * 0.22 * math.sin(math.pi * t) ** 0.6 * (1 - 0.35 * t)
        nx, ny = math.cos(th) * side, math.sin(th) * side   # unit normal
        upper.append((sx - nx * w * 0.25, sy - ny * w * 0.25))
        # leaflets: the lower edge swings between full width and a notch near the spine
        # sawtooth: each leaflet runs out to a point aimed at the tip, then cuts back to the spine
        cut = 1.0 if t < 0.22 else 0.15 + 0.85 * ((t - 0.22) * notches / 0.78 % 1) ** 0.7
        lower.append((sx + nx * w * cut, sy + ny * w * cut))
    pts = upper + lower[::-1]
    return 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in pts) + 'Z'


def palm(x0, x1, y, cap, fill):
    """Palm on the I: a small gap above the letter, a leaf base exactly as wide as the stem
    (same slant, so it reads as the top of the trunk), then a full crown of fronds."""
    gap, h = cap * 0.055, cap * 0.075
    sx = lambda dy: dy * SLANT          # horizontal shift for a rise of dy, following the italic
    yb, yt = y - gap, y - gap - h
    base = (f'M{x0 + sx(gap):.1f},{yb:.1f} L{x1 + sx(gap):.1f},{yb:.1f} '
            f'L{x1 + sx(gap + h):.1f},{yt:.1f} L{x0 + sx(gap + h):.1f},{yt:.1f}Z')
    hx, hy = (x0 + x1) / 2 + sx(gap + h), yt + h * 0.15
    L = cap * 0.78
    spec = [  # (start angle, curl, length): tall fronds that rise first, then arch over
        (76, 70, 0.78), (52, 78, 0.92), (30, 84, 1.00), (12, 72, 1.04),
        (-76, -70, 0.78), (-52, -78, 0.92), (-30, -84, 1.00), (-12, -72, 1.04),
        (2, 26, 0.80),
    ]
    d = ' '.join(frond(hx, hy, L * l, a, b) for a, b, l in spec)
    return f'<g fill="{fill}"><path d="{base}"/><path d="{d}"/></g>'


def mark(width, cx, cy, grad='url(#sunset)', accent=GREEN):
    """Wordmark with a single-colour palm crown on the I, centred on (cx, cy)."""
    _, (bx0, by0, bx1, by1), _ = wordmark(width, cx, 0)
    cap = by1 - by0
    # Re-centre: the shear pushes the tops right, and the letters sit on cy by their cap height.
    path, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(width, 2 * cx - (bx0 + bx1) / 2, cy + cap * 0.85)
    # The italic I is a parallelogram: its top edge is the right-hand end of its bounding box.
    stem = (ix1 - ix0) - cap * SLANT
    body = (palm(ix1 - stem, ix1, by0, cap, accent)
            + f'<path d="{path}" fill="{grad}"/>')
    defs = (f'<linearGradient id="sunset" gradientUnits="userSpaceOnUse" x1="0" y1="{by0:.1f}" x2="0" y2="{by1:.1f}">'
            f'<stop offset="0.12" stop-color="{ORANGE}"/><stop offset="0.9" stop-color="{PINK}"/></linearGradient>')
    return defs, body


def svg(w, h, defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'  <title>IBLITZA</title>\n  <defs>{defs}</defs>\n  {body}\n</svg>\n')


files = {}
# Badge, as on Instagram: lime disc with the wordmark breaking out of it. Transparent corners.
d, b = mark(1020, 560, 500)
files['iblitza-badge.svg'] = svg(1120, 1000, d, f'<circle cx="560" cy="500" r="440" fill="{LIME}"/>{b}')
# Avatar: full-bleed lime square with everything inside the safe area (GitHub/Slack crop the corners).
d, b = mark(820, 512, 512)
files['iblitza-avatar.svg'] = svg(1024, 1024, d, f'<rect width="1024" height="1024" fill="{LIME}"/>{b}')
# Same, dark background.
files['iblitza-avatar-dark.svg'] = svg(1024, 1024, d, f'<rect width="1024" height="1024" fill="{INK}"/>{b}')
# Wordmark only, transparent: gradient, and single-colour versions for print / one-colour use.
d, b = mark(1000, 540, 300)
files['iblitza-wordmark.svg'] = svg(1080, 520, d, b)
for name, col in [('ink', INK), ('white', '#ffffff')]:
    d1, b1 = mark(1000, 540, 300, grad=col, accent=col)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 520, '', b1)

# Black & white: square avatars and wide wordmarks, each on a solid background.
for name, fg, bg in [('black-on-white', '#000000', '#ffffff'), ('white-on-black', '#ffffff', '#000000')]:
    _, b1 = mark(820, 512, 512, grad=fg, accent=fg)
    files[f'iblitza-avatar-{name}.svg'] = svg(1024, 1024, '', f'<rect width="1024" height="1024" fill="{bg}"/>{b1}')
    _, b1 = mark(1000, 540, 300, grad=fg, accent=fg)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 520, '', f'<rect width="1080" height="520" fill="{bg}"/>{b1}')
_, b1 = mark(1000, 540, 300, grad='#000000', accent='#000000')
files['iblitza-wordmark-black.svg'] = svg(1080, 520, '', b1)

for n, s in files.items():
    with open(os.path.join(HERE, n), 'w') as fh:
        fh.write(s)
    print(n, len(s))
