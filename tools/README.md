# tools

The header plates and the social preview are generated, not exported from a
design tool. Two reasons:

1. **GitHub strips CSS from READMEs.** All the styling has to live inside an
   SVG served as an image, and an SVG inside `<img>` cannot fetch a web font.
   So every glyph is converted to a `<path>`.
2. **Color has to be deterministic.** Translucent strokes render differently
   across SVG engines (and ImageMagick gets them wrong), so every tint is
   pre-blended onto the paper color.

## Regenerate

```sh
python3 -m venv .venv
.venv/bin/pip install fonttools
.venv/bin/python tools/generate-assets.py
magick -background none assets/og.svg -resize 1280x -depth 8 -strip assets/og.png
```

Outputs `assets/header-dark.svg`, `assets/header-light.svg` and `assets/og.svg`.

## Edit the content

Everything lives in `generate-assets.py`:

- `THEMES` — the two palettes.
- `INDEX` — the section list on the right side of the plate.
- `header_svg()` / `og_svg()` — copy, sizes and positions.

The `REV 2026.11` stamp at the bottom right is a string in `header_svg()`.
Bump it when the content changes.

## Fonts

`fonts/SpaceGrotesk.ttf` and `fonts/JetBrainsMono.ttf` are the variable
versions from Google Fonts, under the SIL Open Font License. The license files
sit next to them.
