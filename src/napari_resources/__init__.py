"""Napari resources such as logos."""

from __future__ import annotations

# `importlib.resources` is aliased to `_resources`: this package contains a
# subpackage also named `resources`, and importing it would overwrite the plain
# `resources` name on this module (a classic name clash).
from importlib import resources as _resources
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.abc import Traversable

__all__ = ["logo_path", "logo_templates", "logo_variants"]

logos_dir = _resources.files("napari_resources.resources.logos")


def logo_path(name: str) -> Traversable:
    """Return the path to a generated logo SVG.

    Parameters
    ----------
    name : str
        Filename of the generated logo, e.g. ``"gradient-plain-dark.svg"``.

    Returns
    -------
    Traversable
        Path-like handle to the logo. The generated SVGs are produced at build
        time (see ``hatch_build.py``), so this works for both installed wheels
        and editable installs.

    Raises
    ------
    FileNotFoundError
        If the generated asset is not present, e.g. the package was not built
        (or the working tree is a fresh checkout).
    """
    path = logos_dir / "generated" / name
    if not path.is_file():
        raise FileNotFoundError(
            f"Generated logo {name!r} not found at {path}. "
            "The SVGs are produced at build time; reinstall the package "
            "(e.g. `pip install -e .` or `uv sync --reinstall-package "
            "napari-resources`) or run the generator "
            "(`python -m napari_resources.generate_logos <dest_dir>`) first."
        )
    return path


def logo_variants() -> list[str]:
    """List the available logo variant names (e.g. ``"gradient"``).

    These are the ``<variant>`` components of generated filenames, e.g.
    ``"gradient-plain-dark.svg"``.
    """
    variants = _resources.files("napari_resources.resources.logos.variants")
    return sorted(p.name.removesuffix(".svg") for p in variants.iterdir() if p.name.endswith(".svg"))


def logo_templates() -> list[str]:
    """List the available logo template names (e.g. ``"plain"``).

    These are the ``<template>`` components of generated filenames, e.g.
    ``"gradient-plain-dark.svg"``.
    """
    templates = _resources.files("napari_resources.resources.logos.templates")
    return sorted(p.name.removesuffix(".svg") for p in templates.iterdir() if p.name.endswith(".svg"))
