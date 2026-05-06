# Greg Gudin voice clone — production notes

For producing the VO on `spot-30-politician-style.md` (and the cutdowns,
regional swaps, and Spanish read where applicable) without booking Greg for
every single session.

## Consent first — non-negotiable

Cloning your own voice for your own commercials is fine. Cloning Greg's
requires written consent from Greg, and the studio T&Cs require it too.
Before any audio is uploaded:

- Signed voice-clone consent (scope, duration, exclusivity, kill switch).
- Internal note documenting that the consent is on file.
- Decision on whether the clone is **firm-owned** or **Greg-owned** — this
  matters if Greg ever leaves the firm or sells.

## Tooling

- **ElevenLabs** Pro tier (Professional Voice Clone). Higher fidelity than
  Instant Clone; required for broadcast-quality output and for the API.
  Paid tier is what unlocks commercial-use rights on outputs.
- Backup option: Resemble.ai or PlayHT Pro if ElevenLabs read doesn't
  capture Greg's specific cadence. Run a bake-off before committing.

## Training audio capture (one studio session, ~90 minutes)

This is the single most important step. Garbage in = robotic clone.

Capture:

1. **30 minutes of clean read** — script-agnostic. Newspapers, his own bio,
   case summaries. Same mic, same room tone, no plosives.
2. **15 minutes of conversational** — interviewer asks him about his career,
   Cleveland, his family. Looser cadence — this is what gives the clone
   warmth.
3. **10 minutes of "ad reads"** — old commercials, charity PSAs, voicemail
   greeting style. Models the *spot* register specifically.
4. **5 minutes of "the close"** — just CTAs and phone numbers, repeated:
   "Call me. 1‑800‑411‑PAIN." — many takes, slight variations.
   Pays off when the clone has to deliver the end card cleanly.

Mic chain: Sennheiser MKH 416 or Neumann TLM 103 → Apollo / clean preamp →
48 kHz / 24-bit WAV. No plug-ins, no compression, no de-essing. Treated
room, not a closet.

## Clone build & QA

- Train the Professional Voice Clone with the **clean read** corpus. Hold
  back the conversational + ad-read corpora as evaluation references.
- QA gates before any spot ships:
  - Phone-number read is intelligible at low bitrate (geofence inventory
    is often 64 kbps mobile audio).
  - "Buckeye Law Group" pronounced with Ohio "Buckeye" cadence, not the
    flat AI default.
  - "1‑800‑411‑PAIN" lands with a mini-pause before "PAIN" — that beat is
    the brand.
- Have Greg sign off on the *exact* output stems before broadcast. Don't
  ship anything he hasn't personally listened to.

## Production loop (the actual reason we cloned him)

Once the clone is approved, the workflow per new variant is:

1. Write copy as plaintext.
2. Generate VO via ElevenLabs API with stability ~45, similarity ~75,
   style exaggeration ~10. Adjust per script.
3. Light human edit in iZotope RX (de-breath, pacing).
4. Drop into the locked picture cut as the new VO bed.
5. Greg approves the output. Then it ships.

A 30s spot variant in this loop is ~30 minutes of work versus a half-day
of Greg's calendar.

## Where we still book Greg in person

- The hero on-camera shots (timecode 0:00–0:03, 0:13–0:18, 0:23–0:28 of the
  master). The clone is for VO and end cards — **not** for lip-sync.
- The first read of any *new* claim (e.g., "over $1.2 billion") so we have
  a real reference take.

## Risks to flag

- **Consent revocation.** If Greg leaves or pulls consent, every running
  variant has to be re-VO'd. Keep the picture cuts modular so VO can be
  swapped without a re-edit.
- **Detection.** Some platforms (esp. Meta) are starting to flag synthetic
  voices in political-style ads. We're not political, but the framing is
  similar — disclose synthetic voice in the spot's metadata where the
  platform asks for it.
- **Bar review.** Ohio's bar advertising rules don't (yet) require disclosing
  AI-generated VO, but that's likely to change. Keep an internal note that
  the clone is in use; revisit quarterly.

## Sources

- [ElevenLabs — homepage](https://elevenlabs.io/)
- [ElevenLabs commercial rights / output ownership](https://terms.law/ai-output-rights/elevenlabs/)
- [ElevenLabs voice-clone consent policy](https://terms.law/forum/thread/elevenlabs-voice-clone-legal.html)
- [ElevenLabs pricing](https://magichour.ai/blog/elevenlabs-pricing)
