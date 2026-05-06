# Buckeye Law Group :30 commercial — render kit

The actual finished spot, packaged as a JSON2Video movie spec. Submit it to
their API with one shell command and you get an MP4 back in ~60 seconds.

This is the path that works inside the constraints: there is no public
CapCut API for assembling video, and the Claude session that produced
this kit has no ffmpeg, no stock-footage egress, and no audio
generation tooling. JSON2Video is the API that does what CapCut's API
does not.

## Files

- `commercial.json` — the movie spec. Six scenes, 30 seconds total, with
  text overlays, voiceover slot, music slot, end-card with phone and
  logo.
- `render.sh` — submits `commercial.json` to JSON2Video, polls until the
  render is done, prints the final MP4 URL.

## What you need to fill in before rendering

`commercial.json` has eight placeholders. Search the file for `PASTE_` —
every match is a slot that needs a real URL.

### 1. Voiceover (1 slot — `PASTE_VOICEOVER_URL_HERE.mp3`)

Record yourself reading this script on your phone (Voice Memos, WhatsApp
voice note — anything). Aim for 28 seconds, calm and direct. Upload the
file somewhere with a direct URL (Google Drive "anyone with link" share,
Dropbox public link, S3 bucket, even an unlisted GitHub Gist's raw URL).

```
The insurance company already decided what your accident is worth. They're wrong.

Medical bills. Lost wages. Pain. The first offer won't cover any of it. Or what comes next.

I'm Greg Gudin, Buckeye Law Group. We've recovered over a billion dollars for injured Ohioans — because we know what your case is really worth. And they do too.

Don't sign anything. Don't settle. Call us first.

One-eight-hundred, four-one-one, P-A-I-N. Buckeye Law Group.
```

### 2. Music (1 slot — `PASTE_MUSIC_URL_HERE.mp3`)

Optional. Sparse cinematic-tension piano + low strings, around 70 BPM.
Sources:

- JSON2Video's built-in stock library (their UI lets you browse and
  copy URLs)
- Artlist.io / Epidemic Sound (paid — needed for broadcast clearance)
- YouTube Audio Library (free — fine for social, not for broadcast)

If you don't want music, delete the second `audio` element in
`commercial.json` (the one with `volume: 0.18`).

### 3. Six B-roll clips (6 slots — `PASTE_STOCK_URL_SCENE*.mp4`)

Each scene's `_comment` field tells you what to source and the search
term to use. Quick pull-list:

| Scene | Search term                                         | Duration |
| ----- | --------------------------------------------------- | -------- |
| 1     | "insurance paperwork close up" / "settlement check" | 4 sec    |
| 2     | "stack of medical bills" / "overdue envelopes"      | 3 sec    |
| 3     | "phone call insurance adjuster" / "signing document"| 4 sec    |
| 4     | "Cleveland skyline" / "courthouse exterior dusk"    | 7 sec    |
| 5     | "attorney conference room" / "lawyer at desk"       | 6 sec    |
| 6     | (end card uses solid black background — no clip)    | 6 sec    |

Source clips from one of:

- **Pexels Videos** (https://www.pexels.com/videos/) — free, commercial
  use, no attribution required. Right-click any clip → "copy video
  address." That URL goes straight into `commercial.json`.
- **Pixabay Video** — same terms.
- **JSON2Video built-in stock library** — search and use their URLs.
- **Storyblocks / Artgrid** — paid, broader selection.

### 4. Logo (1 slot — `PASTE_LOGO_URL.png`)

The Buckeye Law Group logo as a PNG, hosted at a public URL. If you
don't have a hosted version, the fastest path:

- Right-click the logo on `buckeyeaccidentattorneys.com`, save it as
  PNG.
- Upload to Drive, set "anyone with link," copy the direct URL (use
  the `uc?id=FILE_ID` form, not the share form).
- Paste in.

If you want to skip the logo for now, replace the line with a text
element saying `"BUCKEYE LAW GROUP"` and the spot still renders.

## Render

```bash
export JSON2VIDEO_API_KEY="sk_live_..."
./render/render.sh
```

Output: a direct MP4 URL. Download it, post it, send it to TV ad
trafficking, whatever.

## Editing after first render

The fastest iteration loop is:

1. Edit `commercial.json` (swap a clip URL, change a headline, retime
   a beat).
2. Re-run `render/render.sh`.
3. Watch the new MP4 in ~60s.

Common iterations:

- **Length:** change `duration` on a scene; total of all `duration`s =
  total spot length.
- **Cutdowns:** copy `commercial.json` to `commercial-15.json`, delete
  scenes 2 and 5, retime — produces a :15 pre-roll.
- **Vertical (9:16) cut for Reels / TikTok / mobile geofence
  inventory:** add `"width": 1080, "height": 1920` at the top, replace
  `"resolution": "full-hd"`, re-render. JSON2Video repositions text
  elements automatically.
- **Voiceover swap:** change the `src` on the voiceover audio element.
  Re-render.

## Why this path instead of Canva / CapCut / a video editor

| Path                | Strengths                       | Why we didn't use it             |
| ------------------- | ------------------------------- | -------------------------------- |
| Canva slideshow MP4 | Fast, no code                   | Slides ≠ commercial. No real B‑roll. |
| CapCut API          | Mobile-friendly editor          | No public assembly API in 2026.  |
| Premiere / DaVinci  | Broadcast-grade finish          | Manual, can't be driven from script. |
| **JSON2Video**      | **Script in → MP4 out**         | What you actually asked for.     |
| Pictory / InVideo   | Auto B-roll selection           | Less control over timing/text.   |

## Limits worth knowing

- JSON2Video's free tier has rendering minutes per month. A 30s spot
  with a few iterations fits comfortably; a network buy would want the
  paid tier.
- For an actual TV master (not just digital / social / OTT), this
  output should still pass through a finishing house for broadcast-safe
  color, captions, and audio loudness normalization (-24 LUFS US TV
  spec). The MP4 we render is broadcast-acceptable for streaming and
  ready-to-use for geofence delivery.
- All claims on screen ("$1B+ recovered," "no fee unless we win,"
  "ADVERTISING MATERIAL," responsible attorney address) need final
  sign-off from Buckeye's GC against Ohio Rules of Professional
  Conduct 7.x before air.
