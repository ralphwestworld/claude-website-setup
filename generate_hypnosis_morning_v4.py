"""
Morning Hypnosis v4 - Ralph (English).
Designed as the activation companion to night v7.
Night plants the seeds (identity, mansion, mastery, health, wealth).
Morning ACTIVATES execution for today.

Short (~20 min). Direct-literal commands (88% Physical Suggestibility).
Wake-up at end (NOT sleep transition).
"""

import io
import os
import re
import time
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "morning_hypnosis_ralph_v4.mp3"
WORK_DIR = Path("/tmp/hypnosis_morning_v4_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 22 * 60 * 1000  # 22 min

VOICE_ID = "yL36RsgevEFpAJK9HWYh"  # Ralph West cloned
MODEL_ID = "eleven_multilingual_v2"

VOICE_SETTINGS_INTRO = {
    "stability": 0.75,
    "similarity_boost": 0.85,
    "style": 0.08,
    "speed": 0.85,
    "use_speaker_boost": True,
}

VOICE_SETTINGS = {
    "stability": 0.6,
    "similarity_boost": 0.85,
    "style": 0.15,
    "speed": 0.92,
    "use_speaker_boost": True,
}

VOICE_SETTINGS_WAKE = {
    "stability": 0.5,
    "similarity_boost": 0.85,
    "style": 0.3,
    "speed": 1.0,
    "use_speaker_boost": True,
}

SEGMENTS = [
    {
        "name": "01_setup",
        "start_ms": 0,
        "use_intro_settings": True,
        "text": (
            "Good morning. <<3>>\n\n"
            "Sit or lie down. Eyes can close. <<3>> You don't need to do anything except listen. <<3>> This is short. This is focused. This sets the next twelve hours of your life. <<5>>\n\n"
            "Pay attention to your breath. <<3>> The rise. The fall. Happening on its own. <<4>>\n\n"
            "Three deep breaths. <<3>>\n\n"
            "Push all the way out. <<4>> And breathe in. <<5>>\n\n"
            "Push all the way out. <<4>> And breathe in. <<5>>\n\n"
            "One more. Push all the way out. <<4>> And breathe in."
        ),
    },
    {
        "name": "02_deepener",
        "start_ms": 2 * 60 * 1000,  # 2:00
        "use_intro_settings": True,
        "text": (
            "And now, counting from five to one. <<3>> With each number, you go a little deeper. Just enough to receive everything that follows. <<5>>\n\n"
            "Five. Softer. Calmer. <<4>>\n\n"
            "Four. Mind clearing. <<4>>\n\n"
            "Three. Body relaxed but alert. <<4>>\n\n"
            "Two. Open. Receptive. <<4>>\n\n"
            "One. <<3>> Perfect state. Every word lands deep."
        ),
    },
    {
        "name": "03_anchor",
        "start_ms": 3 * 60 * 1000 + 30 * 1000,  # 3:30
        "text": (
            "Place one hand on your chest. <<3>> Feel the warmth. <<4>>\n\n"
            "Breathe in. <<3>> Breathe out. <<3>>\n\n"
            "Say in your mind: I am centered. I am clear. I am ready. <<5>>\n\n"
            "Again. I am centered. I am clear. I am ready. <<5>>\n\n"
            "This is your anchor for today. <<3>> Any moment you need to come back to yourself, hand goes to chest, breath, words. <<3>> You return instantly."
        ),
    },
    {
        "name": "04_today_identity",
        "start_ms": 5 * 60 * 1000,  # 5:00
        "text": (
            "And now, today, you are: <<4>>\n\n"
            "A successful real estate investor. <<3>> Decisive. Focused. Executing. <<5>>\n\n"
            "A master of marketing, sales, and e-commerce. <<3>> You see what moves people. You craft. You close. <<5>>\n\n"
            "A master of psychology. <<3>> You read people instantly. You influence. You lead. <<5>>\n\n"
            "You are healthy. You are fit. You are unshakeable. <<5>>\n\n"
            "You are wealthy. <<3>> Your money grows. Your work compounds. <<5>>\n\n"
            "You are the man who built the life you wanted. Today, you continue building."
        ),
    },
    {
        "name": "05_today_behaviors",
        "start_ms": 7 * 60 * 1000,  # 7:00
        "text": (
            "Today, your actions are clear. <<4>>\n\n"
            "You work on YOUR projects first. <<3>> Before phone. Before news. Before anyone else's problems. <<5>>\n\n"
            "You drink water. You move your body. You eat clean. <<5>>\n\n"
            "You analyze deals. You make offers. You reach out. You send messages. <<5>>\n\n"
            "You execute marketing. You execute sales. You build systems. <<5>>\n\n"
            "You manage your money. You watch it grow. You make decisions that compound. <<5>>\n\n"
            "You do not procrastinate. <<3>> When you decide, you act. When you commit, you finish. <<5>>\n\n"
            "You do not vape. <<3>> You have no interest. Your lungs breathe clean today. <<5>>\n\n"
            "You do not allow news or others' pressure to enter your mind. <<3>> You filter. You protect your focus. <<5>>\n\n"
            "If anxiety tries to start, your hand goes to your chest. You breathe. You return to center. <<3>> In seconds. <<5>>\n\n"
            "You help only when invited. <<3>> You respect your own time. You give from overflow."
        ),
    },
    {
        "name": "06_dichotic_execute",
        "start_ms": 11 * 60 * 1000,  # 11:00
        "repeat": 3,
        "repeat_gap_ms": 2500,
        "left_text": (
            "You execute today, you finish what you start, you stay in your lane\n"
            "---\n"
            "You move forward with clarity, you handle every challenge with calm\n"
            "---\n"
            "You build for yourself, your work compounds into wealth"
        ),
        "right_text": (
            "I execute. I finish. I stay in my lane\n"
            "---\n"
            "I move with clarity. I am calm under any challenge\n"
            "---\n"
            "I build for myself. My work compounds into wealth"
        ),
    },
    {
        "name": "07_visualize_today",
        "start_ms": 14 * 60 * 1000,  # 14:00
        "text": (
            "Now see today, in your mind. <<5>>\n\n"
            "You start strong. <<3>> Water. Movement. Breath. <<3>> Then your laptop opens. You work. <<5>>\n\n"
            "Mid-day, you eat clean. You move again. You stay clear. <<5>>\n\n"
            "You handle whatever comes with calm. <<3>> Triggers are signals to breathe, not signals to react. <<5>>\n\n"
            "By evening, you have done what mattered. <<3>> You feel earned tiredness, not exhaustion. <<5>>\n\n"
            "You sleep deeply tonight, and tomorrow you wake up ready again. <<5>>\n\n"
            "This is your day. <<3>> Already in motion. <<3>> Already inevitable."
        ),
    },
    {
        "name": "08_centered_close",
        "start_ms": 17 * 60 * 1000,  # 17:00
        "text": (
            "And before we finish, remember: <<4>>\n\n"
            "You are centered. Even when the day pushes. <<5>>\n\n"
            "You are unshakeable. News doesn't move you. Opinions don't bend you. <<5>>\n\n"
            "You are the man who built this. Today, you keep building. <<5>>\n\n"
            "Hand on chest. Breath. Words. <<3>> Always available."
        ),
    },
    {
        "name": "09_wake_up",
        "start_ms": 19 * 60 * 1000,  # 19:00
        "use_wake_settings": True,
        "text": (
            "Now I count from one to five. With each number, you become more alert. More energized. More ready. <<4>>\n\n"
            "One. Body waking up. Energy returning. <<4>>\n\n"
            "Two. Mind clearing. Focus sharpening. <<4>>\n\n"
            "Three. You feel strong. Confident. Capable. <<4>>\n\n"
            "Four. Eyes ready to open. Body ready to move. <<4>>\n\n"
            "Five. Eyes open. Awake. Alert. <<3>>\n\n"
            "Centered. Clear. Ready to win the day."
        ),
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
            rendered.append(AudioSegment.silent(duration=500, frame_rate=SAMPLE_RATE).set_channels(2))

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


def render_dichotic_segment(client, seg):
    l_phrases = [p.strip() for p in seg["left_text"].split("---") if p.strip()]
    r_phrases = [p.strip() for p in seg["right_text"].split("---") if p.strip()]
    cache_dir = WORK_DIR / seg["name"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    l_full = AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2)
    r_full = AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2)
    inter_phrase_gap = AudioSegment.silent(duration=1200, frame_rate=SAMPLE_RATE).set_channels(2)
    for i, (l_text, r_text) in enumerate(zip(l_phrases, r_phrases)):
        l_a, r_a = render_dichotic_phrase_pair(client, l_text, r_text, cache_dir, i)
        l_full += l_a
        r_full += r_a
        if i < len(l_phrases) - 1:
            l_full += inter_phrase_gap
            r_full += inter_phrase_gap
    return l_full, r_full


def pan_segment(seg, pan):
    if seg.channels == 1:
        seg = seg.set_channels(2)
    return seg.pan(pan)


def build_voice_track():
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
            lead_in = AudioSegment.silent(duration=800, frame_rate=SAMPLE_RATE).set_channels(2)
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
            lead_in = AudioSegment.silent(duration=800, frame_rate=SAMPLE_RATE).set_channels(2)
            voice = lead_in + voice
            full = full.overlay(voice, position=seg["start_ms"])
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, length {len(voice)/1000:.1f}s")
    return full[:TOTAL_DURATION_MS]


def generate_binaural_track():
    """Morning: alpha -> theta (suggestion) -> alpha (alert calm) -> beta (wake-up)"""
    print("[binaural] Synthesizing morning progression...")
    carrier = 200.0
    stages = [
        (0, 2, 10.0),
        (2, 11, 7.0),       # theta during deepest suggestion work
        (11, 17, 10.0),     # alpha for dichotic + visualization
        (17, 19, 14.0),     # low beta starting to rise
        (19, 22, 18.0),     # mid beta for wake-up
    ]
    total_samples = int(SAMPLE_RATE * (TOTAL_DURATION_MS / 1000.0))
    t = np.arange(total_samples) / SAMPLE_RATE
    beat_curve = np.zeros(total_samples, dtype=np.float64)
    crossfade_s = 4.0
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


def _note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def generate_ambient_track():
    print("[ambient] Synthesizing morning music pad (C-G-Am-F)...")
    progression_midi = [
        [48, 55, 60, 64],
        [43, 50, 55, 62],
        [45, 52, 57, 64],
        [41, 48, 53, 60],
    ]
    chord_duration_s = 12.0
    crossfade_s = 3.0
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
    print("Morning Hypnosis v4 - Ralph (activation companion to night v7)")
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
    mixed = mixed.fade_in(2000).fade_out(5000)
    print(f"[export] Writing {OUTPUT_FILE}...")
    mixed.export(str(OUTPUT_FILE), format="mp3", bitrate="192k",
                 parameters=["-ar", str(SAMPLE_RATE), "-ac", "2"])
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
