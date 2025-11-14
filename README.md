# resources
graphics and copy resources for the napari project


## logos

Logos are generated programmatically based on the content of the `variants` directory (which contains the actual logo icon) and the content of the `templates` directory (which contains the various arrangements of icons and text). To generate new logos, a new version need to be added into `variants`. This logo needs to follow the same structure as the exising ones: group hierarchy and labels in inskcape need to be maintained (such as `outer-border` and `logo`).

> [!IMPORTANT]
> If you add text to a variant or template, convert the Object to Path before saving it, so it will work even on systems where the font is not available! Also, use the custom AlataPlus font when appropriate.

Then, by running

```sh
uv run tools/generate_logos.py
```

svgs for each logo combinations will be created and dumped in `generated`. To convert these to PNGs, install inkscape and run:

```sh
./tools/generate_logo_pngs.sh
```

## fonts

The "napari" font `AlataPlus` is generated starting from [Alata](https://fonts.google.com/specimen/Alata), and adding missing glyphs from the [M_PLUS_1p](https://fonts.google.com/specimen/M+PLUS+1p). This is done running

```sh
uv run tools/generate_font.py
```
