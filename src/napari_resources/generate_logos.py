#!/usr/bin/env python3

# /// script
# dependencies = [
#   "click",
#   "lxml",
#   "sh",
# ]
# ///

"""Tool to generate all the napari logo variations."""

import copy
import re
import shutil
from importlib import resources
from itertools import product
from pathlib import Path

import click
import sh
from lxml import etree

# NOTE: these colors should be without alpha, otherwise for some reason inkscape
#       fucks up and you end up with a random graident instead of a fill O.o
DARK_VARIANT_COLORS = {
    "christmas": "e3c300",
    "flat": "ccb98f",
    "gradient": "ccb98f",
    "halloween": "cdd7db",
    "jedi": "00b6e1",
    "mochi": "83be1e",
    "pierogi": "dd0c39",
    "pride": "f4b0c9",
    "round": "ccb98f",
    "sith": "00b6e1",
    "workshop": "ccb98f",
    "outline": "ffffff",
}


fill_color_regex = r"fill:(#.*?);"
stroke_color_regex = r"stroke:(#.*?);"
logo_xpath = ".//*[@inkscape:label='logo']"
napari_text_xpath = ".//*[@inkscape:label='napari']"
border_xpath = ".//*[@inkscape:label='outer-border']"
namespace = {
    "svg": "http://www.w3.org/2000/svg",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape",
}


TEMPLATE_DIR = resources.files("napari-resources.resources.logos.templates")
VARIANT_DIR = resources.files("napari-resources.resources.logos.variants")

TEMPLATE_FILES = {
    template_path.stem: template_path
    for template_path in TEMPLATE_DIR.iterdir()  # type: ignore
}
VARIANT_FILES = {
    variant_path.stem: variant_path
    for variant_path in VARIANT_DIR.iterdir()  # type: ignore
}


def _change_border_color(root, color):
    """Replace outer-border's color with the given color in an svg document."""
    # change the color of the border
    # this affects anything labeled as `outer-border` as well as children nodes
    base_logo_border = root.findall(border_xpath, namespaces=namespace)
    for border in base_logo_border:
        for element in (border, *border.getchildren()):
            if not element.get("style"):
                continue
            new_border_style = re.sub(fill_color_regex, f"fill:{color};", element.get("style"))
            new_border_style = re.sub(stroke_color_regex, f"stroke:{color};", new_border_style)
            element.set("style", new_border_style)

    # change the color of the text if present
    napari_text = root.find(napari_text_xpath, namespaces=namespace)
    if napari_text is not None:
        new_text_style = re.sub(fill_color_regex, f"fill:{color};", napari_text.get("style"))
        napari_text.set("style", new_text_style)


def _copy_defs(orig, dest):
    """Copy definitions (filters etc) from one svg root to another."""
    orig_defs = orig.find(".//svg:defs", namespaces=namespace)
    dest_defs = dest.find(".//svg:defs", namespaces=namespace)

    for el in orig_defs:
        dest_defs.append(copy.deepcopy(el))


