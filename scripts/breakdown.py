#!/usr/bin/env python3
"""Break down winning reference ads (videos you saved from the Meta Ad Library, TikTok Creative Center, etc.).
Run with the skill's own Python (<skill>/.venv).

  breakdown.py <project_dir> <ad1.mp4> [<ad2.mp4> ...] [--model small.en]

For every ad, into <project_dir>/breakdown/<adN>/:
  transcript.json   words with times (faster-whisper)
  scenes.json       hard cuts (ffmpeg scene detection) -> shot list with start/end
  sheet_NN.jpg      contact sheets, one tile every 2 s, 8 tiles per row, time stamped
and a summary line: length, shots, average shot length, words per minute, first line said.
Claude then looks at the sheets and reads the transcripts to write the breakdown (formats in references/playbook.md).
Nothing is uploaded anywhere.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(SKILL, 'fonts', 'InterTight-Variable.ttf')


def probe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_type',
                        '-of', 'json', p], capture_output=True, text=True)
    d = json.loads(r.stdout or '{}')
    v = next((s for s in d.get('streams', []) if s.get('codec_type') == 'video'), {})
    return float(d.get('format', {}).get('duration', 0)), v.get('width'), v.get('height')


def scenes(p, thr=0.30):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-vf', f"select='gt(scene,{thr})',showinfo", '-an', '-f', 'null', '-'],
                       capture_output=True, text=True)
    return [float(x) for x in re.findall(r'pts_time:([0-9.]+)', r.stderr)]


def sheets(p, out_dir, dur, step=2.0, cols=8, rows=4):
    os.makedirs(out_dir, exist_ok=True)
    tw, th = 180, 320
    font = ImageFont.truetype(FONT, 20) if os.path.isfile(FONT) else ImageFont.load_default()
    times = [t for t in [i * step + .2 for i in range(int(dur / step) + 1)] if t < dur]
    per = cols * rows
    made = []
    with tempfile.TemporaryDirectory() as d:
        for k in range(0, len(times), per):
            chunk = times[k:k + per]
            sheet = Image.new('RGB', (cols * tw, ((len(chunk) + cols - 1) // cols) * th), (15, 15, 15))
            dr = ImageDraw.Draw(sheet)
            for i, t in enumerate(chunk):
                f = os.path.join(d, f'{k + i}.jpg')
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', p, '-frames:v', '1',
                                '-vf', f'scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2', f],
                               check=True)
                x, y = (i % cols) * tw, (i // cols) * th
                sheet.paste(Image.open(f), (x, y))
                dr.rectangle((x, y, x + 64, y + 26), fill=(0, 0, 0))
                dr.text((x + 5, y + 2), f'{t:.0f}s', fill=(255, 220, 0), font=font)
            o = os.path.join(out_dir, f'sheet_{k // per + 1:02d}.jpg')
            sheet.save(o, quality=85)
            made.append(o)
    return made


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ('-h', '--help'):
        print(__doc__.strip())
        return 1
    proj = os.path.abspath(os.path.expanduser(sys.argv[1]))
    ads = [a for a in sys.argv[2:] if not a.startswith('--') and a not in ('small.en', 'base.en', 'medium.en')]
    model = sys.argv[sys.argv.index('--model') + 1] if '--model' in sys.argv else 'small.en'
    from faster_whisper import WhisperModel
    m = WhisperModel(model, compute_type='int8')
    summary = []
    for n, ad in enumerate(ads, 1):
        name = f'ad{n}'
        od = os.path.join(proj, 'breakdown', name)
        os.makedirs(od, exist_ok=True)
        dur, w, h = probe(ad)
        cuts = [c for c in scenes(ad) if .3 < c < dur - .3]
        bounds = [0.0] + cuts + [dur]
        shots = [dict(n=i + 1, start=round(a, 2), end=round(b, 2), dur=round(b - a, 2)) for i, (a, b) in enumerate(zip(bounds, bounds[1:]))]
        with tempfile.TemporaryDirectory() as d:
            wav = os.path.join(d, 'a.wav')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', ad, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
            segs, _ = m.transcribe(wav, word_timestamps=True, vad_filter=True, beam_size=5)
            words = [dict(word=x.word.strip(), start=round(x.start, 2), end=round(x.end, 2)) for s in segs for x in s.words]
        text = ' '.join(x['word'] for x in words)
        json.dump({'source': os.path.abspath(ad), 'duration': dur, 'words': words, 'text': text}, open(os.path.join(od, 'transcript.json'), 'w'), indent=1)
        json.dump({'source': os.path.abspath(ad), 'size': [w, h], 'shots': shots}, open(os.path.join(od, 'scenes.json'), 'w'), indent=1)
        made = sheets(ad, od, dur)
        wpm = len(words) / (dur / 60) if dur else 0
        first = ' '.join(x['word'] for x in words[:18])
        line = (f'{name}: {os.path.basename(ad)}  {dur:.1f}s  {w}x{h}  {len(shots)} shots  avg {dur / max(len(shots), 1):.1f}s/shot  '
                f'{wpm:.0f} wpm  sheets {len(made)}\n   opens: "{first}..."')
        print(line, flush=True)
        summary.append(line)
    with open(os.path.join(proj, 'breakdown', 'SUMMARY.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
