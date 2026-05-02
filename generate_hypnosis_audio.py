"""
Bedtime Hypnosis Audio Generator
Generates a 30-minute custom self-hypnosis audio file with voiced affirmations,
binaural beats, and ambient soundscape.
"""

import io
import os
import sys
from pathlib import Path

import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "bedtime_hypnosis_realestate_v1.mp3"
WORK_DIR = Path("/tmp/hypnosis_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 30 * 60 * 1000  # 30 minutes

VOICE_ID = "onwK4e9ZLuTAKqWW03F9"  # Daniel
MODEL_ID = "eleven_multilingual_v2"

SEGMENTS = [
    {
        "name": "01_induction",
        "start_ms": 0,
        "end_ms": 4 * 60 * 1000,
        "pan": 0.0,
        "text": (
            "As you settle in... close your eyes... and let your body sink into the surface beneath you...\n\n"
            "Take a slow, deep breath in... and let it out completely... letting go of the day...\n\n"
            "Each breath now... is taking you deeper... softer... heavier...\n\n"
            "Feel the weight of your body... being supported... fully... completely...\n\n"
            "You don't have to do anything... you don't have to think about anything... just listen... and let my voice guide you down...\n\n"
            "With every word I speak... you go deeper... and deeper... into a state of complete relaxation..."
        ),
    },
    {
        "name": "02_deepener",
        "start_ms": 4 * 60 * 1000,
        "end_ms": 7 * 60 * 1000,
        "pan": 0.0,
        "text": (
            "As you drift down... I want you to imagine a beautiful place... a place that is yours... a place where everything you want already exists...\n\n"
            "This is the version of your life... where you have already arrived...\n\n"
            "Where you own thirty doors... thirty properties... generating cash flow every single month... while you sleep...\n\n"
            "You see them clearly now... real, tangible, yours...\n\n"
            "And the man who owns them... is the man you already are..."
        ),
    },
    {
        "name": "03_identity_reframe",
        "start_ms": 7 * 60 * 1000,
        "end_ms": 14 * 60 * 1000,
        "pan": 0.0,
        "text": (
            "You are a successful real estate investor...\n\n"
            "You own thirty cash flowing properties... and the number is still growing...\n\n"
            "You close deals with creative financing... seller financing... subject to... lease options... you know how to structure deals other people can't see...\n\n"
            "You are decisive... you act on opportunities the moment you see them...\n\n"
            "You finish what you start... you do not stop when things get easier... you scale...\n\n"
            "When you reach a milestone... your subconscious mind drives you to the next one... immediately... naturally... without effort...\n\n"
            "You are a man who follows through... on every system you build... every routine you commit to... every promise you make to yourself...\n\n"
            "The version of you who quits... no longer exists... that man is gone...\n\n"
            "In his place... is a man who executes... daily... without negotiation... without hesitation..."
        ),
    },
    {
        "name": "04_behavioral_anchoring",
        "start_ms": 14 * 60 * 1000,
        "end_ms": 20 * 60 * 1000,
        "pan": 0.0,
        "text": (
            "Every morning... you open PropStream... you analyze deals... you make offers...\n\n"
            "You contact sellers... you build relationships... you negotiate from a position of certainty...\n\n"
            "You use Claude Code... you build your acquisition systems... you automate what other investors do manually...\n\n"
            "You move forward every single day... no matter how you feel... no matter what is happening around you...\n\n"
            "The discipline... is not something you have to summon... it is who you are...\n\n"
            "You are organized... your time is structured... your priorities are clear...\n\n"
            "You no longer want substances that dull your edge... you have no interest in marijuana... no interest in anything that takes you off your path... your mind is sharp... clear... focused on the next deal..."
        ),
    },
    {
        "name": "05_future_pacing",
        "start_ms": 20 * 60 * 1000,
        "end_ms": 25 * 60 * 1000,
        "pan": 0.0,
        "text": (
            "See yourself one year from now... twenty more doors closed... cash flow funding your life... your team running operations... while you find the next deal...\n\n"
            "Feel the bank account... feel the equity... feel the freedom...\n\n"
            "This is not a fantasy... this is your timeline... already in motion... already inevitable..."
        ),
    },
    {
        "name": "06_sleep_transition",
        "start_ms": 25 * 60 * 1000,
        "end_ms": 28 * 60 * 1000 + 30 * 1000,  # leave last 90s for fade-out silence
        "pan": 0.0,
        "text": (
            "And now... as your body grows heavier... your mind drifts deeper... let everything I have said... sink down... into the deepest part of you...\n\n"
            "While you sleep tonight... your subconscious will rehearse... organize... and reinforce... every system... every belief... every action...\n\n"
            "You will wake up tomorrow... clear... motivated... and already in motion...\n\n"
            "Drift now... deeper... and deeper... into a perfect... healing... sleep...\n\n"
            "Goodnight..."
        ),
    },
]

# Reinforcement layer for segments 3 and 4 - panned secondary phrases
# These play softly in alternating ears underneath the primary affirmation segments.
REINFORCEMENT_LINES = [
    ("you are decisive", -0.6),
    ("you execute daily", 0.6),
    ("you follow through", -0.6),
    ("you scale", 0.6),
    ("the deals come to you", -0.6),
    ("you are inevitable", 0.6),
]


PIPER_MODEL = os.environ.get("PIPER_MODEL", "/tmp/piper_models/en_GB-alan-medium.onnx")
TTS_BACKEND = os.environ.get("TTS_BACKEND", "auto")  # "elevenlabs", "piper", or "auto"


def _piper_render(text: str, wav_path: Path, length_scale: float = 1.35):
    import subprocess
    subprocess.run(
        [
            "piper",
            "--model", PIPER_MODEL,
            "--length_scale", str(length_scale),
            "--sentence_silence", "0.4",
            "--output_file", str(wav_path),
        ],
        input=text.encode("utf-8"),
        capture_output=True,
        check=True,
    )


def piper_tts(text: str, out_path: Path) -> AudioSegment:
    """
    Render text with hypnotic pacing: split on '...' and '\\n\\n', synthesize each
    phrase separately, stitch with long silence between phrases (3-5s per spec).
    """
    import re

    wav_dir = out_path.parent / (out_path.stem + "_chunks")
    wav_dir.mkdir(parents=True, exist_ok=True)

    # Split first on paragraph breaks (longer pause), then on ellipses (medium pause)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    rendered: list[AudioSegment] = []
    for p_idx, para in enumerate(paragraphs):
        phrases = [ph.strip() for ph in re.split(r"\.{2,}", para) if ph.strip()]
        for ph_idx, phrase in enumerate(phrases):
            # Strip trailing punctuation that piper would dramatize awkwardly
            clean = phrase.rstrip(",.;:")
            chunk_wav = wav_dir / f"{p_idx:02d}_{ph_idx:02d}.wav"
            _piper_render(clean + ".", chunk_wav)
            chunk = AudioSegment.from_file(chunk_wav, format="wav").set_channels(2).set_frame_rate(SAMPLE_RATE)
            rendered.append(chunk)
            # Pause between phrases within a paragraph: 3s (matches "3-5 second pauses" spec)
            rendered.append(AudioSegment.silent(duration=3000, frame_rate=SAMPLE_RATE).set_channels(2))
        # Longer pause between paragraphs
        rendered.append(AudioSegment.silent(duration=2500, frame_rate=SAMPLE_RATE).set_channels(2))

    full = sum(rendered, AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2))
    full.export(out_path, format="mp3", bitrate="128k")
    return AudioSegment.from_file(out_path, format="mp3")


