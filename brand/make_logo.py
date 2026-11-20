"""Generate the IBLITZA logo set as self-contained SVGs (lettering outlined, no fonts needed).

The I is a palm tree: the letter is the trunk, with a few wavy rings cut into it, and a crown
of fronds sits on top of it. The word sits across a warm sun disc and breaks out of it.

Colour (flat, on white): blue lettering, palm in three greens, warm orange-yellow sun. One colour: the sun is solid ink and
whatever of the word and palm falls on it is knocked out to the paper colour, so the mark
holds up printed in black only (or white only on a dark ground).

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
ap.add_argument('--font', default=os.path.join(HERE, 'galindo-latin-400-normal.woff2'))
ap.add_argument('--out', default=HERE)
ARGS = ap.parse_args()
FONT = TTFont(ARGS.font)

BLUE = '#0b5cad'                     # lettering: Mediterranean blue
SUN = '#ffb21f'                      # the sun disc
GREENS = ['#0b7a3b', '#13a84b', '#5fcf6e']   # palm, flat: back, middle and front fronds
WHITE = '#ffffff'                    # background


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
    """Outline `text` scaled to `width`, centred on cx. Returns (pathops path, box, I's box).
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
    s = width / (X[-1] + adv[-1])
    final = (s, 0, 0, -s, cx - width / 2, baseline)
    word, first = pathops.Path(), BoundsPen(None)
    for i, n in enumerate(names):
        g = pathops.Path()
        gs[n].draw(TransformPen(g.getPen(), (1, 0, 0, 1, X[i], 0)))
        if i == 0:
            bp = BoundsPen(None); g.draw(bp)
            g.draw(TransformPen(first, final))       # the crown sits on the I as drawn
            g = pathops.op(g, _rings(*bp.bounds), pathops.PathOp.DIFFERENCE)
        placed = pathops.Path()
        g.draw(TransformPen(placed.getPen(), final))
        word = pathops.op(word, placed, pathops.PathOp.UNION)
    return word, word.bounds, first.bounds


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
    (-95, -55, 0.82, .16, 2), (98, 55, 0.84, .16, 2),
    (-135, -25, 0.50, .14, 1), (138, 25, 0.50, .14, 1),
]


def _poly(points):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo(points[0])
    for q in points[1:]:
        pen.lineTo(q)
    pen.closePath()
    return p


def palm(x0, x1, y, cap):
    """The crown's fronds as (pathops path, shade), back to front, sitting on top of the I
    (whose top edge runs x0..x1 at height y)."""
    hx, hy, L = (x0 + x1) / 2, y + cap * 0.02, cap * 0.78
    return [(_poly(frond(hx, hy, L * l, a, b, L * w)), shade) for a, b, l, w, shade in FRONDS]


# ---- composition -------------------------------------------------------------------------

def _d(path):
    pen = SVGPathPen(None, ntos=lambda v: f'{v:.1f}')
    path.draw(pen)
    return pen.getCommands()


def _translate(path, dx, dy):
    out = pathops.Path()
    path.draw(TransformPen(out.getPen(), (1, 0, 0, 1, dx, dy)))
    return out


def layout(width, cx, cy):
    """Word + palm, scaled so the whole thing is `width` wide, centred on (cx, cy).
    Returns (word path, [(frond path, shade)], cap height)."""
    def build(tw):
        word, (bx0, by0, bx1, by1), _ = wordmark(tw, 0, 0)
        cap = by1 - by0
        word, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(tw, 0, cap / 2)
        fronds = palm(ix0, ix1, iy0, cap)
        x0 = min([bx0] + [f.bounds[0] for f, _ in fronds]); x1 = max([bx1] + [f.bounds[2] for f, _ in fronds])
        y0 = min([by0] + [f.bounds[1] for f, _ in fronds]); y1 = max([by1] + [f.bounds[3] for f, _ in fronds])
        return word, fronds, cap, (x0, y0, x1, y1)
    *_, (x0, y0, x1, y1) = build(1000)
    word, fronds, cap, (x0, y0, x1, y1) = build(1000 * width / (x1 - x0))
    dx, dy = cx - (x0 + x1) / 2, cy - (y0 + y1) / 2
    return _translate(word, dx, dy), [(_translate(f, dx, dy), s) for f, s in fronds], cap


