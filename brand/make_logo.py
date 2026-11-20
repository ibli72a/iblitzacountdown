"""Generate the IBLITZA logo set as self-contained SVGs (lettering outlined, no fonts needed).

    pip install fonttools brotli skia-pathops && python3 brand/make_logo.py
"""
import math, os, re
import pathops
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
STRETCH = 1.16  # letters drawn this much taller than the font, slant kept the same


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


def wordmark(width, cx, baseline, text='IBLITZA', gap=0.03):
    """Outline `text` scaled to `width`, centred on cx. Returns (path, box, first-glyph box).

    Spacing: each gap is measured where the two slanted letters come closest, and made the
    same for every pair (the font's own spacing makes T-Z read wider than L-I-T).

    Z-A: the bottoms line up the way T and Z do. Z is left as drawn; A's left leg, which
    meets the baseline at a shallower angle, gets its foot squared off parallel to the end of
    Z's foot, one gap away, over the height of that foot."""
    gs, cmap, upm = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm
    names = [cmap[ord(c)] for c in text]
    adv = [gs[n].width for n in names]
    k = SLANT * STRETCH - ITALIC     # extra shear, in font units of x per unit of y
    edge = ITALIC + k                # slope (dx/dy) of an upright edge after slanting
    G = gap * upm
    profs = [_profile(gs, n, k) for n in names]
    X, trim, trim_i = [0.0], None, None
    for i in range(len(names) - 1):
        a, b = profs[i], profs[i + 1]
        closest = min(b[y][0] + adv[i] - a[y][1] for y in a if y in b)
        X.append(X[i] + adv[i] + G - closest)
        if text[i:i + 2] == 'ZA':
            # Z's foot: from the bottom up, until the right edge steps back to the diagonal
            ys = sorted(a)
            foot = next(y1 for y1, y2 in zip(ys, ys[1:]) if a[y1][1] - a[y2][1] > 25)
            # the end of Z's foot, as a line in layout units: x = zx + edge * (y - foot)
            zx = a[foot][1] + X[i]
            line = lambda y: zx + edge * (y - foot) + G
            # place A so its left edge meets that line at the top of Z's foot, but never
            # closer than one gap to Z anywhere above it
            X[i + 1] = line(foot) - b[foot][0]
            need = min(b[y][0] + X[i + 1] - (a[y][1] + X[i]) for y in a if y in b and y > foot)
            X[i + 1] += max(0, G - need)
            lo, hi = -2000, 4000
            trim = pathops.Path(); pen_ = trim.getPen()
            pen_.moveTo((line(lo), lo)); pen_.lineTo((1e5, lo)); pen_.lineTo((1e5, hi))
            pen_.lineTo((line(hi), hi)); pen_.closePath()
            trim_i = i + 1
    total = X[-1] + adv[-1]
    s = width / total
    x0 = cx - width / 2
    final = (s, 0, 0, -s * STRETCH, x0, baseline)
    pen, allb, first = SVGPathPen(None, ntos=lambda v: f'{v:.2f}'), BoundsPen(None), BoundsPen(None)
    for i, n in enumerate(names):
        g = pathops.Path()
        gs[n].draw(TransformPen(g.getPen(), (1, 0, k, 1, X[i], 0)))
        if i == trim_i:
            g = pathops.op(g, trim, pathops.PathOp.INTERSECTION)
        for p in (pen, allb) + ((first,) if i == 0 else ()):
            g.draw(TransformPen(p, final))
    return pen.getCommands(), allb.bounds, first.bounds


def leaf(x, y, L, a0, bend, W):
    """One pineapple leaf as a closed polygon: a broad, pointed lance shape leaving (x, y) at
    angle a0 (degrees from upright, clockwise) and curving by `bend` degrees along its length,
    zero-width at both ends and widest about 40% of the way out."""
    n = 60
    pts, ang = [(x, y)], [math.radians(a0)]
    px, py = x, y
    for k in range(1, n + 1):
        t = k / n
        th = math.radians(a0 + bend * t * t)
        px += math.sin(th) * L / n
        py -= math.cos(th) * L / n
        pts.append((px, py)); ang.append(th)
    left, right = [], []
    for k, ((sx, sy), th) in enumerate(zip(pts, ang)):
        t = k / n
        w = W * math.sin(math.pi * t ** 0.75) ** 0.85
        nx, ny = math.cos(th), math.sin(th)
        left.append((sx - nx * w, sy - ny * w)); right.append((sx + nx * w, sy + ny * w))
    return left + right[::-1]


