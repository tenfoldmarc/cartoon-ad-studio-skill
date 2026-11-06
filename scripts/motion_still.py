#!/usr/bin/env python3
"""Zero-credit "clip" from a still: a smooth, slow camera move (push-in, pull-out or pan) rendered frame by frame with
sub-pixel resampling, so it never jitters the way ffmpeg zoompan does. Run with the skill's own Python.

  motion_still.py <still.png> <out.mp4> [--move push|pull|left|right|up|down] [--seconds 5] [--strength 0.08]
  motion_still.py --shots <project_dir> [--only 03,07,12]
      makes clips/<id>.mp4 from stills/<id>.png for every shot in shots.json whose "clip" is "still"
      (or for the --only ids), using each shot's "move" (default push) and "strength"

Real AI animation (Kling / MiniMax) moves the characters; this moves only the camera. Use it for the budget tier, or
for calm shots (an establishing room, a calendar, a phone screen, the end) while the emotional and action shots get
real animation (the hybrid tier in references/production.md).
"""
import json
import os
import subprocess
import sys

from PIL import Image

W, H, FPS = 1080, 1920, 30


def ease(x):
    return x * x * (3 - 2 * x)          # smoothstep: starts and ends gently


def render(src, out, move='push', seconds=5.0, strength=.08):
    im = Image.open(src).convert('RGB')
    # cover-fit the still to 9:16 at 2x the output size, so the crop always has detail to spare
    tw, th = W * 2, H * 2
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    ox, oy = (im.width - tw) / 2, (im.height - th) / 2
    n = round(seconds * FPS)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out],
                           stdin=subprocess.PIPE)
    for f in range(n):
        k = ease(f / max(n - 1, 1))
        if move == 'pull':
            z = 1 + strength * (1 - k)
        elif move == 'push':
            z = 1 + strength * k
        else:
            z = 1 + strength              # pans need a little zoom so there is room to travel
        cw, ch = tw / z, th / z
        cx, cy = ox + tw / 2, oy + th / 2
        travel_x, travel_y = (tw - cw) / 2, (th - ch) / 2
        if move == 'left':
            cx += travel_x * (1 - 2 * k)
        elif move == 'right':
            cx -= travel_x * (1 - 2 * k)
        elif move == 'up':
            cy += travel_y * (1 - 2 * k)
        elif move == 'down':
            cy -= travel_y * (1 - 2 * k)
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        frame = im.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
        enc.stdin.write(frame.tobytes())
    enc.stdin.close()
    enc.wait()


def opt(name, default):
    a = sys.argv
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else default


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ('-h', '--help'):
        print(__doc__.strip())
        return 1
    if sys.argv[1] == '--shots':
        P = os.path.abspath(os.path.expanduser(sys.argv[2]))
        spec = json.load(open(f'{P}/shots.json', encoding='utf-8'))
        only = set(opt('--only', '').split(',')) - {''}
        os.makedirs(f'{P}/clips', exist_ok=True)
        done = 0
        for s in spec['shots']:
            if (only and s['id'] not in only) or (not only and s.get('clip') != 'still'):
                continue
            src = f"{P}/stills/{s['id']}.png"
            if not os.path.isfile(src):
                print(f"  missing still for shot {s['id']}: {src}")
                continue
            render(src, f"{P}/clips/{s['id']}.mp4", s.get('move', 'push'), float(s.get('seconds', 5)), float(s.get('strength', .08)))
            print(f"  {s['id']}: {s.get('move', 'push')} -> clips/{s['id']}.mp4", flush=True)
            done += 1
        print(f'{done} motion-still clips')
        return 0
    render(sys.argv[1], sys.argv[2], opt('--move', 'push'), float(opt('--seconds', 5)), float(opt('--strength', .08)))
    print(sys.argv[2])
    return 0


if __name__ == '__main__':
    sys.exit(main())
