#!/usr/bin/env python3
"""Read a GGUF's tensor table and draw it as an ASCII die.

Two steps, both honest:
1. The byte size of every tensor comes from the difference between consecutive
   data offsets in the file, so nothing is assumed about quantisation.
2. The die image is drawn from those numbers: rows are tensor roles, columns are
   blocks, darkness is log(bytes). The drawing is then sampled into glyphs.
"""

from __future__ import annotations

import math
import struct
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

RAMP = " .:-=+*#%@"

# GGUF metadata value types (v2+ enum: uint8 first, string is 8, array is 9)
_U8, _I8, _U16, _I16, _U32, _I32, _F32 = 0, 1, 2, 3, 4, 5, 6
_BOOL, _STR, _ARR, _U64, _I64, _F64 = 7, 8, 9, 10, 11, 12


def _kv(f, t):
    """Read one metadata value; arrays and strings are skipped, not parsed."""
    if t in (_STR,):
        n = struct.unpack("<Q", f.read(8))[0]
        return f.read(n)
    if t in (_U8, _I8, _BOOL):
        return f.read(1)
    if t in (_U16, _I16):
        return f.read(2)
    if t in (_U32, _I32, _F32):
        return f.read(4)
    if t in (_U64, _I64, _F64):
        return f.read(8)
    if t == _ARR:
        it = struct.unpack("<I", f.read(4))[0]
        n = struct.unpack("<Q", f.read(8))[0]
        for _ in range(n):
            _kv(f, it)
        return None
    raise ValueError(f"unknown kv type {t}")


def tensors(path: str | Path) -> list[dict]:
    p = Path(path)
    size = p.stat().st_size
    out = []
    with p.open("rb") as f:
        magic, version = struct.unpack("<4sI", f.read(8))
        if magic != b"GGUF":
            raise ValueError("not a GGUF")
        n_tensors, n_kv = struct.unpack("<QQ", f.read(16))
        for _ in range(n_kv):
            ln = struct.unpack("<Q", f.read(8))[0]
            key = f.read(ln).decode("utf-8", "replace")
            t = struct.unpack("<I", f.read(4))[0]
            _kv(f, t)
        for _ in range(n_tensors):
            ln = struct.unpack("<Q", f.read(8))[0]
            name = f.read(ln).decode("utf-8", "replace")
            nd = struct.unpack("<I", f.read(4))[0]
            dims = struct.unpack("<" + "Q" * nd, f.read(8 * nd))
            dtype = struct.unpack("<I", f.read(4))[0]
            off = struct.unpack("<Q", f.read(8))[0]
            out.append({"name": name, "dims": dims, "type": dtype, "offset": off})
    base = min(t["offset"] for t in out)
    out.sort(key=lambda t: t["offset"])
    for i, t in enumerate(out):
        nxt = out[i + 1]["offset"] if i + 1 < len(out) else size - base
        t["bytes"] = max(0, nxt - t["offset"])
    return out


def profile(path: str | Path):
    """bytes[role][block] plus the model's totals."""
    ts = tensors(path)
    blocks: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for t in ts:
        parts = t["name"].split(".")
        if parts[0] == "blk" and parts[1].isdigit():
            role = ".".join(parts[2:])
            blocks[role][int(parts[1])] += t["bytes"]
        else:
            blocks[t["name"]][-1] += t["bytes"]
    return blocks, ts


