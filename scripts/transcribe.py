#!/usr/bin/env python3
"""Transcribe an audio or video file with word timestamps (faster-whisper, runs on your computer, no API key).
Run with the skill's own Python (<skill>/.venv).

  transcribe.py <audio_or_video> <out.json> [--model small.en] [--language en] [--vocab "Brand, Product"]

Writes {"duration": s, "text": "...", "words": [{"word": "...", "start": s, "end": s}, ...]} and prints the words with
times. --vocab nudges the spelling of brand and product names (it is a hint, not a guarantee: always read the words).
The voiceover is transcribed once after it is final; timeline.py and build.py read this file.
"""
import json
import os
import subprocess
import sys
import tempfile


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else default


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ('-h', '--help'):
        print(__doc__.strip())
        return 1
    src, out = sys.argv[1], sys.argv[2]
    model_name = arg('--model', 'small.en')
    lang = arg('--language', 'en')
    vocab = arg('--vocab')
    from faster_whisper import WhisperModel
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, 'a.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
        m = WhisperModel(model_name, compute_type='int8')
        segs, info = m.transcribe(wav, word_timestamps=True, vad_filter=False, condition_on_previous_text=False,
                                  language=None if model_name.endswith('.en') else lang, initial_prompt=vocab, beam_size=5)
        words = [dict(word=w.word.strip(), start=round(w.start, 3), end=round(w.end, 3)) for s in segs for w in s.words]
        dur = info.duration
    data = {'duration': round(dur, 3), 'text': ' '.join(w['word'] for w in words), 'words': words}
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
    print(f'{len(words)} words, {dur:.2f}s -> {out}')
    print(' '.join(f"{w['word']}@{w['start']:.2f}" for w in words))
    return 0


if __name__ == '__main__':
    sys.exit(main())
