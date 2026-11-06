#!/usr/bin/env python3
"""Assemble the finished cartoon ad: shots cut to the voiceover (hard cuts, frame exact), small centered captions,
end card, voiceover + music bed (+ optional sound cues), loudness -14 LUFS. Run with the skill's own Python.

  build.py <project_dir> [--out out/<name>.mp4]

Inputs in <project_dir>:
  project.json            name, end card, caption position, optional sound cues (templates/project.example.json)
  shots.json              per shot: id, vo, caps (caption groups, words in order), optional display fixes
  timeline.json           from timeline.py
  audio/vo_final.wav      the voiceover; audio/vo_words.json its word times (transcribe.py)
  audio/music.wav         music bed (optional: without it the ad is voice only)
  clips/<id>.mp4          one animated clip per shot (any size; cropped to fill 9:16)
  offsets.json            optional {shot id: seconds into the clip to start from}
Writes out/<name>.mp4 (1080x1920, 30 fps) and out/<name>_phone.mp4 (smaller copy to send to a phone).
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(SKILL, 'fonts', 'InterTight-Variable.ttf')
W, H, FPS = 1080, 1920, 30


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout.strip())


def font(size, weight='Bold'):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__.strip())
        return 1
    P = os.path.abspath(os.path.expanduser(sys.argv[1]))     # absolute: ffmpeg reads list files relative to the list
    proj = json.load(open(f'{P}/project.json', encoding='utf-8'))
    name = proj.get('name', 'cartoon-ad')
    out = os.path.abspath(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else f'{P}/out/{name}.mp4'
    work = f'{P}/work'
    os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tl = json.load(open(f'{P}/timeline.json', encoding='utf-8'))
    spec = json.load(open(f'{P}/shots.json', encoding='utf-8'))
    shots = {s['id']: s for s in spec['shots']}
    display = spec.get('display', {})
    words = json.load(open(f'{P}/audio/vo_words.json', encoding='utf-8'))['words']
    offsets = json.load(open(f'{P}/offsets.json')) if os.path.isfile(f'{P}/offsets.json') else {}
    total = tl['total']
    ec = proj.get('end_card', {})
    bg, accent, text = rgb(ec.get('bg', '#0b1220')), rgb(ec.get('accent', '#f5b072')), rgb(ec.get('text', '#faf3e8'))

    # 1. shots, frame exact so rounding never drifts
    segs = []
    for s in tl['shots']:
        src = f"{P}/clips/{s['id']}.mp4"
        if not os.path.isfile(src):
            raise SystemExit(f'missing clip for shot {s["id"]}: {src}')
        clip_len = probe_dur(src)
        n = round(s['end'] * FPS) - round(s['start'] * FPS)
        dur = n / FPS
        if dur > clip_len + .05:
            print(f'  note: shot {s["id"]} needs {dur:.2f}s but its clip is {clip_len:.2f}s; the last frame holds')
        off = float(offsets.get(s['id'], max(0.0, (clip_len - dur) * .35)))
        off = max(0.0, min(off, max(0.0, clip_len - dur - .05)))
        seg = f"{work}/seg_{s['id']}.mp4"
        vf = (f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},'
              f'tpad=stop_mode=clone:stop_duration=10,eq=contrast=1.02:saturation=1.03')
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{off:.3f}', '-i', src, '-frames:v', str(n), '-an', '-vf', vf,
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', seg])
        segs.append(seg)

    # 2. end card
    card = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(card)
    fk, ft, fo, fu = font(int(W * .042), 'SemiBold'), font(int(W * .105), 'Bold'), font(int(W * .05), 'SemiBold'), font(int(W * .036), 'SemiBold')
    y = int(H * .38)
    if ec.get('kicker'):
        kw = d.textlength(ec['kicker'], font=fk)
        px, py = int(W * .03), int(W * .012)
        d.rounded_rectangle(((W - kw) / 2 - px, y - py, (W + kw) / 2 + px, y + int(W * .055) + py), radius=int(W * .03), fill=accent)
        d.text(((W - kw) / 2, y), ec['kicker'], font=fk, fill=bg)
        y += int(W * .13)
    for line in ec.get('title', [proj.get('brand', '')]):
        lw = d.textlength(line, font=ft)
        d.text(((W - lw) / 2, y), line, font=ft, fill=text)
        y += int(W * .125)
    if ec.get('offer'):
        ow = d.textlength(ec['offer'], font=fo)
        d.text(((W - ow) / 2, y + int(W * .02)), ec['offer'], font=fo, fill=accent)
        y += int(W * .08)
    if ec.get('url'):
        by = y + int(W * .03)
        d.rounded_rectangle(((W - W * .16) / 2, by, (W + W * .16) / 2, by + max(4, W // 160)), radius=3, fill=accent)
        uw = d.textlength(ec['url'], font=fu)
        d.text(((W - uw) / 2, by + int(W * .045)), ec['url'], font=fu, fill=accent)
    card.save(f'{work}/endcard.png')
    frames = round(total * FPS) - round(tl['vo_end'] * FPS)
    if frames > 0:
        run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', f'{work}/endcard.png', '-frames:v', str(frames), '-vf',
             f'fps={FPS},format=yuv420p,fade=t=in:st=0:d=0.3', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', f'{work}/seg_end.mp4'])
        segs.append(f'{work}/seg_end.mp4')

    # 3. concat
    with open(f'{work}/concat.txt', 'w') as fh:
        fh.writelines(f"file '{p}'\n" for p in segs)
    video = f'{work}/video_nocap.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{work}/concat.txt', '-c', 'copy', video])

    # 4. captions: the shot's caption groups, timed by its own words
    cap_cfg = proj.get('captions', {})
    cap_font = font(int(W * float(cap_cfg.get('size', .056))), cap_cfg.get('weight', 'SemiBold'))
    cap_y = int(H * float(cap_cfg.get('y', .62)))
    chunks = []
    for s in tl['shots']:
        sw = words[s['w0']:s['w1'] + 1]
        caps = shots[s['id']].get('caps') or [shots[s['id']]['vo']]
        if sum(len(c.split()) for c in caps) != len(sw):
            raise SystemExit(f"shot {s['id']}: caption words ({sum(len(c.split()) for c in caps)}) != spoken words ({len(sw)}): "
                             f"{[w['word'] for w in sw]}")
        pos = 0
        for c in caps:
            k = len(c.split())
            shown = c
            for key in sorted(display, key=len, reverse=True):            # e.g. "at 4 o clock" -> "at 4 o'clock"
                if f' {key} ' in f' {shown} ':
                    shown = f' {shown} '.replace(f' {key} ', f' {display[key]} ').strip()
            chunks.append((shown, sw[pos]['start'], sw[pos + k - 1]['end']))
            pos += k
    Image.new('RGBA', (W, H), (0, 0, 0, 0)).save(f'{work}/cap_blank.png')
    entries, t = [], 0.0
    for k, (txt, a, end) in enumerate(chunks):
        a = max(a, t)
        b = min(chunks[k + 1][1] if k + 1 < len(chunks) else end + .3, end + .35)
        if b - a < .05:
            continue
        if a > t + .01:
            entries.append((f'{work}/cap_blank.png', a - t))
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        tw = ImageDraw.Draw(img).textlength(txt, font=cap_font)
        x = (W - tw) / 2
        halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(halo).text((x, cap_y), txt, font=cap_font, fill=(0, 0, 0, 190), stroke_width=max(2, W // 180), stroke_fill=(0, 0, 0, 190))
        halo = halo.filter(ImageFilter.GaussianBlur(max(3, W // 120)))
        shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text((x, cap_y + max(1, W // 400)), txt, font=cap_font, fill=(0, 0, 0, 220))
        shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, W // 500)))
        img = Image.alpha_composite(Image.alpha_composite(halo, shadow), img)
        ImageDraw.Draw(img).text((x, cap_y), txt, font=cap_font, fill=(255, 255, 255, 255))
        p = f'{work}/cap_{k:03d}.png'
        img.save(p)
        entries.append((p, b - a))
        t = b
    entries.append((f'{work}/cap_blank.png', max(.1, total - t)))
    with open(f'{work}/captions.txt', 'w') as fh:
        for p, dur in entries:
            fh.write(f"file '{p}'\nduration {dur:.3f}\n")
        fh.write(f"file '{entries[-1][0]}'\n")
    cap_video = f'{work}/captions.mov'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{work}/captions.txt', '-vf', f'fps={FPS},format=rgba',
         '-c:v', 'qtrle', cap_video])

    # 5. audio: voice leveled to -16 LUFS, music bed well under it (louder on the end card), few quiet cues, -14 LUFS out
    st = {s['id']: s['start'] for s in tl['shots']}
    inputs = ['-i', f'{P}/audio/vo_final.wav']
    filters = ['[0:a]aresample=48000,loudnorm=I=-16:TP=-2:LRA=11[vo]']
    mix = ['[vo]']
    music = f'{P}/audio/music.wav'
    if os.path.isfile(music):
        under, end_g = float(proj.get('music_gain_under_vo', .22)), float(proj.get('music_gain_end', .55))
        inputs += ['-i', music]
        filters.append(f"[1:a]aresample=48000,loudnorm=I=-16:TP=-2:LRA=11,volume='if(lt(t,{tl['vo_end']}),{under},{end_g})':eval=frame,"
                       f"afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5[mus]")
        mix.append('[mus]')
    for k, cue in enumerate(proj.get('sfx', [])):
        f = cue['file'] if os.path.isabs(cue['file']) else f"{P}/{cue['file']}"
        at = st.get(cue.get('shot'), 0.0) + float(cue.get('offset', 0))
        ms = int(at * 1000)
        inputs += ['-i', f]
        filters.append(f"[{len(mix)}:a]aresample=48000,volume={float(cue.get('gain', .5))},adelay={ms}|{ms}[x{k}]")
        mix.append(f'[x{k}]')
    filters.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,apad=whole_dur={total:.3f},"
                   f"atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    audio = f'{work}/mix.wav'
    run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters), '-map', '[aout]', '-ar', '48000', audio])

    # 6. final + phone copy
    run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', cap_video, '-i', audio, '-filter_complex',
         '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'slow',
         '-crf', '17', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', f'{total:.3f}', out])
    phone = out[:-4] + '_phone.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-crf', '24',
         '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', phone])
    print(f'{out}  {probe_dur(out):.2f}s\n{phone}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
