"""
Morning Hypnosis v3 - Ralph (English).
Targets the parentified-helper / over-functioning pattern identified in Limitless
conversations May 12-13 2026. Builds on v7-night's McKenna-style soothing intro
+ direct-literal commands (88% Physical Suggestibility profile).

New sections specifically address:
- Identity decoupling (helping is a behavior, not who I am)
- Over-help impulse trigger reversal (urge to over-help -> PAUSE)
- Release & receive dichotic (let go of carrying, allow receiving)
- Eldest brother role release
- Friendship reframe (new connections != old patterns)
- Real income on my terms (build for self, daily compound)
- Abundance & permission dichotic
"""

import io
import os
import re
import time
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "morning_hypnosis_ralph_v3.mp3"
WORK_DIR = Path("/tmp/hypnosis_morning_v3_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 38 * 60 * 1000  # 38 min

VOICE_ID = "yL36RsgevEFpAJK9HWYh"  # Ralph West cloned
MODEL_ID = "eleven_multilingual_v2"

# Slower / drowsier for the McKenna-style induction
VOICE_SETTINGS_INTRO = {
    "stability": 0.78,
    "similarity_boost": 0.85,
    "style": 0.05,
    "speed": 0.82,
    "use_speaker_boost": True,
}

# Standard morning voice
VOICE_SETTINGS = {
    "stability": 0.65,
    "similarity_boost": 0.85,
    "style": 0.1,
    "speed": 0.88,
    "use_speaker_boost": True,
}

# More energy for the wake-up
VOICE_SETTINGS_WAKE = {
    "stability": 0.5,
    "similarity_boost": 0.85,
    "style": 0.3,
    "speed": 1.0,
    "use_speaker_boost": True,
}

SEGMENTS = [
    # === McKenna-style soothing intro (same architecture as v7 night) ===
    {
        "name": "01_welcome",
        "start_ms": 0,
        "use_intro_settings": True,
        "text": (
            "Welcome. <<3>>\n\n"
            "Get comfortable. Sit or lie down. Eyes can close. <<3>>\n\n"
            "This is your time. The next thirty minutes belong to you alone. <<3>>\n\n"
            "This experience is not sleep. <<3>> You'll still have awareness. You'll hear everything I say. <<4>>\n\n"
            "It's like daydreaming. <<3>> Just relax. Let the sounds wash over you. <<4>>\n\n"
            "My voice is soothing and easing your mind. <<3>> You are learning easily. <<3>> You take care of yourself naturally. <<3>> You execute with focus and ease. <<5>>\n\n"
            "Every word I speak goes deep into the part of you that runs your day. The part that decides who you are."
        ),
    },
    {
        "name": "02_breathing",
        "start_ms": 90 * 1000,  # 1:30
        "use_intro_settings": True,
        "text": (
            "Pay attention to your breathing. <<3>> The gentle rise. <<3>> And the gentle fall. <<4>>\n\n"
            "Before you relax further, take some deeper breaths. <<4>>\n\n"
            "Push all the way out. <<5>> And gently breathe in. <<5>>\n\n"
            "Push all the way out. <<5>> And gently breathe in. <<5>>\n\n"
            "One more. Push all the way out. <<5>> And gently breathe in."
        ),
    },
    {
        "name": "03_relaxation",
        "start_ms": 3 * 60 * 1000,  # 3:00
        "use_intro_settings": True,
        "text": (
            "Now scan your body. <<3>> Feel your feet. Feet relax. <<3>>\n\n"
            "Calves and shins. Loose. <<3>>\n\n"
            "Knees and thighs. Heavy. <<3>>\n\n"
            "Hips and lower back. Release. <<3>>\n\n"
            "Stomach and chest. Soften. <<3>>\n\n"
            "Shoulders. Drop them. <<3>> Arms heavy. Hands relaxed. <<3>>\n\n"
            "Neck soft. Jaw soft. <<3>> Eyes still. Forehead smooth. <<4>>\n\n"
            "Your body is awake but calm. <<3>> Alert but relaxed. <<3>> Ready to receive."
        ),
    },
    {
        "name": "04_deepener",
        "start_ms": 5 * 60 * 1000,  # 5:00
        "text": (
            "I count from five to one. Each number takes you deeper into focused calm. <<3>>\n\n"
            "Not asleep. Receptive. <<4>>\n\n"
            "Five. Going deeper. Mind clearing. <<4>>\n\n"
            "Four. Even more focused. Still relaxed. <<4>>\n\n"
            "Three. Halfway there. <<4>>\n\n"
            "Two. Open. Receptive. <<4>>\n\n"
            "One. <<3>> You are in the perfect state to receive everything I say. Every word goes into the place where your day starts."
        ),
    },
    # === Anchor: self-priority (replaces v1's centeredness anchor) ===
    {
        "name": "05_anchor_self_priority",
        "start_ms": 6 * 60 * 1000 + 30 * 1000,  # 6:30
        "text": (
            "Now place one hand on your chest. <<3>> Feel the warmth. The presence. <<4>>\n\n"
            "Breathe in. <<3>> Breathe out. <<3>> And say, in your mind: <<3>>\n\n"
            "My time is mine. My energy is mine. I help from overflow. <<5>>\n\n"
            "Again. My time is mine. My energy is mine. I help from overflow. <<5>>\n\n"
            "This is your morning anchor. <<3>> Hand on chest. Breath. Words. <<4>>\n\n"
            "Anytime today, when you feel the pull to drop your work for someone else's, you do this. Hand. Breath. Words. <<3>> And you come back to yourself."
        ),
    },
    # === Identity decoupling - the surgical core ===
    {
        "name": "06_identity_decoupling",
        "start_ms": 8 * 60 * 1000 + 30 * 1000,  # 8:30
        "text": (
            "And now, your subconscious is learning something new. <<4>>\n\n"
            "Helping is a behavior. <<3>> It is not who you are. <<5>>\n\n"
            "You can help. You can not help. <<3>> Either way, you are whole. <<5>>\n\n"
            "Your identity does not depend on being needed. <<3>> Your worth does not depend on being useful. <<5>>\n\n"
            "You are not the oldest brother carrying the family. <<3>> You are not the fixer. You are not the rescuer. <<5>>\n\n"
            "You are Ralph. Whole. Complete. Free. <<5>>\n\n"
            "The version of you who over-gave is gone. <<3>> The version who exists now helps only when invited. Only when it costs nothing he was not already going to give. <<5>>\n\n"
            "You are still generous. You are still kind. <<3>> But you are no longer your function. <<3>> You are yourself."
        ),
    },
    # === Trigger reversal - the over-help impulse ===
    {
        "name": "07_overhelp_trigger_reversal",
        "start_ms": 11 * 60 * 1000,  # 11:00
        "text": (
            "Your subconscious is rewiring an old pattern. <<4>>\n\n"
            "That impulse you sometimes feel. The urge to step in. To fix. To do more than was asked. <<3>> It now means something different. <<5>>\n\n"
            "When you feel that urge rising, your body automatically pauses. <<3>> One breath. <<3>> Three questions. <<5>>\n\n"
            "Did they ask. <<3>> Is this mine. <<3>> What does this cost me. <<5>>\n\n"
            "If they did not ask, you wait. <<3>> If it is not yours, you let it go. <<3>> If the cost is your own work, you say no. <<5>>\n\n"
            "Saying no is not abandonment. <<3>> It is respect. For them. For yourself. <<5>>\n\n"
            "Letting them have their consequences is how they grow. <<3>> You taking the weight is how they stay stuck. <<5>>\n\n"
            "From today, the impulse to over-help becomes the signal to step back. <<3>> The urge to fix becomes the cue to ask. <<3>> The compulsion to provide becomes the door to your own work."
        ),
    },
    # === Dichotic L/R - release & receive ===
    {
        "name": "08_dichotic_release_receive",
        "start_ms": 14 * 60 * 1000,  # 14:00
        "repeat": 4,
        "repeat_gap_ms": 3000,
        "left_text": (
            "You let go of carrying everyone, you are enough\n"
            "---\n"
            "You stop fixing others, what is mine is mine\n"
            "---\n"
            "You release the weight you never agreed to carry, you are free\n"
            "---\n"
            "You let people meet you halfway, you are home\n"
            "---\n"
            "You stop running ahead of everyone, you return"
        ),
        "right_text": (
            "I receive. I am received. I am enough\n"
            "---\n"
            "I attend to my work. My time is mine\n"
            "---\n"
            "I drop the burden that was never mine. I am free\n"
            "---\n"
            "I let others show up for me. I am home\n"
            "---\n"
            "I come back to my own life. I return"
        ),
    },
    # === Eldest brother role release ===
    {
        "name": "09_eldest_brother_release",
        "start_ms": 18 * 60 * 1000,  # 18:00
        "text": (
            "Now we speak to the part of you that was the oldest brother. <<5>>\n\n"
            "You were given that role early. <<3>> You did what was asked. <<3>> You carried more than a child should carry. <<5>>\n\n"
            "Thank that boy. <<3>> He kept the family running. He did the job. <<5>>\n\n"
            "And now, gently, you set the role down. <<5>>\n\n"
            "Being the oldest was your position. <<3>> It is not your prison. <<5>>\n\n"
            "Your family is loved by you. <<3>> They are not carried by you. <<5>>\n\n"
            "You can love your sister without saving her. <<3>> You can love your brother without leading him. <<3>> You can love your mother without becoming her partner in worry. <<5>>\n\n"
            "From today, love stays. The role is set down. <<5>>\n\n"
            "You are a man, not the oldest son. <<3>> You are Ralph, not the family caretaker. <<3>> You are free to live your own life."
        ),
    },
    # === Friendship reframe ===
    {
        "name": "10_friendship_reframe",
        "start_ms": 21 * 60 * 1000,  # 21:00
        "text": (
            "And now your subconscious is opening to something you closed off. <<5>>\n\n"
            "You can have friends again. <<3>> Real friends. <<5>>\n\n"
            "The version of you who over-gave and got nothing back is gone. <<3>> The version who is alone because every relationship became a transaction is gone. <<5>>\n\n"
            "You are not that man anymore. <<5>>\n\n"
            "New people are not old patterns. <<3>> The next friend is not the last one. <<5>>\n\n"
            "You attract equals now. <<3>> You attract people who give back. <<3>> Because you no longer give from depletion. You give from overflow, and only when it costs you nothing. <<5>>\n\n"
            "You show up. You are met. You are known. <<5>>\n\n"
            "You let people see the real you. <<3>> Not the helper. Not the fixer. Not the provider. <<3>> Just you. <<5>>\n\n"
            "And the people who stay, stay for you. Not for what you do for them."
        ),
    },
    # === Real income on my terms (direct literal, 88% Physical Suggestibility) ===
    {
        "name": "11_income_on_my_terms",
        "start_ms": 24 * 60 * 1000,  # 24:00
        "text": (
            "You build for yourself now. <<4>>\n\n"
            "Every morning, you wake up. <<3>> You drink water. You move your body. <<3>> You open your laptop. You work on your projects first. <<5>>\n\n"
            "Before answering anyone. Before fixing anyone's day. <<3>> Your projects first. <<5>>\n\n"
            "You open PropStream. You analyze deals. You make offers. <<3>> You send emails. <<3>> You move your real estate empire forward. <<5>>\n\n"
            "You build software for yourself. <<3>> You apply your skills to your own income. <<3>> Not to fix others. To build yourself. <<5>>\n\n"
            "Every hour you give yourself compounds. <<3>> Every project you finish for yourself opens the next door. <<3>> Every dollar you earn on your own terms multiplies. <<5>>\n\n"
            "Money flows from your work. <<3>> Real money. On your terms. From your own hands. <<5>>\n\n"
            "You stop trading your effort for nothing. <<3>> Your effort goes where it returns. <<3>> Your work. Your projects. Your future."
        ),
    },
    # === Dichotic L/R - abundance & permission ===
    {
        "name": "12_dichotic_abundance",
        "start_ms": 27 * 60 * 1000,  # 27:00
        "repeat": 3,
        "repeat_gap_ms": 3000,
        "left_text": (
            "You build for yourself, you execute daily\n"
            "---\n"
            "You receive abundantly, what you make is yours\n"
            "---\n"
            "You give from overflow, you owe nothing\n"
            "---\n"
            "You attract equals, you are met where you stand"
        ),
        "right_text": (
            "I work on what is mine. I execute daily\n"
            "---\n"
            "I deserve. I receive. What I make is mine\n"
            "---\n"
            "I help when I choose, never from depletion. I owe nothing\n"
            "---\n"
            "I am surrounded by people who give back. I am met where I stand"
        ),
    },
    # === Centeredness reinforcement ===
    {
        "name": "13_centeredness",
        "start_ms": 30 * 60 * 1000,  # 30:00
        "text": (
            "Before we finish, one more thing. <<4>>\n\n"
            "You are centered. <<3>> Even when others need you. <<3>> Even when the urge to fix rises. <<3>> You stay centered. <<5>>\n\n"
            "When you feel the old pull, hand goes to chest. <<3>> Breath. <<3>> Words. <<5>>\n\n"
            "My time is mine. My energy is mine. I help from overflow. <<5>>\n\n"
            "This is your default state now. <<3>> Not the fixer. Not the rescuer. Not the over-giver. <<3>> Just you. Whole. Working on what is yours. <<5>>\n\n"
            "And the right people, the right relationships, the right work, all find their way to this version of you. <<3>>\n\n"
            "Because this version of you is who you actually are."
        ),
    },
    # === Wake-up energizing 1->5 ===
    {
        "name": "14_wake_up",
        "start_ms": 33 * 60 * 1000,  # 33:00
        "text": (
            "Now I count from one to five. With each number, you become more alert. More energized. More ready. <<4>>\n\n"
            "One. Awareness returning. Body waking up. <<4>>\n\n"
            "Two. Energy rising in your chest. Mind clearing. <<4>>\n\n"
            "Three. You feel strong. Confident. Ready. <<4>>\n\n"
            "Four. Eyes ready to open. Body ready to move. <<4>>\n\n"
            "Five. Eyes open. Awake. Alert. <<3>>\n\n"
            "Centered. Clear. Ready to work on what is yours."
        ),
        "use_wake_settings": True,
    },
]

PAUSE_RE = re.compile(r"<<(\d+(?:\.\d+)?)>>")


def _eleven_render_chunk(client, text: str, settings=VOICE_SETTINGS) -> AudioSegment:
    last_err = None
    for attempt in range(5):
        try:
            audio_iter = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                text=text,
                output_format="mp3_44100_128",
                voice_settings=settings,
            )
            audio_bytes = b"".join(audio_iter)
            return AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3").set_channels(2).set_frame_rate(SAMPLE_RATE)
        except Exception as e:
            last_err = e
            wait = 2 ** attempt
            print(f"  [retry {attempt+1}/5 after {wait}s] {type(e).__name__}: {str(e)[:120]}")
            time.sleep(wait)
    raise last_err


