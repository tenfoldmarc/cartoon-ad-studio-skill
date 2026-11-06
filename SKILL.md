---
name: cartoon-ad-studio
description: "Make viral Pixar-style cartoon video ads for any offer, the format top advertisers are spending millions on: study winning cartoon ads, research the sales page (dream outcomes, pain points), write the script, voice it, generate the characters and every shot, animate them with Kling 3.0 and edit the finished 9:16 ad with captions, music and an end card. Uses the Arcads connector for stills, clips, voice and music. Use for /cartoon-ad-studio, 'make me a cartoon ad', 'Pixar style ad', 'viral cartoon ad for my offer', 'animated story ad', 'copy this cartoon ad format'."
---

# /cartoon-ad-studio

Turns a sales page into a finished cartoon video ad, the same way the best-performing cartoon ads in the Meta Ad
Library are built: a story or a surprising "what if" told by a narrator over Pixar-style 3D shots, hard cuts, small
centered captions, a music bed and a 3 second end card.

The pipeline: **(1) study winners -> (2) research the sales page -> (3) script -> (4) voiceover -> (5) characters +
stills -> (6) animate -> (7) music + edit -> (8) QA and deliver.**

Four budget tiers for the animation, the step that is almost the whole cost (31-shot ad, clips only): **Premium**
Kling 3.0 ~7,400 credits, **Budget** MiniMax H3 ~2,250, **Hybrid** H3 on the acting shots + free camera-move clips on
the calm ones ~600 to 1,000, **Zero** camera-move clips only, 0 (about 100 for the whole ad). Details and when to
use which: `SKILL/references/production.md`, "Pick a tier".

`SKILL` below means this skill's folder (the one holding this file). `PY` means `SKILL/.venv/bin/python`
(Windows: `SKILL\.venv\Scripts\python.exe`). Scripts print plain progress; read their output, don't guess.
Read `SKILL/references/playbook.md` before writing any script, `SKILL/references/research.md` for Step 2 and
`SKILL/references/production.md` before Step 4.

| Command | What happens |
|---|---|
| `/cartoon-ad-studio` | The whole ad: Steps 1 to 8 |
| `/cartoon-ad-studio study <videos>` | Only break down reference ads (Step 1) |
| `/cartoon-ad-studio script` | Research + script only, no credits spent (Steps 2 and 3) |
| `/cartoon-ad-studio budget` | The whole ad on the cheapest real-animation tier (MiniMax H3) unless they pick another |
| `/cartoon-ad-studio resume` | Carry on an ad already started (reads its folder and picks up at the first missing step) |
| `/cartoon-ad-studio setup` | Run or redo first-time setup (Step 0) |

## Hard rules
1. **Credits move only on a yes.** Before every paid batch (voice samples, stills, clips, music) say what will be made
   and its cost in Arcads credits, plus the balance (`arcads_get_credits`), and wait for the user's yes in chat. One
   yes covers one batch. Re-takes of a few clips can share one yes if you said so.
2. **No fake proof.** Characters are fictional and the story is presented as a story, never as a real customer. No
   invented results, reviews, screenshots, follower counts or income claims. Every product claim must match what the
   product really does (the claims check in SCRIPT.md). Numbers about the offer come from the sales page or the user.
3. **The script is approved before anything is generated**, and the stills contact sheet is approved before any clip is
   animated. Clips are the expensive step.
4. **No copying.** Study what makes winners work (structure, pacing, look); never re-use another brand's characters,
   script lines, logos, music or footage. Name sounds and styles in plain words, never "in the style of <brand/film>".
5. **Captions say what the voice says.** The caption groups in shots.json use the transcript's words in order;
   build.py fails if they don't match. Fix the voice, not the captions.
6. **No em dashes** in any script line, caption or on-screen text.
7. Nothing is ever deleted; reference videos and the user's files are only read. Everything for an ad lives in its
   project folder.

