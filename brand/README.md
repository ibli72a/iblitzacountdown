# IBLITZA brand files

All SVGs are self-contained (lettering is outlined, no fonts needed), so they export to PNG at any size.

| File | Use |
| --- | --- |
| `iblitza-avatar.svg` / `iblitza-avatar-1024.png` | Profile picture (GitHub org, Slack…): lime square, safe for round or rounded crops |
| `iblitza-avatar-dark.svg` | Same on a dark background |
| `iblitza-badge.svg` | Lime disc with the wordmark breaking out of it, transparent background |
| `iblitza-wordmark.svg` | Wordmark only, sunset gradient, transparent |
| `iblitza-wordmark-ink.svg`, `iblitza-wordmark-white.svg` | One-colour wordmarks |

Colours: lime `#d3ee5f`, orange `#ff9a0a`, pink `#ff3ea5`, ink `#1b1030`.
Lettering: Barlow Semi Condensed ExtraBold Italic (SIL Open Font License, see `OFL-Barlow.txt`).

Regenerate with `pip install fonttools brotli && python3 brand/make_logo.py`.
