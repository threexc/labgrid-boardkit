"""labgrid-boardkit strategy families.

Import the family classes from here or (preferred at scale) resolve them by
name via ``labgrid_boardkit.loader.strategy_for(manifest)``, which consults
the ``labgrid_boardkit.strategies`` entry-point registry declared in ``pyproject.toml``.
"""

from labgrid_boardkit.strategies.base import BoardStrategy
from labgrid_boardkit.strategies.fastboot import FastbootFlashStrategy, FastbootStatus
from labgrid_boardkit.strategies.qemu import ExternalQemuStrategy, QemuBootStrategy, QemuStatus
from labgrid_boardkit.strategies.sdmux import SdMuxBootStrategy, SdMuxStatus
from labgrid_boardkit.strategies.tftp import TftpBootStrategy, TftpStatus

__all__ = [
    "BoardStrategy",
    "ExternalQemuStrategy",
    "FastbootFlashStrategy",
    "FastbootStatus",
    "QemuBootStrategy",
    "QemuStatus",
    "SdMuxBootStrategy",
    "SdMuxStatus",
    "TftpBootStrategy",
    "TftpStatus",
]