## Step 0. First-time setup (once)
Run `python3 SKILL/scripts/setup_skill.py --check`. If it prints READY and `SKILL/config.json` exists with
`"setupComplete": true`, skip to Step 1. Otherwise:
1. Run `python3 SKILL/scripts/setup_skill.py` (no `--check`). It installs the skill's own Python environment with
   tested versions (1 to 3 minutes the first time). If it prints `fix:` lines (ffmpeg or Python missing), give the
   user those exact lines to run, one per code block, and stop until they say done. Then run it again.
2. **Check the Arcads connector:** call `arcads_get_credits`. If the tool does not exist or fails, stop and say:
   > This skill makes the characters, shots, voice and music with Arcads. To connect it:
   > 1. Make an Arcads account at https://www.arcads.ai (new accounts get free trial credits).
   > 2. In Claude, open Settings > Connectors, find **Arcads**, and connect it (sign in when asked).
   >    In Claude Code you can also add it from the connector directory; if you are unsure, ask me "how do I add the
   >    Arcads connector" and I'll walk you through it.
   > 3. Come back and run /cartoon-ad-studio again.
   If it works, say the balance in one line. If the user has more than one Arcads brand (a tool asks for a
   `productId`), ask which brand the ads are for and save its id.
3. Ask, in one message (short answers are fine): brand or business name, where to keep ad projects (default
   `~/cartoon-ads`), the language of the ads.
4. Save `SKILL/config.json` (see `SKILL/config.example.json`): `setupComplete`, `setupDate`, `brand`, `projects_dir`,
   `language`, `whisper_model` (`small.en` for English, `small` otherwise), `arcads_productId`. No secrets ever go in it.

## Step 1. Study the winners (optional but recommended)
Goal: know what the current winning cartoon ads in the user's market look like before writing.
- Ask for 2 to 5 reference ads. Easiest source: the **Meta Ad Library** (facebook.com/ads/library): search the
  advertiser or a keyword, filter to Active and Videos, sort by most impressions; long-running ads with many variants
  are the winners. Open an ad and use its download option, or save the video files any way the user likes. Links to
  public videos work too if the user can download them.
- Make the ad's project folder now: `<projects_dir>/<short-ad-name>/` and copy
  `SKILL/templates/project.example.json` to `project.json` in it (fill `name`, `brand`).
- Run `PY SKILL/scripts/breakdown.py <project> <ad1.mp4> <ad2.mp4> ...`. Open every `breakdown/adN/sheet_*.jpg` and
  read every `transcript.json`.
- Write `<project>/breakdown/NOTES.md`: per ad the format (A what-if explainer / B family story / other), the hook
  line, the beat structure, shot count and pace, the look (cast, lighting, props, text in scene), the voice, how the
  offer shows up and when. End with "What to steal (structure only)" and "What to avoid".
- No reference ads? Skip this step and use `SKILL/references/playbook.md`, which is a breakdown of the top-spending
  cartoon ads from Nov 2026.

## Step 2. Research the sales page
Follow `SKILL/references/research.md`: read the whole sales page (link, screenshots or text) and write
`<project>/research.md`: the offer facts, the avatar, dream outcomes, pain points, the avatar's pain words, failed
fixes, objections, allowed claims, the format pick and three hook options. Show a short version in chat and get a yes
or edits.

## Step 3. Write the script
- Pick the format with the user (A or B, playbook). Length: 60 to 70 s for a first ad (Format B ~130 to 150 words,
  Format A ~170 to 200 words). Fill the format's beat skeleton from research.md.
- Write `<project>/SCRIPT.md`: the voiceover (one line per beat, short sentences, spoken numbers written the way they
  should be said), then a table mapping each beat to its line, then the **claims check** (every product claim and the
  page line that backs it; who the narrator is: "a fictional character, not a customer").
- Check against the playbook principles: pain word in the first line, a specific number, one picture per line, the
  ending calls back to the hook, the ask is easy.
- Show the script and get a yes. Iterate here; it is free. After a yes, nothing in it changes without the user.