def generate_single_logo(variant, template, mode, output_dir, png=False, icons=False):
    """Generate a single logo combination."""
    if variant in VARIANT_FILES:
        variant_path = VARIANT_FILES[variant]
    else:
        variant_path = Path(variant)
        if not variant_path.is_file() or variant_path.suffix != ".svg":
            raise ValueError(f"variant must be either one of {set(VARIANT_FILES)} or a valid svg file. Got {variant}")
        variant = variant_path.stem
    if template in TEMPLATE_FILES:
        template_path = TEMPLATE_FILES[template]
    else:
        template_path = Path(template)
        if not template_path.is_file() or template_path.suffix != ".svg":
            raise ValueError(
                f"template must be either one of {set(TEMPLATE_FILES)} or a valid svg file. Got {template}"
            )
        template = template_path.stem

    if mode == "light":
        color = None
    elif mode == "dark":
        color = DARK_VARIANT_COLORS.get(variant, None)
    elif mode.startswith("#") and len(mode) == 7:
        color = mode
        mode = "custom"
    else:
        raise ValueError(f"mode must be either light or dark, or a valid hex color code. Got {mode}")

    # extract the variant logo and color
    variant_root = etree.parse(variant_path).getroot()
    variant_logo = variant_root.find(logo_xpath, namespaces=namespace)

    # find the logo and replace it with the new one
    new_tree = etree.parse(template_path)
    new_root = new_tree.getroot()
    new_logo = new_root.find(logo_xpath, namespaces=namespace)
    new_logo.getparent().replace(new_logo, copy.deepcopy(variant_logo))

    if mode != "light":
        _change_border_color(new_root, color)
    _copy_defs(variant_root, new_root)

    # generate outputs
    output_svg = output_dir / f"{variant}-{template}-{mode}.svg"
    output_svg.parent.mkdir(parents=True, exist_ok=True)
    new_tree.write(output_svg, pretty_print=True, xml_declaration=True, encoding="utf-8")
    if png:
        sh.inkscape(output_svg, "-o", output_svg.with_suffix(".png"))
    if icons:
        if template == "plain":
            # windows ico file is simple
            sh.convert(
                "-resize",
                "256x256",
                "-define",
                "icon:auto-resize",
                "-colors",
                256,
                "-background",
                "none",
                output_svg,
                output_svg.with_suffix(".ico"),
            )
        if template == "padded":
            # macos: we need to actually create all the png size variants
            # and pass them to png2icns
            tmp_icns_dir = output_dir / "icns"
            tmp_icns_dir.mkdir(exist_ok=True)
            for size in (16, 32, 128, 256, 512, 1024):
                sh.inkscape(
                    output_svg,
                    "-w",
                    size,
                    "-h",
                    size,
                    "-d",
                    77,
                    "-o",
                    tmp_icns_dir / f"{size}x{size}.png",
                )
            sh.png2icns(
                output_svg.with_suffix(".icns"),
                [str(p) for p in tmp_icns_dir.iterdir()],
            )
            shutil.rmtree(tmp_icns_dir)

    return output_svg


@click.command(
    context_settings={"help_option_names": ["-h", "--help"], "show_default": True},
)
@click.argument(
    "output_dir",
    type=click.Path(exists=True, file_okay=False),
)
@click.option(
    "-v",
    "--variant",
    "selected_variants",
    type=str,
    multiple=True,
    help=f"Logo variant to use. Can be either a custom svg path, or one of: {set(VARIANT_FILES)}",
)
@click.option(
    "-t",
    "--template",
    "selected_templates",
    type=str,
    multiple=True,
    help=f"Logo template to use. Can be either a custom svg path, or one of: {set(TEMPLATE_FILES)}",
)
@click.option(
    "-m",
    "--mode",
    "selected_modes",
    type=str,
    multiple=True,
    help='Logo mode to generate. Can be either "light" (uses variant base color),'
    '"dark" (must be in the hardcoded mapping), or a custom hex color code (e.g: #a0a0a0)',
)
@click.option("-p", "--png", is_flag=True, help="Also generate as png (requires inkscape).")
@click.option("-i", "--icons", is_flag=True, help="Also generate icons (requires icnsutils).")
@click.option(
    "--montage",
    is_flag=True,
    help="Generate a montage with all available pngs (requires imagemagick).",
)
@click.option("-q", "--quiet", is_flag=True, help="Do not print progress.")
def generate_logos(
    output_dir,
    selected_variants=(),
    selected_templates=(),
    selected_modes=(),
    png=False,
    icons=False,
    montage=False,
    quiet=True,
):
    """Generate logos based on variants, template and theme.

    Template, variant and mode options may be passed more than once.
    An empty option means all.
    """
    output_dir = Path(output_dir)
    selected_templates = selected_templates or list(TEMPLATE_FILES)
    selected_variants = selected_variants or list(VARIANT_FILES)
    selected_modes = selected_modes or ("light", "dark")

    for variant, template, mode in product(selected_variants, selected_templates, selected_modes):
        generated_svg = generate_single_logo(
            variant=variant,
            template=template,
            mode=mode,
            output_dir=output_dir,
            png=png,
            icons=icons,
        )
        if not quiet:
            print(f"Generated {generated_svg.stem}")

    if montage:
        sh.montage(
            "*plain-dark.png",
            "-geometry",
            "+100+100",
            "-background",
            "black",
            "montage-dark.png",
            _cwd=str(output_dir),
        )
        sh.montage(
            "*plain-light.png",
            "-geometry",
            "+100+100",
            "-background",
            "white",
            "montage-light.png",
            _cwd=str(output_dir),
        )
        sh.montage(
            "montage-*.png",
            "-geometry",
            "+0+0",
            "-tile",
            "1x",
            "montage.png",
            _cwd=str(output_dir),
        )
        (output_dir / "montage-dark.png").unlink()
        (output_dir / "montage-light.png").unlink()


if __name__ == "__main__":
    generate_logos()
