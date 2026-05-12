"""
Morning Hypnosis Audio Generator - Ralph (English).
Designed for daily morning use:
- Trigger reversal for highs/crashes/burnout (sustains the middle, not eliminates the highs)
- Dichotic listening: LEFT addresses "you", RIGHT first-person "I", convergence words at phrase end
- Direct-literal commands (calibrated for 88% Physical / 13% Emotional suggestibility per HMI)
- Binaural progression goes UP at end (alpha->theta for suggestion, then alpha->beta for alert wake-up)
- Energizing 1-to-5 wake-up at the end (NOT a sleep transition)
"""

import io
import os
import re
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "morning_hypnosis_ralph_v2.mp3"
WORK_DIR = Path("/tmp/hypnosis_morning_v2_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 36 * 60 * 1000  # 36 min - McKenna induction + tinnitus + body healing

VOICE_ID = "yL36RsgevEFpAJK9HWYh"  # Ralph West cloned
MODEL_ID = "eleven_multilingual_v2"

# Slower / more drowsy for the McKenna-style permissive induction
VOICE_SETTINGS_INTRO = {
    "stability": 0.78,
    "similarity_boost": 0.85,
    "style": 0.05,
    "speed": 0.82,
    "use_speaker_boost": True,
}

# Standard morning voice: a touch more energy than the evening Manuela settings
VOICE_SETTINGS = {
    "stability": 0.6,
    "similarity_boost": 0.85,
    "style": 0.15,
    "speed": 0.9,
    "use_speaker_boost": True,
}

# More energy / sharper delivery for the wake-up
VOICE_SETTINGS_WAKE = {
    "stability": 0.5,
    "similarity_boost": 0.85,
    "style": 0.3,
    "speed": 1.0,
    "use_speaker_boost": True,
}

SEGMENTS = [
    {
        "name": "01_welcome_safety",
        "start_ms": 0,  # 0:00
        "use_intro_settings": True,
        "text": (
            "Welcome. <<3>>\n\n"
            "Before we begin, a brief note. <<3>>\n\n"
            "Do not listen to this with your eyes closed while driving, or operating machinery. <<3>> Only listen when you can safely relax. <<5>>\n\n"
            "This is your morning programming. <<3>> The next thirty minutes will help you feel happier in yourself, focused on success, releasing your true potential, and creating more abundance in your life. <<3>> Today, and every day."
        ),
    },
    {
        "name": "02_what_to_expect",
        "start_ms": 70 * 1000,  # 1:10
        "use_intro_settings": True,
        "text": (
            "If you're listening with headphones, and you should be... some words will come from your right side... <<2>> some from your left... <<2>> and some directly in the center. <<5>>\n\n"
            "This experience is not sleep. <<3>> You'll still have awareness. You'll hear everything I say. You'll not become unconscious. <<4>>\n\n"
            "But there will be changes. <<3>> Gentle changes. In how you feel today. And how the rest of your day will go. <<5>>\n\n"
            "It's like daydreaming. <<3>> All you need to do is relax. <<3>> Let the sounds wash over you. <<4>>\n\n"
            "You may not remember everything consciously. But you'll find yourself feeling clear, centered, and ready as we go on. <<5>>\n\n"
            "And if you need to awaken at any time, you'll awaken fully alert. <<3>> At the end of this session, you'll awaken refreshed and invigorated, with a sense of calm and clarity."
        ),
    },
    {
        "name": "03_breathing",
        "start_ms": 4 * 60 * 1000,  # 4:00
        "use_intro_settings": True,
        "text": (
            "So now... make yourself comfortable. <<4>>\n\n"
            "Close your eyes just as soon as you wish... <<3>> and pay attention to your breathing. <<5>>\n\n"
            "The gentle rise... <<3>> and the gentle fall. <<3>> Happening all by itself. <<5>>\n\n"
            "And before you relax further... take some deeper breaths. <<4>>\n\n"
            "Push all the way out. <<5>> And gently... breathe in. <<5>>\n\n"
            "Push all the way out. <<5>> And gently... breathe in. <<5>>\n\n"
            "One more. Push all the way out. <<5>> And gently... breathe in."
        ),
    },
    {
        "name": "04_counting_back",
        "start_ms": 4 * 60 * 1000 + 30 * 1000,  # 4:30
        "use_intro_settings": True,
        "text": (
            "As you focus your attention on your breathing... now my voice will go with you as you relax. <<5>>\n\n"
            "Close your eyes if you haven't already... and begin counting backwards in your mind, from one hundred. <<4>>\n\n"
            "One hundred. <<3>> Ninety-nine. <<3>> Ninety-eight. <<3>> Ninety-seven. <<5>>\n\n"
            "That's right. <<3>> Counting backwards... you'll find it gets easier as you begin to deeply relax. <<5>>\n\n"
            "Keep counting in your mind. <<3>> The numbers may fade. <<3>> The numbers may slow. <<3>> It's all fine. <<5>>\n\n"
            "And as you count... the little muscles at the sides of your eyes... <<3>> and the muscles at the sides of your mouth... <<3>> begin to relax."
        ),
    },
    {
        "name": "05_body_awareness",
        "start_ms": 6 * 60 * 1000 + 30 * 1000,  # 6:30
        "use_intro_settings": True,
        "text": (
            "As you become comfortably aware of your chest... <<3>> and your legs... <<3>> and the comfort... <<4>>\n\n"
            "Of your shoulders relaxing. <<3>> Your arms. <<3>> Your hands. <<4>>\n\n"
            "Sensing the weight of your hands. <<3>> They may feel slightly heavier. <<3>> They may feel slightly warmer. <<5>>\n\n"
            "As you go deeper into this wonderfully relaxing morning daydream. <<3>> Where you can hear my voice in many different ways. Here. Now. <<5>>\n\n"
            "You can feel energies and perceptions. Sounds. Temperature. Sensations. Reactions. <<3>> And the gentle lightness of letting go."
        ),
    },
    {
        "name": "06_inner_stillness",
        "start_ms": 8 * 60 * 1000,  # 8:00
        "use_intro_settings": True,
        "text": (
            "Just let your focus sink deeper... <<3>> and deeper... <<3>> towards your own peaceful inner stillness. <<5>>\n\n"
            "And as you do... new patterns become richer and richer. More and more real. <<5>>\n\n"
            "You can notice words. <<3>> You can notice noticing words. <<3>> You can notice noticing that your body can relax. And your mind can become very sensitive to my suggestions that help you most. <<5>>\n\n"
            "Your breathing carries on all by itself. <<3>> And you can just watch your awareness slow down. <<5>>\n\n"
            "My voice is soothing and easing your mind. <<3>> You are learning easily. <<3>> You wake up clear and energized. <<3>> You take care of yourself naturally. <<3>> You execute with focus and ease."
        ),
    },
    {
        "name": "07_tinnitus",
        "start_ms": 10 * 60 * 1000,  # 10:00
        "use_intro_settings": True,
        "text": (
            "And in this deep state of relaxation... your subconscious is listening. <<5>>\n\n"
            "There is a sound you sometimes hear. <<3>> A ringing. <<2>> A buzzing. <<3>> Always there, in the background. <<5>>\n\n"
            "From this point forward, your subconscious lets it go. <<4>>\n\n"
            "It's like a fan in another room. <<3>> Always running. But you don't hear it. <<3>> Because your brain has filtered it out. <<5>>\n\n"
            "That sound now becomes background. <<3>> Silenced. <<3>> Below your awareness. <<5>>\n\n"
            "Your brain decides what you hear. <<3>> Your brain chooses what matters. <<3>> And that sound doesn't matter. <<5>>\n\n"
            "Your subconscious turns the volume of that sound all the way down. <<3>> Lower. <<3>> Lower. <<3>> And lower still. <<5>>\n\n"
            "Until silence. <<5>>\n\n"
            "What you hear is what you choose to hear. <<3>> And you choose silence. You choose peace. <<5>>\n\n"
            "That ringing fades into nothing. <<3>> It is not part of your experience anymore. <<5>>\n\n"
            "And if it ever tries to return... your brain instantly tunes it out. <<3>> Like static on a radio you turned off. <<3>> Not there. <<5>>\n\n"
            "Silence in your ears. <<3>> Peace in your mind. <<3>> Clear hearing. <<3>> Clear thinking. <<3>> Clear being."
        ),
    },
    {
        "name": "08_anchor",
        "start_ms": 12 * 60 * 1000,  # 12:00
        "text": (
            "Now place one hand on your chest. <<3>> Feel the warmth. The presence. <<4>>\n\n"
            "Breathe in. <<3>> Breathe out. <<3>> And say, in your mind: <<3>>\n\n"
            "I am centered. I am clear. I am ready. <<5>>\n\n"
            "Again. I am centered. I am clear. I am ready. <<5>>\n\n"
            "This is your morning anchor. <<3>> Hand on chest. Breath. Words. <<4>>\n\n"
            "Anytime today, when you need to come back to center, you do this. Hand. Breath. Words. <<3>> And you are back."
        ),
    },
    {
        "name": "09_trigger_reversal",
        "start_ms": 14 * 60 * 1000,  # 14:00
        "text": (
            "Your subconscious is learning something new. <<4>>\n\n"
            "That spike you sometimes feel. The rush. The high. The urge to push everything at once. <<3>> It now means something different. <<5>>\n\n"
            "When you feel that energy rising, your body automatically paces itself. <<3>> You channel it. You don't burn it. <<5>>\n\n"
            "And on the days that used to feel heavy. The days that came after the high. <<3>> Those days are also learning. <<4>>\n\n"
            "The dip becomes a signal to rest. To recover. To take care of yourself. <<3>> Not to crash. Not to spiral. <<3>> Just to slow. <<5>>\n\n"
            "Your highs become sustainable. Your lows become recovery. <<3>> The middle is where you live now. <<5>>\n\n"
            "You are centered. You are paced. You are durable. <<3>>\n\n"
            "Push when it serves you. Rest when it serves you. <<3>> Always centered."
        ),
    },
    {
        "name": "10_dichotic_execution",
        "start_ms": 16 * 60 * 1000 + 30 * 1000,  # 16:30
        "repeat": 4,
        "repeat_gap_ms": 3000,
        "left_text": (
            "You are focused, you are sharp, you execute with clarity\n"
            "---\n"
            "You wake up early, you take action, you make it happen\n"
            "---\n"
            "You move forward today, you stay in your lane\n"
            "---\n"
            "You are paced, you are calm, you are unstoppable\n"
            "---\n"
            "You finish what you start, you keep your word"
        ),
        "right_text": (
            "I have full clarity in everything I do, I move with clarity\n"
            "---\n"
            "Whatever I plan, I make it happen\n"
            "---\n"
            "I trust my path, I stay in my lane\n"
            "---\n"
            "I am steady, I am consistent, I am unstoppable\n"
            "---\n"
            "I show up daily, I keep my word"
        ),
    },
    {
        "name": "11_self_care",
        "start_ms": 20 * 60 * 1000 + 30 * 1000,  # 20:30
        "text": (
            "Your body is your engine. <<3>> You take care of it every day. <<4>>\n\n"
            "You drink water first thing. <<3>> You move your body. <<3>> You eat clean food. <<3>> You sleep deep. <<5>>\n\n"
            "Caffeine when it serves you. None when it doesn't. <<3>> You know the difference. <<5>>\n\n"
            "No substances that dull your edge. None. <<3>> No interest. No pull. <<3>> Your body wants clarity. <<5>>\n\n"
            "Self-care is not optional. <<3>> It is how you stay sharp. <<3>> How you stay durable. <<3>> How you stay you."
        ),
    },
    {
        "name": "12_day_visualization",
        "start_ms": 22 * 60 * 1000 + 30 * 1000,  # 22:30
        "text": (
            "Now see today in front of you. <<5>>\n\n"
            "Six AM. Eyes open. <<3>> You get out of bed. You drink water. You move. <<5>>\n\n"
            "You open the laptop. You open PropStream. You pull deals. You make offers. <<3>> You send emails. <<5>>\n\n"
            "You talk to the team. You lead. You decide. <<5>>\n\n"
            "Noon. You eat. You move again. You walk. <<4>>\n\n"
            "Afternoon. You execute. No distraction. <<3>> One thing at a time. Done. <<5>>\n\n"
            "Evening. You wind down. Family time. <<3>> You are present. Phone away. <<5>>\n\n"
            "You sleep deep. You wake up tomorrow ready. <<5>>\n\n"
            "This is the pattern. <<3>> You. Daily. Centered. Executing."
        ),
    },
    {
        "name": "13_dichotic_identity",
        "start_ms": 25 * 60 * 1000,  # 25:00
        "repeat": 3,
        "repeat_gap_ms": 3000,
        "left_text": (
            "You are abundant, you attract opportunity, you create wealth\n"
            "---\n"
            "You are calm, you are clear, you live in peace\n"
            "---\n"
            "You are loved, you are loving, you are connected"
        ),
        "right_text": (
            "I am abundant in everything I touch, I create wealth\n"
            "---\n"
            "Nothing shakes the peace I live in, I live in peace\n"
            "---\n"
            "I love deeply, I receive love, I am connected"
        ),
    },
    {
        "name": "14_daily_commitment",
        "start_ms": 27 * 60 * 1000,  # 27:00
        "text": (
            "Every morning you do this. <<3>> Every morning. <<3>> Thirty minutes that set the day. <<5>>\n\n"
            "You look forward to it. <<3>> You miss it when you skip it. <<5>>\n\n"
            "This is the most important thing you do for yourself. <<3>> The foundation. <<3>> The reset. <<3>> The aim."
        ),
    },
    {
        "name": "15_body_healing",
        "start_ms": 28 * 60 * 1000 + 30 * 1000,  # 28:30
        "use_intro_settings": True,
        "text": (
            "And now, with your body deeply relaxed... and your mind open... we turn attention inward. <<5>>\n\n"
            "Your body is intelligent. <<3>> It knows how to heal itself. <<3>> Every cell. Every organ. Every system. <<3>> Knows exactly what to do. <<5>>\n\n"
            "Right now, in this state, that healing intelligence is fully active. <<5>>\n\n"
            "Let your awareness travel through your body. <<4>>\n\n"
            "Starting at the top of your head. <<4>> Down through your face. <<3>> Your jaw. <<3>> Your neck. <<5>>\n\n"
            "Down into your shoulders. <<3>> Your chest. <<3>> Your lungs. <<3>> Your heart. <<5>>\n\n"
            "Wherever your attention pauses, healing energy gathers there. <<5>>\n\n"
            "Down through your arms. <<3>> Your hands. <<3>> Your fingers. <<5>>\n\n"
            "Through your stomach. <<3>> Your back. <<3>> Your hips. <<5>>\n\n"
            "Down your legs. <<3>> Your knees. <<3>> Your calves. <<3>> Your feet. <<5>>\n\n"
            "Your subconscious knows exactly where to send the energy. <<3>> What needs more attention. What needs more care. <<5>>\n\n"
            "You don't have to think about it. Your body knows. <<5>>\n\n"
            "Every system tunes itself. <<3>> Every cell does its work. <<3>> Repair happens. <<3>> Restoration happens. <<3>> Health is the default. <<5>>\n\n"
            "Mind over body. <<3>> Body responds. <<5>>\n\n"
            "And every morning you do this... <<3>> the healing deepens. <<3>> The body grows stronger. <<3>> More resilient. <<5>>\n\n"
            "This is you, taking care of yourself, at the deepest level."
        ),
    },
    {
        "name": "16_centeredness",
        "start_ms": 32 * 60 * 1000,  # 32:00
        "text": (
            "Before we finish, one more thing. <<4>>\n\n"
            "You are centered. <<3>> Even when the day pushes, you stay centered. <<5>>\n\n"
            "When the high comes, you are centered. <<3>> When the low comes, you are centered. <<3>> Always centered. <<5>>\n\n"
            "This is your default state. <<3>> Not high. Not low. <<3>> Centered. Durable. You. <<5>>\n\n"
            "And no matter what happens today, you have this. <<3>> Hand on chest. Breath. Words. <<3>> Always available. <<5>>\n\n"
            "You are ready."
        ),
    },
    {
        "name": "17_wake_up",
        "start_ms": 34 * 60 * 1000,  # 34:00
        "text": (
            "Now I count from one to five. With each number, you become more alert. More energized. More ready. <<4>>\n\n"
            "One. Awareness returning. Body waking up. <<4>>\n\n"
            "Two. Energy rising in your chest. Mind clearing. <<4>>\n\n"
            "Three. You feel strong. Confident. Ready. <<4>>\n\n"
            "Four. Eyes ready to open. Body ready to move. <<4>>\n\n"
            "Five. Eyes open. Awake. Alert. <<3>>\n\n"
            "Centered. Clear. Ready to win the day."
        ),
        "use_wake_settings": True,
    },
]

PAUSE_RE = re.compile(r"<<(\d+(?:\.\d+)?)>>")


def _eleven_render_chunk(client, text: str, settings=VOICE_SETTINGS) -> AudioSegment:
    import time
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
            wait = 2 ** attempt  # 1, 2, 4, 8, 16
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
    """
    Morning binaural progression:
    - 0-3 min: 10 Hz (alpha, relaxation onset)
    - 3-13 min: 7 Hz (theta, suggestion-receptive)
    - 13-21 min: 10 Hz (alpha, alert calm)
    - 21-25 min: 14 Hz (low beta, increasing alertness)
    - 25-32 min: 18 Hz (mid beta, fully alert wake-up)
    """
    print("[binaural] Synthesizing morning progression...")
    carrier = 200.0
    stages = [
        (0, 3, 10.0),
        (3, 16, 7.0),
        (16, 25, 10.0),
        (25, 28, 7.0),    # back to theta for body healing work
        (28, 32, 10.0),
        (32, 36, 18.0),   # beta for wake-up at the end
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
    """
    Morning music pad: Brighter, more uplifting progression: C - G - Am - F (I-V-vi-IV)
    Builds slightly toward end with more harmonic motion.
    """
    print("[ambient] Synthesizing morning music pad (C-G-Am-F)...")
    progression_midi = [
        [48, 55, 60, 64],  # C: C3, G3, C4, E4
        [43, 50, 55, 62],  # G: G2, D3, G3, D4
        [45, 52, 57, 64],  # Am: A2, E3, A3, E4
        [41, 48, 53, 60],  # F: F2, C3, F3, C4
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
    print("Morning Hypnosis Audio Generator - Ralph (English)")
    print("=" * 70)

    voice_track = build_voice_track()
    binaural_track = generate_binaural_track()
    ambient_track = generate_ambient_track()

    voice_track = voice_track[:TOTAL_DURATION_MS]
    binaural_track = binaural_track[:TOTAL_DURATION_MS]
    ambient_track = ambient_track[:TOTAL_DURATION_MS]

    print("[mix] Layering tracks...")
    binaural_track = binaural_track - 22
    ambient_track = ambient_track - 9  # slightly louder than evening: morning energy

    base = AudioSegment.silent(duration=TOTAL_DURATION_MS, frame_rate=SAMPLE_RATE).set_channels(2)
    mixed = base.overlay(ambient_track).overlay(binaural_track).overlay(voice_track)
    # Short fade-out so the wake-up at the end doesn't get cut
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
    print(f"Output:        {OUTPUT_FILE}")
    print(f"Duration:      {len(mixed)/1000/60:.2f} min")
    print(f"Size:          {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
