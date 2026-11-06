---
name: cartoon-ad-studio
description: "Make viral Pixar-style cartoon video ads for any offer, the format top advertisers are spending millions on: study winning cartoon ads, research the sales page (dream outcomes, pain points), write the script, voice it, generate the characters and every shot, animate them (Kling 3.0, a cheaper model, or free camera moves) and edit the finished 9:16 ad with captions, music and an end card. Works with the tools the user has connected to Claude: ElevenLabs for voice and music, and any image + video generation tool. Use for /cartoon-ad-studio, 'make me a cartoon ad', 'Pixar style ad', 'viral cartoon ad for my offer', 'animated story ad', 'copy this cartoon ad format'."
---

# /cartoon-ad-studio

Turns a sales page into a finished cartoon video ad, the same way the best-performing cartoon ads in the Meta Ad
Library are built: a story or a surprising "what if" told by a narrator over Pixar-style 3D shots, hard cuts, small
centered captions, a music bed and a 3 second end card.

The pipeline: **(1) study winners -> (2) research the sales page -> (3) script -> (4) voiceover -> (5) characters +
stills -> (6) animate -> (7) music + edit -> (8) QA and deliver.**

It uses the user's own connected tools (no single platform required): a **voice** tool (ElevenLabs recommended),
an **image** tool that takes reference images, an **image-to-video** tool, and a **music** source (ElevenLabs music,
any music tool, or a royalty-free track). Step 0 finds them.

Four budget tiers for the animation, the step that is almost the whole cost: **Premium** (Kling 3.0 or the tool's best
start-frame model on every shot), **Budget** (a cheap start-frame model such as MiniMax / Hailuo, about a third of the
price), **Hybrid** (real animation on the 8 to 12 shots that matter, free camera-move clips on the calm ones), **Zero**
(free camera-move clips only). Details and when to use which: `SKILL/references/production.md`, "Pick a tier".

`SKILL` below means this skill's folder (the one holding this file). `PY` means `SKILL/.venv/bin/python`
(Windows: `SKILL\.venv\Scripts\python.exe`). Scripts print plain progress; read their output, don't guess.
Read `SKILL/references/playbook.md` before writing any script, `SKILL/references/research.md` for Step 2 and
`SKILL/references/production.md` before Step 4.

| Command | What happens |
|---|---|
| `/cartoon-ad-studio` | The whole ad: Steps 1 to 8 |
| `/cartoon-ad-studio study <videos>` | Only break down reference ads (Step 1) |
| `/cartoon-ad-studio script` | Research + script only, nothing spent (Steps 2 and 3) |
| `/cartoon-ad-studio budget` | The whole ad on the cheapest real-animation tier unless they pick another |
| `/cartoon-ad-studio resume` | Carry on an ad already started (reads its folder and picks up at the first missing step) |
| `/cartoon-ad-studio setup` | Run or redo first-time setup (Step 0) |

## Hard rules
1. **Money moves only on a yes.** Before every paid batch (voice samples, stills, clips, music) say what will be made
   and what it costs on the user's own tool (its credits or dollars, from its pricing or a first single generation),
   plus their balance if the tool shows one, and wait for the user's yes in chat. One yes covers one batch. Re-takes of
   a few clips can share one yes if you said so.
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
2. **Find the user's generation tools.** Look at the tools available in this session (connectors / MCP servers) and
   map each capability to one tool (production.md, first table):
   - **voice**: text to speech with a voice list (ElevenLabs is the recommended one);
   - **music**: an instrumental of a set length (ElevenLabs music works; or another music tool; or they supply a
     royalty-free track);
   - **stills**: image generation that accepts reference images and a 9:16 ratio;
   - **clips**: image-to-video from a start frame, 9:16 (note which models it offers: a premium one like Kling 3.0 and
     a cheaper start-frame one, if both exist).
   If one tool covers several, use it for all of them. If more than one tool can do a capability, ask which they want.
   Make one tiny test call where a tool has a free one (a voice list, a balance) to prove it is connected.
   If **voice** or **clips** is missing, stop and say (fill in what is missing):
   > To make the ads I need a [voice / video] tool connected to Claude.
   > - Voice and music: **ElevenLabs** has an official connector. In Claude, open the connectors directory
   >   (Settings > Connectors, or Customize > Connectors), search ElevenLabs, connect it and sign in.
   > - Video (and images): connect the AI video tool you already use (for example Higgsfield, OpenArt, fal or Kling;
   >   most have a Claude connector, usually added from the connectors directory or as a custom connector with the
   >   URL from their docs).
   > Then run /cartoon-ad-studio again.
   Missing **stills** only: the video tool often makes images too; check before asking. Missing **music** only: carry
   on and ask for a royalty-free track at Step 7, or use the voice tool's music feature if it has one.
