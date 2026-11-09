"""Shared fixtures for labgrid_boardkit unit tests.

These tests exercise pure-Python logic only (manifest merging, template
rendering, strategy registry, strategy state machines) with no labgrid
target/hardware required, so they can run in plain CI without a board.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
# Synthetic example boards, one per strategy family, with their rendered
# outputs committed alongside so the render/validate round-trip is covered.
BOARDS_DIR = REPO_ROOT / "tests" / "fixtures" / "boards"
EXAMPLE_BOARDS = sorted(p.parent.name for p in BOARDS_DIR.glob("*/board.yaml"))


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def boards_dir() -> Path:
    return BOARDS_DIR
