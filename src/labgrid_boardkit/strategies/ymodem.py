from pathlib import Path

import attr
from pexpect import TIMEOUT

from labgrid_boardkit import ymodem
from labgrid_boardkit.strategies.fastboot import FastbootFlashStrategy
from labgrid_boardkit.strategies.tftp import TftpBootStrategy


@attr.s(eq=False)
class YmodemBootStrategy(TftpBootStrategy):
    """TFTP-boot a board whose U-Boot can't be loaded from its own storage.

    The board is put into USB download mode (as for ``FastbootFlashStrategy``)
    and each ``fastboot.stage`` image, e.g. an SPL built with YMODEM support,
    is staged and continued. ``ymodem.image`` (e.g. u-boot.itb) is then sent
    to it over the serial console, and the U-Boot it starts TFTP-boots the
    kernel like ``TftpBootStrategy``. Nothing is flashed. Image paths are
    relative to ``fastboot.image_dir``.
    """

    bindings = {
        **TftpBootStrategy.bindings,
        "fastboot": "AndroidFastbootDriver",
        "recovery": "DigitalOutputProtocol",
        "reset": "DigitalOutputProtocol",
    }

    # Download mode and staging work as for a fastboot-flashed board.
    _image = FastbootFlashStrategy._image
    _enter_download_mode = FastbootFlashStrategy._enter_download_mode
    _stage_image = FastbootFlashStrategy._stage_image
    _load_stages = FastbootFlashStrategy._load_stages

    def _getc(self, timeout: float) -> bytes:
        # The console driver's private read/write: its public ones log every
        # byte, which for a ~1 MB transfer buries the test log.
        try:
            return self.console._read(size=1, timeout=timeout, max_size=1)
        except TIMEOUT:
            return b""

    def _power_on(self):
        self._load_stages()
        self.target.deactivate(self.fastboot)
        path = Path(self._image(self.manifest["ymodem"]["image"]))
        ymodem.send(self._getc, self.console._write, path.name, path.read_bytes())
