"""Generate the IBLITZA logo set as self-contained SVGs (text outlined, no fonts needed)."""
import math, os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

REPO = sys.argv[1]
OUT = os.path.join(REPO, 'brand')
os.makedirs(OUT, exist_ok=True)
FONTS = os.path.join(REPO, 'src/app/fonts')

NAVY, STONE, GOLD = '#002559', '#f5f1ea', '#b8862f'


def text_path(text, font_file, size, x, y, tracking=0.0, anchor='middle'):
    """Outline `text` into one SVG path. (x, y) is the baseline anchor point."""
    f = TTFont(os.path.join(FONTS, font_file))
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    upm = f['head'].unitsPerEm
    s = size / upm
    names = [cmap[ord(c)] for c in text]
    adv = [gs[n].width for n in names]
    width = (sum(adv) + tracking * upm * (len(text) - 1)) * s
    x0 = x - width / 2 if anchor == 'middle' else x
    pen = SVGPathPen(gs, ntos=lambda v: f'{v:.2f}')
    cx = 0.0
    for n, a in zip(names, adv):
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, x0 + cx * s, y)))
        cx += a + tracking * upm
    return pen.getCommands(), width


def polar(cx, cy, r, ang):
    return cx + r * math.sin(ang), cy - r * math.cos(ang)


def meander(cx, cy, r_in, r_out, periods):
    """Square-spiral Greek key band mapped onto a ring. Unit grid: period 5 wide, 4 tall."""
    unit_r = (r_out - r_in) / 4
    unit_a = 2 * math.pi / (periods * 5)
    hook = [(0, 0), (0, 4), None, (4, 4), (4, 1), (1, 1), (1, 3), (3, 3), (3, 2), (2, 2)]
    paths = []

    def pt(u, v):
        return polar(cx, cy, r_in + v * unit_r, u * unit_a)

    def seg(p, q):  # densify so angular runs follow the curve
        n = max(1, int(abs(q[0] - p[0]) * 6))
        return [pt(p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n) for i in range(1, n + 1)]

    for k in range(periods):
        o = k * 5
        runs, cur = [], []
        for p in hook:
            if p is None:
                runs.append(cur); cur = []
            else:
                cur.append((p[0] + o, p[1]))
        runs.append(cur)
        for run in runs:
            pts = [pt(*run[0])]
            for a, b in zip(run, run[1:]):
                pts += seg(a, b)
            paths.append('M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts))
    return ' '.join(paths)


def sun_record(cx, cy, r, fg, bg):
    """Half vinyl rising like the sun: grooves, label, spindle, and rays."""
    out = []
    clip = f'<clipPath id="sky"><rect x="{cx - 400}" y="{cy - 400}" width="800" height="400"/></clipPath>'
    rays = []
    for i in range(11):
        a = math.radians(-75 + i * 15)
        w = 9 if i % 2 == 0 else 6
        r1, r2 = r + 26, r + (78 if i % 2 == 0 else 54)
        (x1, y1), (x2, y2) = polar(cx, cy, r1, a), polar(cx, cy, r2, a)
        rays.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke-width="{w}"/>')
    out.append(f'<g stroke="{fg}" stroke-linecap="round">{"".join(rays)}</g>')
    grooves = ''.join(
        f'<circle cx="{cx}" cy="{cy}" r="{gr}" fill="none" stroke="{bg}" stroke-width="{sw}"/>'
        for gr, sw in [(r - 18, 3), (r - 34, 2), (r - 50, 3), (r - 66, 2)])
    out.append(
        f'<g clip-path="url(#sky)"><circle cx="{cx}" cy="{cy}" r="{r}" fill="{fg}"/>{grooves}'
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.36:.1f}" fill="{bg}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.36 - 9:.1f}" fill="none" stroke="{fg}" stroke-width="2"/>'
        f'<circle cx="{cx}" cy="{cy}" r="9" fill="{fg}"/></g>')
    # Glint on the record: a short highlight arc
    a1, a2 = math.radians(-58), math.radians(-28)
    (x1, y1), (x2, y2) = polar(cx, cy, r - 26, a1), polar(cx, cy, r - 26, a2)
    out.append(f'<path d="M{x1:.2f},{y1:.2f} A{r - 26},{r - 26} 0 0 1 {x2:.2f},{y2:.2f}" '
               f'fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round" opacity="0.9"/>')
    return clip, ''.join(out)


def waves(cx, y0, half, fg, rows=3, gap=30, amp=7, wl=56):
    out = []
    for j in range(rows):
        y = y0 + j * gap
        w = half - j * 40
        pts = []
        x = cx - w
        while x <= cx + w + 0.1:
            pts.append(f'{x:.1f},{y + amp * math.sin((x - cx) / wl * 2 * math.pi + j * 1.4):.1f}')
            x += 4
        out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{fg}" '
                   f'stroke-width="{7 - j * 1.5}" stroke-linecap="round" stroke-linejoin="round"/>')
    return ''.join(out)


