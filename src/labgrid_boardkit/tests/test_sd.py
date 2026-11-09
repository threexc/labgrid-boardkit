"""Shared SD-mux boot smoke tests. Auto-skipped for boards whose strategy
isn't an SdMuxBootStrategy (see ``sd`` fixture in ``labgrid_boardkit.fixtures``).
"""

import os

from labgrid.driver import ExecutionError

from labgrid_boardkit import helpers


def test_uname_a(sd):
    version = os.environ.get("VERSION")
    try:
        state = sd.run_check("/bin/uname -a", timeout=60.0)

        assert helpers.kernel_version_in(version, state[0]), state[0]
    except ExecutionError:
        sd.run("ls /bin/uname")
        raise


def test_buildinfo(sd):
    try:
        sd.run_check("cat /etc/buildinfo", timeout=60.0)
    except ExecutionError:
        sd.run("ls /etc/")
        raise
