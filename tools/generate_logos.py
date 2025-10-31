#!/usr/bin/env python3

# /// script
# dependencies = [
#   "click",
#   "lxml",
# ]
# ///

from lxml import etree
import click
from pathlib import Path
import re
import copy

logo_root = Path(__file__).parent.parent / 'logo' / 'base'
logo_only = logo_root / 'logo.svg'
logo_text = logo_root / 'logo-text.svg'
logo_text_side = logo_root / 'logo-text-side.svg'
fill_color_regex = r'fill:(#.*?);'
logo_xpath = ".//svg:*[@inkscape:label='logo']"
border_xpath = ".//svg:*[@inkscape:label='outer-border']"
napari_text_xpath = ".//svg:*[@inkscape:label='napari']"

namespace = {
    "svg": "http://www.w3.org/2000/svg",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape"
}


@click.command()
@click.argument('new-logo-path')
@click.argument('border-color-dark')
def cli(new_logo_path, border_color_dark):
    """Generate all logo variants based on a new logo.

    NEW_LOGO_PATH: the path of the new logo to use to generate. Should be
        normally placed in the `variants` directory.
    BORDER_COLOR_DARK: color (hex) to use for the border and text in the dark mode.
    """
    new_logo_path = Path(new_logo_path)
    new_logo_root = etree.parse(new_logo_path).getroot()
    new_logo = new_logo_root.find(logo_xpath, namespaces=namespace)
    border = new_logo_root.find(border_xpath, namespaces=namespace)
    border_color_light = re.search(fill_color_regex, border.get('style')).group(1)
    if not border_color_dark.startswith('#'):
        border_color_dark = '#' + border_color_dark

    colors = {'-light': border_color_light, '-dark': border_color_dark}
    variants = {'': logo_only, '-text': logo_text, '-text-side': logo_text_side}

    for variant, base_logo_path in variants.items():
        for theme, color in colors.items():
            base_logo_tree = etree.parse(base_logo_path)
            base_logo_root = base_logo_tree.getroot()
            base_logo = base_logo_root.find(logo_xpath, namespaces=namespace)
            base_logo.getparent().replace(base_logo, copy.deepcopy(new_logo))

            base_logo_border = base_logo_root.find(border_xpath, namespaces=namespace)
            new_border_style = re.sub(fill_color_regex, f'fill:{color};', base_logo_border.get('style'))
            base_logo_border.set('style', new_border_style)

            napari_text = base_logo_root.find(napari_text_xpath, namespaces=namespace)
            if napari_text is not None:
                new_text_style = re.sub(fill_color_regex, f'fill:{color};', napari_text.get('style'))
                napari_text.set('style', new_text_style)

            output_path = logo_root.parent / 'generated' / f'{new_logo_path.stem}{variant}{theme}.svg'
            base_logo_tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
            print(f'Generated {output_path}.')


if __name__ == '__main__':
    cli()
