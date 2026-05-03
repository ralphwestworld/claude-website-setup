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
        "name": "01_welcome",
        "start_ms": 0,
        "text": (
            "Welcome.\n\n"
            "Find a comfortable position now. Lying down, with your head supported, your arms relaxed at your sides, your legs uncrossed.\n\n"
            "You don't need to do anything except listen. Just listen to my voice, and let everything else fall away.\n\n"
            "This is your time. Time to let go of the day. Time to step into the version of yourself you have always known you could become.\n\n"
            "Tonight, your subconscious mind takes over the work. While you drift off to sleep, every word, every image, every belief I share will be absorbed deep into the part of you that builds your future. And tomorrow, you will wake up changed."
        ),
    },
    {
        "name": "02_progressive_relaxation",
        "start_ms": 50 * 1000,  # 0:50
        "text": (
            "Now, take a slow, deep breath in through your nose. Fill your lungs completely. And let it out slowly through your mouth.\n\n"
            "Again, breathe in deeply, and exhale, releasing everything that no longer serves you tonight.\n\n"
            "One more breath. In through the nose, hold for a moment, and out, letting your whole body melt into the surface beneath you.\n\n"
            "Now bring your awareness down to your feet. Feel your feet, all the way to the tips of your toes. And as you breathe out, let your feet become heavy, soft, completely relaxed.\n\n"
            "Move that feeling up now into your calves and your shins. Let your lower legs become loose, warm, completely supported by the bed beneath you.\n\n"
            "Bring the relaxation up into your knees, and your thighs. Let those large muscles of your legs surrender, become heavy, sink down.\n\n"
            "Now feel your hips, and your lower back. Notice any tension there, and as you exhale, let it release. Let your hips sink down into the bed.\n\n"
            "Bring the relaxation up through your stomach, and your chest. Feel your breathing slow and deepen. Each breath gentler than the last.\n\n"
            "Drop your shoulders now. Drop them away from your ears. Let your arms become heavy, your hands relaxed, your fingers soft.\n\n"
            "Bring the relaxation now to your neck, and the back of your head. Let your jaw soften. Let your tongue rest gently behind your teeth.\n\n"
            "Soften the muscles around your eyes. Smooth the muscles of your forehead. Let your whole face relax.\n\n"
            "Your whole body now is heavy, warm, completely at ease. And you are going deeper, with every breath."
        ),
    },
    {
        "name": "03_countdown_deepener",
        "start_ms": 3 * 60 * 1000,  # 3:00
        "text": (
            "In a moment I'm going to count down from ten to one. With each number, you will find yourself drifting twice as deep into total relaxation.\n\n"
            "Twice as deep. Twice as peaceful. Twice as ready to receive everything I share with you tonight.\n\n"
            "Ten. Going down now. Letting go.\n\n"
            "Nine. Sinking deeper into the bed beneath you. Heavier.\n\n"
            "Eight. Twice as deep as before. Your mind softening.\n\n"
            "Seven. The outside world drifting further away. Only my voice now.\n\n"
            "Six. Halfway there. Profoundly relaxed.\n\n"
            "Five. Even deeper. Your subconscious wide open.\n\n"
            "Four. So deeply relaxed, you feel like you are floating.\n\n"
            "Three. The deepest level of trance you have ever experienced.\n\n"
            "Two. Beyond thought. Beyond effort. Just being.\n\n"
            "One. You are now in the perfect state to receive everything I say. Every word, every image, every suggestion goes deep into your subconscious mind, where it takes root, and grows."
        ),
    },
    {
        "name": "04_staircase_visualization",
        "start_ms": 4 * 60 * 1000 + 30 * 1000,  # 4:30
        "text": (
            "And in this state, I want you to imagine, in your mind's eye, that you are standing at the top of a beautiful staircase.\n\n"
            "The staircase is yours. It descends gently into your perfect place. The place where the version of you who has already arrived lives.\n\n"
            "There are ten steps down. With each step, you go deeper, and what you see becomes more vivid, more real.\n\n"
            "Take the first step down now. Ten. And another. Nine. The image becoming clearer.\n\n"
            "Eight. You can begin to see what is at the bottom. Seven. A warm light, welcoming you home.\n\n"
            "Six. You feel your feet on each step, solid, real. Five. Halfway down.\n\n"
            "Four. The light becomes brighter, more inviting. Three. You can feel the air of this place.\n\n"
            "Two. One more step. One. You step off the staircase, and you are here.\n\n"
            "Look around. This is your place. This is the version of your life where you have already arrived.\n\n"
            "You are standing in front of a building. It is one of yours. One of your thirty doors. The number on the door is yours.\n\n"
            "Walk inside. Feel the floors beneath your feet. Touch the walls. This is yours.\n\n"
            "Now step outside again, and look down the street. There are more. Each one of them, owned by you. Each one of them, generating cash flow every single month, while you sleep.\n\n"
            "Notice how it feels to own them. Notice the certainty in your body. Notice that this is not a fantasy. This is a memory. A future memory. A timeline already in motion."
        ),
    },
    {
        "name": "05_identity_dichotic",
        "start_ms": 6 * 60 * 1000 + 45 * 1000,  # 6:45
        "repeat": 4,
        "repeat_gap_ms": 3000,
        "left_text": (
            "You are a successful real estate investor.\n\n"
            "You own thirty cash flowing properties, and the number is still growing.\n\n"
            "You close deals with creative financing. Seller financing. Subject to. Lease options.\n\n"
            "You see opportunity where others see only risk.\n\n"
            "You are decisive. You act on opportunities the moment you see them.\n\n"
            "You finish what you start. You scale beyond every milestone.\n\n"
            "You are a man who follows through. On every system you build. Every routine you commit to. Every promise you make to yourself.\n\n"
            "The version of you who quits is gone. In his place is a man who executes daily."
        ),
        "right_text": (
            "I am a successful real estate investor.\n\n"
            "I own thirty cash flowing properties.\n\n"
            "I structure deals other people cannot see.\n\n"
            "I am calm under pressure. I am clear in my decisions.\n\n"
            "The deals come to me. I attract the right opportunities.\n\n"
            "I act with certainty. I finish what I start, because that is who I am.\n\n"
            "I scale. I do not stop. The version of me who hesitates no longer exists.\n\n"
            "I am the man who shows up. Without negotiation. Without hesitation."
        ),
    },
    {
        "name": "06_behavioral_dichotic",
        "start_ms": 11 * 60 * 1000,  # 11:00
        "repeat": 4,
        "repeat_gap_ms": 3000,
        "left_text": (
            "Every morning, you open PropStream. You analyze deals. You make offers.\n\n"
            "You contact sellers. You build relationships. You negotiate from a position of certainty.\n\n"
            "You use Claude Code. You build your acquisition systems. You automate what other investors do manually.\n\n"
            "You move forward every single day. No matter how you feel. No matter what is happening around you.\n\n"
            "Your discipline is not something you summon. It is who you are.\n\n"
            "You are organized. Your time is structured. Your priorities are clear."
        ),
        "right_text": (
            "My mind is sharp. My focus is clear.\n\n"
            "I have no interest in marijuana. I have no interest in anything that dulls my edge.\n\n"
            "I have no interest in anything that takes me off my path.\n\n"
            "Substances no longer call to me. The next deal calls to me.\n\n"
            "The next acquisition calls to me. Building my empire calls to me.\n\n"
            "I am free. Clean. Focused. On the version of me who is already winning."
        ),
    },
    {
        "name": "07_future_pacing",
        "start_ms": 14 * 60 * 1000 + 30 * 1000,  # 14:30
        "text": (
            "Now, in your mind's eye, see yourself one year from now.\n\n"
            "You are standing in front of a wall in your home office. On that wall is a map. Pins mark every property you own. Twenty more pins than there were a year ago. Fifty doors now. Fifty.\n\n"
            "You walk to your desk. You see your accounts. The cash flow is real. The equity is real. It is all yours.\n\n"
            "Your team handles operations. You spend your days finding the next deal. You are not stressed. You are not chasing. You are building. Calmly. Methodically. Inevitably.\n\n"
            "Notice how your body feels in this future. Strong. Centered. Free.\n\n"
            "Notice the relationships you have. Notice the time you spend with the people you love. Notice the man you have become.\n\n"
            "Now reach forward, one year ahead of yourself, and shake your own hand. Thank yourself. Because you did it.\n\n"
            "Every deal. Every offer. Every cold call. Every late night. It all paid off.\n\n"
            "And this version of you, this future version, is closer than you think. Because the path you are on, right now, leads directly here. Inevitably."
        ),
    },
    {
        "name": "07b_identity_dichotic_round2",
        "start_ms": 16 * 60 * 1000 + 15 * 1000,  # 16:15
        "repeat": 3,
        "repeat_gap_ms": 3000,
        "left_text": (
            "You are the man who builds his own freedom.\n\n"
            "Every door you own is a piece of your independence.\n\n"
            "You move with confidence. You make decisions quickly.\n\n"
            "You see the path to thirty doors clearly.\n\n"
            "And beyond thirty, you see fifty. You see one hundred.\n\n"
            "You build wealth that compounds, that lasts, that frees the people you love."
        ),
        "right_text": (
            "I am calm. I am focused. I am unstoppable.\n\n"
            "Every action I take is intentional.\n\n"
            "Money flows to me, because I create real value.\n\n"
            "I am building a legacy.\n\n"
            "I am building security. I am building freedom.\n\n"
            "Nothing in the world can shake my certainty about who I am becoming."
        ),
    },
    {
        "name": "07c_behavioral_round2",
        "start_ms": 20 * 60 * 1000 + 30 * 1000,  # 20:30
        "repeat": 2,
        "repeat_gap_ms": 3000,
        "left_text": (
            "Every morning, you wake up clear and motivated.\n\n"
            "You take action before you check your phone.\n\n"
            "You analyze deals. You make offers. You follow up.\n\n"
            "You build your team. You delegate what you should not be doing.\n\n"
            "You stay in your zone of genius. You acquire."
        ),
        "right_text": (
            "I am grateful for this body and mind.\n\n"
            "I treat them as the engines of my mission.\n\n"
            "I sleep deeply. I eat clean. I move daily.\n\n"
            "I do not numb. I do not avoid. I do not hide.\n\n"
            "I face every day with full presence and full power."
        ),
    },
    {
        "name": "08_sleep_transition",
        "start_ms": 24 * 60 * 1000,  # 24:00
        "text": (
            "And now, as your body grows heavier, your mind drifts deeper. Everything I have said tonight is settling now. Into the place where beliefs live. Where identity is formed.\n\n"
            "While you sleep tonight, your subconscious will rehearse, and organize, and reinforce. Every system. Every belief. Every action.\n\n"
            "Your mind will sort the day. Will let go of what doesn't matter. Will hold tight to what does.\n\n"
            "You will wake up tomorrow morning, clear, motivated, and already in motion. The path will feel obvious. The next step will feel obvious.\n\n"
            "And every night you listen, the changes go deeper. The patterns become more permanent. You become more, of who you already are.\n\n"
            "There is nothing for you to do now. Nothing to think about. Nothing to figure out.\n\n"
            "Just drift. Deeper. And deeper. Into a perfect, healing, restful sleep.\n\n"
            "Tomorrow you wake up new. Tomorrow you wake up ready.\n\n"
            "Goodnight."
        ),
    },
]


