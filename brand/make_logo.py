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
SHEAR = 0.12  # extra slant on top of the font's own italic
ITALIC = math.tan(math.radians(-FONT['post'].italicAngle))
SLANT = ITALIC + SHEAR
STRETCH = 1.22  # letters drawn this much taller than the font, slant kept the same


def _profile(gs, name, k, step=4):
    """Left and right edge of a glyph per height (font units), after shearing x by k*y.
    Returns {y: (xmin, xmax)} sampled every `step` units over the glyph's height."""
    from fontTools.pens.basePen import BasePen

    class Flat(BasePen):
        def __init__(self):
            super().__init__(gs); self.segs = []; self.p = None; self.start = None
        def _moveTo(self, pt): self.p = self.start = pt
        def _lineTo(self, pt): self.segs.append((self.p, pt)); self.p = pt
        def _qCurveToOne(self, c, pt):
            (x0, y0), (x1, y1), (x2, y2) = self.p, c, pt
            prev = self.p
            for i in range(1, 9):
                t = i / 8
                q = ((1-t)**2*x0 + 2*(1-t)*t*x1 + t*t*x2, (1-t)**2*y0 + 2*(1-t)*t*y1 + t*t*y2)
                self.segs.append((prev, q)); prev = q
            self.p = pt
        def _curveToOne(self, c1, c2, pt):
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = self.p, c1, c2, pt
            prev = self.p
            for i in range(1, 11):
                t = i / 10; u = 1 - t
                q = (u**3*x0 + 3*u*u*t*x1 + 3*u*t*t*x2 + t**3*x3, u**3*y0 + 3*u*u*t*y1 + 3*u*t*t*y2 + t**3*y3)
                self.segs.append((prev, q)); prev = q
            self.p = pt
        def _closePath(self):
            if self.p != self.start: self.segs.append((self.p, self.start))

    pen = Flat(); gs[name].draw(pen)
    ys = [y for seg in pen.segs for _, y in seg]
    prof = {}
    for y in range(int(min(ys)) + 1, int(max(ys)), step):
        xs = [x0 + (y - y0) * (x1 - x0) / (y1 - y0) for (x0, y0), (x1, y1) in pen.segs
              if (y0 - y) * (y1 - y) < 0]
        if xs:
            prof[y] = (min(xs) + k * y, max(xs) + k * y)
    return prof


# The gap between neighbours is measured where they come closest (after the slant), and made
# the same for every pair, so T-Z doesn't read wider than L-I-T. Z-A is the exception: their
# feet line up exactly on the baseline.
ALIGN_FEET = {('Z', 'A')}


def wordmark(width, cx, baseline, text='IBLITZA', gap=0.022):
    """Outline `text` scaled to `width`, centred on cx. Returns (path, box, first-glyph box)."""
    gs, cmap, upm = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm
    names = [cmap[ord(c)] for c in text]
    adv = [gs[n].width for n in names]
    k = (SLANT * STRETCH - ITALIC) / STRETCH  # shear per font unit of height
    profs = [_profile(gs, n, k) for n in names]
    kern = []
    for i, pair in enumerate(zip(text, text[1:])):
        a, b = profs[i], profs[i + 1]
        if pair in ALIGN_FEET:
            ya, yb = min(a), min(b)
            kern.append(a[ya][1] - adv[i] - b[yb][0])
        else:
            closest = min(b[y][0] + adv[i] - a[y][1] for y in a if y in b)
            kern.append(gap * upm - closest)
    total = sum(adv) + sum(kern)
    s = width / total
    x0 = cx - width / 2
    pen, allb, first = SVGPathPen(gs, ntos=lambda v: f'{v:.2f}'), BoundsPen(gs), BoundsPen(gs)
    x = 0.0
    for i, (n, a) in enumerate(zip(names, adv)):
        t = (s, 0, (SLANT * STRETCH - ITALIC) * s, -s * STRETCH, x0 + x * s, baseline)
        for p in (pen, allb) + ((first,) if i == 0 else ()):
            gs[n].draw(TransformPen(p, t))
        x += a + (kern[i] if i < len(kern) else 0)
    return pen.getCommands(), allb.bounds, first.bounds