def elevenlabs_tts(text: str, out_path: Path) -> AudioSegment:
    """Generate speech via ElevenLabs and save to disk. Returns AudioSegment."""
    from elevenlabs.client import ElevenLabs

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    client = ElevenLabs(api_key=api_key)
    audio_iter = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        text=text,
        output_format="mp3_44100_128",
        voice_settings={
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.3,
            "speed": 0.85,
            "use_speaker_boost": True,
        },
    )
    audio_bytes = b"".join(audio_iter)
    out_path.write_bytes(audio_bytes)
    return AudioSegment.from_file(out_path, format="mp3")


def tts(text: str, out_path: Path) -> AudioSegment:
    """Dispatch to selected TTS backend. Auto = ElevenLabs if key present, else Piper."""
    backend = TTS_BACKEND
    if backend == "auto":
        backend = "elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "piper"
    if backend == "elevenlabs":
        return elevenlabs_tts(text, out_path)
    if backend == "piper":
        return piper_tts(text, out_path)
    raise ValueError(f"Unknown TTS backend: {backend}")


def pan_segment(seg: AudioSegment, pan: float) -> AudioSegment:
    """Apply stereo pan. -1.0 = full left, 0.0 = center, 1.0 = full right."""
    if seg.channels == 1:
        seg = seg.set_channels(2)
    if pan == 0.0:
        return seg
    return seg.pan(pan)


