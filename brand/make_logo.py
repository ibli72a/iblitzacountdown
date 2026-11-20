"""Generate the IBLITZA logo set as self-contained SVGs (lettering outlined, no fonts needed).

The I is a palm tree: the letter is the trunk, with a few wavy rings cut into it, and a crown
of fronds sits on top of it. The word sits across a warm sun disc and breaks out of it.

Colour: flat blue lettering, palm in two greens, warm orange-yellow sun, transparent ground.
One colour (black or white): word and palm only, no sun, with real gaps between the fronds
and between the palm and the letters, so it works on any ground.

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
GREENS = ['#13a84b', '#5fcf6e']     # palm, flat: mid, light
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
# Two shades (0 mid, 1 light) alternate down each side, mirrored crosswise, so neighbours differ.
FRONDS = [
    (-12, -100, 0.92, .17, 0), (14, 100, 0.90, .17, 1),
    (-58, -80, 1.00, .17, 1), (62, 80, 1.00, .17, 0),
    (-95, -55, 0.82, .16, 0), (98, 55, 0.84, .16, 1),
    (-135, -25, 0.50, .14, 1), (138, 25, 0.50, .14, 0),
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


def _union_bounds(paths):
    bs = [p.bounds for p in paths]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


def build(text_width, cx, cy):
    """Word centred on (cx, cy) by its letters (the palm is left to hang off the I), plus the
    crown. Returns (word path, [(frond path, shade)], cap height)."""
    word, (bx0, by0, bx1, by1), _ = wordmark(text_width, 0, 0)
    cap = by1 - by0
    word, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(text_width, 0, cap / 2)
    fronds = palm(ix0, ix1, iy0, cap)
    dx, dy = cx - (bx0 + bx1) / 2, cy - (by0 + by1) / 2
    return _translate(word, dx, dy), [(_translate(f, dx, dy), sh) for f, sh in fronds], cap


def disc(cx, cy, r, n=180):
    return _poly([(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)])


def colour(word, fronds, sun=None):
    """Full colour, flat: optional sun disc (cx, cy, r), blue word, palm in two greens."""
    out = []
    if sun:
        out.append(f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="{sun[2]:.1f}" fill="{SUN}"/>')
    out.append(f'<path d="{_d(word)}" fill="{BLUE}"/>')
    out += [f'<path d="{_d(f)}" fill="{GREENS[shade]}"/>' for f, shade in fronds]
    return ''.join(out)


def one_colour(word, fronds, cap):
    """Word and palm as one shape for single-colour use. Each frond, and the crown as a whole,
    is cut a thin gap away from what lies behind it, so they still read apart in one ink."""
    gap = cap * 0.035
    def grown(p):
        g = pathops.Path(p)
        g.stroke(gap * 2, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        g.convertConicsToQuads()
        return pathops.op(g, p, pathops.PathOp.UNION)
    crown = pathops.Path()
    for f, _ in fronds:                                    # back to front
        crown = pathops.op(crown, grown(f), pathops.PathOp.DIFFERENCE)
        crown = pathops.op(crown, f, pathops.PathOp.UNION)
    shape = pathops.op(word, grown(crown), pathops.PathOp.DIFFERENCE)
    return pathops.op(shape, crown, pathops.PathOp.UNION)


def svg(box, body, pad=0.04, square=False, bg=None):
    """SVG sized to `box` (x0, y0, x1, y1) plus padding; transparent unless `bg` is given."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    p = pad * max(w, h)
    if square:
        side = max(w, h)
        x0 -= (side - w) / 2; y0 -= (side - h) / 2; w = h = side
    vb = f'{x0 - p:.1f} {y0 - p:.1f} {w + 2 * p:.1f} {h + 2 * p:.1f}'
    W, H = round(w + 2 * p), round(h + 2 * p)
    back = (f'<rect x="{x0 - p:.1f}" y="{y0 - p:.1f}" width="{w + 2 * p:.1f}" height="{h + 2 * p:.1f}" fill="{bg}"/>'
            if bg else '')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{W}" height="{H}">\n'
            f'  <title>IBLITZA</title>\n  {back}{body}\n</svg>\n')


files = {}
INKS = [('black', '#000000'), ('white', '#ffffff')]

# The logo: the word across the sun, centred on it, its ends just breaking out on both sides.
R = 420
sun = (0, 0, R)
word, fronds, cap = build(2 * R * 1.06, 0, R * 0.06)
box = _union_bounds([disc(*sun), word] + [f for f, _ in fronds])
files['iblitza-logo.svg'] = svg(box, colour(word, fronds, sun))
# Square versions are centred on the sun: widen the box to be symmetric about it.
half = max(-box[0], box[2]); sq = (-half, box[1], half, box[3])
files['iblitza-avatar.svg'] = svg(sq, colour(word, fronds, sun), square=True)
# For GitHub: white ground (dark mode would swallow the blue) and room for the rounded corners.
files['iblitza-github.svg'] = svg(sq, colour(word, fronds, sun), pad=0.1, square=True, bg='#ffffff')

# Wordmark (no sun) in colour, and the one-colour versions: word and palm, no sun.
mono = one_colour(word, fronds, cap)
box = _union_bounds([word] + [f for f, _ in fronds])
files['iblitza-wordmark.svg'] = svg(box, colour(word, fronds))
for name, ink in INKS:
    files[f'iblitza-wordmark-{name}.svg'] = svg(box, f'<path d="{_d(mono)}" fill="{ink}"/>')
    files[f'iblitza-avatar-{name}.svg'] = svg(box, f'<path d="{_d(mono)}" fill="{ink}"/>', square=True)
# ... and on a solid ground, for places that need one.
for name, ink, bg in [('white-on-black', '#ffffff', '#000000'), ('black-on-white', '#000000', '#ffffff')]:
    files[f'iblitza-wordmark-{name}.svg'] = svg(box, f'<path d="{_d(mono)}" fill="{ink}"/>', bg=bg)
    files[f'iblitza-avatar-{name}.svg'] = svg(box, f'<path d="{_d(mono)}" fill="{ink}"/>', square=True, bg=bg)

os.makedirs(ARGS.out, exist_ok=True)
for n, s in files.items():
    with open(os.path.join(ARGS.out, n), 'w') as fh:
        fh.write(s)