def render_text_with_pauses(client, text: str, cache_path: Path,
                            settings=VOICE_SETTINGS) -> AudioSegment:
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return AudioSegment.from_file(cache_path, format="mp3").set_channels(2).set_frame_rate(SAMPLE_RATE)

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    rendered: list[AudioSegment] = []
    for p_idx, para in enumerate(paragraphs):
        parts = PAUSE_RE.split(para)
        for i, part in enumerate(parts):
            if i % 2 == 0:
                clean = part.strip().replace("...", ",")
                if not clean:
                    continue
                rendered.append(_eleven_render_chunk(client, clean, settings=settings))
            else:
                pause_ms = int(float(part) * 1000)
                rendered.append(AudioSegment.silent(duration=pause_ms, frame_rate=SAMPLE_RATE).set_channels(2))
        if not paragraphs[p_idx].rstrip().endswith(">>"):
            rendered.append(AudioSegment.silent(duration=600, frame_rate=SAMPLE_RATE).set_channels(2))

    full = sum(rendered, AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2))
    full.export(cache_path, format="mp3", bitrate="128k")
    return full


def render_dichotic_phrase_pair(client, l_text: str, r_text: str, cache_dir: Path, idx: int):
    l_cache = cache_dir / f"L_{idx:02d}.mp3"
    r_cache = cache_dir / f"R_{idx:02d}.mp3"

    if l_cache.exists() and l_cache.stat().st_size > 500:
        l_audio = AudioSegment.from_file(l_cache, format="mp3").set_channels(2).set_frame_rate(SAMPLE_RATE)
    else:
        l_audio = _eleven_render_chunk(client, l_text)
        l_audio.export(l_cache, format="mp3", bitrate="128k")

    if r_cache.exists() and r_cache.stat().st_size > 500:
        r_audio = AudioSegment.from_file(r_cache, format="mp3").set_channels(2).set_frame_rate(SAMPLE_RATE)
    else:
        r_audio = _eleven_render_chunk(client, r_text)
        r_audio.export(r_cache, format="mp3", bitrate="128k")

    max_len = max(len(l_audio), len(r_audio))
    if len(l_audio) < max_len:
        l_audio = AudioSegment.silent(duration=max_len - len(l_audio), frame_rate=SAMPLE_RATE).set_channels(2) + l_audio
    if len(r_audio) < max_len:
        r_audio = AudioSegment.silent(duration=max_len - len(r_audio), frame_rate=SAMPLE_RATE).set_channels(2) + r_audio
    return l_audio, r_audio


