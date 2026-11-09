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
a file listed under `inherits:`. For example (more, one per family, in
`tests/fixtures/boards/`):

```yaml
name: qemuriscv64
yocto_machine: qemuriscv64
strategy: qemu
arch: riscv64
description: QEMU RISC-V 64 virt machine. Yocto image, no physical hardware

boot:
  method: qemu
  bootargs: root=/dev/vda rw console=ttyS0 earlycon

qemu:
  binary: qemu-system-riscv64
  machine: virt
  cpu: rva23s64
  memory: 8192
  ssh_port: 2222
  telnet_port: 2323

images:
  bios: /home/labgrid/fw_jump.elf
  kernel: /home/labgrid/Image
  ext4: /home/labgrid/ptest_image.ext4

shell:
  username: root
  password: null

strategy_class: QEMUYoctoStrategy
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
pytest --lg-env boards/qemuriscv64/env.yaml --pyargs labgrid_boardkit.ptest
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