PIPER_MODEL = os.environ.get("PIPER_MODEL", "/tmp/piper_models/en_GB-jenny_dioco-medium.onnx")
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
    Render text by paragraph (preserves natural prosody within a paragraph), with
    short pauses between phrases via piper's built-in sentence_silence and a small
    pause between paragraphs.
    """
    wav_dir = out_path.parent / (out_path.stem + "_chunks")
    wav_dir.mkdir(parents=True, exist_ok=True)

    # Convert ellipses inside the text to commas so piper treats them as natural
    # mid-sentence pauses rather than us padding silence between separate renders.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    rendered: list[AudioSegment] = []
    for p_idx, para in enumerate(paragraphs):
        prosodic = para.replace("...", ",")
        chunk_wav = wav_dir / f"{p_idx:02d}.wav"
        _piper_render(prosodic, chunk_wav)
        chunk = AudioSegment.from_file(chunk_wav, format="wav").set_channels(2).set_frame_rate(SAMPLE_RATE)
        rendered.append(chunk)
        # Brief pause between paragraphs only
        rendered.append(AudioSegment.silent(duration=500, frame_rate=SAMPLE_RATE).set_channels(2))

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
    print("[voice] Generating segments...")
    full = AudioSegment.silent(duration=TOTAL_DURATION_MS, frame_rate=SAMPLE_RATE).set_channels(2)

    for seg in SEGMENTS:
        if "left_text" in seg and "right_text" in seg:
            # Dichotic: separate L and R streams, hard panned, layered at same start.
            left_cache = WORK_DIR / f"{seg['name']}_L.mp3"
            right_cache = WORK_DIR / f"{seg['name']}_R.mp3"

            if left_cache.exists() and left_cache.stat().st_size > 1000:
                print(f"[voice]   {seg['name']} L: cached")
                left_voice = AudioSegment.from_file(left_cache, format="mp3")
            else:
                print(f"[voice]   {seg['name']} L: generating ({len(seg['left_text'])} chars)")
                left_voice = tts(seg["left_text"], left_cache)

            if right_cache.exists() and right_cache.stat().st_size > 1000:
                print(f"[voice]   {seg['name']} R: cached")
                right_voice = AudioSegment.from_file(right_cache, format="mp3")
            else:
                print(f"[voice]   {seg['name']} R: generating ({len(seg['right_text'])} chars)")
                right_voice = tts(seg["right_text"], right_cache)

            left_voice = left_voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
            right_voice = right_voice.set_channels(2).set_frame_rate(SAMPLE_RATE)

            # Hard pan
            left_voice = pan_segment(left_voice, -1.0)
            right_voice = pan_segment(right_voice, 1.0)

            # Pad shorter to match longer so the pair ends together (the McKenna
            # "converge at the end" feel comes from both streams running concurrently).
            max_len = max(len(left_voice), len(right_voice))
            if len(left_voice) < max_len:
                left_voice += AudioSegment.silent(duration=max_len - len(left_voice), frame_rate=SAMPLE_RATE).set_channels(2)
            if len(right_voice) < max_len:
                right_voice += AudioSegment.silent(duration=max_len - len(right_voice), frame_rate=SAMPLE_RATE).set_channels(2)

            repeat = seg.get("repeat", 1)
            gap_ms = seg.get("repeat_gap_ms", 2500)
            lead_in = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
            for r in range(repeat):
                offset = seg["start_ms"] + r * (max_len + gap_ms)
                full = full.overlay(lead_in + left_voice, position=offset)
                full = full.overlay(lead_in + right_voice, position=offset)
            total_len = repeat * max_len + (repeat - 1) * gap_ms
            print(f"[voice]   {seg['name']} (dichotic x{repeat}): placed at {seg['start_ms']/1000:.0f}s, total {total_len/1000:.1f}s")
        else:
            cache_path = WORK_DIR / f"{seg['name']}.mp3"
            if cache_path.exists() and cache_path.stat().st_size > 1000:
                print(f"[voice]   {seg['name']}: cached")
                voice = AudioSegment.from_file(cache_path, format="mp3")
            else:
                print(f"[voice]   {seg['name']}: generating ({len(seg['text'])} chars)")
                voice = tts(seg["text"], cache_path)

            voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)

            lead_in = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
            voice = lead_in + voice

            full = full.overlay(voice, position=seg["start_ms"])
            print(f"[voice]   {seg['name']}: placed at {seg['start_ms']/1000:.0f}s, voice length {len(voice)/1000:.1f}s")

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


def _note_hz(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def generate_ambient_track() -> AudioSegment:
    """
    Slow ambient pad: A minor progression (Am - F - C - G) cycling at ~16s/chord,
    each chord is a sine pad with octave + fifth + third, slight detune for warmth,
    crossfaded so chord changes are seamless. Stereo movement via slow LFO panning.
    """
    print("[ambient] Synthesizing ambient music pad (Am - F - C - G)...")

    # Chord roots: A2, F2, C3, G2 — kept low so they don't fight voice
    progression_midi = [
        [45, 48, 52, 57],  # Am: A2, C3, E3, A3
        [41, 45, 48, 53],  # F:  F2, A2, C3, F3
        [48, 52, 55, 60],  # C:  C3, E3, G3, C4
        [43, 47, 50, 55],  # G:  G2, B2, D3, G3
    ]
    chord_duration_s = 16.0
    crossfade_s = 4.0

    n_samples = int(SAMPLE_RATE * (TOTAL_DURATION_MS / 1000.0))
    t_full = np.arange(n_samples) / SAMPLE_RATE

    out_left = np.zeros(n_samples, dtype=np.float32)
    out_right = np.zeros(n_samples, dtype=np.float32)

    chord_samples = int(chord_duration_s * SAMPLE_RATE)
    cf_samples = int(crossfade_s * SAMPLE_RATE)
    step = chord_samples - cf_samples
    n_chords_needed = (n_samples // step) + 2

    # Per-chord crossfade envelope: linear ramp up over cf, sustain, linear ramp down over cf
    env = np.ones(chord_samples, dtype=np.float32)
    env[:cf_samples] = np.linspace(0.0, 1.0, cf_samples)
    env[-cf_samples:] = np.linspace(1.0, 0.0, cf_samples)

    for i in range(n_chords_needed):
        chord = progression_midi[i % len(progression_midi)]
        start = i * step
        if start >= n_samples:
            break
        end = min(start + chord_samples, n_samples)
        length = end - start
        local_t = np.arange(length) / SAMPLE_RATE

        # Build chord: each note as sine + slightly detuned sine for chorusing
        chord_wave_l = np.zeros(length, dtype=np.float32)
        chord_wave_r = np.zeros(length, dtype=np.float32)
        for j, midi in enumerate(chord):
            freq = _note_hz(midi)
            # Slight per-voice detune (±2-4 cents) for warmth
            detune_cents = (j - 1.5) * 2.5
            freq_l = freq * 2 ** (detune_cents / 1200.0)
            freq_r = freq * 2 ** (-detune_cents / 1200.0)
            phase_l = 2 * np.pi * freq_l * local_t + (j * 1.7)
            phase_r = 2 * np.pi * freq_r * local_t + (j * 0.9)
            # Lower notes louder for body
            voice_amp = 0.32 if j == 0 else (0.24 if j == 1 else 0.18)
            chord_wave_l += voice_amp * np.sin(phase_l).astype(np.float32)
            chord_wave_r += voice_amp * np.sin(phase_r).astype(np.float32)

        # Soft saturation for warmth
        chord_wave_l = np.tanh(chord_wave_l * 0.9)
        chord_wave_r = np.tanh(chord_wave_r * 0.9)

        # Apply envelope (sliced to actual length)
        local_env = env[:length]
        chord_wave_l *= local_env
        chord_wave_r *= local_env

        out_left[start:end] += chord_wave_l
        out_right[start:end] += chord_wave_r

    # Slow stereo panning LFO (~0.04 Hz - one cycle per 25 sec) for gentle movement
    pan_lfo = 0.15 * np.sin(2 * np.pi * 0.04 * t_full).astype(np.float32)
    out_left *= (1.0 - pan_lfo)
    out_right *= (1.0 + pan_lfo)

    # Normalize
    peak = max(np.max(np.abs(out_left)), np.max(np.abs(out_right))) or 1.0
    out_left = out_left / peak * 0.85
    out_right = out_right / peak * 0.85

    stereo = np.empty((n_samples, 2), dtype=np.float32)
    stereo[:, 0] = out_left
    stereo[:, 1] = out_right
    int16 = (stereo * 32767).astype(np.int16)

    seg = AudioSegment(
        int16.tobytes(),
        frame_rate=SAMPLE_RATE,
        sample_width=2,
        channels=2,
    )
    print(f"[ambient] {len(seg)/1000:.0f}s of ambient pad generated")
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
    # Voice at 0 dB reference. Binaural -22 dB. Ambient music -16 dB.
    binaural_track = binaural_track - 22
    ambient_track = ambient_track - 16

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
    dichotic_count = sum(1 for s in SEGMENTS if "left_text" in s)
    print(f"Segments:      {len(SEGMENTS)} total ({dichotic_count} dichotic L/R)")
    print(f"Binaural:      200 Hz carrier, beat 10/7/4/2 Hz with 5s crossfades, -24 dB")
    print(f"Ambient:       Ambient music pad (Am-F-C-G progression), -16 dB")
    print()


if __name__ == "__main__":
    main()