def fit_segment_to_window(voice: AudioSegment, window_ms: int) -> AudioSegment:
    """
    Place voice within a target time window. Pads tail with silence if voice is shorter.
    If voice is longer than window, it overruns (we accept slight overrun rather than truncate).
    """
    if len(voice) >= window_ms:
        return voice
    pad = AudioSegment.silent(duration=window_ms - len(voice), frame_rate=SAMPLE_RATE)
    return voice + pad


def build_voice_track() -> AudioSegment:
    """Generate all segments, place at correct timing offsets, return full voice track."""
    print("[voice] Generating segments via ElevenLabs...")
    full = AudioSegment.silent(duration=TOTAL_DURATION_MS, frame_rate=SAMPLE_RATE).set_channels(2)

    for seg in SEGMENTS:
        cache_path = WORK_DIR / f"{seg['name']}.mp3"
        if cache_path.exists() and cache_path.stat().st_size > 1000:
            print(f"[voice]   {seg['name']}: cached")
            voice = AudioSegment.from_file(cache_path, format="mp3")
        else:
            print(f"[voice]   {seg['name']}: generating ({len(seg['text'])} chars)")
            voice = tts(seg["text"], cache_path)

        voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
        if seg["pan"] != 0.0:
            voice = pan_segment(voice, seg["pan"])

        # leading silence inside segment to ease entry
        lead_in = AudioSegment.silent(duration=2000, frame_rate=SAMPLE_RATE).set_channels(2)
        voice = lead_in + voice

        full = full.overlay(voice, position=seg["start_ms"])
        print(f"[voice]   {seg['name']}: placed at {seg['start_ms']/1000:.0f}s, voice length {len(voice)/1000:.1f}s")

    # Generate panned reinforcement lines and overlay underneath segment 3 (7-14 min)
    print("[voice] Generating reinforcement lines (panned)...")
    seg3_start = 7 * 60 * 1000
    seg3_window = 7 * 60 * 1000  # 7 minutes
    spacing = seg3_window // (len(REINFORCEMENT_LINES) + 1)
    for i, (line, pan) in enumerate(REINFORCEMENT_LINES):
        cache_path = WORK_DIR / f"reinforce_{i}.mp3"
        if cache_path.exists() and cache_path.stat().st_size > 500:
            voice = AudioSegment.from_file(cache_path, format="mp3")
        else:
            voice = tts(line, cache_path)
        voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
        voice = pan_segment(voice, pan) - 6  # -6 dB so it sits underneath
        position = seg3_start + (i + 1) * spacing
        full = full.overlay(voice, position=position)
        print(f"[voice]   reinforce '{line[:30]}' pan={pan:+.1f} at {position/1000:.0f}s")

    return full[:TOTAL_DURATION_MS]


