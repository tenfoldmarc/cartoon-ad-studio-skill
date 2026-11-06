# Cartoon Ad Studio
### A Claude Code Skill by [@tenfoldmarc](https://www.instagram.com/tenfoldmarc)

Make viral Pixar-style cartoon video ads for your offer, the format some of the biggest advertisers on Facebook and
Instagram are spending millions on right now. You give Claude your sales page. It studies the winning cartoon ads,
researches your buyer's dream outcomes and pain points, writes the script, voices it, creates the characters and every
shot, animates them, and edits the finished vertical ad with captions, music and an end card. You approve the script,
the voice and the shots before anything expensive gets made.

---

## What It Does

1. **Studies winning cartoon ads** (optional): drop in a few ads you saved from the Meta Ad Library and Claude breaks
   down their hook, structure, pace and look.
2. **Researches your sales page**: who buys, their dream outcomes, their pain points, the exact words they use.
3. **Writes the script** in one of the two formats that are winning right now (a Pixar family story, or an
   "impossible what-if" explainer), with a claims check so the ad never promises what your product doesn't do.
4. **Voices it**: you pick the narrator from a few samples.
5. **Creates your characters and every shot** as Pixar-style stills, and shows you a contact sheet to approve.
6. **Animates every shot** on the budget you pick: from free camera moves to a cheap video model or Kling 3.0 (sharpest).
7. **Edits the finished ad**: hard cuts timed to the voice, small centered captions, a music bed, your end card.
   You get a 1080x1920 ad ready to upload, plus a phone copy.

---

## Requirements

- A Mac, Windows or Linux computer
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or the Claude Desktop app
- **A voice tool connected to Claude.** ElevenLabs is recommended (it has an official Claude connector and also makes
  the music).
- **An AI image + video tool connected to Claude**, whichever one you already use. It needs to make images from
  reference pictures (so your characters look the same in every shot) and turn an image into a video. Most popular
  tools (Higgsfield, OpenArt, fal, Kling and others) have a Claude connector.
- ffmpeg and Python 3.11 or newer (the skill checks and tells you exactly how to install them if they're missing)

You pick how much to spend on the animation, which is almost the whole cost (a 60 to 70 second ad is about 30 shots):

| Tier | Animation | Cost |
|---|---|---|
| Zero | smooth camera moves over each still, made on your computer | free (you only pay for the voice and music) |
| Hybrid | real animation on the 8 to 12 shots that matter, camera moves on the rest | about a third of Budget |
| Budget | a cheaper video model (MiniMax / Hailuo class) on every shot | about a third of Premium |
| Premium | Kling 3.0 on every shot (sharpest) | full price on your tool |

The skill reads your tool's prices, tells you the cost and asks before every batch.
- ffmpeg and Python 3.11 or newer (the skill checks and tells you exactly how to install them if they're missing)

Don't worry about connecting these manually. The skill walks you through everything on first run.

---

## Install

No terminal needed.

### Step 1: Open Claude

Open the Claude Desktop app (or Claude Code, if you already use it).

### Step 2: Paste this message

Copy-paste this into the chat and hit Enter:

```
Install this skill for me: https://github.com/tenfoldmarc/cartoon-ad-studio-skill
```

Claude downloads the skill into your skills folder and tells you when it's ready. Takes a few seconds.

### Step 3: Run the skill

Type:

```
/cartoon-ad-studio
```

Hit Enter. On your first run, the skill sets itself up (about 2 minutes) and finds your connected voice and video tools. Just
follow the prompts.

<details>
<summary>Prefer the terminal? Manual install</summary>

Open Terminal (Mac: `Command + Space`, type Terminal. Windows: `Win + R`, type cmd). Paste this one line and hit Enter:

```bash
git clone https://github.com/tenfoldmarc/cartoon-ad-studio-skill ~/.claude/skills/cartoon-ad-studio
```

Then type `claude` to open Claude Code and run `/cartoon-ad-studio`.
</details>

---

## Usage

**Make a full ad:**
```
/cartoon-ad-studio
Here's my sales page: https://yourbrand.com/offer
```
Claude researches the page, proposes a format and three hooks, writes the script, and walks you through voice,
shots and the edit, asking before it spends anything.

**Study a competitor's cartoon ads first:**
```
/cartoon-ad-studio study
I saved 3 ads from the Meta Ad Library in my Downloads folder
```

**Just the script (nothing spent):**
```
/cartoon-ad-studio script
```

**Pick up where you left off:**
```
/cartoon-ad-studio resume
```

---

## Updating

Paste this into Claude:

```
Update the cartoon-ad-studio skill from https://github.com/tenfoldmarc/cartoon-ad-studio-skill
```

Or in Terminal: `cd ~/.claude/skills/cartoon-ad-studio && git pull`

---

## Built By

[@tenfoldmarc](https://www.instagram.com/tenfoldmarc). Follow for daily AI automation walkthroughs. Real systems, not theory.
