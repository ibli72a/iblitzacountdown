# IBLITZA brand files

The I is a palm tree: the letter is the trunk (with wavy rings cut into it) and a crown of
fronds sits on top. The word sits across a warm sun and breaks out of it on both sides.

All SVGs are self-contained (lettering is outlined, no fonts needed), so they export to PNG at
any size.

| File | Use |
| --- | --- |
| `iblitza-avatar.svg` / `iblitza-avatar-1024.png` | Profile picture (GitHub org, Slack…): the badge on a sand square |
| `iblitza-avatar-black-on-white.svg`, `iblitza-avatar-white-on-black.svg` (+ `-1024.png`) | Same, one colour |
| `iblitza-badge.svg` | Word + sun, transparent background |
| `iblitza-badge-black-on-white.svg`, `iblitza-badge-white-on-black.svg` | Same, one colour |
| `iblitza-wordmark.svg` | Word + palm only, colour, transparent |
| `iblitza-wordmark-black.svg`, `-white.svg`, `-blue.svg` | Word + palm in one colour, transparent |
| `iblitza-wordmark-black-on-white.svg`, `iblitza-wordmark-white-on-black.svg` | One colour on a solid ground |

**One colour:** the sun is solid ink, and the parts of the word and palm that fall on it are
knocked out to the paper colour, so the mark works printed in black only, or white only on a
dark ground.

Colours: blue `#0b5cad` (lettering), sun `#ffd23f` → `#ff9a1f`, palm `#0b7d36` / `#13a84b`,
sand `#fff4e2` (avatar ground).
Lettering: Galindo (SIL Open Font License, see `OFL-Galindo.txt`).

Regenerate with `pip install fonttools brotli skia-pathops && python3 brand/make_logo.py`
(`--font` and `--out` to try another font or write elsewhere).