def blade(x, y, L, a0, bend, w0):
    """One spider-plant leaf: a long, narrow ribbon with smooth edges that leaves (x, y) at
    angle a0 (degrees from straight up, clockwise), arches over by `bend` degrees and
    tapers to a sharp point. The curl tightens towards the tip, so it ends pointing down."""
    n = 80
    pts, ang = [(x, y)], [math.radians(a0)]
    px, py = x, y
    for k in range(1, n + 1):
        t = k / n
        th = math.radians(a0 + bend * t ** 1.25)
        px += math.sin(th) * L / n
        py -= math.cos(th) * L / n
        pts.append((px, py)); ang.append(th)
    left, right = [], []
    for k, ((sx, sy), th) in enumerate(zip(pts, ang)):
        t = k / n
        w = w0 * (1 - t) ** 0.85 * (0.55 + 0.45 * math.sin(math.pi * min(1, t * 2.2)))
        nx, ny = math.cos(th), math.sin(th)
        left.append((sx - nx * w, sy - ny * w)); right.append((sx + nx * w, sy + ny * w))
    poly = left + right[::-1]
    return 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in poly) + 'Z'


def palm(x0, x1, y, cap, fill):
    """Palm on the I: a small gap above the letter, a leaf base exactly as wide as the stem
    (same slant, so it reads as the top of the trunk), then a spray of arching leaves."""
    gap, h = cap * 0.055, cap * 0.075
    sx = lambda dy: dy * SLANT          # horizontal shift for a rise of dy, following the italic
    yb, yt = y - gap, y - gap - h
    base = (f'M{x0 + sx(gap):.1f},{yb:.1f} L{x1 + sx(gap):.1f},{yb:.1f} '
            f'L{x1 + sx(gap + h):.1f},{yt:.1f} L{x0 + sx(gap + h):.1f},{yt:.1f}Z')
    hx, hy = (x0 + x1) / 2 + sx(gap + h), yt + h * 0.15
    L, W = cap * 1.35, cap * 0.06
    spec = [  # (start angle, curl, length, width). The I is the first letter, so the plant
              # leans into the word: long leaves arch right and come down onto the letters,
              # shorter ones fall to the left. Uneven so it looks natural.
        (4, 126, 1.00, 1.0), (18, 120, 0.92, 1.0), (34, 112, 0.78, 0.95), (54, 100, 0.60, 0.9),
        (76, 84, 0.42, 0.8), (-2, 118, 0.70, 0.9), (10, 96, 0.62, 0.85),
        (-10, -112, 0.62, 1.0), (-26, -110, 0.54, 0.95), (-46, -98, 0.44, 0.9), (-68, -84, 0.36, 0.8),
        (-4, -80, 0.50, 0.85),
    ]
    d = ' '.join(blade(hx, hy, L * l, a, b, W * w) for a, b, l, w in spec)
    return f'<g fill="{fill}"><path d="{base}"/><path d="{d}"/></g>'


def mark(width, cx, cy, grad='url(#sunset)', accent=GREEN):
    """Wordmark with a single-colour palm crown on the I, centred on (cx, cy)."""
    _, (bx0, by0, bx1, by1), _ = wordmark(width, cx, 0)
    cap = by1 - by0
    # Re-centre: the shear pushes the tops right, and the letters sit on cy by their cap height.
    path, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(width, 2 * cx - (bx0 + bx1) / 2, cy + cap * 0.80)
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
d, b = mark(900, 560, 380)
files['iblitza-wordmark.svg'] = svg(1080, 680, d, b)
for name, col in [('ink', INK), ('white', '#ffffff')]:
    d1, b1 = mark(900, 560, 380, grad=col, accent=col)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, '', b1)

# Black & white: square avatars and wide wordmarks, each on a solid background.
for name, fg, bg in [('black-on-white', '#000000', '#ffffff'), ('white-on-black', '#ffffff', '#000000')]:
    _, b1 = mark(820, 512, 512, grad=fg, accent=fg)
    files[f'iblitza-avatar-{name}.svg'] = svg(1024, 1024, '', f'<rect width="1024" height="1024" fill="{bg}"/>{b1}')
    _, b1 = mark(900, 560, 380, grad=fg, accent=fg)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, '', f'<rect width="1080" height="680" fill="{bg}"/>{b1}')
_, b1 = mark(900, 560, 380, grad='#000000', accent='#000000')
files['iblitza-wordmark-black.svg'] = svg(1080, 680, '', b1)

for n, s in files.items():
    with open(os.path.join(HERE, n), 'w') as fh:
        fh.write(s)
    print(n, len(s))
