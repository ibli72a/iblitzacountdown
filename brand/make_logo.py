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
LIME, ORANGE, PINK, INK = '#d3ee5f', '#ff9a0a', '#ff3ea5', '#1b1030'


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
        t = (s, 0, 0, -s, x0 + x * s, baseline)
        for p in (pen, allb) + ((first,) if i == 0 else ()):
            gs[n].draw(TransformPen(p, t))
        x += a + tracking * upm
    return pen.getCommands(), allb.bounds, first.bounds


def palm(x, y, size, fill):
    """Palm crown: six fronds fanning from (x, y), drooping at the tips, on a short trunk."""
    out = []
    for deg, ln in [(-98, 1.0), (-62, 0.92), (-28, 1.0), (4, 0.82), (-134, 0.95), (-168, 0.8)]:
        a = math.radians(deg)
        L = size * ln
        ex, ey = x + L * math.cos(a), y + L * math.sin(a) + L * 0.30  # tip droops
        mx, my = x + L * 0.55 * math.cos(a), y + L * 0.55 * math.sin(a) - L * 0.10
        nx, ny = -math.sin(a) * size * 0.17, math.cos(a) * size * 0.17  # frond half-width
        out.append(f'M{x:.1f},{y:.1f} Q{mx + nx:.1f},{my + ny:.1f} {ex:.1f},{ey:.1f} '
                   f'Q{mx - nx:.1f},{my - ny:.1f} {x:.1f},{y:.1f}Z')
    t = size * 0.11
    out.append(f'M{x - t:.1f},{y - t:.1f} L{x + t:.1f},{y - t:.1f} L{x + t * 0.2:.1f},{y + size * 0.62:.1f} '
               f'L{x - t * 1.6:.1f},{y + size * 0.62:.1f}Z')
    return f'<path d="{" ".join(out)}" fill="{fill}"/>'


def swoosh(x1, x2, y, thick, fill):
    """Brush underline: thick on the left, tapering to a point, rising slightly to the right."""
    rise = (x2 - x1) * 0.022
    return (f'<path d="M{x1:.1f},{y + thick * 0.45:.1f} '
            f'Q{x1 - thick * 0.9:.1f},{y - thick * 0.2:.1f} {x1 + thick:.1f},{y - thick * 0.5:.1f} '
            f'Q{(x1 + x2) / 2:.1f},{y - thick * 0.9 - rise * 0.4:.1f} {x2:.1f},{y - rise:.1f} '
            f'Q{(x1 + x2) / 2:.1f},{y + thick * 0.75:.1f} {x1:.1f},{y + thick * 0.45:.1f}Z" fill="{fill}"/>')


def mark(width, cx, cy, grad='url(#sunset)', accent_top=ORANGE, accent_bottom=PINK):
    """Wordmark + palm on the I + underline, vertically centred on cy."""
    path, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(width, cx, 0)
    cap = by1 - by0
    base = cy + cap * 0.42
    path, (bx0, by0, bx1, by1), (ix0, iy0, ix1, iy1) = wordmark(width, cx, base)
    lean = (ix1 - ix0) * 0.30  # the italic I leans right: sit the palm over its top end
    body = (palm(ix0 + (ix1 - ix0) * 0.5 + lean, by0 - cap * 0.20, cap * 0.20, accent_top)
            + f'<path d="{path}" fill="{grad}"/>'
            + swoosh(bx0 + width * 0.02, bx1 - width * 0.14, by1 + cap * 0.22, cap * 0.085, accent_bottom))
    defs = (f'<linearGradient id="sunset" gradientUnits="userSpaceOnUse" x1="0" y1="{by0:.1f}" x2="0" y2="{by1:.1f}">'
            f'<stop offset="0.12" stop-color="{ORANGE}"/><stop offset="0.9" stop-color="{PINK}"/></linearGradient>')
    return defs, body


def svg(w, h, defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'  <title>IBLITZA</title>\n  <defs>{defs}</defs>\n  {body}\n</svg>\n')


files = {}
# Badge, as on Instagram: lime disc with the wordmark breaking out of it. Transparent corners.
d, b = mark(1060, 560, 500)
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
    d1, b1 = mark(1000, 540, 300, grad=col, accent_top=col, accent_bottom=col)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 520, '', b1)

# Black & white: square avatars and wide wordmarks, each on a solid background.
for name, fg, bg in [('black-on-white', '#000000', '#ffffff'), ('white-on-black', '#ffffff', '#000000')]:
    _, b1 = mark(820, 512, 512, grad=fg, accent_top=fg, accent_bottom=fg)
    files[f'iblitza-avatar-{name}.svg'] = svg(1024, 1024, '', f'<rect width="1024" height="1024" fill="{bg}"/>{b1}')
    _, b1 = mark(1000, 540, 300, grad=fg, accent_top=fg, accent_bottom=fg)
    files[f'iblitza-wordmark-{name}.svg'] = svg(1080, 520, '', f'<rect width="1080" height="520" fill="{bg}"/>{b1}')
_, b1 = mark(1000, 540, 300, grad='#000000', accent_top='#000000', accent_bottom='#000000')
files['iblitza-wordmark-black.svg'] = svg(1080, 520, '', b1)

for n, s in files.items():
    with open(os.path.join(HERE, n), 'w') as fh:
        fh.write(s)
    print(n, len(s))