3. Ask, in one message (short answers are fine): brand or business name, where to keep ad projects (default
   `~/cartoon-ads`), the language of the ads.
4. Save `SKILL/config.json` (see `SKILL/config.example.json`): `setupComplete`, `setupDate`, `brand`, `projects_dir`,
   `language`, `whisper_model` (`small.en` for English, `small` otherwise), and `tools` (which connected tool and model
   does voice, music, stills, clips premium, clips budget). No secrets ever go in it.

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
Follow `production.md` Step 4: shortlist voices on the voice tool (ElevenLabs recommended), make hook samples (cost +
yes first), the user picks, generate the full voice, transcribe (`transcribe.py`), tighten pauses (`tighten_vo.py`),
transcribe the final into `audio/vo_words.json`. Save the voice in project.json `voice` (name + id).

## Step 5. Characters and stills
Follow `production.md` Step 5:
1. Character sheets for every recurring person (Format B) or the mannequin (Format A). Show them, fix, lock.
2. Write `<project>/shots.json` (template `SKILL/templates/shots.example.json`): one shot per line or phrase, `vo` in
   the transcript's own words, `caps`, `refs`, `anchor`, `still`, `motion`. Run `python3 SKILL/scripts/timeline.py <project>`
   to prove the shots cover the voice exactly (it prints each shot's length; fix any mismatch it reports).
3. Quote the stills batch (count x cost) and wait for a yes. Generate, download to `stills/<id>.png`, make the contact
   sheet (`qa.py stills`), look at it, re-make weak ones.
4. Show the contact sheet to the user with the **clip quote for each tier** (production.md "Pick a tier"): this ad's
   shot count x the premium model's price on their tool, x the budget model's price, the Hybrid split you propose
   (which shots get real animation and why), and Zero (free); plus a few re-takes and their balance if the tool shows
   one. Recommend Budget or Hybrid for a first test, Premium for the version they scale. Wait for their pick and a yes.
   Write each shot's `clip` (`premium` / `budget` / `still`) and, for stills, a `move` into shots.json.

## Step 6. Animate
Follow `production.md` Step 6: each shot made the way its `clip` field says (the premium or budget model on their
video tool, or a free camera-move clip with `motion_still.py`), saved to `clips/<id>.mp4`. QA every clip with
`qa.py clips` and look at the sheets; re-take broken ones (say how many and the cost first if it is more than the few
you quoted). A shot that keeps breaking on the budget model (hands, fast action) goes to the premium one.

## Step 7. Music and edit
1. Music bed (`production.md` Step 7), the length of `timeline.json` `total`. Cost + yes first.
2. Fill the end card in project.json (`kicker`, `title`, `offer`, `url`, colors that fit the brand). Only facts from
   the sales page or the user.
3. `python3 SKILL/scripts/timeline.py <project>` then `PY SKILL/scripts/build.py <project>`.
   It writes `out/<name>.mp4` (1080x1920) and `out/<name>_phone.mp4`.

## Step 8. QA and deliver
- Make a frame sheet of the final (`ffmpeg -i out/<name>.mp4 -vf "fps=1,scale=180:-1,tile=10x8" -frames:v 1 qa/final.jpg`)
  and look at it: every shot reads, captions sit in the middle and never cover a face, the end card is right.
- Listen check: transcribe the final (`transcribe.py out/<name>.mp4 qa/final_words.json`) and read it against the
  script for clipped or wrong words; if a connected tool can watch or listen to media, ask it to "list any
  mispronounced words, clipped words, music that drowns the voice, awkward pauses, with timestamps" and verify anything
  it flags yourself before changing it.
- Deliver: the file paths, length, the tier used, what it cost (balance before and after if shown), and the honest list of
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
