#!/usr/bin/env python3
"""Time every shot to the voiceover's word timings. Standard library only.

  timeline.py <project_dir>

Reads <project>/shots.json (each shot's "vo" = the exact words said over it, in order) and
<project>/audio/vo_words.json (transcribe.py). Each shot starts at its first word (minus a small lead) and ends where
the next shot starts; the last shot runs 0.3 s past the last word, then the end card (project.json end_card.seconds).
Writes <project>/timeline.json and prints the shot table.
Fails loudly if the script and the transcript disagree: fix the "vo" text (write it the way the transcript spells it,
numbers as digits if Whisper wrote digits) or fix the voiceover, then run again.
"""
import json
import os
import re
import sys

LEAD = 0.08
nz = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__.strip())
        return 1
    P = os.path.abspath(os.path.expanduser(sys.argv[1]))
    spec = json.load(open(f'{P}/shots.json', encoding='utf-8'))
    proj = json.load(open(f'{P}/project.json', encoding='utf-8')) if os.path.isfile(f'{P}/project.json') else {}
    end_card = float(proj.get('end_card', {}).get('seconds', 3.0))
    words = json.load(open(f'{P}/audio/vo_words.json', encoding='utf-8'))['words']
    wi, out = 0, []
    for shot in spec['shots']:
        target = nz(shot['vo'])
        first, got = wi, ''
        while wi < len(words) and len(got) < len(target):
            got += nz(words[wi]['word'])
            wi += 1
        if got != target:
            raise SystemExit(f"shot {shot['id']}: script {target!r} != transcript {got!r} (near {words[first]['start'] if first < len(words) else 'end'}s)")
        out.append({'id': shot['id'], 'w0': first, 'w1': wi - 1, 'vo': shot['vo']})
    if wi != len(words):
        raise SystemExit(f'{len(words) - wi} transcript words left over after the last shot: {[w["word"] for w in words[wi:wi + 8]]}')
    for k, s in enumerate(out):
        s['start'] = 0.0 if k == 0 else round(words[s['w0']]['start'] - LEAD, 3)
    for k, s in enumerate(out):
        s['end'] = out[k + 1]['start'] if k + 1 < len(out) else round(words[-1]['end'] + 0.3, 3)
        s['dur'] = round(s['end'] - s['start'], 3)
    vo_end = out[-1]['end']
    json.dump({'shots': out, 'vo_end': vo_end, 'end_card': end_card, 'total': round(vo_end + end_card, 3)},
              open(f'{P}/timeline.json', 'w', encoding='utf-8'), indent=1)
    for s in out:
        flag = '  << long for one clip' if s['dur'] > 9.5 else ''
        print(f"{s['id']} {s['start']:6.2f}-{s['end']:6.2f} ({s['dur']:4.2f}s) {s['vo']}{flag}")
    print(f'VO ends {vo_end:.2f}s, total with end card {vo_end + end_card:.2f}s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