def disc(cx, cy, r, n=180):
    return _poly([(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)])


def colour(word, fronds, cap, sun=None):
    """Full colour, flat: optional sun disc (cx, cy, r), blue word, palm in three flat greens."""
    out = []
    if sun:
        out.append(f'<circle cx="{sun[0]}" cy="{sun[1]}" r="{sun[2]}" fill="{SUN}"/>')
    out.append(f'<path d="{_d(word)}" fill="{BLUE}"/>')
    out += [f'<path d="{_d(f)}" fill="{GREENS[shade]}"/>' for f, shade in fronds]
    return '', ''.join(out)


def mono(word, fronds, cap, ink, paper=None, sun=None):
    """One colour. Fronds are split by thin `paper` lines when a paper colour is given.
    With a sun disc, the parts of the word and palm that fall on it are knocked out: drawn
    in the paper colour with ink lines between the fronds."""
    sw = cap * 0.03
    line = lambda c: f' stroke="{c}" stroke-width="{sw:.1f}" stroke-linejoin="round"' if c else ''
    out = [f'<path d="{_d(word)}" fill="{ink}"/>']
    out += [f'<path d="{_d(f)}" fill="{ink}"{line(paper)}/>' for f, _ in fronds]
    if sun:
        D = disc(*sun)
        out.insert(0, f'<circle cx="{sun[0]}" cy="{sun[1]}" r="{sun[2]}" fill="{ink}"/>')
        out.append(f'<path d="{_d(pathops.op(word, D, pathops.PathOp.INTERSECTION))}" fill="{paper}"/>')
        for f, _ in fronds:
            inside = pathops.op(f, D, pathops.PathOp.INTERSECTION)
            out.append(f'<path d="{_d(inside)}" fill="{paper}"{line(ink)}/>')
    return ''.join(out)


def svg(w, h, body, defs='', bg=None):
    back = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'  <title>IBLITZA</title>\n  <defs>{defs}</defs>\n  {back}{body}\n</svg>\n')


files = {}
BW = [('black-on-white', '#000000', '#ffffff'), ('white-on-black', '#ffffff', '#000000')]

# Badge: the word across a sun disc, breaking out of it on both sides.
sun = (560, 500, 400)
word, fronds, cap = layout(1000, 560, 500)
d, b = colour(word, fronds, cap, sun)
files['iblitza-badge.svg'] = svg(1120, 1000, b, d, bg=WHITE)
for name, ink, paper in BW:
    files[f'iblitza-badge-{name}.svg'] = svg(1120, 1000, mono(word, fronds, cap, ink, paper, sun), bg=paper)

# Avatar: the badge on a full square (GitHub/Slack crop the corners), kept inside the safe area.
sun = (512, 512, 360)
word, fronds, cap = layout(860, 512, 512)
d, b = colour(word, fronds, cap, sun)
files['iblitza-avatar.svg'] = svg(1024, 1024, b, d, bg=WHITE)
for name, ink, paper in BW:
    files[f'iblitza-avatar-{name}.svg'] = svg(1024, 1024, mono(word, fronds, cap, ink, paper, sun), bg=paper)

# Wordmark only (no sun), transparent and on solid grounds.
word, fronds, cap = layout(960, 540, 340)
d, b = colour(word, fronds, cap)
files['iblitza-wordmark.svg'] = svg(1080, 680, b, d, bg=WHITE)
for name, ink in [('black', '#000000'), ('white', '#ffffff'), ('blue', BLUE)]:
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, mono(word, fronds, cap, ink))
for name, ink, paper in BW:
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, mono(word, fronds, cap, ink, paper), bg=paper)

os.makedirs(ARGS.out, exist_ok=True)
for n, s in files.items():
    with open(os.path.join(ARGS.out, n), 'w') as fh:
        fh.write(s)
