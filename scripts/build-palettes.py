#!/usr/bin/env python3
"""Generate both Leylah Void variants from one structural template.

Both variants share the same hue family (warm: rose, warm violet, periwinkle,
teal, olive-green, gold, coral) and differ only in finish:

  neon  - vivid, max in-gamut chroma, signal tier at ~8.4:1
  matte - dusty, chroma held at 0.46 of maximum, compressed contrast

Usage: python3 scripts/build-palettes.py
"""
import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "themes", "_base.json")
OUT = os.path.join(ROOT, "themes")


# ---------------------------------------------------------------- colour math
def oklch_to_linear(L, C, H):
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def encode(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def to_hex(L, C, H):
    r, g, b = oklch_to_linear(L, C, H)
    if min(r, g, b) < -0.002 or max(r, g, b) > 1.002:
        return None
    return "#%02X%02X%02X" % tuple(round(encode(v) * 255) for v in (r, g, b))


def luminance(hx):
    r, g, b = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b="#000000"):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def max_chroma(L, H):
    lo, hi = 0.0, 0.25
    for _ in range(45):
        mid = (lo + hi) / 2
        if to_hex(L, mid, H):
            lo = mid
        else:
            hi = mid
    return max(0.0, lo - 0.004)


def solve_ratio(H, factor, target):
    """Most saturated colour of this hue at the requested contrast."""
    best = None
    L = 0.35
    while L < 0.95:
        hx = to_hex(L, factor * max_chroma(L, H), H)
        if hx:
            delta = abs(contrast(hx) - target)
            if best is None or delta < best[0]:
                best = (delta, hx)
        L += 0.002
    return best[1]


def solve_neutral(H, chroma, target):
    best = None
    L = 0.35
    while L < 0.95:
        hx = to_hex(L, chroma, H)
        if hx:
            delta = abs(contrast(hx) - target)
            if best is None or delta < best[0]:
                best = (delta, hx)
        L += 0.002
    return best[1]


# ------------------------------------------------------------------ variants
# role: (hue, chroma factor, contrast target)
VARIANTS = {
    "neon": {
        "label": "Leylah Void: Neon",
        "roles": {
            "keyword":    (342, 1.00, 8.4),
            "declaration": (305, 0.95, 8.4),
            "function":   (255, 0.95, 8.4),
            "string":     (182, 0.90, 8.4),
            "annotation": (126, 0.80, 8.4),
            "type":       (76,  0.95, 8.4),
            "number":     (28,  0.95, 8.4),
        },
        "support": {
            "property": (305, 0.75, 6.1),
        },
        "neutrals": {
            "variable": (38, 0.030, 6.1),
            "operator": (38, 0.027, 4.6),
            "comment":  (38, 0.019, 4.3),
            "text":     (38, 0.016, 15.0),
        },
        "extra": {
            "accent_light": "#FFA6DD",
            "type_light":   "#EDB45F",
            "ui_text":      "#E9DFD9",
            "ui_muted":     "#B5A9A2",
            "ui_dim":       "#7A6E68",
            "line_number":  "#6B5F59",
            "error":        "#FF6B5E",
            "invalid":      "#FF806E",
            "term_blue":    "#8FBCF7",
            "term_cyan":    "#7FD3B4",
            "term_red":     "#FF9B8C",
        },
        "surfaces": {
            "#08060F": "#0C0908",
            "#171129": "#241B18",
            "#241A3A": "#33251F",
            "#100A1B": "#140F0D",
            "#040308": "#070505",
            "#1F0D2E": "#2A1622",
            "#150F28": "#1A1210",
            "#33265A": "#3A2A22",
            "#453570": "#4A362B",
            "#06040C": "#080605",
            "#2A1140": "#331A28",
            "#050307": "#060404",
            "#6E5A1C": "#6E541C",
            "#2A2342": "#332821",
            "#221B38": "#2A211D",
            "#240C34": "#2E1826",
            "#7A2A6E": "#7A2A5A",
            "#1A1530": "#1E1613",
            "#2A0A12": "#2A0F0B",
            "#2A200A": "#2A210C",
            "#0A1A2A": "#0F1A22",
            "#140E22": "#161010",
        },
    },
    "matte": {
        "label": "Leylah Void: Matte",
        "roles": {
            "keyword":    (345, 0.34, 7.8),
            "declaration": (308, 0.34, 6.3),
            "function":   (258, 0.34, 7.2),
            "string":     (182, 0.34, 6.8),
            "annotation": (126, 0.34, 7.0),
            "type":       (76,  0.34, 7.6),
            "number":     (26,  0.34, 7.4),
        },
        "support": {
            "property": (308, 0.34, 5.2),
        },
        "neutrals": {
            "variable": (38, 0.016, 5.0),
            "operator": (38, 0.012, 4.0),
            "comment":  (38, 0.010, 3.8),
            "text":     (38, 0.014, 8.6),
        },
        "extra": {
            "accent_light": "#E4B2CB",
            "type_light":   "#D4B893",
            "ui_text":      "#C9BFB8",
            "ui_muted":     "#9C928B",
            "ui_dim":       "#6F6660",
            "line_number":  "#615852",
            "error":        "#C98078",
            "invalid":      "#C98A82",
            "term_blue":    "#A9B9CE",
            "term_cyan":    "#A3B7AE",
            "term_red":     "#D3A099",
        },
        "surfaces": {
            "#08060F": "#0D0A09",
            "#171129": "#261E1B",
            "#241A3A": "#342925",
            "#100A1B": "#161110",
            "#040308": "#080606",
            "#1F0D2E": "#241A1A",
            "#150F28": "#1B1513",
            "#33265A": "#382C27",
            "#453570": "#463830",
            "#06040C": "#090707",
            "#2A1140": "#2A1F1D",
            "#050307": "#070505",
            "#6E5A1C": "#6E5A2A",
            "#2A2342": "#332B26",
            "#221B38": "#2A2320",
            "#240C34": "#261B1B",
            "#7A2A6E": "#6B3A48",
            "#1A1530": "#1F1917",
            "#2A0A12": "#2A100D",
            "#2A200A": "#2A2210",
            "#0A1A2A": "#111A20",
            "#140E22": "#171211",
        },
    },
}

