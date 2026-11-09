"""Minimal YMODEM sender (one file, 1K blocks, CRC-16), for handing a boot
image to a loader waiting on the serial console, e.g. a U-Boot SPL built with
SPL_YMODEM_SUPPORT.
"""

import binascii
import time

SOH, STX, EOT, ACK, NAK, CAN, CRC = b"\x01", b"\x02", b"\x04", b"\x06", b"\x15", b"\x18", b"C"


class YmodemError(Exception):
    pass


def _packet(seq: int, payload: bytes, size: int) -> bytes:
    # Block 0 (the file header) pads with NULs, data blocks with SUB (0x1a).
    payload = payload.ljust(size, b"\x1a" if seq else b"\0")
    seq &= 0xFF
    return (
        (SOH if size == 128 else STX)
        + bytes([seq, 0xFF - seq])
        + payload
        + binascii.crc_hqx(payload, 0).to_bytes(2, "big")
    )


def send(getc, putc, name: str, data: bytes, timeout: float = 10.0, retries: int = 10):
    """Send ``data`` as file ``name``.

    ``getc(timeout)`` returns one byte, or b"" if none arrived in time;
    ``putc(bytes)`` writes. Bytes the receiver prints that aren't protocol
    replies (log output, repeated "C"s) are skipped.
    """

    def wait(wanted, t=timeout):
        deadline = time.monotonic() + t
        while (left := deadline - time.monotonic()) > 0:
            c = getc(left)
            if c in wanted:
                return c
        return b""

    def send_packet(pkt):
        for _ in range(retries):
            putc(pkt)
            c = wait((ACK, NAK, CAN))
            if c == ACK:
                return
            if c == CAN:
                raise YmodemError("receiver cancelled the transfer")
        raise YmodemError(f"block {pkt[1]} not acknowledged after {retries} tries")

    # The receiver asks for CRC mode by sending "C" until a sender starts.
    if not wait((CRC,), 60.0):
        raise YmodemError("receiver never asked for a transfer")
    send_packet(_packet(0, f"{name}\0{len(data)}".encode(), 128))
    wait((CRC,))  # receiver asks again before the data blocks
    for i in range(0, len(data), 1024):
        send_packet(_packet(i // 1024 + 1, data[i : i + 1024], 1024))

    putc(EOT)
    if wait((ACK, NAK)) == NAK:  # the classic EOT handshake NAKs the first one
        putc(EOT)
        wait((ACK,))
    # End the batch with an empty header, if the receiver still listens: a
    # loader that has what it needs may already have moved on.
    if wait((CRC,), 2.0):
        putc(_packet(0, b"", 128))
        wait((ACK,), 2.0)
