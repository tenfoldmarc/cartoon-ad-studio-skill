# Production: voice, stills, clips, music (through the Arcads connector)

Everything is generated through the **Arcads connector** in Claude (tools named `arcads_*`). No API keys are pasted
anywhere. Read each tool's schema before the first call. Credits are the user's money: say the cost and wait for a yes
before every batch (Hard rule 1 in SKILL.md).

## The stack (tested Nov 2026 on 3 real shots, same start frame per model)

| Step | Tool | Setting | Cost (Arcads credits, Nov 2026) |
|---|---|---|---|
| Character sheets + scene stills | `arcads_generate_image_nano_banana` | `model: "nano-banana-2-1"`, `aspectRatio: "9:16"`, `resolution: "2K"`, up to 14 `referenceImages` | 0 when tested (Nov 2026); check `arcads_get_credits` before and after the first still |
| Animate each still (premium) | `arcads_generate_video_kling_30` | `startFrame` = the still's asset id, `aspectRatio: "9:16"`, `duration: 5` (3 to 15) | ~240 per 5 s clip |
| Animate each still (budget) | `arcads_generate_video_minimax_h3` | `startFrame` = the still's asset id, `aspectRatio: "9:16"`, `duration: 5` (5 to 15), `resolution: "720p"` | **72 per 5 s clip** (measured Nov 2026) |
| Camera-move clip (zero credits) | `SKILL/scripts/motion_still.py` | a smooth push, pull or pan over the still, made on the computer | 0 |
| Voiceover | `arcads_list_voices` then `arcads_text_to_speech` | `voiceId` from the list | small (tens) |
| Music bed | `arcads_create_music` | `model: "elevenlabs"`, `instrumentalOnly: true`, `duration` = ad length, optional `sections` | ~24 for 70 s |
| Downloads | `arcads_get_asset` (waitSeconds up to 40) then the `downloadUrl` it returns, or `arcads_get_download_link` | curl the signed URL into the project folder | 0 |
| Listen / watch check (optional) | `arcads_analyze_media` | Gemini, a second pair of ears | 0 |

Why Kling 3.0: it was the only model solid on all 3 test shots. It starts on the exact still, keeps the character and
any 3D text intact, and gives the sharpest output (1072x1928). Weakness: timid camera moves (asks for a tilt, gives a
push). Veo 3.1 follows complex action best but costs ~3x and changed a recurring face, so only use it (if the user
asks) for faceless-mannequin hero shots. Seedance 2.5 is good on slow emotional close-ups but failed a
hands-and-action shot and can't be locked to an exact first frame. The two defaults: Kling 3.0 (premium) and
MiniMax H3 (budget, 72 credits per 5 s), plus zero-credit camera-move clips; see the tiers below.

## Pick a tier (ask the user before Step 5; the clips are almost the whole bill)

| Tier | Clips | 31-shot ad, clips only | Looks |
|---|---|---|---|
| **Premium** | Kling 3.0 on every shot | ~7,400 credits | sharpest (1072x1928), holds faces and 3D text best |
| **Budget** (recommended start) | MiniMax H3 on every shot | ~2,250 credits (3.3x cheaper) | a touch softer (768x1344, scaled up in the edit), real character motion, follows camera moves well |
| **Hybrid** | MiniMax H3 (or Kling) on the 8 to 12 shots where someone acts or something happens (the hook, the knock, the turn, the ending); `motion_still.py` on the calm ones (rooms, calendars, screens, the CTA) | ~600 to 1,000 credits with H3 | most of the movement where it matters |
| **Zero** | `motion_still.py` on every shot | 0 credits for clips (the whole ad ~100 for voice + music) | a slideshow with smooth camera moves; good for testing a script or hook before spending |

Voice, music and stills are small next to the clips (stills cost 0 when tested). Always quote the real number from the
shot list: count the shots per clip type x the price above, plus 2 or 3 re-takes, and show the balance.

MiniMax H3 notes (tested Nov 2026 on a calm story shot from a real ad; not yet on a hands-and-action shot): it starts
on the exact still, kept both characters' faces and clothes, and did the push-in it was asked for. It makes its own
audio (dialogue / ambience); the edit drops clip audio, and the prompt still ends with "No text, no speech." If an
action shot breaks on H3 (hands, fast moves), re-take that one shot on Kling 3.0.
The winning cartoon ads all have real motion in every shot, so the Zero tier is for tests, not for the ad you scale.

Projects: create one Arcads project per ad (`arcads_create_project`) and pass its `projectId` to every generation, so
the user finds the whole ad in one place in the Arcads library. Save `productId` / `projectId` in project.json.
Give every generation a readable `title`: `<ad>_s07_still_v1`, `<ad>_c07_v2`, `<ad>_maya_sheet_v1`.

## Step 4: voice
1. `arcads_list_voices` with `language` (and `gender` / `age` if the narrator is known). Shortlist 3 or 4 that fit the
   format (A: calm, quick documentary narrator; B: warm, unhurried first person). Describe each by how it sounds.
2. Make a sample of the hook (first 2 or 3 lines) with each, download them, tell the user where they are and let them
   pick (or pick yourself if they said to).
3. Generate the full script with the chosen voice. Download to `audio/vo_raw.wav` (convert to wav with ffmpeg).
4. `PY SKILL/scripts/transcribe.py audio/vo_raw.wav audio/vo_raw_words.json --vocab "<brand, product, names>"`.
   Read the words against the script: a wrong word is fixed by re-generating that line, never by editing captions.
