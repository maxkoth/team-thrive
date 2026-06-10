# Figma assets — Team Thrive React native

Extracted from the Figma file `Ch5F8G90eeggHnx03jFl15` via an exported, compressed PDF
(`Team Thrive React native-2-compressed-compressed.pdf`, 143 frames).

## Contents
- `images/` — 104 unique embedded raster photos (JPEG), de-duplicated across all frames.
  Named `img_<n>_p<firstPage>_<w>x<h>.jpeg`.
- `screens/` — every frame rendered to PNG at 2× scale (`frame_<page>.png`).
- `svg/` — every frame as SVG (`frame_<page>.svg`). Vector icons/illustrations are
  preserved as paths here; embedded photos are inlined as base64 (hence the larger size).
- `manifest.json` — machine-readable index of all of the above.

## Notes
- The source PDF was compressed before export, so embedded photos show JPEG artifacts and
  are not pixel-perfect. For original-resolution assets, pull directly from the Figma API
  (requires allowlisting `api.figma.com`).
- Icons are vectors, not bitmaps — extract individual icons from the per-frame SVGs in a
  vector editor (Figma/Illustrator/Inkscape) by selecting the icon's paths.
