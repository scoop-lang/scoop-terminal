#!/usr/bin/env python3
"""Generate the tiny PNG protocol/CPU-codec fixtures using only Python's standard library."""
from pathlib import Path
import argparse
import struct
import zlib


ROOT = Path(__file__).resolve().parents[1]
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))


def header(width: int, height: int, depth: int, color: int, interlace: int = 0) -> bytes:
    return chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, depth, color, 0, 0, interlace))


def png(ihdr: bytes, pixels: bytes, extra: bytes = b"") -> bytes:
    return SIGNATURE + ihdr + extra + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


def fixtures() -> dict[str, bytes]:
    rgba = bytes((255, 0, 0, 255, 0, 255, 0, 128, 0, 0, 255, 64,
                  0, 0, 0, 0, 255, 255, 255, 255, 0, 0, 0, 128))
    raw = b"\0" + rgba[:12] + b"\0" + rgba[12:]
    ihdr = header(3, 2, 8, 6)
    result = {
        "rgba.png": png(ihdr, raw),
        "rgba.pixels": rgba,
        "palette.png": png(header(3, 1, 2, 3), b"\0\x18",
                           chunk(b"PLTE", bytes((255, 0, 0, 0, 255, 0, 0, 0, 255))) +
                           chunk(b"tRNS", bytes((255, 128, 64)))),
        "palette.pixels": rgba[:12],
        "gray16.png": png(header(2, 1, 16, 0), b"\0\0\0\xff\xff"),
        "gray16.pixels": bytes((0, 0, 0, 255, 255, 255, 255, 255)),
        "truncated-deflate.png": SIGNATURE + ihdr + chunk(b"IDAT", zlib.compress(raw)[:-6]) + chunk(b"IEND", b""),
        "short-pixels.png": png(ihdr, raw[:13]),
        "bad-filter.png": png(ihdr, b"\5" + raw[1:]),
        "huge.png": png(header(0xffffffff, 0xffffffff, 8, 6), b""),
        "no-iend.png": png(ihdr, raw)[:-12],
        "unknown-critical.png": png(ihdr, raw, chunk(b"WXYZ", b"")),
        "ancillary.png": png(ihdr, raw, chunk(b"tEXt", b"fixture\0generated locally")),
        "animated.png": png(ihdr, raw, chunk(b"acTL", struct.pack(">II", 1, 0))),
        "duplicate-ihdr.png": png(ihdr, raw, ihdr),
        "trailing.png": png(ihdr, raw) + b"trailing",
        "no-palette.png": png(header(3, 1, 2, 3), b"\0\x18"),
        "bad-chunk-length.png": SIGNATURE + ihdr + struct.pack(">I", 0xffffffff) + b"IDAT0000",
    }
    broken = bytearray(result["rgba.png"])
    broken[-15] ^= 1
    result["bad-crc.png"] = bytes(broken)
    # Adam7, 5x5: exercises passes with different dimensions and omitted empty passes.
    pixels = bytes(channel for y in range(5) for x in range(5)
                   for channel in (255 if x % 2 else 0, 255 if y % 2 else 0, 255, 128 if x == y else 255))
    passes = bytearray()
    for start_x, start_y, step_x, step_y in ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8),
                                            (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)):
        for y in range(start_y, 5, step_y):
            row = b"".join(pixels[(y * 5 + x) * 4:(y * 5 + x + 1) * 4] for x in range(start_x, 5, step_x))
            if row:
                passes += b"\0" + row
    result["adam7.png"] = png(header(5, 5, 8, 6, 1), bytes(passes))
    result["adam7.pixels"] = pixels
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    core_only = {"huge.png", "no-iend.png", "unknown-critical.png", "ancillary.png",
                 "animated.png", "duplicate-ihdr.png", "trailing.png", "no-palette.png",
                 "bad-chunk-length.png", "bad-crc.png"}
    codec_only = {"truncated-deflate.png", "short-pixels.png", "bad-filter.png"}
    for cone in ("emulator", "terminal-ui"):
        directory = ROOT / cone / "tests" / "data" / "images"
        if not args.check:
            directory.mkdir(parents=True, exist_ok=True)
        for name, data in fixtures().items():
            destination = directory / name
            wanted = (name not in codec_only and not name.endswith(".pixels")) if cone == "emulator" else name not in core_only
            if not wanted:
                if not args.check:
                    destination.unlink(missing_ok=True)
                continue
            if args.check:
                if not destination.exists() or destination.read_bytes() != data:
                    raise SystemExit(f"fixture differs: {destination}")
            else:
                destination.write_bytes(data)


if __name__ == "__main__":
    main()
