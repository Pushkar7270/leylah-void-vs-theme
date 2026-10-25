# Changelog

## 2.1.0

Two finishes, one hue family.

- **Leylah Void: Neon** - vivid, warm, peak contrast capped at 8.4:1.
- **Leylah Void: Matte** - dusty, warm, chroma held at 34% of maximum and
  contrast compressed into the 6.3-7.8:1 band.
- Palette warmed throughout: rose, warm violet, periwinkle, teal, olive-green,
  gold and coral; warm charcoal surfaces; warm off-white text.
- Removed the saturated cyan and electric blue that caused glare on black.
- Theme files are now generated from `themes/_base.json` by
  `scripts/build-palettes.py`.
- `scripts/check-palette.py` validates both variants.

## 2.0.0

Complete palette rebuild after design review.

- **One register:** every syntax color is now maximum-chroma neon, pushed to the
  edge of the sRGB gamut. No more mixing pastel, muted and neon tokens.
- **Three contrast tiers**, each with a fixed contrast band against `#000000`:
  signal 8.0-10.0:1, support 6.0-6.7:1, noise 4.3-4.6:1.
- Function names are now bold and sit in the signal tier, so they are the first
  thing the eye lands on.
- Variables, parameters and doc comments moved to the support tier; operators,
  punctuation and comments moved to the noise tier.
- Hues form an analogous magenta -> violet -> blue -> cyan -> green arc with warm
  gold and coral anchors; minimum OKLab separation 0.13.
- Workbench UI recolored to match; neon buttons now use dark text.

## 1.1.1

- README now shows a real VSCodium screenshot of the theme instead of the
  generated mockup.

## 1.1.0

- Renamed the theme to **Leylah Void** (was Hanabi Void).
- Annotations, decorators and preprocessor directives are now emerald green
  (`#7CE38B`), including Java `@Override`, Python decorators, TypeScript
  decorators and Rust attributes.
- Expanded annotation coverage to 25 grammar scopes.
- Added extension icon and README preview.

## 1.0.0

- Initial release: pitch-black workbench, magenta/violet/gold/ice-blue syntax
  palette, semantic highlighting, bracket pair colorization.
