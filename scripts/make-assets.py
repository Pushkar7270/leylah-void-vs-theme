#!/usr/bin/env python3
"""Generate the README previews and the extension icon.

Renders the same code sample with both variants so the finish difference is
visible side by side. Needs Pillow.

Usage: python3 scripts/make-assets.py
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

SURFACES = {
    "neon": {"tabbar": "#080605", "status": "#0A0706", "legend": "#070505", "border": "#33251F"},
    "matte": {"tabbar": "#090707", "status": "#0B0807", "legend": "#080606", "border": "#342925"},
}


def load_palette(variant):
    path = os.path.join(ROOT, "themes", f"leylah-void-{variant}-color-theme.json")
    theme = json.load(open(path))
    rules = {r["name"]: r["settings"].get("foreground") for r in theme["tokenColors"]}
    sem = theme["semanticTokenColors"]
    pick = lambda name: rules[name]
    return {
        "kw": pick("Keywords — control flow"),
        "storage": pick("Keywords — declarations, storage, modifiers"),
        "type": pick("Types, classes, interfaces, enums"),
        "func": pick("Functions and methods"),
        "string": pick("Strings"),
        "num": pick("Numbers"),
        "prop": pick("Properties, fields, attributes, keys"),
        "param": pick("Function parameters"),
        "comment": pick("Comments"),
        "op": pick("Operators"),
        "punct": pick("Punctuation and brackets"),
        "esc": pick("String escapes"),
        "self": pick("Language variables (this, self, super)"),
        "ann": pick("Annotations / decorators / attributes"),
        "text": pick("Base text"),
        "dim": theme["colors"]["editorLineNumber.foreground"],
        "accent": theme["colors"]["editorCursor.foreground"],
    }


def code_sample(C):
    return [
        [("from", C["kw"], "b"), (" ", None, ""), ("dataclasses", C["string"], ""), (" ", None, ""),
         ("import", C["kw"], "b"), (" ", None, ""), ("dataclass", C["type"], "")],
        [("import", C["kw"], "b"), (" ", None, ""), ("asyncio", C["type"], ""), (",", C["punct"], ""), (" ", None, ""), ("time", C["string"], "")],
        [],
        [("# Leylah Void \u2014 pitch black, warm, no glare", C["comment"], "i")],
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


def make_preview(variant, C):
    S = 2
    W, H = 1120, 660
    sf = SURFACES[variant]
    img = Image.new("RGB", (W * S, H * S), "#000000")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(MONO, 15 * S)
    fb = ImageFont.truetype(MONO_B, 15 * S)
    fsmall = ImageFont.truetype(MONO, 12 * S)

    d.rectangle([0, 0, W * S, 38 * S], fill=sf["tabbar"])
    for i, col in enumerate([C["kw"], C["type"], C["string"]]):
        d.ellipse([(16 + i * 20) * S, 15 * S, (26 + i * 20) * S, 25 * S], fill=col)
    d.text((96 * S, 12 * S), "app.py", font=fsmall, fill=C["text"])
    d.text((196 * S, 12 * S), "actor.py", font=fsmall, fill=C["comment"])
    d.text((306 * S, 12 * S), "README.md", font=fsmall, fill=C["comment"])
    d.line([0, 38 * S, W * S, 38 * S], fill=sf["border"], width=S)
    d.rectangle([86 * S, 0, 186 * S, 3 * S], fill=C["kw"])

    d.rectangle([0, 38 * S, 62 * S, (H - 58) * S], fill="#000000")
    d.line([62 * S, 38 * S, 62 * S, (H - 58) * S], fill=sf["border"], width=S)

    y = 52 * S
    for n, parts in enumerate(code_sample(C), start=1):
        d.text((32 * S, y), str(n), font=fsmall, fill=C["dim"])
        x = 78 * S
        for txt, col, style in parts:
            if not txt:
                continue
            font = fb if style == "b" or col == C["func"] else f
            d.text((x, y), txt, font=font, fill=col or C["text"])
            x += d.textlength(txt, font=font)
        y += 24 * S

    d.rectangle([0, (H - 58) * S, W * S, (H - 30) * S], fill=sf["status"])
    d.line([0, (H - 58) * S, W * S, (H - 58) * S], fill=sf["border"], width=S)
    d.text((16 * S, (H - 50) * S), "main*", font=fsmall, fill=C["kw"])
    d.text((86 * S, (H - 50) * S), "0 errors", font=fsmall, fill=C["string"])
    d.text((176 * S, (H - 50) * S), "2 warnings", font=fsmall, fill=C["type"])
    label = "Leylah Void: Neon" if variant == "neon" else "Leylah Void: Matte"
    tx = (W * S) - d.textlength(label, font=fsmall) - 20 * S
    d.text((tx, (H - 50) * S), label, font=fsmall, fill=C["text"])

    d.rectangle([0, (H - 30) * S, W * S, H * S], fill=sf["legend"])
    legend = [("keyword", C["kw"]), ("storage", C["storage"]), ("type", C["type"]),
              ("function", C["func"]), ("string", C["string"]), ("number", C["num"]),
              ("property", C["prop"]), ("parameter", C["param"]),
              ("annotation", C["ann"]), ("comment", C["comment"])]
    x = 16 * S
    for name, col in legend:
        d.rectangle([x, (H - 20) * S, x + 9 * S, (H - 11) * S], fill=col)
        d.text((x + 14 * S, (H - 21) * S), name, font=fsmall, fill=C["text"])
        x += d.textlength(name, font=fsmall) + 34 * S

    out = os.path.join(ASSETS, f"preview-{variant}.png")
    img.save(out)
    print(f"assets/preview-{variant}.png")


def make_icon():
    N = 256
    img = Image.new("RGB", (N, N), "#000000")
    d = ImageDraw.Draw(img)
    steps = 180
    for i in range(steps):
        a0, a1 = 360 * i / steps, 360 * (i + 1) / steps + 1
        t = i / steps
        r = int(0xF8 + (0xBE - 0xF8) * t)
        g = int(0x74 + (0x8F - 0x74) * t)
        b = int(0xCC + (0xF2 - 0xCC) * t)
        d.arc([44, 44, N - 44, N - 44], a0, a1, fill=(r, g, b), width=12)
    cx = cy = N // 2
    d.polygon([(cx, cy - 62), (cx + 15, cy - 15), (cx + 62, cy), (cx + 15, cy + 15),
               (cx, cy + 62), (cx - 15, cy + 15), (cx - 62, cy), (cx - 15, cy - 15)],
              fill="#D3993B")
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill="#000000")
    d.ellipse([cx + 48, cy - 66, cx + 68, cy - 46], fill="#6CA7F1")
    img.save(os.path.join(ASSETS, "icon.png"))
    print("assets/icon.png")


for variant in ("neon", "matte"):
    make_preview(variant, load_palette(variant))
make_icon()
