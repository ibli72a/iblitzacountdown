"""Generate the IBLITZA logo set as self-contained SVGs (lettering outlined, no fonts needed).

The I is a palm tree: the letter is the trunk, with a few wavy rings cut into it, and a crown
of fronds sits on top of it.

    pip install fonttools brotli skia-pathops
    python3 brand/make_logo.py                       # default font, files written to brand/
    python3 brand/make_logo.py --font some.woff2 --out some/dir
"""
import argparse, math, os, re
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--font', default=os.path.join(HERE, 'righteous-latin-400-normal.woff2'))
ap.add_argument('--out', default=HERE)
ARGS = ap.parse_args()
FONT = TTFont(ARGS.font)

LIME, ORANGE, PINK, INK = '#d3ee5f', '#ff9a0a', '#ff3ea5', '#1b1030'
FROND = ['#0b7d36', '#0fae4b']   # back and front fronds


# ---- lettering ---------------------------------------------------------------------------

def _profile(gs, name, step=4):
    """Left and right edge of a glyph per height (font units): {y: (xmin, xmax)}."""
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
    for y in range((int(min(ys)) // step + 1) * step, int(max(ys)), step):   # shared grid
        xs = [x0 + (y - y0) * (x1 - x0) / (y1 - y0) for (x0, y0), (x1, y1) in pen.segs
              if (y0 - y) * (y1 - y) < 0]
        if xs:
            prof[y] = (min(xs), max(xs))
    return prof


def _rings(x0, x1, y0, y1, n=4, thick=0.035, amp=0.025):
    """Wavy bands across the trunk (font units), cut out of the I like the rings of a palm."""
    h = y1 - y0
    rings = pathops.Path()
    for j in range(n):
        yc = y0 + h * (0.16 + 0.68 * j / (n - 1))
        top, bot = [], []
        steps = 24
        for k in range(steps + 1):
            x = x0 - 50 + (x1 - x0 + 100) * k / steps
            wave = amp * h * math.sin((x - x0) / (x1 - x0) * 2 * math.pi)
            top.append((x, yc + wave + thick * h / 2)); bot.append((x, yc + wave - thick * h / 2))
        band = pathops.Path(); pen = band.getPen()
        pen.moveTo(top[0])
        for q in top[1:] + bot[::-1]:
            pen.lineTo(q)
        pen.closePath()
        rings = pathops.op(rings, band, pathops.PathOp.UNION)
    return rings


def wordmark(width, cx, baseline, text='IBLITZA', gap=0.045):
    """Outline `text` scaled to `width`, centred on cx. Returns (path, box, first-glyph box).
    Each gap is measured where two neighbours come closest and made the same for every pair.
    The I (first letter) gets palm-trunk rings cut into it."""
    gs, cmap, upm = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm
    names = [cmap[ord(c)] for c in text]
    adv = [gs[n].width for n in names]
    profs = [_profile(gs, n) for n in names]
    X = [0.0]
    for i in range(len(names) - 1):
        a, b = profs[i], profs[i + 1]
        closest = min(b[y][0] + adv[i] - a[y][1] for y in a if y in b)
        X.append(X[i] + adv[i] + gap * upm - closest)
    total = X[-1] + adv[-1]
    s = width / total
    x0 = cx - width / 2
    final = (s, 0, 0, -s, x0, baseline)
    pen, allb, first = SVGPathPen(None, ntos=lambda v: f'{v:.2f}'), BoundsPen(None), BoundsPen(None)
    for i, n in enumerate(names):
        g = pathops.Path()
        gs[n].draw(TransformPen(g.getPen(), (1, 0, 0, 1, X[i], 0)))
        if i == 0:
            bp = BoundsPen(None); g.draw(bp)
            gx0, gy0, gx1, gy1 = bp.bounds
            g.draw(TransformPen(first, final))       # the crown sits on the I as drawn
            g = pathops.op(g, _rings(gx0, gx1, gy0, gy1), pathops.PathOp.DIFFERENCE)
        for p in (pen, allb):
            g.draw(TransformPen(p, final))
    return pen.getCommands(), allb.bounds, first.bounds


# ---- palm crown --------------------------------------------------------------------------

def frond(x, y, L, a0, bend, W, teeth=4):
    """One palm frond as a closed polygon. It leaves (x, y) at a0 (degrees from upright,
    clockwise) and curls by `bend` degrees, so it arches over and droops. The outer edge is a
    smooth curve; the inner edge is cut into a few big leaflets that point toward the tip."""
    n = 120
    pts, ang = [(x, y)], [math.radians(a0)]
    px, py = x, y
    for k in range(1, n + 1):
        t = k / n
        th = math.radians(a0 + bend * t ** 1.3)
        px += math.sin(th) * L / n
        py -= math.cos(th) * L / n
        pts.append((px, py)); ang.append(th)
    side = 1 if bend >= 0 else -1                     # outer side of the curl
    outer, inner = [], []
    for k, ((sx, sy), th) in enumerate(zip(pts, ang)):
        t = k / n
        w = W * math.sin(math.pi * min(1, t ** 0.8)) ** 0.7
        nx, ny = -math.cos(th) * side, -math.sin(th) * side
        outer.append((sx + nx * w * 0.55, sy + ny * w * 0.55))
        c = 1.0 if t < 0.15 else 0.25 + 0.75 * (((t - 0.15) / 0.85 * teeth) % 1) ** 0.5
        inner.append((sx - nx * w * c, sy - ny * w * c))
    return outer + inner[::-1]


# (angle from upright, curl, length, half-width, shade), back to front: two fronds arching
# up and over, two long ones spreading out, two drooping lower, two short ones hanging close.
FRONDS = [
    (-12, -100, 0.92, .17, 0), (14, 100, 0.90, .17, 0),
    (-58, -80, 1.00, .17, 1), (62, 80, 1.00, .17, 1),
    (-95, -55, 0.82, .16, 0), (98, 55, 0.84, .16, 0),
    (-135, -25, 0.50, .14, 1), (138, 25, 0.50, .14, 1),
]


def palm(x0, x1, y, cap, fill, line):
    """Palm crown on top of the I (its top edge runs x0..x1 at height y). `fill` None draws
    it in two greens; a colour draws every frond in that colour, separated by `line` (the
    background) if given."""
    hx, hy = (x0 + x1) / 2, y + cap * 0.02
    L = cap * 0.78
    sw = L * 0.016
    parts = []
    for a, b, l, w, shade in FRONDS:
        poly = frond(hx, hy, L * l, a, b, L * w)
        d = 'M' + ' L'.join(f'{u:.1f},{v:.1f}' for u, v in poly) + 'Z'
        if fill is None:
            parts.append(f'<path d="{d}" fill="{FROND[shade]}"/>')
        elif line:
            parts.append(f'<path d="{d}" fill="{fill}" stroke="{line}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
        else:
            parts.append(f'<path d="{d}" fill="{fill}"/>')
    return '<g>' + ''.join(parts) + '</g>'


# ---- composition -------------------------------------------------------------------------

def _mark(text_width, cx, cy, grad, accent, line):
    _, (bx0, by0, bx1, by1), _ = wordmark(text_width, cx, 0)
    cap = by1 - by0
    path, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(text_width, cx, cy + cap / 2)
    plant = palm(ix0, ix1, iy0, cap, accent, line)
    pts = [tuple(map(float, m)) for m in re.findall(r'(-?[\d.]+),(-?[\d.]+)', plant)]
    xs = [bx0, bx1] + [x for x, _ in pts]
    ys = [by0, by1] + [y for _, y in pts]
    # letters first, crown on top of the I
    return f'<path d="{path}" fill="{grad}"/>' + plant, (min(xs), min(ys), max(xs), max(ys)), (by0, by1)


def mark(width, cx, cy, grad='url(#sunset)', accent=None, line=None):
    """Wordmark with the palm I, the whole thing `width` wide and centred on (cx, cy)."""
    _, (x0, y0, x1, y1), _ = _mark(1000, 0, 0, grad, accent, line)
    tw = 1000 * width / (x1 - x0)
    body, (x0, y0, x1, y1), (by0, by1) = _mark(tw, cx, cy, grad, accent, line)
    dx, dy = cx - (x0 + x1) / 2, cy - (y0 + y1) / 2
    body = f'<g transform="translate({dx:.1f} {dy:.1f})">{body}</g>'
    defs = (f'<linearGradient id="sunset" gradientUnits="userSpaceOnUse" x1="0" y1="{by0:.1f}" x2="0" y2="{by1:.1f}">'
            f'<stop offset="0.12" stop-color="{ORANGE}"/><stop offset="0.9" stop-color="{PINK}"/></linearGradient>')
    return defs, body


def svg(w, h, defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'  <title>IBLITZA</title>\n  <defs>{defs}</defs>\n  {body}\n</svg>\n')


files = {}
# Badge, as on Instagram: lime disc with the wordmark breaking out of it. Transparent corners.
d, b = mark(940, 560, 500)
files['iblitza-badge.svg'] = svg(1120, 1000, d, f'<circle cx="560" cy="500" r="440" fill="{LIME}"/>{b}')
# Avatar: full-bleed lime square, everything inside the safe area (GitHub/Slack crop corners).
d, b = mark(800, 512, 512)
files['iblitza-avatar.svg'] = svg(1024, 1024, d, f'<rect width="1024" height="1024" fill="{LIME}"/>{b}')
files['iblitza-avatar-dark.svg'] = svg(1024, 1024, d, f'<rect width="1024" height="1024" fill="{INK}"/>{b}')
# Wordmark only, transparent: gradient, and single-colour versions for print / one-colour use.
d, b = mark(960, 540, 340)
files['iblitza-wordmark.svg'] = svg(1080, 680, d, b)
for name, col in [('ink', INK), ('white', '#ffffff'), ('black', '#000000')]:
    _, b1 = mark(960, 540, 340, grad=col, accent=col)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, '', b1)
# Black & white: square avatars and wide wordmarks, each on a solid background.
for name, fg, bg in [('black-on-white', '#000000', '#ffffff'), ('white-on-black', '#ffffff', '#000000')]:
    _, b1 = mark(800, 512, 512, grad=fg, accent=fg, line=bg)
    files[f'iblitza-avatar-{name}.svg'] = svg(1024, 1024, '', f'<rect width="1024" height="1024" fill="{bg}"/>{b1}')
    _, b1 = mark(960, 540, 340, grad=fg, accent=fg, line=bg)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, '', f'<rect width="1080" height="680" fill="{bg}"/>{b1}')

os.makedirs(ARGS.out, exist_ok=True)
for n, s in files.items():
    with open(os.path.join(ARGS.out, n), 'w') as fh:
        fh.write(s)
