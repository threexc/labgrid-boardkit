import binascii
import time

import pytest

from labgrid_boardkit import ymodem


def _run(replies, data, name="u-boot.itb"):
    """Send ``data`` to a receiver that answers with ``replies``, one per
    getc call (b"" is a timeout); return the packets written."""
    replies = iter(replies)
    written = []

    def getc(t):
        c = next(replies, None)
        if c is None:  # out of replies: time out like a quiet line
            time.sleep(t)
            return b""
        return c

    ymodem.send(getc, written.append, name, data, timeout=0.01)
    return written


def _check(pkt, size):
    payload = pkt[3 : 3 + size]
    assert pkt[1] == 0xFF - pkt[2]
    assert pkt[3 + size :] == binascii.crc_hqx(payload, 0).to_bytes(2, "big")
    return pkt[1], payload


def test_send_skips_noise_retries_nak_and_reassembles():
    data = bytes(range(256)) * 10  # 2560 bytes: three 1K blocks
    replies = [b"U", b"C", b"C", b"\x06", b"C"]  # log noise, then block 0
    replies += [b"\x06", b"\x15", b"\x06", b"\x06"]  # block 2 is NAKed once
    replies += [b"\x15", b"\x06"]  # EOT, EOT
    written = _run(replies, data)

    seq, header = _check(written[0], 128)
    assert seq == 0
    assert header.rstrip(b"\0") == b"u-boot.itb\x002560"
    blocks = [_check(p, 1024) for p in written[1:5]]
    assert [s for s, _ in blocks] == [1, 2, 2, 3]
    assert b"".join(p for _, p in blocks[:2] + blocks[3:]).rstrip(b"\x1a") == data
    assert written[5:] == [ymodem.EOT, ymodem.EOT]


def test_send_raises_on_cancel():
    with pytest.raises(ymodem.YmodemError, match="cancelled"):
        _run([b"C", b"\x18"], b"x")