def die_image(blocks, width: int = 900, height: int = 900, mark: str = "") -> Image.Image:
    """A die whose core is the tensor table: columns blocks, rows roles.

    The silicon is lit from the top left, cells are separated by gutters so the
    lattice survives being sampled into characters, and the package has fiducials
    and pads like a real part.
    """
    img = Image.new("L", (width, height), 255)
    d = ImageDraw.Draw(img)

    # package
    d.rounded_rectangle((34, 34, width - 34, height - 34), radius=22, outline=40, width=3)
    # pads: alternating lengths, on all four sides
    for i in range(28):
        t = 34 + (width - 68) * (i + 0.5) / 28
        ln = 34 if i % 2 else 26
        d.rectangle((t - 9, 34 - ln, t + 9, 34), fill=70)
        d.rectangle((t - 9, height - 34, t + 9, height - 34 + ln), fill=70)
        d.rectangle((34 - ln, t - 9, 34, t + 9), fill=70)
        d.rectangle((width - 34, t - 9, width - 34 + ln, t + 9), fill=70)
    # fiducials
    for (fx, fy) in ((70, 70), (width - 70, 70), (70, height - 70), (width - 70, height - 70)):
        d.ellipse((fx - 9, fy - 9, fx + 9, fy + 9), outline=60, width=2)

    # silicon, lit from the top left
    core = (78, 78, width - 78, height - 78)
    x0, y0, x1, y1 = core
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        d.line([(x0, y), (x1, y)], fill=int(252 - 34 * t))
    # a soft diagonal falloff, so sampling produces a gradient rather than a slab
    for i in range(0, x1 - x0, 3):
        g = int(16 * (1 - i / max(1, x1 - x0)))
        d.line([(x0 + i, y0), (x0 + i, y1)], fill=255 - g)
    d.rectangle(core, outline=50, width=2)

    block_ids = sorted({b for r in blocks for b in blocks[r] if b >= 0})
    roles = [r for r in blocks if any(b >= 0 for b in blocks[r])]
    order = ["attn_q", "attn_k", "attn_v", "attn_output", "attn_q_norm", "attn_k_norm",
             "attn_norm", "ffn_gate", "ffn_up", "ffn_down", "ffn_norm"]
    def key(r):
        head = r.split(".")[0]
        return (order.index(head) if head in order else len(order), r)
    roles.sort(key=key)
    nb, nr = len(block_ids), len(roles)
    if not nb or not nr:
        return img
    pad = 22
    ix0, iy0, ix1, iy1 = x0 + pad, y0 + pad, x1 - pad, y1 - pad
    cw = (ix1 - ix0) / nb
    gut = 5
    ch = (iy1 - iy0 - gut * (nr - 1)) / nr
    vals = sorted(math.log1p(v) for r in roles for b, v in blocks[r].items() if b >= 0)
    lo = 0.0  # absolute scale: a small tensor stays visibly light instead of vanishing
    hi = vals[-1]
    span = max(1e-6, hi - lo)
    for r_i, role in enumerate(roles):
        for b_i, blk in enumerate(block_ids):
            v = blocks[role].get(blk, 0)
            if not v:
                continue
            t = min(1.0, max(0.0, (math.log1p(v) - lo) / span)) ** 0.7
            shade = int(236 - 178 * t)
            band_y = iy0 + r_i * (ch + gut)
            cx0, cy0 = ix0 + b_i * cw + 2, band_y + 1
            d.rectangle((cx0, cy0, ix0 + (b_i + 1) * cw - 2, band_y + ch - 1), fill=shade)

    # bond wires from the pads to the silicon edge
    for i in range(12):
        t = 34 + (width - 68) * (i + 0.5) / 12
        d.line((t, 44, ix0 + 12 + i * (ix1 - ix0 - 24) / 11, y0 - 10), fill=120, width=1)
        d.line((t, height - 44, ix0 + 12 + i * (ix1 - ix0 - 24) / 11, y1 + 10), fill=120, width=1)
    return img


def to_ascii(img: Image.Image, cols: int = 74, gamma: float = 1.0, invert: bool = True) -> list[str]:
    """Sample luminance into glyph rows, preserving aspect for a mono cell."""
    w, h = img.size
    cell_w = w / cols
    cell_h = cell_w / 0.52  # mono glyphs are about twice as tall as wide
    rows = max(1, int(h / cell_h))
    small = img.resize((cols, rows), Image.LANCZOS)
    px = small.load()
    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            v = px[x, y] / 255.0
            if invert:
                v = 1.0 - v
            v = min(1.0, max(0.0, (v ** gamma)))
            line.append(RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))])
        out.append("".join(line))
    return out