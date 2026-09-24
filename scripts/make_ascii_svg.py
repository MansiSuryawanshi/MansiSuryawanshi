#!/usr/bin/env python3
"""Create a self-typing, GitHub-safe ASCII portrait using Pillow only."""

import argparse
import html
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

RAMP = " .`:-=+*cs#%@"
COLS = 118
CHAR_W = 7.74
FONT_SIZE = 12.9
LINE_H = 15
ROW_DELAY = 0.055
FG_LIGHT = "#57606a"
FG_DARK = "#c9d1d9"


def prepare(path: Path) -> Image.Image:
    image = Image.open(path).convert("L")
    # This source photo is already tightly framed. A soft oval removes the
    # distracting corners while retaining the hair silhouette.
    w, h = image.size
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    cx, cy = w * 0.50, h * 0.48
    rx, ry = w * 0.51, h * 0.55
    feather = 0.10
    for y in range(h):
        for x in range(w):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1 - feather:
                px[x, y] = 255
            elif d < 1:
                px[x, y] = int(255 * (1 - d) / feather)
    image = image.filter(ImageFilter.MedianFilter(3))
    image = ImageOps.autocontrast(image, cutoff=(1, 2))
    image = ImageEnhance.Contrast(image).enhance(1.18)
    white = Image.new("L", image.size, 255)
    return Image.composite(image, white, mask)


def to_lines(image: Image.Image, cols: int, gamma: float) -> list[str]:
    w, h = image.size
    rows = max(1, int(cols * (h / w) * 0.44))
    image = image.resize((cols, rows), Image.Resampling.LANCZOS)
    values = list(image.getdata())
    lines = []
    for row in range(rows):
        chars = []
        for col in range(cols):
            darkness = (1 - values[row * cols + col] / 255.0) ** gamma
            chars.append(RAMP[min(len(RAMP) - 1, int(darkness * len(RAMP)))])
        lines.append("".join(chars).rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def build_svg(lines: list[str], destination: Path, cols: int) -> None:
    pad = 16
    width = int(cols * CHAR_W + 2 * pad)
    height = len(lines) * LINE_H + 2 * pad
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Animated ASCII portrait of Mansi Suryawanshi</title>',
        '<desc id="desc">A monochrome portrait types itself from top to bottom.</desc>',
        f'<style>.a{{fill:{FG_LIGHT};font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}@media(prefers-color-scheme:dark){{.a{{fill:{FG_DARK}}}}}</style>',
    ]
    for i, line in enumerate(lines):
        y = pad + i * LINE_H
        begin = i * ROW_DELAY
        width_px = max(len(line), 1) * CHAR_W
        safe = html.escape(line)
        parts.append(
            f'<clipPath id="c{i}"><rect x="{pad}" y="{y}" height="{LINE_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{width_px:.1f}" begin="{begin:.3f}s" dur="{ROW_DELAY:.3f}s" fill="freeze"/>'
            '</rect></clipPath>'
        )
        parts.append(
            f'<text xml:space="preserve" x="{pad}" y="{y + 11.2:.1f}" class="a" font-size="{FONT_SIZE}" clip-path="url(#c{i})">{safe}</text>'
        )
        parts.append(
            f'<rect y="{y + 1}" width="6" height="12" class="a" opacity="0">'
            f'<animate attributeName="x" from="{pad}" to="{pad + width_px:.1f}" begin="{begin:.3f}s" dur="{ROW_DELAY:.3f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.78" begin="{begin:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + ROW_DELAY:.3f}s"/>'
            '</rect>'
        )
    parts.append('</svg>')
    destination.write_text("".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path, nargs="?", default=Path("assets/ascii.svg"))
    parser.add_argument("--cols", type=int, default=COLS)
    parser.add_argument("--gamma", type=float, default=1.12)
    args = parser.parse_args()
    lines = to_lines(prepare(args.source), args.cols, args.gamma)
    build_svg(lines, args.destination, args.cols)
    print(f"Wrote {args.destination} with {len(lines)} rows")


if __name__ == "__main__":
    main()
