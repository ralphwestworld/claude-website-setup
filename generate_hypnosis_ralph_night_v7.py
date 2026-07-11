"""
Bedtime Hypnosis - Ralph v7.
v6 content preserved exactly. v7 = v6 + three new sections + softer voice settings:
- 00_soothing_intro (NEW, before v6's welcome): McKenna-style permissive prep
- 03b_tinnitus (NEW, after countdown deepener while deepest in trance)
- 07d_body_healing (NEW, before sleep transition)
All v6 sections kept as-is.
"""

import io
import os
import re
import time
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "bedtime_hypnosis_realestate_v7.mp3"
WORK_DIR = Path("/tmp/hypnosis_ralph_v7_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 52 * 60 * 1000  # 52 min - reordered: newest sections front-loaded before sleep onset

VOICE_ID = "yL36RsgevEFpAJK9HWYh"  # Ralph West cloned
MODEL_ID = "eleven_multilingual_v2"

# Softer / more soothing base for all v6 sections (vs v6's original)
VOICE_SETTINGS = {
    "stability": 0.7,
    "similarity_boost": 0.85,
    "style": 0.05,
    "speed": 0.85,
    "use_speaker_boost": True,
}

# Even slower / drowsier for the new McKenna-style intro + tinnitus + body healing
VOICE_SETTINGS_INTRO = {
    "stability": 0.8,
    "similarity_boost": 0.85,
    "style": 0.05,
    "speed": 0.8,
    "use_speaker_boost": True,
}

# Terminal-tone for the final goodnight - forces falling intonation
VOICE_SETTINGS_FINAL = {
    "stability": 0.9,
    "similarity_boost": 0.85,
    "style": 0.0,
    "speed": 0.78,
    "use_speaker_boost": True,
}

SEGMENTS = [
    # === NEW: McKenna-style soothing intro (BEFORE v6 begins) ===
    {
        "name": "00_soothing_intro",
        "start_ms": 0,
        "use_intro_settings": True,
        "text": (
            "Welcome. <<3>>\n\n"
            "Make yourself comfortable. <<3>> Lying down. Arms relaxed. Legs uncrossed. <<3>> No need to do anything yet. Just listen. <<5>>\n\n"
            "This experience is not yet sleep. <<3>> You'll still have awareness. You'll hear everything I say. You won't become unconscious. <<4>>\n\n"
            "But there will be changes. <<3>> Gentle changes. <<3>> In how you feel. How you think. How you act tomorrow. <<5>>\n\n"
            "It's like daydreaming. <<3>> All you need to do is relax. Let the sounds wash over you. <<5>>\n\n"
            "Pay attention to your breathing. <<3>> The gentle rise. <<3>> And the gentle fall. <<3>> Happening all by itself. <<5>>\n\n"
            "Before you relax further... take some deeper breaths. <<4>>\n\n"
            "Push all the way out. <<5>> And gently... breathe in. <<5>>\n\n"
            "Push all the way out. <<5>> And gently... breathe in. <<5>>\n\n"
            "One more. Push all the way out. <<4>> And gently... breathe in. <<5>>\n\n"
            "And now my voice will go with you as you relax. <<4>>\n\n"
            "Tonight, your subconscious takes over. <<3>> Every word will be absorbed deep into the part of you that builds your future."
        ),
    },
    # === v6's 02_progressive_relaxation (PRESERVED EXACTLY) ===
    {
        "name": "02_progressive_relaxation",
        "start_ms": 3 * 60 * 1000,  # 3:00
        "text": (
            "Take a slow, deep breath in through your nose. <<3>> And let it out slowly through your mouth. <<4>>\n\n"
            "Again. Breathe in deeply. <<4>> And out, releasing everything that no longer serves you. <<4>>\n\n"
            "One more breath. In. <<3>> And out, letting your body melt into the bed. <<5>>\n\n"
            "Now bring your awareness to your feet. <<3>> Let your feet become heavy, soft, relaxed. <<3>>\n\n"
            "Move that feeling up into your calves and shins. <<3>> Loose, warm, supported. <<3>>\n\n"
            "Up into your knees and thighs. Let them surrender, sink down. <<3>>\n\n"
            "Feel your hips and lower back. <<2>> Let it all release. <<3>>\n\n"
            "Up through your stomach, and chest. Each breath gentler than the last. <<3>>\n\n"
            "Drop your shoulders. Away from your ears. <<2>> Arms heavy. Hands relaxed. <<3>>\n\n"
            "Now your neck, your jaw. <<2>> Soften the muscles around your eyes, your forehead. <<3>>\n\n"
            "Your whole body is heavy, warm, at ease. And you are going deeper with every breath."
        ),
    },
    # === v6's 03_countdown_deepener (PRESERVED EXACTLY) ===
    {
        "name": "03_countdown_deepener",
        "start_ms": 6 * 60 * 1000,  # 6:00
        "text": (
            "In a moment I am going to count down from ten to one. With each number, you will find yourself drifting twice as deep into total relaxation. <<3>>\n\n"
            "Twice as deep. Twice as peaceful. Twice as ready to receive everything I share with you tonight. <<3>>\n\n"
            "Ten. Going down now. Letting go. <<3>>\n\n"
            "Nine. Sinking deeper into the bed beneath you. Heavier. <<3>>\n\n"
            "Eight. Twice as deep as before. Your mind softening. <<3>>\n\n"
            "Seven. The outside world drifting further away. Only my voice now. <<3>>\n\n"
            "Six. Halfway there. Profoundly relaxed. <<3>>\n\n"
            "Five. Even deeper. Your subconscious wide open. <<3>>\n\n"
            "Four. So deeply relaxed, you feel like you are floating. <<3>>\n\n"
            "Three. The deepest level of trance you have ever experienced. <<3>>\n\n"
            "Two. Beyond thought. Beyond effort. Just being. <<3>>\n\n"
            "One. You are now in the perfect state to receive everything I say. Every word, every image, every suggestion goes deep into your subconscious mind, where it takes root, and grows."
        ),
    },
    # === NEW: Tinnitus suppression (inserted at deepest point in trance) ===
    {
        "name": "03b_tinnitus",
        "start_ms": 39 * 60 * 1000,  # 39:00 (OLD - nearly locked, still lands in delta)
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
    # === v6's 04_staircase_visualization (PRESERVED EXACTLY) ===
    {
        "name": "04_staircase_visualization",
        "start_ms": 9 * 60 * 1000,  # 9:00 (visualization deepener completes induction)
        "text": (
            "Imagine yourself at the top of a beautiful staircase. <<4>>\n\n"
            "It descends into your perfect place. The version of your life where you have already arrived. <<3>>\n\n"
            "Ten steps down. With each step, deeper. <<3>>\n\n"
            "Take the first step. Ten. <<3>>\n\n"
            "Nine. The image becoming clearer. <<3>>\n\n"
            "Eight. Seven. A warm light welcomes you. <<3>>\n\n"
            "Six. Five. Halfway down. <<3>>\n\n"
            "Four. Three. You can feel the air. <<3>>\n\n"
            "Two. One. You step off, and you are here. <<5>>\n\n"
            "Look around. <<4>> This is your place. <<4>>\n\n"
            "You are standing in front of a building. One of yours. One of your thirty doors. <<5>>\n\n"
            "Walk inside. <<3>> Feel the floors. Touch the walls. This is yours. <<4>>\n\n"
            "Step outside, and look down the street. There are more. Each one yours. Each one generating cash flow while you sleep. <<5>>\n\n"
            "Notice the certainty in your body. This is not a fantasy. This is a memory. A future memory already in motion."
        ),
    },
    # === v6's 05_identity_dichotic (PRESERVED EXACTLY) ===
    {
        "name": "05_identity_dichotic",
        "start_ms": 25 * 60 * 1000 + 30 * 1000,  # 25:30 (OLD - nearly locked, moved later)
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
    # === v6's 06_behavioral_dichotic (PRESERVED EXACTLY) ===
    {
        "name": "06_behavioral_dichotic",
        "start_ms": 30 * 60 * 1000,  # 30:00 (OLD - nearly locked)
        "repeat": 4,
        "repeat_gap_ms": 3000,
        "left_text": (
            "Every morning, you show up. You analyze deals. You make offers.\n\n"
            "You contact sellers. You build relationships. You negotiate from a position of certainty.\n\n"
            "You build your acquisition systems. You automate what other investors do manually.\n\n"
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
    # === v6's 07_future_pacing (PRESERVED EXACTLY) ===
    {
        "name": "07_future_pacing",
        "start_ms": 34 * 60 * 1000,  # 34:00 (OLD)
        "text": (
            "See yourself one year from now. <<5>>\n\n"
            "You are in your home office. On the wall, a map. Pins mark every property you own. Fifty doors now. Fifty. <<5>>\n\n"
            "You see your accounts. The cash flow is real. The equity is real. It is all yours. <<4>>\n\n"
            "Your team handles operations. You find the next deal. You are not stressed. You are building. Calmly. Inevitably. <<4>>\n\n"
            "Notice your body in this future. <<3>> Strong. Centered. Free. <<4>>\n\n"
            "Notice the people you love around you. Notice the man you have become. <<5>>\n\n"
            "Reach forward and shake your own hand. <<3>> Thank yourself. You did it. <<4>>\n\n"
            "Every deal, every offer, every cold call paid off. <<3>>\n\n"
            "This future is closer than you think. The path you are on right now leads directly here. Inevitably."
        ),
    },
    # === NEW: Abundance / Lakefront Mansion (wealth lifestyle visualization) ===
    {
        "name": "07a_abundance_mansion",
        "start_ms": 20 * 60 * 1000,  # 20:00 (NEWEST - front-loaded)
        "text": (
            "And now, see another part of your future. The wealth your work creates. <<5>>\n\n"
            "You are rich. You are successful. <<3>> The numbers in your accounts grow every month. <<3>> Money flows in faster than it flows out. <<5>>\n\n"
            "This wealth provides for your entire family. <<3>> Not minimums. <<3>> The full life. <<3>> The life they deserve. The life you build for them. <<5>>\n\n"
            "Anything they want, you buy. <<3>> Anything they need, you provide. <<5>>\n\n"
            "You travel anywhere, anytime, as much as you wish. <<3>> No questions. No constraints. No stress about money. <<5>>\n\n"
            "Money is no longer a problem. <<3>> Money is a tool. <<3>> And you wield it well. <<5>>\n\n"
            "Your bank account holds forty-nine million, three hundred eighty-three thousand, thirty-six dollars and three cents. <<4>> Forty-nine million dollars. <<3>> Real. Earned. Yours. <<5>>\n\n"
            "Now see your home. <<5>>\n\n"
            "You drive up to your house on the Erie lakefront. <<3>> The road curves toward water. <<3>> The lake stretches out before you. Blue. Vast. Calm. <<5>>\n\n"
            "The house is yours. <<3>> Modern. Beautiful. Built exactly the way you wanted it. <<3>> Clean lines. Big windows. Light pouring in. <<5>>\n\n"
            "You pull into the garage. <<3>> Six cars. Yours. <<3>> Each one chosen by you. <<3>> The space is wide. Clean. Organized. <<5>>\n\n"
            "You walk through the front door. <<3>> The space is open. Warm. Quiet. <<3>> Yours. <<5>>\n\n"
            "Your family is here. <<3>> Safe. Comfortable. Happy. <<3>> The home you built makes their lives easier. Better. Fuller. <<5>>\n\n"
            "This is your reality now. <<3>> Not someday. <<3>> This is the future already in motion. <<3>> The future you are walking toward, every day, every decision, every action. <<5>>\n\n"
            "You are the man who built this. <<3>> The man whose work created it. <<3>> The man whose discipline brought him here. <<5>>\n\n"
            "You are rich. <<3>> You are successful. <<3>> You provide. <<3>> You give. <<3>> You build. <<5>>\n\n"
            "And it gets better every year. <<3>> Bigger. Fuller. Richer. <<3>> The mansion. The family. The freedom. <<3>> All real. All yours."
        ),
    },
    # === v6's 07b_identity_dichotic_round2 (PRESERVED EXACTLY) ===
    {
        "name": "07b_identity_dichotic_round2",
        "start_ms": 36 * 60 * 1000,  # 36:00 (OLD)
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
    # === v6's 07c_behavioral_round2 (PRESERVED EXACTLY) ===
    {
        "name": "07c_behavioral_round2",
        "start_ms": 38 * 60 * 1000,  # 38:00 (OLD)
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
    # === NEW: Mind, Mastery & External Resilience ===
    {
        "name": "07e_mind_mastery",
        "start_ms": 11 * 60 * 1000 + 30 * 1000,  # 11:30 (NEWEST - front-loaded, deep trance, still awake)
        "text": (
            "And now your subconscious is installing a new operating system for your mind. <<5>>\n\n"
            "You are intelligent. <<3>> You think fast. <<3>> Your mind moves with clarity and speed. <<5>>\n\n"
            "You are responsible. <<3>> You do what you say you will do. <<3>> You finish what you start. <<3>> You do not procrastinate. <<5>>\n\n"
            "When you decide, you act. <<3>> When you commit, you execute. <<3>> The gap between thought and action closes. <<5>>\n\n"
            "You are a master of marketing. <<3>> You understand what moves people to buy. You craft messages that convert. <<5>>\n\n"
            "You are a master of sales. <<3>> You read the moment. You ask the right questions. You close. <<5>>\n\n"
            "You are a master of e-commerce. <<3>> You understand the funnels, the conversions, the data. You build systems that scale. <<5>>\n\n"
            "You are a master of the real estate industry. <<3>> Deals. Financing. Valuations. Negotiations. You see what others miss. <<5>>\n\n"
            "You are great at personal finances. <<3>> You manage your money efficiently. <<3>> Your money grows. Your money compounds. Your wealth multiplies, month after month, year after year. <<5>>\n\n"
            "You are a master of psychology. <<3>> You understand how people think. You read behavior patterns instantly. You see motivations clearly. <<5>>\n\n"
            "You influence and persuade anyone. <<3>> Your words land. Your presence moves people. You lead any conversation. You shape any interaction. <<5>>\n\n"
            "You shape the world around you with the power of your mind. <<3>> What you focus on expands. What you decide manifests. <<3>> Your thoughts shape your reality. <<5>>\n\n"
            "And you are immune to external noise. <<3>> The news of the world does not shake you. <<3>> The pressure of others does not bend you. <<3>> The opinions of people who do not know you do not move you. <<5>>\n\n"
            "You filter what enters your mind. <<3>> You choose what to focus on. <<3>> You protect your inner state, because your inner state determines your outer life. <<5>>\n\n"
            "You are unshakeable."
        ),
    },
    # === NEW: Health, Body & Vitality ===
    {
        "name": "07f_health_vitality",
        "start_ms": 16 * 60 * 1000 + 30 * 1000,  # 16:30 (NEWEST - front-loaded)
        "text": (
            "And now your subconscious turns to your body. To your health. <<5>>\n\n"
            "You are healthy. <<3>> Your body is well. <<3>> Every system functioning at its peak. <<5>>\n\n"
            "The anxiety that used to come, no longer comes. <<3>> The panic attacks that used to seize you, no longer seize you. <<3>> They are a memory. A past version. <<3>> Not you anymore. <<5>>\n\n"
            "Your body remains calm under any circumstance. <<3>> Your nervous system stays regulated. <<3>> Your heart steady. Your breath even. <<5>>\n\n"
            "If something needs healing in your body, you heal it. Fast. <<3>> Your body repairs itself rapidly. <<3>> Your immune system is strong. <<3>> Your recovery is quick. <<5>>\n\n"
            "You are fit. <<3>> Your body is lean. <<3>> Your muscles are defined. <<3>> You move with strength and grace. <<5>>\n\n"
            "You eat what serves you. <<3>> You move daily. <<3>> You sleep deeply. <<3>> Your body responds to the care you give it. <<5>>\n\n"
            "And you have stopped vaping. <<3>> The pull is gone. <<3>> The craving is gone. <<3>> Your lungs breathe clean air now. <<3>> Your body thanks you, every breath. <<5>>\n\n"
            "That habit belongs to a past version of you. <<3>> The version who is gone."
        ),
    },
    # === NEW: Body healing (mind over body, autonomic balance, before sleep transition) ===
    {
        "name": "07d_body_healing",
        "start_ms": 42 * 60 * 1000 + 30 * 1000,  # 42:30 (works during sleep - stays near end)
        "use_intro_settings": True,
        "text": (
            "And now, with your body deeply relaxed, and your mind open, we turn attention inward. <<5>>\n\n"
            "Your body is intelligent. <<3>> It knows how to heal itself. <<3>> Every cell. Every organ. Every system. <<3>> Knows exactly what to do. <<5>>\n\n"
            "Right now, in this state, that healing intelligence is fully active. <<5>>\n\n"
            "Let your awareness travel through your body. <<4>>\n\n"
            "Starting at the top of your head. <<4>> Down through your face. <<3>> Your jaw. <<3>> Your neck. <<5>>\n\n"
            "Your thyroid, in your neck, balances itself. <<3>> Hormones flow correctly. <<3>> Every gland in your endocrine system finds its natural rhythm. <<5>>\n\n"
            "Down into your shoulders. <<3>> Your chest. <<3>> Your lungs breathe deeper, easier. <<3>> Your heart slows to its natural rhythm. Steady. Calm. <<5>>\n\n"
            "Wherever your attention pauses, healing energy gathers there. <<5>>\n\n"
            "Down through your arms. <<3>> Your hands. <<3>> Your fingers. <<5>>\n\n"
            "Through your stomach. <<3>> Your digestion calms. <<3>> Your appetite returns, steady and healthy. You eat what your body asks for. <<5>>\n\n"
            "Your back. <<3>> Your hips. <<3>> Your lower belly. <<5>>\n\n"
            "Down your legs. <<3>> Your knees. <<3>> Your calves. <<3>> Your feet. <<5>>\n\n"
            "Now your nervous system finds calm. <<3>> The fight side eases. The rest side rises. <<3>> You shift from alert to rest, automatically. <<5>>\n\n"
            "Cortisol drops as the night deepens. <<3>> Melatonin rises naturally. <<3>> Your body knows the timing. <<5>>\n\n"
            "Your sleep tonight is repairing. <<3>> Deep sleep, deeper. <<3>> REM sleep, clearer. <<3>> The architecture of your sleep, restored. <<5>>\n\n"
            "Your subconscious knows exactly where to send the energy. <<3>> What needs more attention. What needs more care. <<5>>\n\n"
            "You don't have to think about it. Your body knows. <<5>>\n\n"
            "Every system tunes itself. <<3>> Every cell does its work. <<3>> Repair happens. <<3>> Restoration happens. <<3>> Health is the default. <<5>>\n\n"
            "And now, your body and your mind are one team. <<3>> Working together. <<3>> Your body knows what your mind decides. Your mind trusts what your body feels. <<5>>\n\n"
            "No more split. <<3>> No more two-people feeling. <<3>> One person. One Ralph. Whole. <<5>>\n\n"
            "Every night you do this, the healing deepens. <<3>> The body grows stronger. More resilient. <<3>> The mind grows clearer. More integrated. <<5>>\n\n"
            "This is you, taking care of yourself, at the deepest level."
        ),
    },
    # === v6's 08_sleep_transition (PRESERVED EXACTLY + final phrase for terminal intonation) ===
    {
        "name": "08_sleep_transition",
        "start_ms": 49 * 60 * 1000,  # 49:00 (must stay last)
        "text": (
            "And now, your body grows heavier, your mind drifts deeper. <<3>> Everything is settling. Into the place where identity is formed. <<4>>\n\n"
            "While you sleep, your subconscious will rehearse, organize, reinforce. Every system. Every belief. Every action. <<4>>\n\n"
            "You will wake up tomorrow clear, motivated, already in motion. <<4>>\n\n"
            "Every night you listen, the changes go deeper. You become more of who you already are. <<4>>\n\n"
            "Nothing to do now. Nothing to think about. <<4>>\n\n"
            "Just drift. <<3>> Deeper. <<3>> Into a perfect, healing sleep."
        ),
        "final_phrase": "Goodnight.",
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
                            settings=VOICE_SETTINGS,
                            final_phrase: str | None = None) -> AudioSegment:
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

    if final_phrase:
        rendered.append(AudioSegment.silent(duration=4000, frame_rate=SAMPLE_RATE).set_channels(2))
        rendered.append(_eleven_render_chunk(client, final_phrase, settings=VOICE_SETTINGS_FINAL))

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
    # v6 used \n\n as phrase separator, not ---
    l_phrases = [p.strip() for p in seg["left_text"].split("\n\n") if p.strip()]
    r_phrases = [p.strip() for p in seg["right_text"].split("\n\n") if p.strip()]
    assert len(l_phrases) == len(r_phrases), f"Phrase count mismatch in {seg['name']}: L={len(l_phrases)} R={len(r_phrases)}"

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
            settings = VOICE_SETTINGS_INTRO if seg.get("use_intro_settings") else VOICE_SETTINGS
            voice = render_text_with_pauses(client, seg["text"], cache_path,
                                            settings=settings,
                                            final_phrase=seg.get("final_phrase"))
            voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
            lead_in = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
            voice = lead_in + voice
            full = full.overlay(voice, position=seg["start_ms"])
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, length {len(voice)/1000:.1f}s")

    return full[:TOTAL_DURATION_MS]


def generate_binaural_track() -> AudioSegment:
    """
    40-min sleep-bound progression aligned to the new structure:
    - 0-4 min: 10 Hz alpha (the new soothing intro + v6 welcome)
    - 4-9 min: 7 Hz theta (relaxation + countdown deepening)
    - 9-14 min: 4 Hz delta (deepest - tinnitus suppression)
    - 14-31 min: 4 Hz delta (sustained for staircase + identity + behavioral + future + rounds)
    - 31-36 min: 3 Hz mid-delta (body healing)
    - 36-40 min: 2 Hz deep delta (sleep transition)
    """
    print("[binaural] Synthesizing sleep-bound progression...")
    carrier = 200.0
    stages = [
        (0, 3, 10.0),
        (3, 8, 7.0),
        (8, 42, 4.0),      # delta across the front-loaded suggestion window
        (42, 49, 3.0),     # mid-delta during body healing
        (49, 52, 2.0),     # deep delta for sleep transition
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
    """Same Am-F-C-G evening pad as v6."""
    print("[ambient] Synthesizing evening music pad (Am-F-C-G)...")
    progression_midi = [
        [45, 48, 52, 57],
        [41, 45, 48, 53],
        [48, 52, 55, 60],
        [43, 47, 50, 55],
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
            voice_amp = 0.32 if j == 0 else (0.24 if j == 1 else 0.18)
            chord_wave_l += voice_amp * np.sin(phase_l).astype(np.float32)
            chord_wave_r += voice_amp * np.sin(phase_r).astype(np.float32)
        chord_wave_l = np.tanh(chord_wave_l * 0.9)
        chord_wave_r = np.tanh(chord_wave_r * 0.9)
        local_env = env[:length]
        chord_wave_l *= local_env
        chord_wave_r *= local_env
        out_left[start:end] += chord_wave_l
        out_right[start:end] += chord_wave_r
    pan_lfo = 0.15 * np.sin(2 * np.pi * 0.04 * t_full).astype(np.float32)
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
    print("Bedtime Hypnosis - Ralph v7 (v6 + soothing intro + tinnitus + healing)")
    print("=" * 70)

    voice_track = build_voice_track()
    binaural_track = generate_binaural_track()
    ambient_track = generate_ambient_track()

    voice_track = voice_track[:TOTAL_DURATION_MS]
    binaural_track = binaural_track[:TOTAL_DURATION_MS]
    ambient_track = ambient_track[:TOTAL_DURATION_MS]

    print("[mix] Layering tracks...")
    binaural_track = binaural_track - 22
    ambient_track = ambient_track - 10

    base = AudioSegment.silent(duration=TOTAL_DURATION_MS, frame_rate=SAMPLE_RATE).set_channels(2)
    mixed = base.overlay(ambient_track).overlay(binaural_track).overlay(voice_track)
    mixed = mixed.fade_in(5000).fade_out(45000)

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
