#!/usr/bin/env python3

# /// script
# dependencies = [
#   "click",
#   "lxml",
#   "sh",
# ]
# ///

import click
from pathlib import Path
import re
import copy
import sh
import shutil

from lxml import etree

# NOTE: these colors should be without alpha, otherwise for some reason inkscape
#       fucks up and you end up with a random graident instead of a fill O.o
DARK_VARIANT_COLORS = {
    'gradient': 'ccb98f',
    'flat': 'ccb98f',
    'round': 'ccb98f',
    'halloween': 'cdd7db',
    'christmas': 'e3c300',
    'jedi': '00b6e1',
    'sith': '00b6e1',
    'pride': 'f4b0c9',
    'mochi': '83be1e',
}


fill_color_regex = r'fill:(#.*?);'
stroke_color_regex = r'stroke:(#.*?);'
logo_xpath = ".//*[@inkscape:label='logo']"
napari_text_xpath = ".//*[@inkscape:label='napari']"
border_xpath = ".//*[@inkscape:label='outer-border']"
namespace = {
    "svg": "http://www.w3.org/2000/svg",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape"
}


TEMPLATE_DIR = Path(__file__).parent.parent / 'logo' / 'templates'
TEMPLATE_FILES = {
    template_path.stem: template_path
    for template_path in TEMPLATE_DIR.glob('*.svg')
}
GENERATED_DIR = TEMPLATE_DIR.parent / 'generated'

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


def generate_variants(new_logo_path, border_color_dark, templates=None, modes=None, png=False, icons=False):
    """Generate all logo variants based on a new logo.

    NEW_LOGO_PATH: the path of the new logo to use to generate. Should be
        normally placed in the `variants` directory.
    BORDER_COLOR_DARK: color (hex) to use for the border and text in the dark mode.
    """

    # extract the new logo and color
    new_logo_path = Path(new_logo_path)
    new_logo_root = etree.parse(new_logo_path).getroot()
    new_logo = new_logo_root.find(logo_xpath, namespaces=namespace)
    new_border = new_logo_root.find(border_xpath, namespaces=namespace)
    border_color_light = re.search(fill_color_regex, new_border.get('style')).group(1)
    if not border_color_dark.startswith('#'):
        border_color_dark = '#' + border_color_dark

    mode_colors = {'light': border_color_light, 'dark': border_color_dark}

    for template, template_path in TEMPLATE_FILES.items():
        if templates and template not in templates:
            continue
        for mode, color in mode_colors.items():
            if modes and mode not in modes:
                continue
            # find the logo and replace it with the new one
            template_tree = etree.parse(template_path)
            template_root = template_tree.getroot()
            template_logo = template_root.find(logo_xpath, namespaces=namespace)
            template_logo.getparent().replace(template_logo, copy.deepcopy(new_logo))

            change_border_color(template_root, color)
            copy_defs(new_logo_root, template_root)

            # generate outputs
            output_svg = GENERATED_DIR / f'{new_logo_path.stem}-{template}-{mode}.svg'
            output_svg.parent.mkdir(parents=True, exist_ok=True)
            template_tree.write(output_svg, pretty_print=True, xml_declaration=True, encoding="utf-8")
            if png:
                sh.inkscape(output_svg, '-o', output_svg.with_suffix('.png'))
            if icons:
                # windows ico file is simple
                sh.convert(output_svg, '-define', 'icon:auto-resize=256,64,48,32,16', output_svg.with_suffix('.ico'))
                # we need to actually create all the png size variants for macos
                tmp_icns_dir = GENERATED_DIR / 'icns'
                tmp_icns_dir.mkdir(exist_ok=True)
                for size in (16, 32, 128, 256, 512):
                    sh.inkscape(output_svg, '-w', size, '-h', size, '-d', 77, tmp_icns_dir / f'{size}x{size}.png')
                    # for retina
                    sh.inkscape(output_svg, '-w', size * 2, '-h', size * 2, '-d', 144, tmp_icns_dir / f'{size}x{size}@2x.png')
                sh.png2icns(output_svg.with_suffix('.icns'), [str(p) for p in tmp_icns_dir.iterdir()])
                shutil.rmtree(tmp_icns_dir)
            print(f'Generated {output_svg.stem}')



@click.command(
    context_settings={"help_option_names": ["-h", "--help"], "show_default": True},
)
@click.option('-v', '--variant', type=click.Choice(DARK_VARIANT_COLORS), multiple=True)
@click.option('-t', '--template', type=click.Choice(TEMPLATE_FILES), multiple=True)
@click.option('-m', '--mode', type=click.Choice(('light', 'dark')), multiple=True)
@click.option('-p', '--png', is_flag=True, help='Also generate as png (requires inkscape).')
@click.option('-i', '--icons', is_flag=True, help='Also generate icons (requires icnsutils).')
@click.option('--montage', is_flag=True, help='Generate a montage with all available pngs (requires imagemagick).')
def cli(variant, template, mode, png, icons, montage):
    """Generate logos based on variants, template and theme.

    Options may be passed more than once. An empty option means all.
    """
    logo_variants = Path(__file__).parent.parent / 'logo' / 'variants'

    for variant_name, dark_color in DARK_VARIANT_COLORS.items():
        if variant and variant_name not in variant:
            continue
        path = logo_variants / f'{variant_name}.svg'
        generate_variants(path, dark_color, template, mode, png, icons)

    if montage:
        sh.montage('*plain-dark.png', '-geometry', '+100+100', '-background', 'black', 'montage-dark.png', _cwd=GENERATED_DIR)
        sh.montage('*plain-light.png', '-geometry', '+100+100', '-background', 'white', 'montage-light.png', _cwd=GENERATED_DIR)
        sh.montage('montage-*.png', '-geometry', '+0+0', '-tile', '1x', 'montage.png', _cwd=GENERATED_DIR)
        (GENERATED_DIR / 'montage-dark.png').unlink()
        (GENERATED_DIR / 'montage-light.png').unlink()


if __name__ == '__main__':
    cli()