def generate_binaural_track() -> AudioSegment:
    """
    Generate continuous binaural beat track with smooth crossfades between stages.
    Left ear: 200 Hz carrier. Right ear: 200 Hz + beat frequency.
    """
    print("[binaural] Synthesizing...")
    carrier = 200.0
    stages = [
        # (start_min, end_min, beat_hz)
        (0, 3, 10.0),   # alpha
        (3, 8, 7.0),    # theta
        (8, 25, 4.0),   # delta
        (25, 30, 2.0),  # deep delta
    ]

    total_samples = int(SAMPLE_RATE * (TOTAL_DURATION_MS / 1000.0))
    t = np.arange(total_samples) / SAMPLE_RATE

    # Build a per-sample beat-frequency curve with linear crossfades at boundaries
    beat_curve = np.zeros(total_samples, dtype=np.float64)
    crossfade_s = 5.0  # 5 second crossfade between stages
    for i, (s_min, e_min, beat) in enumerate(stages):
        s = int(s_min * 60 * SAMPLE_RATE)
        e = int(e_min * 60 * SAMPLE_RATE)
        beat_curve[s:e] = beat
        if i > 0:
            # Crossfade from previous beat to current beat over crossfade_s seconds
            cf_samples = int(crossfade_s * SAMPLE_RATE)
            cf_start = max(0, s - cf_samples // 2)
            cf_end = min(total_samples, s + cf_samples // 2)
            prev_beat = stages[i - 1][2]
            ramp = np.linspace(prev_beat, beat, cf_end - cf_start)
            beat_curve[cf_start:cf_end] = ramp

    # Phase accumulation for left and right
    # Left = sin(2*pi*carrier*t)
    # Right = sin(2*pi*(carrier+beat)*t) — but with time-varying beat we need integrated phase
    left_phase = 2 * np.pi * carrier * t
    right_inst_freq = carrier + beat_curve
    right_phase = 2 * np.pi * np.cumsum(right_inst_freq) / SAMPLE_RATE

    left = np.sin(left_phase)
    right = np.sin(right_phase)

    # Reduce amplitude — this is the raw signal, the dB attenuation happens at mix time.
    amp = 0.6
    left *= amp
    right *= amp

    # Interleave to int16 stereo
    stereo = np.empty((total_samples, 2), dtype=np.float32)
    stereo[:, 0] = left
    stereo[:, 1] = right
    int16 = (stereo * 32767).astype(np.int16)

    seg = AudioSegment(
        int16.tobytes(),
        frame_rate=SAMPLE_RATE,
        sample_width=2,
        channels=2,
    )
    print(f"[binaural] {len(seg)/1000:.0f}s generated, {len(stages)} frequency stages with crossfades")
    return seg


def generate_pink_noise(duration_ms: int) -> np.ndarray:
    """Generate pink noise via Voss-McCartney algorithm. Returns float32 mono array in [-1, 1]."""
    n_samples = int(SAMPLE_RATE * (duration_ms / 1000.0))
    # Use Paul Kellet's filter approximation - efficient and good quality pink noise
    rng = np.random.default_rng(42)
    white = rng.standard_normal(n_samples).astype(np.float32)
    b = np.zeros(7, dtype=np.float32)
    out = np.zeros(n_samples, dtype=np.float32)
    for i in range(n_samples):
        w = white[i]
        b[0] = 0.99886 * b[0] + w * 0.0555179
        b[1] = 0.99332 * b[1] + w * 0.0750759
        b[2] = 0.96900 * b[2] + w * 0.1538520
        b[3] = 0.86650 * b[3] + w * 0.3104856
        b[4] = 0.55000 * b[4] + w * 0.5329522
        b[5] = -0.7616 * b[5] - w * 0.0168980
        out[i] = b[0] + b[1] + b[2] + b[3] + b[4] + b[5] + b[6] + w * 0.5362
        b[6] = w * 0.115926
    # Normalize
    peak = np.max(np.abs(out)) or 1.0
    out /= peak
    return out


def generate_ambient_track() -> AudioSegment:
    """Pink noise bed + low frequency drone."""
    print("[ambient] Generating pink noise bed...")
    pink = generate_pink_noise(TOTAL_DURATION_MS)

    print("[ambient] Generating low frequency drone (70 Hz)...")
    n_samples = pink.shape[0]
    t = np.arange(n_samples) / SAMPLE_RATE
    drone = 0.5 * np.sin(2 * np.pi * 70.0 * t).astype(np.float32)
    # Slow amplitude modulation to avoid sterile drone
    drone *= (0.85 + 0.15 * np.sin(2 * np.pi * 0.05 * t)).astype(np.float32)

    # Mix pink louder than drone within ambient track; final dB applied at mix
    mixed_mono = 0.7 * pink + 0.3 * drone
    peak = np.max(np.abs(mixed_mono)) or 1.0
    mixed_mono = mixed_mono / peak * 0.85

    # Slight stereo decorrelation: shift right channel by ~9ms for width
    delay_samples = int(SAMPLE_RATE * 0.009)
    left = mixed_mono
    right = np.concatenate([np.zeros(delay_samples, dtype=np.float32), mixed_mono[:-delay_samples]])

    stereo = np.empty((n_samples, 2), dtype=np.float32)
    stereo[:, 0] = left
    stereo[:, 1] = right
    int16 = (stereo * 32767).astype(np.int16)

    seg = AudioSegment(
        int16.tobytes(),
        frame_rate=SAMPLE_RATE,
        sample_width=2,
        channels=2,
    )
    print(f"[ambient] {len(seg)/1000:.0f}s generated")
    return seg


def main():
    print("=" * 70)
    print("Bedtime Hypnosis Audio Generator")
    print("=" * 70)

    voice_track = build_voice_track()
    binaural_track = generate_binaural_track()
    ambient_track = generate_ambient_track()

    # Normalize lengths
    voice_track = voice_track[:TOTAL_DURATION_MS]
    binaural_track = binaural_track[:TOTAL_DURATION_MS]
    ambient_track = ambient_track[:TOTAL_DURATION_MS]

    print("[mix] Layering tracks...")
    # Voice at 0 dB reference. Binaural -24 dB. Ambient -30 dB.
    binaural_track = binaural_track - 24
    ambient_track = ambient_track - 30

    base = AudioSegment.silent(duration=TOTAL_DURATION_MS, frame_rate=SAMPLE_RATE).set_channels(2)
    mixed = base.overlay(ambient_track).overlay(binaural_track).overlay(voice_track)

    print("[mix] Applying fade in (5s) and fade out (30s)...")
    mixed = mixed.fade_in(5000).fade_out(30000)

    print(f"[export] Writing {OUTPUT_FILE}...")
    mixed.export(
        str(OUTPUT_FILE),
        format="mp3",
        bitrate="192k",
        parameters=["-ar", str(SAMPLE_RATE), "-ac", "2"],
    )

    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)
    print(f"Output:        {OUTPUT_FILE}")
    print(f"Duration:      {len(mixed)/1000/60:.2f} min")
    print(f"Size:          {size_mb:.2f} MB")
    print(f"Format:        MP3 192 kbps stereo {SAMPLE_RATE} Hz")
    backend = TTS_BACKEND if TTS_BACKEND != "auto" else ("elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "piper")
    if backend == "elevenlabs":
        print(f"Voice:         ElevenLabs voice_id={VOICE_ID}, model={MODEL_ID}")
    else:
        print(f"Voice:         Piper TTS, model={Path(PIPER_MODEL).name}")
    print(f"Segments:      {len(SEGMENTS)} primary + {len(REINFORCEMENT_LINES)} reinforcement")
    print(f"Binaural:      200 Hz carrier, beat 10/7/4/2 Hz with 5s crossfades, -24 dB")
    print(f"Ambient:       Pink noise + 70 Hz drone, -30 dB")
    print()


if __name__ == "__main__":
    main()
