#!/usr/bin/env python3
"""Build the gallery listing from whatever is sitting in assets/gallery/.

The site is static — a browser visiting GitHub Pages cannot ask a folder what
is in it. So the folder is read here, at deploy time, and written out as
assets/gallery/manifest.js, which both pages load. The deploy workflow runs
this on every push, so adding a photo or a video is only ever:

    drop the file into assets/gallery/  ->  commit  ->  it is on the site

Two things are produced:

  * a 400px thumbnail in assets/gallery/thumbs/ for anything that lacks one —
    the grid and the homepage conveyor belt show these, never the originals,
    which run to hundreds of KB each. Videos get a still frame grabbed from
    one second in, so they appear as a picture with a play badge rather than
    as a downloaded video.

  * assets/gallery/manifest.js, listing every file in natural order
    (2.jpg before 10.jpg) with its type and thumbnail.

Existing thumbnails are left alone, so re-running is cheap. Pass --force to
rebuild every one — needed after replacing a photo with a different picture
under the same file name, where the old thumbnail would otherwise stay.

Run it by hand after adding files if you want to preview the site locally:

    python3 tools/build-gallery.py
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit('Pillow is needed: pip install pillow')

GALLERY_DIR = os.path.join('assets', 'gallery')
THUMBS_DIR = os.path.join(GALLERY_DIR, 'thumbs')
MANIFEST = os.path.join(GALLERY_DIR, 'manifest.js')

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
VIDEO_EXTS = {'.mp4', '.webm', '.mov'}

THUMB_EDGE = 400
THUMB_QUALITY = 80


def natural_key(name):
    """'2.jpg' before '10.jpg'; anything non-numeric sorts after, by name."""
    stem = os.path.splitext(name)[0]
    if re.fullmatch(r'\d+', stem):
        return (0, int(stem), '')
    return (1, 0, name.lower())


def media_files():
    if not os.path.isdir(GALLERY_DIR):
        return []
    out = []
    for name in os.listdir(GALLERY_DIR):
        if name.startswith('.'):
            continue
        if not os.path.isfile(os.path.join(GALLERY_DIR, name)):
            continue        # skips thumbs/
        if os.path.splitext(name)[1].lower() in IMAGE_EXTS | VIDEO_EXTS:
            out.append(name)
    return sorted(out, key=natural_key)


def save_thumb(im, dest):
    im = ImageOps.exif_transpose(im).convert('RGB')
    im.thumbnail((THUMB_EDGE, THUMB_EDGE), Image.LANCZOS)
    im.save(dest, 'JPEG', quality=THUMB_QUALITY, optimize=True)


def thumb_from_image(src, dest):
    with Image.open(src) as im:
        save_thumb(im, dest)          # a GIF lands on its first frame
    return True


def thumb_from_video(src, dest):
    """Grab a still ~1s in. Silently gives up if ffmpeg is not installed."""
    if not shutil.which('ffmpeg'):
        return False
    with tempfile.TemporaryDirectory() as tmp:
        frame = os.path.join(tmp, 'frame.png')
        done = subprocess.run(
            ['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', src,
             '-frames:v', '1', frame],
            capture_output=True)
        # a clip shorter than a second yields nothing — retry from the start
        if done.returncode != 0 or not os.path.exists(frame):
            done = subprocess.run(
                ['ffmpeg', '-v', 'error', '-y', '-i', src,
                 '-frames:v', '1', frame],
                capture_output=True)
        if done.returncode != 0 or not os.path.exists(frame):
            print(f'  ! no still frame from {os.path.basename(src)}')
            return False
        with Image.open(frame) as im:
            save_thumb(im, dest)
    return True


def build(force=False):
    files = media_files()
    if not files:
        print(f'nothing in {GALLERY_DIR}/')
    os.makedirs(THUMBS_DIR, exist_ok=True)

    entries, made, kept = [], 0, 0
    for name in files:
        src = os.path.join(GALLERY_DIR, name)
        stem, ext = os.path.splitext(name)
        is_video = ext.lower() in VIDEO_EXTS
        thumb_name = stem + '.jpg'
        thumb_path = os.path.join(THUMBS_DIR, thumb_name)

        have = os.path.exists(thumb_path)
        if have and not force:
            kept += 1
        else:
            try:
                have = (thumb_from_video(src, thumb_path) if is_video
                        else thumb_from_image(src, thumb_path))
            except Exception as exc:                  # unreadable / odd file
                print(f'  ! {name}: {exc}')
                have = False
            if have:
                made += 1
                print(f'  + thumbs/{thumb_name}')

        entries.append({
            'file': name,
            'type': 'video' if is_video else 'image',
            # null means "no thumbnail": the page then falls back to the file
            # itself, so the item still shows up
            'thumb': thumb_name if have else None,
        })

    lines = ',\n'.join('    ' + json.dumps(e) for e in entries)
    with open(MANIFEST, 'w') as fh:
        fh.write(
            '/* GENERATED by tools/build-gallery.py - do not edit by hand.\n'
            ' *\n'
            ' * Every media file in assets/gallery/, in the order it appears\n'
            ' * on the site. Rebuilt on each deploy, so this file only needs\n'
            ' * committing to keep the pages working when opened straight\n'
            ' * from disk. To add a photo or video, put it in the folder -\n'
            ' * nothing here or in the HTML has to be touched.\n'
            ' */\n'
            'window.GALLERY_MEDIA = [\n' + lines + '\n];\n')

    print(f'{len(entries)} items -> {MANIFEST} '
          f'({made} thumbnails built, {kept} already there)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--force', action='store_true',
                    help='rebuild every thumbnail, not just the missing ones')
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    build(force=args.force)
