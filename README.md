# resources

Graphics and copy resources for the napari project.

## Permissions and usage guidelines

### License

The resources in this repo are available under a [CC-BY-NC-ND 4.0] license.

We further kindly request that you follow the guidelines below when using the
logo.

### Usage guidelines

You may use the napari logo to describe factual use of the software in your own
projects, for example in papers, figures, posters, conference talks, and
project websites. Examples:

- ✅ We explored the data in napari and came to the conclusion that…
- ✅ We provide a reader for napari to visualize our novel data…
- ✅ In addition to our standalone library, we provide a napari plugin to…
- ✅ We provide training and consultation in the use of napari for…
- ✅ We intend to analyze the resulting data by using napari with the following
  plugins…

You should **not** use the napari logo to imply endorsement of your project by
napari without prior written permission by the napari Steering Council.
Examples:

- 🚫 The napari team will support this effort with…
- 🚫 The napari community needs this functionality because…
- 🚫 napari supports this proposed standard…

Conjecture is allowed when clearly marked as such:

- ✅ We believe that the napari project would benefit from these changes…

You may use the napari logo in swag (pens, pins, stickers, etc) for personal or
small group usage, as long as that use is not for fundraising.

## logos

Logos are generated programmatically based on the content of the `variants` directory (which contains the actual logo icon) and the content of the `templates` directory (which contains the various arrangements of icons and text). To generate new logos, a new version need to be added into `variants`. This logo needs to follow the same structure as the exising ones: group hierarchy and labels in inskcape need to be maintained (such as `outer-border` and `logo`).

> [!IMPORTANT]
> If you add text to a variant or template, convert the Object to Path before saving it, so it will work even on systems where the font is not available! Also, use the custom AlataPlus font when appropriate.

Then, by running

```sh
uv run tools/generate_logos.py
```

svgs (and pngs if requested and inkscape is installed) for each logo combinations will be created and dumped in `generated`.
By passing the names of specific templates, variants and themes via the relevant options, you can also generate only a subset of the possible combinations. Check out the `-h` for details.
## fonts

The "napari" font `AlataPlus` is generated starting from [Alata](https://fonts.google.com/specimen/Alata), and adding missing glyphs from the [M_PLUS_1p](https://fonts.google.com/specimen/M+PLUS+1p). This is done running

```sh
uv run tools/generate_font.py
```

[CC-BY-NC-ND 4.0]: https://creativecommons.org/licenses/by-nc-nd/4.0/
