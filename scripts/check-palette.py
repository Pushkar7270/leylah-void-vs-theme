#!/usr/bin/env python3
"""Verify both variants against their own design rules.

Checks:
  1. every syntax colour sits in its declared contrast band vs #000000
  2. signal hues are at least 30 degrees apart
  3. pairwise perceptual distance (OKLab) clears the variant's threshold
  4. how each palette degrades under colour-vision deficiency (report only)

Usage: python3 scripts/check-palette.py
Exit code 1 if a hard rule fails.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROLE_RULES = {
    "keyword": "Keywords — control flow",
    "declaration": "Keywords — declarations, storage, modifiers",
    "function": "Functions and methods",
    "string": "Strings",
    "annotation": "Annotations / decorators / attributes",
    "type": "Types, classes, interfaces, enums",
    "number": "Numbers",
    "property": "Properties, fields, attributes, keys",
    "variable": "Variables and identifiers",
    "operator": "Operators",
    "comment": "Comments",
}

VARIANTS = {
    "neon": {
        "file": "themes/leylah-void-neon-color-theme.json",
        "bands": {"signal": (8.2, 8.6), "support": (6.0, 6.2), "noise": (4.2, 4.7)},
        "tiers": {"signal": ("keyword", "declaration", "function", "string",
                             "annotation", "type", "number"),
                  "support": ("property", "variable"),
                  "noise": ("operator", "comment")},
        "min_de": 0.10,
    },
    "matte": {
        "file": "themes/leylah-void-matte-color-theme.json",
        "bands": {"signal": (6.2, 7.9), "support": (4.9, 5.3), "noise": (3.7, 4.1)},
        "tiers": {"signal": ("keyword", "declaration", "function", "string",
                             "annotation", "type", "number"),
                  "support": ("property", "variable"),
                  "noise": ("operator", "comment")},
        "min_de": 0.04,
    },
}


def rgb(hx):
    return [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hx):
    r, g, b = [lin(c) for c in rgb(hx)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b="#000000"):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def oklab(hx):
    r, g, b = [lin(c) for c in rgb(hx)]
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


CVD = {
    "protan": [[0.152286, 1.052583, -0.204868],
               [0.114503, 0.786281, 0.099216],
               [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968],
               [0.280085, 0.672501, 0.047413],
               [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.076749, -0.178779],
               [-0.078411, 0.930809, 0.147602],
               [0.004733, 0.691367, 0.303900]],
}


def simulate(hx, kind):
    r, g, b = [lin(c) for c in rgb(hx)]
    m = CVD[kind]
    out = [m[i][0] * r + m[i][1] * g + m[i][2] * b for i in range(3)]

    def enc(c):
        c = max(0.0, min(1.0, c))
        return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

    l = 0.4122214708 * enc(out[0]) + 0.5363325363 * enc(out[1]) + 0.0514459929 * enc(out[2])
    mm = 0.2119034982 * enc(out[0]) + 0.6806995451 * enc(out[1]) + 0.1073969566 * enc(out[2])
    s = 0.0883024619 * enc(out[0]) + 0.2817188376 * enc(out[1]) + 0.6299787005 * enc(out[2])
    l, mm, s = l ** (1 / 3), mm ** (1 / 3), s ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * mm - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * mm + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * mm - 0.8086757660 * s)


def hue(hx):
    _, a, b = oklab(hx)
    return math.degrees(math.atan2(b, a)) % 360


def load(variant):
    theme = json.load(open(os.path.join(ROOT, VARIANTS[variant]["file"])))
    rules = {r["name"]: r["settings"].get("foreground") for r in theme["tokenColors"]}
    return {role: rules[rule] for role, rule in ROLE_RULES.items()}


def check(variant):
    spec = VARIANTS[variant]
    pal = load(variant)
    failures = []
    print(f"\n=== {variant.upper()} ===")

    print("1. contrast bands")
    for tier, roles in spec["tiers"].items():
        lo, hi = spec["bands"][tier]
        for role in roles:
            hx = pal[role]
            r = contrast(hx)
            ok = lo <= r <= hi
            if not ok:
                failures.append(f"{variant}/{role} {hx} at {r:.2f}:1 outside {tier} {lo}-{hi}")
            print(f"   {'ok  ' if ok else 'FAIL'} {role:12s} {hx}  {r:5.2f}:1  ({tier})")

    print("2. hue steps (signal)")
    angles = sorted((hue(pal[r]), r) for r in spec["tiers"]["signal"])
    for i in range(len(angles)):
        a, na = angles[i]
        b, nb = angles[(i + 1) % len(angles)]
        step = (b - a) % 360
        ok = step >= 30
        if not ok:
            failures.append(f"{variant}/{na}->{nb} hue step {step:.1f} deg")
        print(f"   {'ok  ' if ok else 'FAIL'} {na:12s} -> {nb:12s} {step:5.1f} deg")

    print("3. perceptual distance")
    sig = spec["tiers"]["signal"]
    worst = min(((math.dist(oklab(pal[a]), oklab(pal[b])), a, b)
                 for i, a in enumerate(sig) for b in sig[i + 1:]), key=lambda x: x[0])
    ok = worst[0] >= spec["min_de"]
    if not ok:
        failures.append(f"{variant}/{worst[1]}/{worst[2]} dE {worst[0]:.3f} < {spec['min_de']}")
    print(f"   {'ok  ' if ok else 'FAIL'} closest: {worst[1]} / {worst[2]}  dE={worst[0]:.3f}"
          f"  (target {spec['min_de']})")

    print("4. colour-vision deficiency (report only)")
    for kind in CVD:
        worst = min(((math.dist(simulate(pal[a], kind), simulate(pal[b], kind)), a, b)
                     for i, a in enumerate(sig) for b in sig[i + 1:]), key=lambda x: x[0])
        print(f"   {kind:6s} closest: {worst[1]} / {worst[2]}  dE={worst[0]:.3f}")

    return failures


def main():
    failures = []
    for variant in VARIANTS:
        failures += check(variant)
    print()
    if failures:
        print("FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("All hard checks passed for both variants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
