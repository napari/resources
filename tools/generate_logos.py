#!/usr/bin/env python3

# /// script
# dependencies = [
#   "click",
#   "lxml",
# ]
# ///

import click
from pathlib import Path
import re
import copy

from lxml import etree

fill_color_regex = r'fill:(#.*?);'
stroke_color_regex = r'stroke:(#.*?);'
logo_xpath = ".//*[@inkscape:label='logo']"
napari_text_xpath = ".//*[@inkscape:label='napari']"
border_xpath = ".//*[@inkscape:label='outer-border']"
namespace = {
    "svg": "http://www.w3.org/2000/svg",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape"
}

def change_border_color(root, color):
    # change the color of the border
    # this affects anything labeled as `outer-border` as well as children nodes
    base_logo_border = root.findall(border_xpath, namespaces=namespace)
    for border in base_logo_border:
        for element in (border, *border.getchildren()):
            if not element.get('style'):
                continue
            new_border_style = re.sub(fill_color_regex, f'fill:{color};', element.get('style'))
            new_border_style = re.sub(stroke_color_regex, f'stroke:{color};', new_border_style)
            element.set('style', new_border_style)

    # change the color of the text if present
    napari_text = root.find(napari_text_xpath, namespaces=namespace)
    if napari_text is not None:
        new_text_style = re.sub(fill_color_regex, f'fill:{color};', napari_text.get('style'))
        napari_text.set('style', new_text_style)


def copy_defs(orig, dest):
    """Copy definitions (filters etc) from one svg root to another."""
    orig_defs = orig.find(".//svg:defs", namespaces=namespace)
    dest_defs = dest.find(".//svg:defs", namespaces=namespace)

    for el in orig_defs:
        dest_defs.append(copy.deepcopy(el))


def generate_variants(new_logo_path, border_color_dark):
    """Generate all logo variants based on a new logo.

    NEW_LOGO_PATH: the path of the new logo to use to generate. Should be
        normally placed in the `variants` directory.
    BORDER_COLOR_DARK: color (hex) to use for the border and text in the dark mode.
    """

    template_dir = Path(__file__).parent.parent / 'logo' / 'templates'

    # extract the new logo and color
    new_logo_path = Path(new_logo_path)
    new_logo_root = etree.parse(new_logo_path).getroot()
    new_logo = new_logo_root.find(logo_xpath, namespaces=namespace)
    new_border = new_logo_root.find(border_xpath, namespaces=namespace)
    border_color_light = re.search(fill_color_regex, new_border.get('style')).group(1)
    if not border_color_dark.startswith('#'):
        border_color_dark = '#' + border_color_dark

    colors = {'-light': border_color_light, '-dark': border_color_dark}
    variants = {
        template_path.stem.removeprefix('logo'): template_path
        for template_path in template_dir.glob('*.svg')
    }

    for variant, template_path in variants.items():
        for theme, color in colors.items():
            # find the logo and replace it with the new one
            template_tree = etree.parse(template_path)
            template_root = template_tree.getroot()
            template_logo = template_root.find(logo_xpath, namespaces=namespace)
            template_logo.getparent().replace(template_logo, copy.deepcopy(new_logo))

            change_border_color(template_root, color)
            copy_defs(new_logo_root, template_root)

            # generate outputs
            output_svg = template_dir.parent / 'generated' / f'{new_logo_path.stem}{variant}{theme}.svg'
            output_svg.parent.mkdir(parents=True, exist_ok=True)
            template_tree.write(output_svg, pretty_print=True, xml_declaration=True, encoding="utf-8")
            print(f'Generated {output_svg.stem}.')


@click.command()
@click.option('-o', '--only')
def cli(only):
    logo_variants = Path(__file__).parent.parent / 'logo' / 'variants'

    # NOTE: these colors should be without alpha, otherwise for some reason inkscape
    #       fucks up and you end up with a random graident instead of a fill O.o
    dark_variant_colors = {
        'logo-gradient': 'ccb98f',
        'logo-flat': 'ccb98f',
        'logo-halloween': 'cdd7db',
        'logo-christmas': 'e3c300',
        'logo-japan': '83be1e',
    }

    if only is not None:
        dark_variant_colors = {only: dark_variant_colors.get(only)}

    for variant, dark_color in dark_variant_colors.items():
        path = logo_variants / f'{variant}.svg'
        generate_variants(path, dark_color)


if __name__ == '__main__':
    cli()
