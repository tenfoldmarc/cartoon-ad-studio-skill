# Production: voice, stills, clips, music (with the tools the user has connected)

The skill does not depend on one platform. It needs four capabilities, each from whatever tool the user connected to
Claude (Step 0 of SKILL.md finds them and saves the choice in config.json `tools`):

| Capability | What it must do | Recommended / examples |
|---|---|---|
| **Voice** | text to speech with a choice of voices | **ElevenLabs** (official connector in Claude's connector directory) |
| **Music** | an instrumental bed of an exact length | ElevenLabs music (same connector), any music tool, or a royalty-free track the user supplies |
| **Stills** | image generation with **reference images** (to keep the same characters in every shot), portrait 9:16 | Nano Banana (Gemini image) or the strongest reference-capable image model on their tool |
| **Clips** | **image-to-video from a start frame**, 9:16, 5 s | Kling 3.0 (premium), a cheaper start-frame model such as MiniMax / Hailuo (budget), on whatever video tool they use (Higgsfield, OpenArt, fal, Kling, or another) |

Read each tool's schema before its first call, and use its own parameter names: the start frame may be called
`startFrame`, `image`, `first_frame` or `image_url`; aspect ratio `9:16`; duration 5 s; switch generated audio off
when the tool allows it (the edit drops clip audio either way). Money is the user's: quote the cost from the tool's own
price (its pricing page, the tool description, or the cost shown on a first single generation) and wait for a yes
before every batch (Hard rule 1 in SKILL.md). If a tool can't show prices, make ONE item first, check what it cost,
then quote the batch.

Name every generation readably when the tool allows a title: `<ad>_s07_still_v1`, `<ad>_c07_v2`, `<ad>_maya_sheet_v1`.
Keep a project/folder per ad on the tool if it has one, so the user finds the whole ad in one place.

## The models, from a side-by-side test (Nov 2026, same start frame per model, one platform)
- **Kling 3.0** was the only model solid on all 3 test shots: starts on the exact still, keeps the character and any 3D
  text intact, sharpest output (about 1080x1920). Weakness: timid camera moves (asks for a tilt, gives a push).
- **MiniMax H3** (budget): about **a third of Kling 3.0's price** on the platform tested. Started on the exact still,
  kept both characters' faces and clothes on a calm story shot and did the push-in it was asked for. A touch softer
  (768x1344, scaled up in the edit). Not yet tested on a hands-and-action shot: if one breaks, re-take that shot on
  the premium model.
- **Veo 3.1** follows complex action best but cost about 3x Kling and changed a recurring face: only for faceless
  "mannequin" hero shots, and only if the user asks.
- **Seedance 2.5** is good on slow emotional close-ups but failed a hands-and-action shot and could not be locked to an
  exact first frame on the platform tested.
Prices differ by tool and change often: always quote the user's own tool, never these.

## Pick a tier (ask the user before Step 5; the clips are almost the whole bill)

| Tier | Clips | Cost of the clips | Looks |
|---|---|---|---|
| **Premium** | Kling 3.0 (or their tool's best start-frame model) on every shot | highest: shots x the premium price | sharpest, holds faces and 3D text best |
| **Budget** (recommended start) | a cheap start-frame model (MiniMax / Hailuo class) on every shot | about a third of Premium | a touch softer, real character motion |
| **Hybrid** | real animation (Budget or Premium model) on the 8 to 12 shots where someone acts or something happens (the hook, the knock, the turn, the ending); `motion_still.py` on the calm ones (rooms, calendars, screens, the CTA) | about a third of the chosen model's full-ad price | most of the movement where it matters |
| **Zero** | `SKILL/scripts/motion_still.py` on every shot | nothing for the clips (only the voice and music) | a slideshow with smooth camera moves; good for testing a script or hook before spending |

Quote the real numbers: shots per clip type x the user's tool price, plus 2 or 3 re-takes, and their balance if the
tool shows one. Voice, music and stills are small next to the clips.
The winning cartoon ads all have real motion in every shot, so the Zero tier is for tests, not for the ad you scale.

## Step 4: voice (ElevenLabs recommended)
1. List voices (ElevenLabs: search the voice library by language, gender, age and use case such as "narration" or
   "storytelling"). Shortlist 3 or 4 that fit the format (A: calm, quick documentary narrator; B: warm, unhurried first
   person). Describe each by how it sounds.
2. Make a sample of the hook (first 2 or 3 lines) with each, save them in `audio/samples/`, tell the user where they are
   and let them pick (or pick yourself if they said to).
3. Generate the full script with the chosen voice. Save to `audio/vo_raw.wav` (convert to wav with ffmpeg if the tool
   returns mp3). Use a stable, natural setting (ElevenLabs: a multilingual / v3 model, stability around the middle).
4. `PY SKILL/scripts/transcribe.py audio/vo_raw.wav audio/vo_raw_words.json --vocab "<brand, product, names>"`.
   Read the words against the script: a wrong word is fixed by re-generating that line, never by editing captions.
5. Tighten: `PY SKILL/scripts/tighten_vo.py audio/vo_raw.wav audio/vo_raw_words.json audio/vo_final.wav`
   (Format B: add `--beat` for the 2 or 3 lines that need a long pause, e.g. `--beat counted=0.7`).
6. Transcribe the final: `... transcribe.py audio/vo_final.wav audio/vo_words.json`. This is the file the edit uses.
7. Changing one line later: re-read just that line with the same voice and splice it in at the silences before and
   after it (ffmpeg atrim + concat, gain-matched), then transcribe again.
Save the voice name and id in project.json `voice`.

## Step 5: cast and stills
**Character sheets first** (Format B, or the mannequin in Format A): one image per character, front view, full body
and a face close-up, plain background, the exact outfit they wear in the ad, same style prompt as the shots. Prompt
shape: "Character sheet of <name>, <age>, <look: hair, skin, build>, wearing <outfit>. Front view full body and a
face close-up side by side, neutral pose, plain light grey background. <style>". Show the sheets, fix, then save each
sheet (file path or the tool's asset id) in `shots.json` `refs`.

**shots.json** (template: `SKILL/templates/shots.example.json`): one shot per script line or phrase.
- `vo`: the exact words said over this shot, in order. All shots together = the whole script, nothing missing.
- `caps`: how those words show as captions, 1 to 3 words per group, same words in the same order.
- `refs`: character names (their sheet) and/or `@NN` (another shot's still) to keep a set consistent.
- `anchor`: the location name. Shots in the same place reference the first still of that place (`@NN`).
- `still`: the frame, in detail: who (by "from the first reference"), where, what they do, the prop that carries the
  emotion, the light. End with nothing about style (the `style` string is added to every still).
- `motion`: what moves in 5 s, small and physical ("keeps typing, glances at the door; slow push-in"). Always end with
  "No text, no speech." Video models add mouth movement and garbled text if you don't.
- `clip`: `premium`, `budget` or `still` (Step 6); `move` / `strength` for `still` shots.

**Still prompt rules**
- One literal picture per line (playbook principle 5). Big 3D numbers inside the scene for Format A.
- Phone and laptop screens: describe what is on them in words, or keep them blurred. Stray text leaks onto screens;
  check every still for fake words and re-make it.
- Mirror the before/after scenes on purpose: same angle, same set, changed details.
- Keep the subject in the middle third (captions sit at 62% of the height, the platform UI covers the edges).

Generate stills in small batches, save to `stills/<id>.png`, then
`PY SKILL/scripts/qa.py stills qa/stills.jpg stills/*.png` and **look at it**. Check: same faces and clothes in every
shot, no extra fingers, no text where there should be none, the prop is there, the light matches the set. Re-make the
weak ones (bump the version in the title). Then show the user the contact sheet and the tier quote, and wait for a yes.

## Step 6: clips
Each shot's `clip` field says how it is made (default: the tier the user picked):
- `premium` / `budget`: the user's video tool, image-to-video, start frame = that shot's still, prompt = the shot's
  `motion`, 9:16, 5 s (more only if the shot runs longer than 5 s in the timeline; a shot can also hold its last frame
  for a beat), generated audio off if the tool allows it.
- `still`: no cost. `PY SKILL/scripts/motion_still.py --shots <project>` makes `clips/<id>.mp4` for every shot
  marked `"still"`, using its `move` (`push` default, `pull`, `left`, `right`, `up`, `down`) and `strength`
  (0.08 default; 0.04 subtle, 0.14 strong). Vary the moves from shot to shot so it doesn't feel mechanical.
Run the paid ones in parallel, a handful at a time. Save each to `clips/<id>.mp4` (the shot id, e.g. `clips/07.mp4`).
- QA: `PY SKILL/scripts/qa.py clips qa/clips_1.jpg clips/0*.mp4` (and the rest) and look at every row. Re-take a clip
  when a face melts or changes, hands break, text warps, or nothing moves. Usually 0 to 3 re-takes per ad.
- Where in a clip each shot starts: by default 35% of the spare length; override per shot in `offsets.json`
  (`{"07": 0.4}`) when the best moment is earlier or later.

## Step 7: music
An instrumental bed exactly as long as the timeline `total` (rounded up). ElevenLabs music (or the user's music tool):
describe the music in musical terms only (genre, mood, instruments, tempo, how it evolves); naming an artist, film or
brand often gets a request rejected. Format B: gentle piano and soft strings, warm, lifting in the last third.
Format A: light curious documentary underscore, pizzicato and soft synth pulse, ~100 BPM. If the tool takes timed
sections, lift the music at the turn (the messenger / the reframe) and swell under the end card. Save to
`audio/music.wav`. No music tool? A royalty-free track the user owns works; the edit fades it under the voice.

Sound effects (optional, few): put files in `audio/sfx/` and list them in project.json `sfx` with the shot they land
in. A knock, a ding, a click. Use sounds the user owns or royalty-free ones (ElevenLabs can also make short sound
effects).

## Saving results
Most tools return a download URL or a file: save every result into the project folder right away
(`curl -sL -o <file> "<url>"`; signed URLs expire, so fetch a fresh one if a download fails). Never print, paste or
save the user's API keys or passwords; connectors handle sign-in.
