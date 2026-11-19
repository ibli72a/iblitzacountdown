# IBLITZA brand files

All SVGs are self-contained (lettering is outlined, no fonts needed), so they export to PNG at any size.

| File | Use |
| --- | --- |
| `iblitza-avatar.svg` / `iblitza-avatar-1024.png` | GitHub org / social avatar (square, reads at 40px) |
| `iblitza-avatar-light.svg` | Same mark on stone |
| `iblitza-seal.svg`, `iblitza-seal-night.svg` | Round seal with Greek-key border |
| `iblitza-icon.svg` | Seal on a navy square |
| `iblitza-lockup.svg`, `iblitza-lockup-night.svg` | Seal + wordmark (night version is for dark backgrounds) |
| `iblitza-wordmark.svg` | Wordmark only |

Colours: navy `#002559`, stone `#f5f1ea`, gold `#b8862f`. Lettering: Cinzel Bold.

Regenerate with `pip install fonttools brotli && python3 brand/make_logo.py .` from the repo root.
