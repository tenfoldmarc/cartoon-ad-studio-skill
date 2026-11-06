#!/usr/bin/env python3
"""Contact sheets for review. Run with the skill's own Python.

  qa.py stills <out.jpg> <img1> [<img2> ...] [--cols 6]
      labeled grid of shot stills (or character sheets): the approval sheet before any clip is animated
  qa.py clips <out.jpg> <clip1.mp4> [<clip2.mp4> ...] [--frames 6]
      one row per clip, N frames across its whole length: catch melting faces, extra fingers, text that warps,
      a character that changes between shots, a camera that does not move
Look at every sheet yourself (open the image) before saying a step is done.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(SKILL, 'fonts', 'InterTight-Variable.ttf')


def label_font(size):
    return ImageFont.truetype(FONT, size) if os.path.isfile(FONT) else ImageFont.load_default()


def opt(name, default):
    a = sys.argv
    return int(a[a.index(name) + 1]) if name in a and a.index(name) + 1 < len(a) else default


def files():
    skip = {sys.argv[sys.argv.index(f) + 1] for f in ('--cols', '--frames') if f in sys.argv}
    return [a for a in sys.argv[3:] if not a.startswith('--') and a not in skip]


def stills(out, paths, cols):
    w, h = 300, 533
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * (h + 34)), (20, 20, 20))
    d, f = ImageDraw.Draw(sheet), label_font(22)
    for i, p in enumerate(paths):
        im = Image.open(p).convert('RGB')
        im.thumbnail((w, h))
        x, y = (i % cols) * w, (i // cols) * (h + 34)
        sheet.paste(im, (x + (w - im.width) // 2, y + 34))
        d.text((x + 8, y + 5), os.path.splitext(os.path.basename(p))[0], fill=(255, 220, 0), font=f)
    sheet.save(out, quality=85)


def clips(out, paths, n):
    fw, fh = 180, 320
    sheet = Image.new('RGB', (fw * n + 80, fh * len(paths)), (15, 15, 15))
    d, f = ImageDraw.Draw(sheet), label_font(18)
    with tempfile.TemporaryDirectory() as tmp:
        for r, c in enumerate(paths):
            dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', c],
                                       capture_output=True, text=True).stdout)
            d.text((6, r * fh + 8), os.path.splitext(os.path.basename(c))[0], fill=(255, 220, 0), font=f)
            for k in range(n):
                t = .05 + (dur - .15) * k / max(n - 1, 1)
                p = os.path.join(tmp, f'{r}_{k}.jpg')
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', c, '-frames:v', '1',
                                '-vf', f'scale={fw}:{fh}:force_original_aspect_ratio=decrease,pad={fw}:{fh}:(ow-iw)/2:(oh-ih)/2', p], check=True)
                sheet.paste(Image.open(p), (80 + k * fw, r * fh))
    sheet.save(out, quality=85)


def main():
    if len(sys.argv) < 4 or sys.argv[1] not in ('stills', 'clips'):
        print(__doc__.strip())
        return 1
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if mode == 'stills':
        stills(out, files(), opt('--cols', 6))
    else:
        clips(out, files(), opt('--frames', 6))
    print(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