def render_dichotic_segment(client, seg) -> tuple[AudioSegment, AudioSegment]:
    l_phrases = [p.strip() for p in seg["left_text"].split("---") if p.strip()]
    r_phrases = [p.strip() for p in seg["right_text"].split("---") if p.strip()]
    assert len(l_phrases) == len(r_phrases), f"Phrase count mismatch in {seg['name']}"

    cache_dir = WORK_DIR / seg["name"]
    cache_dir.mkdir(parents=True, exist_ok=True)

    l_full = AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2)
    r_full = AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2)
    inter_phrase_gap = AudioSegment.silent(duration=1500, frame_rate=SAMPLE_RATE).set_channels(2)
    for i, (l_text, r_text) in enumerate(zip(l_phrases, r_phrases)):
        l_a, r_a = render_dichotic_phrase_pair(client, l_text, r_text, cache_dir, i)
        l_full += l_a
        r_full += r_a
        if i < len(l_phrases) - 1:
            l_full += inter_phrase_gap
            r_full += inter_phrase_gap
    return l_full, r_full


def pan_segment(seg: AudioSegment, pan: float) -> AudioSegment:
    if seg.channels == 1:
        seg = seg.set_channels(2)
    return seg.pan(pan)


def build_voice_track() -> AudioSegment:
    print("[voice] Generating segments...")
    from elevenlabs.client import ElevenLabs
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set")
    client = ElevenLabs(api_key=api_key)

    full = AudioSegment.silent(duration=TOTAL_DURATION_MS, frame_rate=SAMPLE_RATE).set_channels(2)

    for seg in SEGMENTS:
        if "left_text" in seg and "right_text" in seg:
            print(f"[voice]   {seg['name']} (dichotic)")
            l_audio, r_audio = render_dichotic_segment(client, seg)
            l_audio = pan_segment(l_audio, -1.0)
            r_audio = pan_segment(r_audio, 1.0)

            repeat = seg.get("repeat", 1)
            gap_ms = seg.get("repeat_gap_ms", 2500)
            unit_len = len(l_audio)
            lead_in = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
            for r in range(repeat):
                offset = seg["start_ms"] + r * (unit_len + gap_ms)
                full = full.overlay(lead_in + l_audio, position=offset)
                full = full.overlay(lead_in + r_audio, position=offset)
            total_len = repeat * unit_len + (repeat - 1) * gap_ms
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, total {total_len/1000:.1f}s ({repeat}x)")
        else:
            cache_path = WORK_DIR / f"{seg['name']}.mp3"
            print(f"[voice]   {seg['name']} (mono)")
            if seg.get("use_wake_settings"):
                settings = VOICE_SETTINGS_WAKE
            elif seg.get("use_intro_settings"):
                settings = VOICE_SETTINGS_INTRO
            else:
                settings = VOICE_SETTINGS
            voice = render_text_with_pauses(client, seg["text"], cache_path, settings=settings)
            voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
            lead_in = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
            voice = lead_in + voice
            full = full.overlay(voice, position=seg["start_ms"])
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, length {len(voice)/1000:.1f}s")

    return full[:TOTAL_DURATION_MS]


