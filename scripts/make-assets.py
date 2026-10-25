#!/usr/bin/env python3
"""Generate the README preview and extension icon (no external assets needed)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

C = dict(
    kw="#FE6BF5", storage="#A890FD", type="#E0AA12", func="#28A7FD",
    string="#1AC6C6", num="#FD7770", prop="#9570FD", param="#918DAB",
    comment="#726E8B", op="#777390", punct="#777390", esc="#E0AA12",
    self="#918DAB", teal="#1AC6C6", ann="#11CD61", text="#EDE9F7", dim="#5A5468",
)

CODE = [
    [("from", C["kw"], "b"), (" ", None, ""), ("dataclasses", C["teal"], ""), (" ", None, ""),
     ("import", C["kw"], "b"), (" ", None, ""), ("dataclass", C["type"], "")],
    [("import", C["kw"], "b"), (" ", None, ""), ("asyncio", C["type"], ""), (",", C["punct"], ""), (" ", None, ""), ("time", C["teal"], "")],
    [],
    [("# Leylah Void \u2014 pitch black, zero compromise", C["comment"], "i")],
    [],
    [("@dataclass", C["ann"], "i")],
    [("class", C["storage"], "b"), (" ", None, ""), ("Leylah", C["type"], ""), ("(", C["punct"], ""), ("Actor", C["type"], ""), ("):", C["punct"], "")],
    [("    ", None, ""), ('"""Void dweller, magenta eyes."""', C["comment"], "i")],
    [("    ", None, ""), ("limit", C["prop"], ""), (":", C["punct"], ""), (" ", None, ""), ("int", C["type"], ""), (" ", None, ""), ("=", C["op"], ""), (" ", None, ""), ("3", C["num"], "")],
    [],
    [("    ", None, ""), ("@staticmethod", C["ann"], "i")],
    [("    ", None, ""), ("async", C["storage"], ""), (" ", None, ""), ("def", C["storage"], "b"), (" ", None, ""), ("strike", C["func"], ""), ("(", C["punct"], ""), ("self", C["self"], "i"), (", ", C["punct"], ""), ("target", C["param"], "i"), ("):", C["punct"], "")],
    [("        ", None, ""), ("for", C["kw"], "b"), (" ", None, ""), ("i", None, ""), (" ", None, ""), ("in", C["kw"], "b"), (" ", None, ""), ("range", C["func"], ""), ("(", C["punct"], ""), ("3", C["num"], ""), ("):", C["punct"], "")],
    [("            ", None, ""), ("if", C["kw"], "b"), (" ", None, ""), ("not", C["kw"], "b"), (" ", None, ""), ("self", C["self"], "i"), (".", C["punct"], ""), ("alive", C["prop"], ""), (":", C["punct"], "")],
    [("                ", None, ""), ("await", C["kw"], "b"), (" ", None, ""), ("asyncio", C["type"], ""), (".", C["punct"], ""), ("sleep", C["func"], ""), ("(", C["punct"], ""), ("0.25", C["num"], ""), (")", C["punct"], "")],
    [("            ", None, ""), ("print", C["func"], ""), ("(", C["punct"], ""), ('f"strike {', C["string"], ""), ("target", C["prop"], ""), ("} {", C["string"], ""), ("i", None, ""), ('}"', C["string"], ""), (")", C["punct"], "")],
    [("        ", None, ""), ("return", C["kw"], "b"), (" ", None, ""), ("True", C["num"], "b"), (" ", None, ""), ("if", C["kw"], "b"), (" ", None, ""), ("i", None, ""), (" ", None, ""), (">", C["op"], ""), (" ", None, ""), ("1", C["num"], ""), (" ", None, ""), ("else", C["kw"], "b"), (" ", None, ""), ("False", C["num"], "b")],
    [],
    [("    ", None, ""), ("@property", C["ann"], "i")],
    [("    ", None, ""), ("def", C["storage"], "b"), (" ", None, ""), ("alive", C["func"], ""), ("(", C["punct"], ""), ("self", C["self"], "i"), (")", C["punct"], ""), (" ", None, ""), ("->", C["op"], ""), (" ", None, ""), ("bool", C["type"], ""), (":", C["punct"], "")],
    [("        ", None, ""), ("return", C["kw"], "b"), (" ", None, ""), ("self", C["self"], "i"), (".", C["punct"], ""), ("limit", C["prop"], ""), (" ", None, ""), (">", C["op"], ""), (" ", None, ""), ("0", C["num"], "")],
]

LEGEND = [
    ("keyword", C["kw"]), ("storage", C["storage"]), ("type", C["type"]),
    ("function", C["func"]), ("string", C["string"]), ("number", C["num"]),
    ("property", C["prop"]), ("parameter", C["param"]), ("annotation", C["ann"]),
    ("comment", C["comment"]),
]


def make_preview():
    S = 2
    W, H = 1120, 660
    img = Image.new("RGB", (W * S, H * S), "#000000")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(MONO, 15 * S)
    fb = ImageFont.truetype(MONO_B, 15 * S)
    fsmall = ImageFont.truetype(MONO, 12 * S)

    # title bar
    d.rectangle([0, 0, W * S, 38 * S], fill="#060409")
    for i, col in enumerate(["#FF3D9A", "#FFC857", "#7BE0CE"]):
        d.ellipse([(16 + i * 20) * S, 15 * S, (26 + i * 20) * S, 25 * S], fill=col)
    d.text((96 * S, 12 * S), "app.py", font=fsmall, fill="#FFFFFF")
    d.text((196 * S, 12 * S), "actor.py", font=fsmall, fill="#7E7799")
    d.text((306 * S, 12 * S), "README.md", font=fsmall, fill="#7E7799")
    d.line([0, 38 * S, W * S, 38 * S], fill="#1C1530", width=S)

    # active tab marker
    d.rectangle([86 * S, 0, 186 * S, 3 * S], fill="#FF3D9A")

    # gutter
    d.rectangle([0, 38 * S, 62 * S, (H - 58) * S], fill="#000000")
    d.line([62 * S, 38 * S, 62 * S, (H - 58) * S], fill="#1C1530", width=S)

    y = 52 * S
    for n, parts in enumerate(CODE, start=1):
        d.text((32 * S, y), str(n), font=fsmall, fill=C["dim"])
        x = 78 * S
        for txt, col, style in parts:
            if not txt:
                continue
            font = fb if style == "b" or col == C["func"] else f
            d.text((x, y), txt, font=font, fill=col or "#E8E2F2")
            x += d.textlength(txt, font=font)
        y += 24 * S

    # status bar
    d.rectangle([0, (H - 58) * S, W * S, (H - 30) * S], fill="#08050E")
    d.line([0, (H - 58) * S, W * S, (H - 58) * S], fill="#FF3D9A55", width=S)
    d.text((16 * S, (H - 50) * S), "main*", font=fsmall, fill="#FF8FD0")
    d.text((86 * S, (H - 50) * S), "0 errors", font=fsmall, fill="#7BE0CE")
    d.text((176 * S, (H - 50) * S), "2 warnings", font=fsmall, fill="#FFC857")
    tx = (W * S) - d.textlength("Leylah Void", font=fsmall) - 20 * S
    d.text((tx, (H - 50) * S), "Leylah Void", font=fsmall, fill="#C9C2DC")

    # legend
    d.rectangle([0, (H - 30) * S, W * S, H * S], fill="#050308")
    x = 16 * S
    for name, col in LEGEND:
        d.rectangle([x, (H - 20) * S, x + 9 * S, (H - 11) * S], fill=col)
        d.text((x + 14 * S, (H - 21) * S), name, font=fsmall, fill="#C9C2DC")
        x += d.textlength(name, font=fsmall) + 34 * S

    img.save(os.path.join(ASSETS, "preview.png"))
    print("assets/preview.png")


def make_icon():
    N = 256
    img = Image.new("RGB", (N, N), "#000000")
    d = ImageDraw.Draw(img)
    # subtle violet glow
    glow = Image.new("RGB", (N, N), "#000000")
    gd = ImageDraw.Draw(glow)
    gd.ellipse([28, 28, N - 28, N - 28], outline="#B98CFF", width=10)
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.blend(img, glow, 0.55)
    d = ImageDraw.Draw(img)

    # ring split: magenta -> violet
    steps = 180
    for i in range(steps):
        a0, a1 = 360 * i / steps, 360 * (i + 1) / steps + 1
        t = i / steps
        r = int(0xFF + (0xC0 - 0xFF) * t)
        g = int(0x3D + (0x9C - 0x3D) * t)
        b = int(0x9A + (0xFF - 0x9A) * t)
        d.arc([44, 44, N - 44, N - 44], a0, a1, fill=(r, g, b), width=12)

    # gold four-point spark inside the void
    cx = cy = N // 2
    d.polygon([(cx, cy - 62), (cx + 15, cy - 15), (cx + 62, cy), (cx + 15, cy + 15),
               (cx, cy + 62), (cx - 15, cy + 15), (cx - 62, cy), (cx - 15, cy - 15)],
              fill="#FFC857")
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill="#000000")
    d.ellipse([cx + 48, cy - 66, cx + 68, cy - 46], fill="#5CC8FF")

    img.save(os.path.join(ASSETS, "icon.png"))
    print("assets/icon.png")


make_preview()
make_icon()
