#!/usr/bin/env python3
"""Cap the pauses in a voiceover (cuts only inside real silences, never inside a word), then an optional light tempo.
Run with the skill's own Python.

  tighten_vo.py <in.wav> <words.json> <out.wav> [--tempo 1.0] [--pause 0.30] [--sentence 0.42] [--beat word=0.6 ...]

  --pause     longest pause kept between words (default 0.30 s)
  --sentence  longest pause kept after a sentence ends (. ? !) (default 0.42 s)
  --beat      a word after which a dramatic pause stays longer, e.g. --beat counted=0.65 (story ads breathe)
  --tempo     0.95 to 1.08 sounds natural; 1.0 = unchanged
After it runs, transcribe the new file again (transcribe.py): the word times changed.
"""
import json
import re
import subprocess
import sys


def opt(name, default):
    a = sys.argv
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else default


def main():
    if len(sys.argv) < 4 or sys.argv[1] in ('-h', '--help'):
        print(__doc__.strip())
        return 1
    src, words_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    tempo = float(opt('--tempo', 1.0))
    pause, sentence = float(opt('--pause', .30)), float(opt('--sentence', .42))
    beats = {}
    for i, a in enumerate(sys.argv):
        if a == '--beat' and i + 1 < len(sys.argv) and '=' in sys.argv[i + 1]:
            w, s = sys.argv[i + 1].split('=', 1)
            beats[w.lower().strip()] = float(s)
    words = json.load(open(words_path, encoding='utf-8'))['words']
    r = subprocess.run(['ffmpeg', '-i', src, '-af', 'silencedetect=noise=-45dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', r.stderr)]
    silences = list(zip(starts, ends))
    keep, cursor = [], 0.0
    for i in range(len(words) - 1):
        end, nxt = words[i]['end'], words[i + 1]['start']
        raw = words[i]['word']
        w = re.sub(r'[^\w\']', '', raw.lower())
        cap = beats.get(w, sentence if raw.rstrip().endswith(('.', '?', '!')) else pause)
        sil = [s for s in silences if s[0] < nxt + .15 and s[1] > end - .15]
        if not sil:
            continue
        s0, s1 = max(sil, key=lambda s: s[1] - s[0])
        if s1 - s0 <= cap:
            continue
        cut_from, cut_to = s0 + cap * .6, s1 - cap * .4          # keep 60% of the pause after the sound, 40% before
        if cut_from > cursor and cut_to > cut_from:
            keep.append((cursor, cut_from))
            cursor = cut_to
    keep.append((cursor, words[-1]['end'] + .8))
    parts = [f'[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[s{k}]' for k, (a, b) in enumerate(keep)]
    fc = ';'.join(parts) + ';' + ''.join(f'[s{k}]' for k in range(len(keep))) + f'concat=n={len(keep)}:v=0:a=1'
    if abs(tempo - 1) > 1e-3:
        fc += f',atempo={tempo}'
    fc += '[out]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[out]', '-ar', '48000', out], check=True)
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip()
    print(f'{len(keep)} pieces, tempo {tempo}x -> {float(d):.2f}s  ({out})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
