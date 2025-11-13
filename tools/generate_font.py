#!/usr/bin/env python3

# /// script
# dependencies = [
#   "fontTools",
# ]
# ///


from fontTools.ttLib import TTFont
from pathlib import Path

fonts = Path(__file__).parent.parent / 'fonts'
Alata = TTFont(fonts / 'Alata' / 'Alata-Regular.ttf')
Inconsolata = TTFont(fonts / 'Inconsolata' / 'Inconsolata-Regular.ttf')

missing_glyphs = set(Inconsolata.getGlyphOrder()) - set(Alata.getGlyphOrder())

for glyph in missing_glyphs:
    Alata['glyf'][glyph] = Inconsolata['glyf'][glyph]
    Alata['hmtx'][glyph] = Inconsolata['hmtx'][glyph]

for table in Inconsolata['cmap'].tables:
    for codepoint, glyph_name in table.cmap.items():
        if codepoint not in [cp for t in Alata['cmap'].tables for cp in t.cmap]:
            Alata['cmap'].tables[0].cmap[codepoint] = glyph_name

Alata.save(fonts / 'napari' / 'napari-Regular.ttf')
