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

# for clarity
napari_font = Alata

for glyph in missing_glyphs:
    napari_font['glyf'][glyph] = Inconsolata['glyf'][glyph]
    napari_font['hmtx'][glyph] = Inconsolata['hmtx'][glyph]

for table in Inconsolata['cmap'].tables:
    for codepoint, glyph_name in table.cmap.items():
        if codepoint not in [cp for t in napari_font['cmap'].tables for cp in t.cmap]:
            napari_font['cmap'].tables[0].cmap[codepoint] = glyph_name

family_name = "napari"
style_name = "Regular"
full_name = f"{family_name} {style_name}"
postscript_name = "napari-Regular"

name_table = napari_font["name"]
for record in name_table.names:
    if record.nameID == 1:
        record.string = family_name.encode(record.getEncoding())
    elif record.nameID == 2:
        record.string = style_name.encode(record.getEncoding())
    elif record.nameID == 4:
        record.string = full_name.encode(record.getEncoding())
    elif record.nameID == 6:
        record.string = postscript_name.encode(record.getEncoding())

napari_font.save(fonts / 'napari' / f'{postscript_name}.ttf')