# template hex -> role name (the template is the v2 structural base)
ROLE_OF = {
    "#FE6BF5": "keyword",
    "#A890FD": "declaration",
    "#28A7FD": "function",
    "#1AC6C6": "string",
    "#11CD61": "annotation",
    "#E0AA12": "type",
    "#FD7770": "number",
    "#9570FD": "property",
    "#918DAB": "variable",
    "#918F9F": "variable",
    "#777390": "operator",
    "#767384": "operator",
    "#726E8B": "comment",
    "#EDE9F7": "text",
    "#FE8BF6": "accent_light",
    "#F2C43C": "type_light",
    "#C4BCD6": "ui_text",
    "#9A93B8": "ui_muted",
    "#6B6579": "ui_dim",
    "#5A5468": "line_number",
    "#FF4D5E": "error",
    "#FE6A84": "invalid",
    "#7CC2FD": "term_blue",
    "#7CE8E8": "term_cyan",
    "#FF8F9E": "term_red",
    "#EA58E2": "button",
}


def palette_for(spec):
    pal = {}
    for role, (h, f, t) in spec["roles"].items():
        pal[role] = solve_ratio(h, f, t)
    for role, (h, f, t) in spec["support"].items():
        pal[role] = solve_ratio(h, f, t)
    for role, (h, c, t) in spec["neutrals"].items():
        pal[role] = solve_neutral(h, c, t)
    pal.update(spec["extra"])
    pal["button"] = pal["keyword"]
    return pal


def main():
    base = json.load(open(BASE))
    hex_re = re.compile(r"#[0-9A-Fa-f]{6}")
    report = []

    for name, spec in VARIANTS.items():
        pal = palette_for(spec)
        mapping = {old: pal[role] for old, role in ROLE_OF.items()}
        mapping.update(spec["surfaces"])
        mapping["#000000"] = "#000000"
        mapping["#FFFFFF"] = "#FFFFFF"
        mapping["#0B0714"] = "#0B0714"

        missing = set()

        def remap(value):
            if not isinstance(value, str):
                return value

            def sub(m):
                old = m.group(0).upper()
                if old in mapping:
                    return mapping[old]
                if old not in ("#000000", "#FFFFFF"):
                    missing.add(old)
                return m.group(0)

            return hex_re.sub(sub, value)

        theme = json.loads(json.dumps(base))
        theme["name"] = spec["label"]
        for k, v in list(theme["colors"].items()):
            theme["colors"][k] = remap(v)
        for rule in theme["tokenColors"]:
            for key in ("foreground", "background"):
                if key in rule["settings"]:
                    rule["settings"][key] = remap(rule["settings"][key])
        for k, v in list(theme["semanticTokenColors"].items()):
            if isinstance(v, str):
                theme["semanticTokenColors"][k] = remap(v)
            elif isinstance(v, dict):
                for key in ("foreground", "background"):
                    if key in v:
                        v[key] = remap(v[key])

        path = os.path.join(OUT, f"leylah-void-{name}-color-theme.json")
        json.dump(theme, open(path, "w"), indent=2, ensure_ascii=False)
        open(path, "a").write("\n")

        report.append((name, spec["label"], pal, sorted(missing)))
        print(f"wrote themes/{os.path.basename(path)}")

    print()
    for name, label, pal, missing in report:
        print(f"{label}")
        for role in ("keyword", "declaration", "function", "string", "annotation",
                     "type", "number", "property", "variable", "operator",
                     "comment", "text"):
            hx = pal[role]
            print(f"  {role:12s} {hx}  {contrast(hx):5.2f}:1")
        if missing:
            print("  UNMAPPED:", ", ".join(missing))
        print()


if __name__ == "__main__":
    main()
