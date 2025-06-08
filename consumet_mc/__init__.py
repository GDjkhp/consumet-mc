from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .providers import Kisskh, HiAnime

plugin: PluginHookData = {
    "version": 1,
    "package_name": "consumet-mc",  # Required for the plugin update checker.
    "scrapers": {"hianime": HiAnime, "kisskh": Kisskh, "DEFAULT": HiAnime},
}

__version__ = "1.0.0"