def generate_binaural_track() -> AudioSegment:
    """Morning progression: alpha -> theta (suggestion) -> alpha -> beta (alert wake-up)."""
    print("[binaural] Synthesizing morning progression...")
    carrier = 200.0
    stages = [
        (0, 3, 10.0),
        (3, 14, 7.0),     # theta for the deep suggestion work
        (14, 27, 10.0),
        (27, 32, 14.0),
        (32, 38, 18.0),   # beta for alert wake-up
    ]
    total_samples = int(SAMPLE_RATE * (TOTAL_DURATION_MS / 1000.0))
    t = np.arange(total_samples) / SAMPLE_RATE
    beat_curve = np.zeros(total_samples, dtype=np.float64)
    crossfade_s = 6.0
    for i, (s_min, e_min, beat) in enumerate(stages):
        s = int(s_min * 60 * SAMPLE_RATE)
        e = min(int(e_min * 60 * SAMPLE_RATE), total_samples)
        beat_curve[s:e] = beat
        if i > 0:
            cf_samples = int(crossfade_s * SAMPLE_RATE)
            cf_start = max(0, s - cf_samples // 2)
            cf_end = min(total_samples, s + cf_samples // 2)
            prev_beat = stages[i - 1][2]
            ramp = np.linspace(prev_beat, beat, cf_end - cf_start)
            beat_curve[cf_start:cf_end] = ramp
    left_phase = 2 * np.pi * carrier * t
    right_inst_freq = carrier + beat_curve
    right_phase = 2 * np.pi * np.cumsum(right_inst_freq) / SAMPLE_RATE
    left = np.sin(left_phase) * 0.6
    right = np.sin(right_phase) * 0.6
    stereo = np.empty((total_samples, 2), dtype=np.float32)
    stereo[:, 0] = left
    stereo[:, 1] = right
    int16 = (stereo * 32767).astype(np.int16)
    return AudioSegment(int16.tobytes(), frame_rate=SAMPLE_RATE, sample_width=2, channels=2)


def _note_hz(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def generate_ambient_track() -> AudioSegment:
    print("[ambient] Synthesizing morning music pad (C-G-Am-F)...")
    progression_midi = [
        [48, 55, 60, 64],  # C
        [43, 50, 55, 62],  # G
        [45, 52, 57, 64],  # Am
        [41, 48, 53, 60],  # F
    ]
    chord_duration_s = 14.0
    crossfade_s = 4.0
    n_samples = int(SAMPLE_RATE * (TOTAL_DURATION_MS / 1000.0))
    t_full = np.arange(n_samples) / SAMPLE_RATE
    out_left = np.zeros(n_samples, dtype=np.float32)
    out_right = np.zeros(n_samples, dtype=np.float32)
    chord_samples = int(chord_duration_s * SAMPLE_RATE)
    cf_samples = int(crossfade_s * SAMPLE_RATE)
    step = chord_samples - cf_samples
    n_chords_needed = (n_samples // step) + 2
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
        chord_wave_l = np.zeros(length, dtype=np.float32)
        chord_wave_r = np.zeros(length, dtype=np.float32)
        for j, midi in enumerate(chord):
            freq = _note_hz(midi)
            detune_cents = (j - 1.5) * 2.5
            freq_l = freq * 2 ** (detune_cents / 1200.0)
            freq_r = freq * 2 ** (-detune_cents / 1200.0)
            phase_l = 2 * np.pi * freq_l * local_t + (j * 1.7)
            phase_r = 2 * np.pi * freq_r * local_t + (j * 0.9)
            voice_amp = 0.30 if j == 0 else (0.22 if j == 1 else 0.18)
            chord_wave_l += voice_amp * np.sin(phase_l).astype(np.float32)
            chord_wave_r += voice_amp * np.sin(phase_r).astype(np.float32)
        chord_wave_l = np.tanh(chord_wave_l * 0.9)
        chord_wave_r = np.tanh(chord_wave_r * 0.9)
        local_env = env[:length]
        chord_wave_l *= local_env
        chord_wave_r *= local_env
        out_left[start:end] += chord_wave_l
        out_right[start:end] += chord_wave_r
    pan_lfo = 0.12 * np.sin(2 * np.pi * 0.05 * t_full).astype(np.float32)
    out_left *= (1.0 - pan_lfo)
    out_right *= (1.0 + pan_lfo)
    peak = max(np.max(np.abs(out_left)), np.max(np.abs(out_right))) or 1.0
    out_left = out_left / peak * 0.85
    out_right = out_right / peak * 0.85
    stereo = np.empty((n_samples, 2), dtype=np.float32)
    stereo[:, 0] = out_left
    stereo[:, 1] = out_right
    int16 = (stereo * 32767).astype(np.int16)
    return AudioSegment(int16.tobytes(), frame_rate=SAMPLE_RATE, sample_width=2, channels=2)


def main():
    print("=" * 70)
    print("Morning Hypnosis v3 - Ralph (pattern reprogramming)")
    print("=" * 70)

    voice_track = build_voice_track()
    binaural_track = generate_binaural_track()
    ambient_track = generate_ambient_track()

    voice_track = voice_track[:TOTAL_DURATION_MS]
    binaural_track = binaural_track[:TOTAL_DURATION_MS]
    ambient_track = ambient_track[:TOTAL_DURATION_MS]

    print("[mix] Layering tracks...")
    binaural_track = binaural_track - 22
    ambient_track = ambient_track - 9

    base = AudioSegment.silent(duration=TOTAL_DURATION_MS, frame_rate=SAMPLE_RATE).set_channels(2)
    mixed = base.overlay(ambient_track).overlay(binaural_track).overlay(voice_track)
    mixed = mixed.fade_in(3000).fade_out(8000)

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
    print(f"Output:   {OUTPUT_FILE}")
    print(f"Duration: {len(mixed)/1000/60:.2f} min")
    print(f"Size:     {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