# Pineapple crown, back to front: (angle from upright, curl, length, shade, half-width).
# Tall upright leaves at the back, a middle row opening out, short side leaves flaring, and a
# cup of short, broad leaves in front. Shades run dark at the back to pale at the front.
CROWN = [
    (-4, -4, 1.00, 0, .12), (8, 6, 0.96, 1, .12),
    (-16, -10, 0.86, 1, .12), (20, 12, 0.88, 0, .12),
    (-30, -16, 0.74, 0, .115), (32, 16, 0.76, 1, .115),
    (-42, -18, 0.58, 1, .11), (44, 18, 0.58, 0, .11),
    (-14, -8, 0.58, 2, .13), (16, 8, 0.56, 2, .13),
    (-32, -16, 0.40, 2, .12), (34, 16, 0.40, 2, .12),
    (2, 2, 0.40, 3, .13),
]
SHADES = ['#0b7d36', '#0fae4b', '#2fc864', '#62dd8a']


def palm(x0, x1, y, cap, fill, line):
    """Pineapple crown on the I, a small gap above it, its leaves gathered at the bottom into
    a bunch as wide as the I. `fill` GREEN draws it in shades of green; any other colour draws
    it in that colour with `line` (the background) separating the leaves, or as a plain
    silhouette when `line` is None."""
    gap, H = cap * 0.035, cap * 0.85
    bx, by = (x0 + x1) / 2 + gap * SLANT, y - gap
    lean = math.degrees(math.atan(SLANT)) * 0.5
    sw = H * 0.014
    parts = []
    for a, b, l, shade, w in CROWN:
        ox = bx + (x1 - x0) * 0.75 * math.sin(math.radians(a))
        poly = leaf(ox, by, H * l, a + lean, b, H * w)
        d = 'M' + ' L'.join(f'{u:.1f},{v:.1f}' for u, v in poly) + 'Z'
        if fill == GREEN:
            parts.append(f'<path d="{d}" fill="{SHADES[shade]}"/>')
        elif line:
            parts.append(f'<path d="{d}" fill="{fill}" stroke="{line}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
        else:
            parts.append(f'<path d="{d}" fill="{fill}"/>')
    return '<g>' + ''.join(parts) + '</g>'


def _mark(text_width, cx, cy, grad, accent, line):
    _, (bx0, by0, bx1, by1), _ = wordmark(text_width, cx, 0)
    cap = by1 - by0
    path, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(text_width, cx, cy + cap / 2)
    # The italic I is a parallelogram: its top edge is the right-hand end of its bounding box.
    stem = (ix1 - ix0) - cap * SLANT
    plant = palm(ix1 - stem, ix1, by0, cap, accent, line)
    leaf = [tuple(map(float, m)) for m in re.findall(r'(-?[\d.]+),(-?[\d.]+)', plant)]
    xs = [bx0, bx1] + [x for x, _ in leaf]
    ys = [by0, by1] + [y for _, y in leaf]
    return plant + f'<path d="{path}" fill="{grad}"/>', (min(xs), min(ys), max(xs), max(ys)), (by0, by1)


def mark(width, cx, cy, grad='url(#sunset)', accent=GREEN, line=None):
    """Wordmark with the pineapple crown on the I, the whole thing `width` wide and centred on (cx, cy)."""
    _, (x0, y0, x1, y1), _ = _mark(1000, 0, 0, grad, accent, line)
    tw = 1000 * width / (x1 - x0)                       # text width that makes the total `width`
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
# Avatar: full-bleed lime square with everything inside the safe area (GitHub/Slack crop the corners).
d, b = mark(800, 512, 512)
files['iblitza-avatar.svg'] = svg(1024, 1024, d, f'<rect width="1024" height="1024" fill="{LIME}"/>{b}')
# Same, dark background.
files['iblitza-avatar-dark.svg'] = svg(1024, 1024, d, f'<rect width="1024" height="1024" fill="{INK}"/>{b}')
# Wordmark only, transparent: gradient, and single-colour versions for print / one-colour use.
d, b = mark(960, 540, 340)
files['iblitza-wordmark.svg'] = svg(1080, 680, d, b)
for name, col in [('ink', INK), ('white', '#ffffff')]:
    d1, b1 = mark(960, 540, 340, grad=col, accent=col, line=None)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, '', b1)

# Black & white: square avatars and wide wordmarks, each on a solid background.
for name, fg, bg in [('black-on-white', '#000000', '#ffffff'), ('white-on-black', '#ffffff', '#000000')]:
    _, b1 = mark(800, 512, 512, grad=fg, accent=fg, line=bg)
    files[f'iblitza-avatar-{name}.svg'] = svg(1024, 1024, '', f'<rect width="1024" height="1024" fill="{bg}"/>{b1}')
    _, b1 = mark(960, 540, 340, grad=fg, accent=fg, line=bg)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 680, '', f'<rect width="1080" height="680" fill="{bg}"/>{b1}')
_, b1 = mark(960, 540, 340, grad='#000000', accent='#000000', line=None)
files['iblitza-wordmark-black.svg'] = svg(1080, 680, '', b1)

for n, s in files.items():
    with open(os.path.join(HERE, n), 'w') as fh:
        fh.write(s)
    print(n, len(s))