5. Tighten: `PY SKILL/scripts/tighten_vo.py audio/vo_raw.wav audio/vo_raw_words.json audio/vo_final.wav`
   (Format B: add `--beat` for the 2 or 3 lines that need a long pause, e.g. `--beat counted=0.7`).
6. Transcribe the final: `... transcribe.py audio/vo_final.wav audio/vo_words.json`. This is the file the edit uses.
7. Changing one line later: re-read just that line with the same voice and splice it in at the silences before and
   after it (ffmpeg atrim + concat, gain-matched), then transcribe again.

## Step 5: cast and stills
**Character sheets first** (Format B, or the mannequin in Format A): one image per character, front view, full body
and a face close-up, plain background, the exact outfit they wear in the ad, same style prompt as the shots. Prompt
shape: "Character sheet of <name>, <age>, <look: hair, skin, build>, wearing <outfit>. Front view full body and a
face close-up side by side, neutral pose, plain light grey background. <style>". Show the sheets, fix, then lock
their asset ids in `shots.json` `refs`.

**shots.json** (template: `SKILL/templates/shots.example.json`): one shot per script line or phrase.
- `vo`: the exact words said over this shot, in order. All shots together = the whole script, nothing missing.
- `caps`: how those words show as captions, 1 to 3 words per group, same words in the same order.
- `refs`: character names (their sheet) and/or `@NN` (another shot's still) to keep a set consistent.
- `anchor`: the location name. Shots in the same place reference the first still of that place (`@NN`).
- `still`: the frame, in detail: who (by "from the first reference"), where, what they do, the prop that carries the
  emotion, the light. End with nothing about style (the `style` string is added to every still).
- `motion`: what moves in 5 s, small and physical ("keeps typing, glances at the door; slow push-in"). Always end with
  "No text, no speech." Kling adds mouth movement and garbled text if you don't.

**Still prompt rules**
- One literal picture per line (playbook principle 5). Big 3D numbers inside the scene for Format A.
- Phone and laptop screens: describe what is on them in words, or keep them blurred. Stray text leaks onto screens;
  check every still for fake words and re-make it.
- Mirror the before/after scenes on purpose: same angle, same set, changed details.
- Keep the subject in the middle third (captions sit at 62% of the height, the platform UI covers the edges).

Generate stills in batches (`nbGenerations: 1`, a few calls in parallel), download to `stills/sNN.png`, then
`PY SKILL/scripts/qa.py stills qa/stills.jpg stills/*.png` and **look at it**. Check: same faces and clothes in every
shot, no extra fingers, no text where there should be none, the prop is there, the light matches the set. Re-make the
weak ones (bump the version in the title). Then show the user the contact sheet and the clip cost, and wait for a yes.

## Step 6: clips
Each shot's `clip` field in shots.json says how it is made: `"kling"`, `"minimax"` or `"still"` (default: the tier
the user picked).
- `kling`: `arcads_generate_video_kling_30`, `startFrame` = that still's asset id, `prompt` = the shot's `motion`,
  `aspectRatio: "9:16"`, `duration: 5` (use more only if the shot is longer than 5 s in the timeline; a shot can also
  hold its last frame for a beat).
- `minimax`: `arcads_generate_video_minimax_h3`, same `startFrame` / `prompt` / `aspectRatio`, `duration: 5`,
  `resolution: "720p"`.
- `still`: no credits. `PY SKILL/scripts/motion_still.py --shots <project>` makes `clips/<id>.mp4` for every shot
  marked `"still"`, using its `move` (`push` default, `pull`, `left`, `right`, `up`, `down`) and `strength`
  (0.08 default; 0.04 subtle, 0.14 strong). Vary the moves from shot to shot so it doesn't feel mechanical.
Run the paid ones in parallel, a handful at a time.
- Download each to `clips/<id>.mp4` (the shot id, e.g. `clips/07.mp4`). Clips come with no needed audio; the edit
  drops their audio.
- QA: `PY SKILL/scripts/qa.py clips qa/clips_1.jpg clips/0*.mp4` (and the rest) and look at every row. Re-take a clip
  when a face melts or changes, hands break, text warps, or nothing moves. Usually 0 to 3 re-takes per ad.
- Where in a clip each shot starts: by default 35% of the spare length; override per shot in `offsets.json`
  (`{"07": 0.4}`) when the best moment is earlier or later.

## Step 7: music
`arcads_create_music`, `model: "elevenlabs"`, `instrumentalOnly: true`, `duration` = the timeline total (rounded up).
Describe the music in musical terms only (genre, mood, instruments, tempo, how it evolves); naming an artist, film or
brand gets the request rejected. Format B: gentle piano and soft strings, warm, lifting in the last third. Format A:
light curious documentary underscore, pizzicato and soft synth pulse, ~100 BPM. Use `sections` to lift the music at
the turn (the messenger / the reframe) and to swell under the end card. Download to `audio/music.wav`.

Sound effects (optional, few): put files in `audio/sfx/` and list them in project.json `sfx` with the shot they land
in. A knock, a ding, a click. Use sounds the user owns or royalty-free ones; never generate fake "sound effects" with a
music model.

## Downloading an asset
`arcads_get_asset` with `waitSeconds: 40` until `status` is `generated`, then download its `downloadUrl` with
`curl -sL -o <file> "<url>"` (the URL is signed and expires; fetch it fresh if a download fails). Never print or save
the user's Arcads credentials; the connector handles them.
