#!/usr/bin/env python3

# /// script
# dependencies = [
#   "fontTools",
# ]
# ///


from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

fonts = Path(__file__).parent.parent / 'fonts'
Mplus = TTFont(fonts / 'M_PLUS_1p' / 'MPLUS1p-Regular.ttf')
Alata = TTFont(fonts / 'Alata' / 'Alata-Regular.ttf')
AlataPlus = TTFont(fonts / 'M_PLUS_1p' / 'MPLUS1p-Regular.ttf')

missing_glyphs = Alata.getGlyphOrder()

scale_factor = Alata['head'].unitsPerEm / Mplus['head'].unitsPerEm

for glyph in missing_glyphs:
    g = Alata['glyf'][glyph]
    # rescale glyph (if the unitsPerEm are different the sizes would mismatch)
    pen = TTGlyphPen(Alata.getGlyphSet())
    tpen = TransformPen(pen, (scale_factor, 0, 0, scale_factor, 0, 0))
    g.draw(tpen, Alata.getGlyphSet())

    # copy the glyph and its scale metrics into the new font
    AlataPlus['glyf'][glyph] = pen.glyph()
    width, lsb = Alata['hmtx'][glyph]
    AlataPlus['hmtx'][glyph] = (int(width * scale_factor), int(lsb * scale_factor))

# we need a format12 cmap in order to store glyphs from unicode above U+10FFFF
# so we find or create one
format12 = None
for t in AlataPlus['cmap'].tables:
    if t.format == 12:
        format12 = t
        break
if not format12:
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

    format12 = CmapSubtable.newSubtable(12)
    format12.platformID = 3       # Windows
    format12.platEncID = 10       # Unicode full repertoire
    format12.language = 0
    format12.cmap = {}
    AlataPlus['cmap'].tables.append(format12)


# copy codepoints from mplus into format12 cmap
for table in Mplus['cmap'].tables:
    for codepoint, glyph_name in table.cmap.items():
        if codepoint not in format12.cmap:
            format12.cmap[codepoint] = glyph_name

# set all the family and name metadata so it can be found correctly by the system
family_name = "AlataPlus"
style_name = "Regular"
full_name = f"{family_name} {style_name}"
postscript_name = f"{family_name}-{style_name}"

name_table = AlataPlus["name"]
for record in name_table.names:
    enc = record.getEncoding()
    if record.nameID in (1, 16):    # Family + Typographic Family
        record.string = family_name.encode(enc)
    elif record.nameID in (2, 17):  # Subfamily + Typographic Subfamily
        record.string = style_name.encode(enc)
    elif record.nameID == 4:        # Full font name
        record.string = full_name.encode(enc)
    elif record.nameID == 6:        # PostScript name
        record.string = postscript_name.encode(enc)
    elif record.nameID == 3:        # Unique identifier
        record.string = postscript_name.encode(enc)
    elif record.nameID == 5:        # Version string
        record.string = b"Version 1.0"

outdir = fonts / family_name
outdir.mkdir(parents=True, exist_ok=True)
AlataPlus.save(outdir / f'{postscript_name}.ttf', reorderTables=True)
