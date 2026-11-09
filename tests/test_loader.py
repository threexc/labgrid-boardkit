import pytest

from labgrid_boardkit.loader import UnknownStrategy, available_strategies, strategy_for
from labgrid_boardkit.strategies.fastboot import FastbootFlashStrategy
from labgrid_boardkit.strategies.qemu import QemuBootStrategy
from labgrid_boardkit.strategies.sdmux import SdMuxBootStrategy
from labgrid_boardkit.strategies.tftp import TftpBootStrategy


def test_available_strategies_lists_builtin_families():
    strategies = available_strategies()
    assert strategies["tftp"] == "labgrid_boardkit.strategies.tftp:TftpBootStrategy"
    assert strategies["sdmux"] == "labgrid_boardkit.strategies.sdmux:SdMuxBootStrategy"
    assert strategies["fastboot"] == "labgrid_boardkit.strategies.fastboot:FastbootFlashStrategy"
    assert strategies["qemu"] == "labgrid_boardkit.strategies.qemu:QemuBootStrategy"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("tftp", TftpBootStrategy),
        ("sdmux", SdMuxBootStrategy),
        ("fastboot", FastbootFlashStrategy),
        ("qemu", QemuBootStrategy),
    ],
)
def test_strategy_for_resolves_registered_families(name, expected):
    assert strategy_for({"strategy": name}) is expected


def test_strategy_for_missing_key_raises():
    with pytest.raises(UnknownStrategy, match="missing"):
        strategy_for({})


def test_strategy_for_unregistered_name_raises():
    with pytest.raises(UnknownStrategy, match="not registered"):
        strategy_for({"strategy": "does-not-exist"})
