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
InconsAlata = Alata

for glyph in missing_glyphs:
    InconsAlata['glyf'][glyph] = Inconsolata['glyf'][glyph]
    InconsAlata['hmtx'][glyph] = Inconsolata['hmtx'][glyph]

for table in Inconsolata['cmap'].tables:
    for codepoint, glyph_name in table.cmap.items():
        if codepoint not in [cp for t in InconsAlata['cmap'].tables for cp in t.cmap]:
            InconsAlata['cmap'].tables[0].cmap[codepoint] = glyph_name

family_name = "InconsAlata"
style_name = "Regular"
full_name = f"{family_name} {style_name}"
postscript_name = f"{family_name}-{style_name}"

name_table = InconsAlata["name"]
for record in name_table.names:
    if record.nameID == 1:
        record.string = family_name.encode(record.getEncoding())
    elif record.nameID == 2:
        record.string = style_name.encode(record.getEncoding())
    elif record.nameID == 4:
        record.string = full_name.encode(record.getEncoding())
    elif record.nameID == 6:
        record.string = postscript_name.encode(record.getEncoding())

InconsAlata.save(fonts / 'InconsAlata' / f'{postscript_name}.ttf')
