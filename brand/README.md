# IBLITZA brand files

All SVGs are self-contained (lettering is outlined, no fonts needed), so they export to PNG at any size.

| File | Use |
| --- | --- |
| `iblitza-avatar.svg` / `iblitza-avatar-1024.png` | Profile picture (GitHub org, Slack…): lime square, safe for round or rounded crops |
| `iblitza-avatar-dark.svg` | Same on a dark background |
| `iblitza-badge.svg` | Lime disc with the wordmark breaking out of it, transparent background |
| `iblitza-wordmark.svg` | Wordmark only, sunset gradient, transparent |
| `iblitza-avatar-black-on-white.svg`, `iblitza-avatar-white-on-black.svg` (+ `-1024.png`) | Black & white square avatars |
| `iblitza-wordmark-black-on-white.svg`, `iblitza-wordmark-white-on-black.svg` | Black & white wordmarks on a solid background |
| `iblitza-wordmark-black.svg` | Pure black wordmark, transparent |
| `iblitza-wordmark-ink.svg`, `iblitza-wordmark-white.svg` | One-colour wordmarks |

Colours: lime `#d3ee5f`, orange `#ff9a0a`, pink `#ff3ea5`, ink `#1b1030`, crown in greens `#0b7d36`, `#0fae4b`, `#2fc864`, `#62dd8a`.
Lettering: Barlow Semi Condensed ExtraBold Italic, slanted further (SIL Open Font License, see `OFL-Barlow.txt`).

Regenerate with `pip install fonttools brotli skia-pathops && python3 brand/make_logo.py`.
