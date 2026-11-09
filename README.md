# labgrid-boardkit

Board manifests, boot strategies, pytest fixtures and test suites for
[labgrid](https://github.com/labgrid-project/labgrid).

Describe a board once in a `board.yaml` manifest, and labgrid-boardkit
generates its labgrid `client.yaml` and drives it through a reusable boot
strategy family:

| Family     | Boots via                                   |
|------------|---------------------------------------------|
| `tftp`     | U-Boot `tftpboot` (kernel, DTB, initramfs/FIT) |
| `sdmux`    | an SD card image written through a USB-SD-Mux |
| `fastboot` | images flashed to eMMC/NOR over fastboot    |
| `qemu`     | QEMU, no hardware needed                    |

## Install

```
pip install labgrid-boardkit
```

## Usage

Lay out your boards as `boards/<name>/board.yaml`. Shared settings can go in
a file listed under `inherits:`. For example (`tests/fixtures/boards/` has one
board per family, plus a shared `families/` file and a variant):

```yaml
name: example-qemu
yocto_machine: qemuriscv64
strategy: qemu
arch: riscv64
description: QEMU RISC-V virt machine, no hardware needed

boot:
  bootargs: root=/dev/vda rw console=ttyS0

qemu:
  binary: qemu-system-riscv64
  machine: virt
  cpu: rv64
  memory: 2048
  ssh_port: 2222
  telnet_port: 2323

images:
  bios: /srv/images/example-qemu/fw_jump.elf
  kernel: /srv/images/example-qemu/Image
  ext4: /srv/images/example-qemu/rootfs.ext4

shell:
  username: root
```

From the directory that contains `boards/`:

```
boardkit-validate          # check every boards/*/board.yaml against the schema
boardkit-render            # write each board's client.yaml/env.yaml and boards/machines.tsv
boardkit-render --check    # exit 1 if any rendered file is out of date (for CI)
```

Installing the package also registers a pytest plugin. It picks `--lg-env`
from `$BOARD` or the nearest `client.yaml`, and provides the `tftp`, `sd` and
`fastboot` fixtures. Generic on-target suites ship with the package:

```
BOARD=boards/my-board pytest --pyargs labgrid_boardkit.tests
pytest --lg-env boards/example-qemu/env.yaml --pyargs labgrid_boardkit.ptest
```

## Adding a strategy family

Families are found through the `labgrid_boardkit.strategies` entry-point
group, so another package can add one without changing this one:

```toml
[project.entry-points."labgrid_boardkit.strategies"]
myfamily = "my_package.strategies:MyBootStrategy"
```

## Development

```
uv run pytest
uv run ruff check . && uv run ruff format --check .
```