def seal(fg, bg, ox=0, oy=0):
    """The round emblem on a 1000x1000 box. fg = disc colour, bg = line colour on it."""
    cx, cy = 500 + ox, 500 + oy
    word, ww = text_path('IBLITZA', 'cinzel-latin-700-normal.woff2', 104, cx, cy + 258, tracking=0.08)
    clip, sun = sun_record(cx, cy + 70, 150, bg, fg)
    parts = [
        f'<defs>{clip}</defs>',
        f'<circle cx="{cx}" cy="{cy}" r="490" fill="{fg}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="470" fill="none" stroke="{bg}" stroke-width="5"/>',
        f'<path d="{meander(cx, cy, 380, 446, 30)}" fill="none" stroke="{bg}" stroke-width="7.5" '
        f'stroke-linecap="square" stroke-linejoin="miter"/>',
        f'<circle cx="{cx}" cy="{cy}" r="380" fill="none" stroke="{bg}" stroke-width="7.5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="446" fill="none" stroke="{bg}" stroke-width="7.5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="358" fill="none" stroke="{bg}" stroke-width="2.5"/>',
        sun,
        f'<line x1="{cx - 300}" y1="{cy + 70}" x2="{cx + 300}" y2="{cy + 70}" stroke="{bg}" '
        f'stroke-width="7" stroke-linecap="round"/>',
        waves(cx, cy + 104, 230, bg),
        f'<path d="{word}" fill="{bg}"/>',
        # three dots under the wordmark, like the seal's foot
        ''.join(f'<circle cx="{cx + dx}" cy="{cy + 300}" r="{5 if dx == 0 else 3.5}" fill="{bg}"/>'
                for dx in (-22, 0, 22)),
    ]
    return '\n  '.join(parts)


def svg(w, h, body, title, bg=None):
    back = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'  <title>{title}</title>\n  {back}{body}\n</svg>\n')


files = {}
files['iblitza-seal.svg'] = svg(1000, 1000, seal(NAVY, STONE), 'IBLITZA')
files['iblitza-seal-night.svg'] = svg(1000, 1000, seal(STONE, NAVY), 'IBLITZA')

# Horizontal lockup: seal + wordmark + small mono line
lock_word, lw = text_path('IBLITZA', 'cinzel-latin-700-normal.woff2', 300, 1080, 610, tracking=0.06, anchor='start')
tag, tw = text_path('AEGEAN  ·  SOUND  ·  SUN', 'jetbrains-mono-latin-500-normal.woff2', 46, 1084, 720,
                    tracking=0.22, anchor='start')
W = int(1080 + max(lw, tw) + 60)
for name, fg, bg, page in [('iblitza-lockup.svg', NAVY, STONE, None),
                           ('iblitza-lockup-night.svg', STONE, NAVY, None)]:
    body = (f'<g transform="translate(40 100) scale(0.8)">{seal(fg, bg)}</g>'
            f'<path d="{lock_word}" fill="{fg}"/>'
            f'<rect x="1084" y="652" width="{lw - 10:.0f}" height="5" fill="{GOLD}"/>'
            f'<path d="{tag}" fill="{fg}" opacity="0.72"/>')
    files[name] = svg(W, 1000, body, 'IBLITZA', page)

# Wordmark only
wm, ww = text_path('IBLITZA', 'cinzel-latin-700-normal.woff2', 300, 0, 0, tracking=0.06, anchor='start')
files['iblitza-wordmark.svg'] = svg(int(ww + 80), 340, f'<path transform="translate(40 290)" d="{wm}" fill="{NAVY}"/>',
                                    'IBLITZA')

# App icon: seal on a full navy square
files['iblitza-icon.svg'] = svg(1024, 1024, f'<g transform="translate(42 42) scale(0.94)">{seal(STONE, NAVY)}</g>',
                                'IBLITZA', NAVY)

# GitHub org avatar: bold, text-free mark that still reads at 40px. Full-bleed navy square
# (GitHub rounds the corners itself), everything inside the central safe area.
def avatar(fg, bg):
    cx, cy, r = 512, 560, 250
    rays = ''
    for i in range(7):
        a = math.radians(-72 + i * 24)
        (x1, y1), (x2, y2) = polar(cx, cy, r + 52, a), polar(cx, cy, r + (150 if i % 2 == 0 else 112), a)
        rays += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
    grooves = ''.join(f'<circle cx="{cx}" cy="{cy}" r="{g}" fill="none" stroke="{bg}" stroke-width="9"/>'
                      for g in (r - 42, r - 84))
    return (
        f'<defs><clipPath id="sky"><rect x="0" y="0" width="1024" height="{cy}"/></clipPath></defs>'
        f'<g stroke="{fg}" stroke-width="30" stroke-linecap="round">{rays}</g>'
        f'<g clip-path="url(#sky)"><circle cx="{cx}" cy="{cy}" r="{r}" fill="{fg}"/>{grooves}'
        f'<circle cx="{cx}" cy="{cy}" r="96" fill="{bg}"/><circle cx="{cx}" cy="{cy}" r="30" fill="{fg}"/></g>'
        f'<line x1="{cx - 370}" y1="{cy}" x2="{cx + 370}" y2="{cy}" stroke="{fg}" stroke-width="30" stroke-linecap="round"/>'
        + ''.join(
            '<polyline points="' + ' '.join(
                f'{x},{cy + 82 + j * 80 + 20 * math.sin((x - cx) / 150 * 2 * math.pi + j * math.pi):.1f}'
                for x in range(cx - w, cx + w + 1, 6)) +
            f'" fill="none" stroke="{GOLD if j == 0 else fg}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>'
            for j, w in enumerate((290, 180))))

files['iblitza-avatar.svg'] = svg(1024, 1024, avatar(STONE, NAVY), 'IBLITZA', NAVY)
files['iblitza-avatar-light.svg'] = svg(1024, 1024, avatar(NAVY, STONE), 'IBLITZA', STONE)

for n, s in files.items():
    with open(os.path.join(OUT, n), 'w') as fh:
        fh.write(s)
    print(n, len(s))