## Step 4. Voiceover
Follow `production.md` Step 4: shortlist voices (`arcads_list_voices`), make hook samples (cost + yes first), the
user picks, generate the full voice, transcribe (`transcribe.py`), tighten pauses (`tighten_vo.py`), transcribe the
final into `audio/vo_words.json`. Save the voice in project.json `arcads.voiceId` / `voiceName`.

## Step 5. Characters and stills
Follow `production.md` Step 5:
1. Character sheets for every recurring person (Format B) or the mannequin (Format A). Show them, fix, lock.
2. Write `<project>/shots.json` (template `SKILL/templates/shots.example.json`): one shot per line or phrase, `vo` in
   the transcript's own words, `caps`, `refs`, `anchor`, `still`, `motion`. Run `python3 SKILL/scripts/timeline.py <project>`
   to prove the shots cover the voice exactly (it prints each shot's length; fix any mismatch it reports).
3. Quote the stills batch (count x cost) and wait for a yes. Generate, download to `stills/<id>.png`, make the contact
   sheet (`qa.py stills`), look at it, re-make weak ones.
4. Show the contact sheet to the user with the **clip quote for each tier** (production.md "Pick a tier"): this ad's
   shot count x 240 (Premium, Kling 3.0), x 72 (Budget, MiniMax H3), the Hybrid split you propose (which shots get
   real animation and why), and Zero; plus a few re-takes and the current balance. Recommend Budget or Hybrid for a
   first test, Premium for the version they scale. Wait for their pick and a yes. Write each shot's `clip`
   (`kling` / `minimax` / `still`) and, for stills, a `move` into shots.json.

## Step 6. Animate
Follow `production.md` Step 6: each shot made the way its `clip` field says (Kling 3.0, MiniMax H3, or a free
camera-move clip with `motion_still.py`), saved to `clips/<id>.mp4`. QA every clip with `qa.py clips` and look at the
sheets; re-take broken ones (say how many and the cost first if it is more than the few you quoted). A shot that
keeps breaking on MiniMax H3 (hands, fast action) goes to Kling 3.0.

## Step 7. Music and edit
1. Music bed (`production.md` Step 7), the length of `timeline.json` `total`. Cost + yes first.
2. Fill the end card in project.json (`kicker`, `title`, `offer`, `url`, colors that fit the brand). Only facts from
   the sales page or the user.
3. `python3 SKILL/scripts/timeline.py <project>` then `PY SKILL/scripts/build.py <project>`.
   It writes `out/<name>.mp4` (1080x1920) and `out/<name>_phone.mp4`.

## Step 8. QA and deliver
- Make a frame sheet of the final (`ffmpeg -i out/<name>.mp4 -vf "fps=1,scale=180:-1,tile=10x8" -frames:v 1 qa/final.jpg`)
  and look at it: every shot reads, captions sit in the middle and never cover a face, the end card is right.
- Listen to it (or `arcads_analyze_media` with the video: "list any mispronounced words, clipped words, music that
  drowns the voice, awkward pauses, with timestamps"); verify anything it flags yourself before changing it.
- Deliver: the file paths, length, the tier used, credits spent (balance before and after), and the honest list of
  anything that may look off. If they used Zero or Hybrid and the ad tests well, offer to re-make the camera-move shots
  with real animation for the version they scale. Offer the usual next steps: a 60 s or 30 s cutdown, a second hook on the same body (re-voice and re-make
  only the first 2 or 3 shots), a 16:9 or 1:1 version (re-make the stills in that aspect ratio).

## Project folder
```
<projects_dir>/<ad-name>/
  project.json   research.md   SCRIPT.md   shots.json   timeline.json   offsets.json (optional)
  breakdown/     reference ad sheets, transcripts, NOTES.md
  audio/         vo_raw.wav  vo_final.wav  vo_words.json  music.wav  sfx/
  stills/        <id>.png and character sheets
  clips/         <id>.mp4
  qa/            contact sheets
  out/           <name>.mp4  <name>_phone.mp4
```

---
Built by [@tenfoldmarc](https://instagram.com/tenfoldmarc). Follow for daily AI automation builds: real systems, not theory.
