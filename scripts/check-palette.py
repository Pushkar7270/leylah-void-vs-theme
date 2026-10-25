#!/usr/bin/env python3
"""Verify the palette against its own design rules.

Checks, in order:
  1. every syntax colour sits in its declared contrast band vs #000000
  2. hues are spaced far enough apart to be told apart at a glance
  3. pairwise perceptual distance (OKLab) is above the JND threshold
  4. how the palette degrades under colour-vision deficiency (report only)

Usage: python3 scripts/check-palette.py
Exit code 1 if a hard rule fails.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME = os.path.join(ROOT, "themes", "leylah-void-color-theme.json")

# role: (hex, tier)
TIERS = {"signal": (8.0, 10.0), "support": (6.0, 6.7), "noise": (4.2, 4.8)}
ROLES = {
    "keyword":     ("#FE6BF5", "signal"),
    "declaration": ("#A890FD", "signal"),
    "function":    ("#28A7FD", "signal"),
    "string":      ("#1AC6C6", "signal"),
    "annotation":  ("#11CD61", "signal"),
    "type":        ("#E0AA12", "signal"),
    "number":      ("#FD7770", "signal"),
    "property":    ("#9570FD", "support"),
    "variable":    ("#918DAB", "support"),
    "operator":    ("#777390", "noise"),
    "comment":     ("#726E8B", "noise"),
}


def rgb(hx):
    return [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(hx):
    r, g, b = [lin(c) for c in rgb(hx)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b="#000000"):
    la, lb = lum(a), lum(b)
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


def main():
    theme = json.load(open(THEME))
    theme_hex = json.dumps(theme)
    failures = []

    print("1. CONTRAST BANDS vs #000000")
    for role, (hx, tier) in ROLES.items():
        lo, hi = TIERS[tier]
        r = contrast(hx)
        ok = lo <= r <= hi
        if not ok:
            failures.append(f"{role} {hx} at {r:.2f}:1 outside {tier} band")
        if hx not in theme_hex:
            failures.append(f"{role} {hx} is not present in the theme file")
        print(f"   {'ok ' if ok else 'FAIL'} {role:12s} {hx}  {r:5.2f}:1  ({tier})")

    print("\n2. HUE GEOMETRY (signal tier)")
    sig = [(r, hx) for r, (hx, t) in ROLES.items() if t == "signal"]
    angles = sorted((hue(hx), r) for r, hx in sig)
    for i in range(len(angles)):
        a, name_a = angles[i]
        b, name_b = angles[(i + 1) % len(angles)]
        step = (b - a) % 360
        flag = "ok " if step >= 30 else "FAIL"
        if step < 30:
            failures.append(f"{name_a}->{name_b} hue step only {step:.1f} deg")
        print(f"   {flag} {name_a:12s} -> {name_b:12s} {step:5.1f} deg")

    print("\n3. PERCEPTUAL DISTANCE (normal vision)")
    worst = min(((math.dist(oklab(a), oklab(b)), na, nb)
                 for i, (na, a) in enumerate(sig)
                 for nb, b in sig[i + 1:]), key=lambda x: x[0])
    ok = worst[0] >= 0.10
    if not ok:
        failures.append(f"{worst[1]}/{worst[2]} dE {worst[0]:.3f} below 0.10")
    print(f"   {'ok ' if ok else 'FAIL'} closest pair: {worst[1]} / {worst[2]}  dE={worst[0]:.3f}")
    print(f"   (JND is about 0.02; the design target is 0.10)")

    print("\n4. COLOUR-VISION DEFICIENCY (report only, no pass/fail)")
    for kind in CVD:
        worst = min(((math.dist(simulate(a, kind), simulate(b, kind)), na, nb)
                     for i, (na, a) in enumerate(sig)
                     for nb, b in sig[i + 1:]), key=lambda x: x[0])
        print(f"   {kind:6s} closest: {worst[1]} / {worst[2]}  dE={worst[0]:.3f}")

    print()
    if failures:
        print("FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("All hard checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
