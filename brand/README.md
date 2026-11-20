# IBLITZA brand files

The I is a palm tree: the letter is the trunk (with wavy rings cut into it) and a crown of
fronds sits on top. In the full logo the word is centred across a warm sun, its ends just
breaking out on both sides.

All files have a transparent background. The SVGs are self-contained (lettering is outlined, no
fonts needed), so they export to PNG at any size.

| File | Use |
| --- | --- |
| `iblitza-logo.svg` | The logo: word + palm + sun, colour |
| `iblitza-avatar.svg` / `iblitza-avatar-1024.png` | Same, on a square canvas (GitHub org, Slack…) |
| `iblitza-wordmark.svg` | Word + palm, no sun, colour |
| `iblitza-wordmark-black.svg`, `iblitza-wordmark-white.svg` | Word + palm in one colour |
| `iblitza-avatar-black.svg`, `iblitza-avatar-white.svg` (+ `-1024.png`) | Same, on a square canvas |

**One colour:** no sun. The palm and the letters are one shape with real gaps between the fronds
and between the crown and the letters, so they stay readable in a single ink on any ground.

Colours, all flat: blue `#0b5cad` (lettering), sun `#ffb21f`, palm in two greens `#13a84b` /
`#5fcf6e`, alternating across the fronds.
Lettering: Galindo (SIL Open Font License, see `OFL-Galindo.txt`).

Regenerate with `pip install fonttools brotli skia-pathops && python3 brand/make_logo.py`
(`--font` and `--out` to try another font or write elsewhere).
