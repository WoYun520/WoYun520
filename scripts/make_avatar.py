#!/usr/bin/env python3
"""Turn a supplied local avatar image into the text portrait used by profile.svg.

Requires Pillow only for this one-time preparation step; the daily renderer
uses Python's standard library. The input image itself is never uploaded.
"""
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageOps
except ImportError as exc:
    raise SystemExit("Install Pillow first: python3 -m pip install Pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
RAMP = "@%#*+=-:. "


def convert(image_path, columns=58, rows=38):
    with Image.open(image_path) as original:
        rgba = ImageOps.exif_transpose(original).convert("RGBA")
        background = Image.new("RGBA", rgba.size, "white")
        background.alpha_composite(rgba)
        # Crop like a square profile image first. Sampling it into a rectangular
        # grid compensates for terminal characters being taller than wide.
        square = ImageOps.fit(background.convert("L"), (348, 348), method=Image.Resampling.LANCZOS)
        square = square.resize((columns, rows), resample=Image.Resampling.LANCZOS)
        square = ImageOps.autocontrast(square, cutoff=1)
        square = ImageEnhance.Contrast(square).enhance(1.08)
        pixels = list(square.getdata())
    return ["".join(RAMP[min(len(RAMP) - 1, px * len(RAMP) // 256)] for px in pixels[y * columns:(y + 1) * columns]).rstrip() for y in range(rows)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="local avatar image")
    args = parser.parse_args()
    lines = convert(args.image)
    path = ROOT / "assets" / "avatar.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {path}")
    print("Run python3 scripts/render_profile.py to update the preview.")


if __name__ == "__main__":
    main()
