#!/usr/bin/env python3
"""Build the site's favicons from logo.png.

Google will only show a site's own icon in search results if the icon is
square AND its side is a multiple of 48px — 48, 96, 144, 192 and so on.
The sizes below are chosen to satisfy that rule, so run this rather than
resizing by hand.

Outputs, all at the site root:
  favicon.ico          16 + 32 + 48, the path Googlebot falls back to
  favicon.png          192x192, the one named by <link rel="icon">
  apple-touch-icon.png 180x180, used when the site is saved to an iOS
                       home screen (Apple's size, not Google's rule)

Usage:  python3 tools/build-favicons.py
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "logo.png"

# Sizes packed inside the .ico. 48 is the one Google reads; 16 and 32 are
# what browsers pick for tab strips and bookmark bars.
ICO_SIZES = [(16, 16), (32, 32), (48, 48)]


def scaled(image, side):
    """The logo redrawn at `side` x `side`, smoothly."""
    return image.resize((side, side), Image.LANCZOS)


def main():
    logo = Image.open(SOURCE).convert("RGBA")
    if logo.width != logo.height:
        raise SystemExit(f"{SOURCE.name} must be square, got {logo.size}")

    # Pillow builds the multi-resolution .ico itself; it downsamples the
    # 48px copy to fill in the smaller entries listed in sizes=.
    scaled(logo, 48).save(ROOT / "favicon.ico", sizes=ICO_SIZES)
    scaled(logo, 192).save(ROOT / "favicon.png", optimize=True)
    scaled(logo, 180).save(ROOT / "apple-touch-icon.png", optimize=True)

    for name in ("favicon.ico", "favicon.png", "apple-touch-icon.png"):
        print(f"wrote {name:22} {(ROOT / name).stat().st_size:>7,} bytes")


if __name__ == "__main__":
    main()
