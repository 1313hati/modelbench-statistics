#!/usr/bin/env python3
"""Two small models, drawn as ASCII dies, with the bench numbers beside them.

Paper ground and drafting geometry: the sheet is a field note, not a dashboard.
The dies are real: every row is a tensor role, every column a block, and the
shade of a cell is that tensor's size on disk.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import blueprint as bp
from gguf_map import die_image, profile, to_ascii

# ---- paper palette -------------------------------------------------------
PAPER = (239, 228, 208)
PAPER_DEEP = (226, 212, 188)
INK = (32, 25, 18)
MUTED = (122, 108, 88)
OXBLOOD = (123, 45, 38)
TEAL = (44, 84, 96)
RULE = (198, 184, 160)

SERIF_B = "/usr/share/fonts/gsfonts/C059-Bold.otf"
SERIF = "/usr/share/fonts/gsfonts/C059-Roman.otf"
MONO = "/usr/share/fonts/liberation/LiberationMono-Regular.ttf"
MONO_B = "/usr/share/fonts/liberation/LiberationMono-Bold.ttf"

W, H = 1600, 900

MODELS = [
    ("qwen3-4b", "QWEN3-4B-INSTRUCT-2507", "/home/hati/.cache/llama-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", "CUDA0"),
    ("gemma3-4b", "GEMMA-3-4B-IT", "/home/hati/.cache/llama-models/gemma-3-4b-it-Q4_K_M.gguf", "CUDA1"),
]
RUNS = Path("/home/hati/.hermes/cache/scratch/smallbench/runs")


# ---- stats ---------------------------------------------------------------
def stats(slug: str) -> dict:
    """Aggregate every sample: the score is a mean, the run-to-run spread is shown."""
    recs = [json.loads(line) for line in (RUNS / slug / "results.jsonl").read_text().splitlines() if line.strip()]
    if not recs:
        return {}
    samples: dict[int, list] = {}
    for r in recs:
        samples.setdefault(r["sample"], []).append(r)
    tokens = 0
    rates = []
    for r in recs:
        for phase in ("first", "repair"):
            p = r.get(phase)
            if p:
                tokens += p.get("prompt_tokens", 0) + p.get("completion_tokens", 0)
                if p.get("tok_per_s"):
                    rates.append(p["tok_per_s"])
    per_run = [statistics.mean(x["final_score"] for x in group) for group in samples.values()]
    solved = [sum(1 for x in group if x.get("final_solved")) for group in samples.values()]
    return {
        "tasks": len(samples[min(samples)]),
        "samples": len(samples),
        "solved": int(statistics.median_low(solved)),
        "solved_runs": solved,
        "score": statistics.mean(per_run),
        "scores": per_run,
        "tokens": tokens,
        "tok_per_task": tokens / max(1, len(recs)),
        "tok_s": statistics.median(rates) if rates else 0,
        "wall": sum(r.get("wall_s", 0) for r in recs),
    }


def wilson(k: int, n: int, z: float = 1.959963985) -> tuple[float, float]:
    if not n:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def families(blocks: dict) -> dict:
    """Fold tensor roles into four families so the die reads in bold bands."""
    fam = {"attn_in": {}, "attn_out": {}, "ffn": {}, "norm": {}}
    for role, per_block in blocks.items():
        head = role.split(".")[0]
        if head in ("attn_q", "attn_k", "attn_v"):
            k = "attn_in"
        elif head == "attn_output":
            k = "attn_out"
        elif head.startswith("ffn_"):
            k = "ffn"
        elif head.endswith("_norm"):
            k = "norm"
        else:
            continue
        for blk, nbytes in per_block.items():
            fam[k][blk] = fam[k].get(blk, 0) + nbytes
    return {k: v for k, v in fam.items() if v}


def gib(path: str) -> float:
    return Path(path).stat().st_size / 1024 ** 3


# ---- drawing -------------------------------------------------------------
def paper(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    # fibres: a few thousand short strokes, then a vignette
    import random
    rnd = random.Random(91)
    for _ in range(5200):
        x, y = rnd.randrange(w), rnd.randrange(h)
        ln = rnd.randint(2, 9)
        a = rnd.randint(6, 16)
        d.line([(x, y), (x + ln, y + rnd.choice([-1, 0, 0, 1]))], fill=(210, 196, 172, a), width=1)
    vig = Image.new("L", (w, h), 0)
    dv = ImageDraw.Draw(vig)
    for i in range(70):
        dv.rectangle((i * 4, i * 3, w - i * 4, h - i * 3), outline=int(2.2 * (70 - i)))
    vig = vig.filter(bp.ImageFilter.GaussianBlur(26))
    shade = Image.new("RGB", (w, h), (188, 172, 146))
    img = Image.composite(img, shade, Image.eval(vig, lambda v: 255 - min(255, v)))
    return img


def ascii_block(d, cols: int, x: float, y: float, rows: list[str], size: int = 9,
                colour=INK, alpha_max: int = 245) -> tuple[float, float]:
    f = ImageFont.truetype(MONO, size)
    cw = size * 0.6
    lh = size * 1.0
    ramp = " .:-=+*#%@"
    for j, line in enumerate(rows):
        for i, ch in enumerate(line):
            if ch == " ":
                continue
            t = ramp.index(ch) / (len(ramp) - 1)
            a = int(alpha_max * (0.18 + 0.82 * t))
            d.text((x + i * cw, y + j * lh), ch, font=f, fill=colour + (a,))
    return x + cols * cw, y + len(rows) * lh


def render(out: str, preview: bool = False) -> str:
    img = paper(W, H)
    d = ImageDraw.Draw(img, "RGBA")

    # drafting grid, very light, in sepia
    for x in range(40, W - 40, 24):
        major = (x - 40) % 120 == 0
        d.line([(x, 40), (x, H - 40)], fill=INK + (14 if major else 7,), width=1)
    for y in range(40, H - 40, 24):
        major = (y - 40) % 120 == 0
        d.line([(40, y), (W - 40, y)], fill=INK + (14 if major else 7,), width=1)

    d.rectangle((40, 40, W - 40, H - 40), outline=INK + (210,), width=2)
    d.rectangle((50, 50, W - 50, H - 50), outline=INK + (90,), width=1)
    for x in range(50, W - 49, 24):
        d.line([(x, 40), (x, 40 + (12 if (x - 50) % 120 == 0 else 6))], fill=INK + (150,), width=1)
    for y in range(50, H - 49, 24):
        d.line([(40, y), (40 + (12 if (y - 50) % 120 == 0 else 6), y)], fill=INK + (150,), width=1)

    # ---- header ----------------------------------------------------------
    tracked = lambda xy, txt, font, col, tr: _tracked(d, xy, txt, font, col, tr)
    tracked((86, 72), "FIELD NOTE  ·  SMALL MODELS  ·  MEASURED", ImageFont.truetype(MONO, 18), OXBLOOD, 2.6)

    head = "Two 4B models, one card each"
    f_head = _fitted(d, head, SERIF_B, 72, W - 2 * 88)
    d.text((86, 96), head, font=f_head, fill=INK)
    sub = ImageFont.truetype(MONO, 16)
    tracked((88, 96 + f_head.size + 14),
            "QWEN3-4B-INSTRUCT-2507   ·   GEMMA-3-4B-IT   ·   Q4_K_M   ·   CORE-V2: 12 TASKS, 296 CHECKS",
            sub, MUTED, 1.4)
    d.line([(86, 218), (W - 86, 218)], fill=RULE + (255,), width=2)

    # ---- two dies --------------------------------------------------------
    cols, size = 58, 14
    lh = size * 1.02
    positions = [(118, 238), (868, 238)]
    for (slug, label, path, dev), (dx, dy) in zip(MODELS, positions):
        # a soft shadow so the sheet reads as a print of a physical part
        blocks, ts = profile(path)
        rows = to_ascii(die_image(families(blocks), 900, 900), cols=cols, gamma=1.0)
        ascii_block(d, cols, dx, dy, rows, size=size)
        cap_y = dy + len(rows) * lh + 18

        n_blocks = len({int(t["name"].split(".")[1]) for t in ts if t["name"].startswith("blk.")})
        fb = ImageFont.truetype(MONO_B, 19)
        tracked((dx, cap_y), label, fb, INK, 1.5)
        fsm = ImageFont.truetype(MONO, 14)
        tracked((dx, cap_y + 26), f"{n_blocks} LAYERS  ·  {len(ts)} TENSORS  ·  {gib(path):.2f} GiB  ·  {dev}", fsm, MUTED, 1.1)

        st = stats(slug)
        if st and st["tasks"] >= 12 and st.get("samples"):
            runs = "  ·  ".join(f"{x*100:.1f}" for x in st["scores"])
            f_big = ImageFont.truetype(MONO_B, 30)
            tracked((dx, cap_y + 52), f"{st['solved']}/{st['tasks']}  ·  {st['score']*100:.1f}%", f_big, INK, 1.0)
            f_ci = ImageFont.truetype(MONO, 14)
            tracked((dx, cap_y + 92), f"RUNS {runs}  ·  {st['tok_s']:.0f} TOK/S  ·  {st['tok_per_task']:,.0f} TOK/TASK",
                    f_ci, TEAL, 0.7)
        else:
            f_big = ImageFont.truetype(MONO, 17)
            tracked((dx, cap_y + 56), "RUNNING…", f_big, MUTED, 1.4)

    # ---- bottom strip ----------------------------------------------------
    d.line([(86, 806), (W - 86, 806)], fill=RULE + (255,), width=1)
    note = ImageFont.truetype(MONO, 14)
    tracked((86, 818), "EACH DIE IS THAT MODEL'S OWN TENSOR TABLE: ROWS ARE ROLES, COLUMNS ARE BLOCKS, DARKNESS IS SIZE ON DISK.",
            note, MUTED, 0.9)
    tracked((86, 840), "SCORE IS THE MEAN TASK SCORE OVER 12 TASKS AND 2 RUNS EACH.  LLAMA.CPP, 16,384 CTX, FLASH ATTENTION ON.",
            note, MUTED, 0.9)

    _title_block(d, "FN-004")

    img.save(out)
    return out


def _tracked(d, xy, text, font, colour, tracking):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=colour if len(colour) == 4 else colour + (255,))
        x += d.textlength(ch, font=font) + tracking
    return x


def _tw(d, text, font, tracking):
    return sum(d.textlength(c, font=font) for c in text) + tracking * max(0, len(text) - 1)


def _fitted(d, text, path, size, width, tracking=1.0):
    while size > 18:
        f = ImageFont.truetype(path, size)
        if _tw(d, text, f, tracking) <= width:
            return f
        size -= 2
    return ImageFont.truetype(path, 18)


def _title_block(d, dwg: str):
    bw, bh = 330, 66
    x1, y1 = W - 40, H - 40
    x0, y0 = x1 - bw, y1 - bh
    d.rectangle((x0, y0, x1, y1), fill=PAPER + (245,))
    d.rectangle((x0, y0, x1, y1), outline=INK + (200,), width=2)
    d.line([(x0, y0 + 36), (x1, y0 + 36)], fill=INK + (140,), width=1)
    fb = ImageFont.truetype(MONO_B, 15)
    fs = ImageFont.truetype(MONO, 12)
    _tracked(d, (x0 + 10, y0 + 10), dwg.upper() + "  MODELBENCH", fb, INK, 1.4)
    _tracked(d, (x0 + 10, y0 + 44), "1:1  ·  19 OCT 2026", fs, MUTED, 1.0)
    _tracked(d, (x0 + 224, y0 + 44), "@1313hati", fs, OXBLOOD, 1.0)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/home/hati/.hermes/cache/scratch/small-models.png"
    print(render(out))