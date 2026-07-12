"""
Manuela Morning Hypnosis v1 (Brazilian Portuguese).
Activation companion to bedtime v3.
Night tape plants; morning activates execution for today.
"""

import io
import os
import re
import time
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "morning_hypnosis_manuela_v1.mp3"
WORK_DIR = Path("/tmp/hypnosis_manuela_morning_v1_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 22 * 60 * 1000  # 22 min

VOICE_ID = "t9UJ0smqFgPZJnchMfob"  # Manuela cloned
MODEL_ID = "eleven_multilingual_v2"

VOICE_SETTINGS_INTRO = {
    "stability": 0.75,
    "similarity_boost": 0.85,
    "style": 0.08,
    "speed": 0.85,
    "use_speaker_boost": True,
}

VOICE_SETTINGS = {
    "stability": 0.65,
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
        "name": "01_bom_dia",
        "start_ms": 0,
        "use_intro_settings": True,
        "text": (
            "Bom dia. <<3>>\n\n"
            "Sente ou deite. Olhos podem fechar. <<3>> Você não precisa fazer nada além de ouvir. <<3>> Isto é curto. Isto é focado. <<3>> Isto define as próximas doze horas da sua vida. <<5>>\n\n"
            "Preste atenção à sua respiração. <<3>> A subida. A descida. Acontecendo por si só. <<4>>\n\n"
            "Três respirações profundas. <<3>>\n\n"
            "Solte todo o ar. <<4>> E inspire. <<5>>\n\n"
            "Solte todo o ar. <<4>> E inspire. <<5>>\n\n"
            "Mais uma. Solte todo o ar. <<4>> E inspire."
        ),
    },
    {
        "name": "02_contagem",
        "start_ms": 2 * 60 * 1000,  # 2:00
        "use_intro_settings": True,
        "text": (
            "Agora, contando de cinco até um. <<3>> A cada número, você vai um pouco mais fundo. <<3>> Apenas o suficiente para receber tudo o que vem a seguir. <<5>>\n\n"
            "Cinco. Mais leve. Mais calma. <<4>>\n\n"
            "Quatro. A mente clareando. <<4>>\n\n"
            "Três. Corpo relaxado mas alerta. <<4>>\n\n"
            "Dois. Aberta. Receptiva. <<4>>\n\n"
            "Um. <<3>> Estado perfeito. Cada palavra entra fundo."
        ),
    },
    {
        "name": "03_ancora",
        "start_ms": 3 * 60 * 1000 + 30 * 1000,  # 3:30
        "text": (
            "Coloque uma das mãos no seu peito. <<3>> Sinta o calor. <<4>>\n\n"
            "Respire. <<3>>\n\n"
            "Diga na sua mente: Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<5>>\n\n"
            "De novo. Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<5>>\n\n"
            "Esta é a sua âncora para hoje. <<3>> Em qualquer momento que você precisar voltar pra você mesma, mão no peito, respiração, palavras. <<3>> Você volta na hora."
        ),
    },
    {
        "name": "04_identidade_hoje",
        "start_ms": 5 * 60 * 1000,  # 5:00
        "text": (
            "E hoje, você é: <<4>>\n\n"
            "Capaz. Forte. O Rock Balboa. <<5>>\n\n"
            "Estável. Saudável. Inteira. <<5>>\n\n"
            "Uma mulher que vem em primeiro lugar. Que se cuida primeiro, pra poder cuidar dos outros depois. <<5>>\n\n"
            "Uma profissional com voz. Com presença. Com marca. <<5>>\n\n"
            "Uma mãe presente, estável, saudável, profunda. <<5>>\n\n"
            "Você é aceita. Por você. <<3>> Você não precisa da aceitação de ninguém. <<5>>\n\n"
            "Você é maravilhosa. Você é bonita. Você aguenta. <<3>> Você consegue."
        ),
    },
    {
        "name": "05_comportamentos_hoje",
        "start_ms": 7 * 60 * 1000,  # 7:00
        "text": (
            "Hoje, suas ações estão claras. <<4>>\n\n"
            "Você acorda grata. Estável. Levemente feliz por acordar. <<5>>\n\n"
            "Você se levanta com vontade. <<3>> Você se move. Pode ser musculação. Pode ser ioga. Pode ser uma corrida. <<3>> Movimento que te dá adrenalina, que te acorda por inteira. <<5>>\n\n"
            "Você toma um banho longo, sozinha. Sem pressa. <<3>> Esse momento é seu. <<5>>\n\n"
            "Você vai para o trabalho com presença. <<3>> Sua voz nas reuniões. Sua marca no que você faz. <<3>> Você se conecta com seu time. Você dá suporte ao negócio. <<5>>\n\n"
            "Você busca seus filhos. <<3>> Você está presente com eles, de verdade. <<5>>\n\n"
            "Você janta em família. Calma. Conectada. <<5>>\n\n"
            "E uma noite tranquila. <<3>> Você dorme bem. <<3>> E amanhã, você acorda assim de novo. <<5>>\n\n"
            "Se o pensamento eu não sou capaz tentar voltar, mão no peito. Respiração. Palavras. <<3>> Você volta em segundos. <<5>>\n\n"
            "Você coloca limites com amor. <<3>> Você diz não sem culpa, quando precisa. <<3>> Você se prioriza, não como egoísmo, mas como sabedoria."
        ),
    },
    {
        "name": "06_dichotic_hoje",
        "start_ms": 11 * 60 * 1000,  # 11:00
        "repeat": 3,
        "repeat_gap_ms": 2500,
        "left_text": (
            "Você vem primeiro hoje, você se cuida, você está bem\n"
            "---\n"
            "Você é capaz, você é forte, você consegue\n"
            "---\n"
            "Você coloca limites com amor, você diz não com tranquilidade\n"
            "---\n"
            "Você é aceita, você se aceita, você não precisa de aprovação"
        ),
        "right_text": (
            "Eu venho primeiro hoje. Eu me cuido. Eu estou bem\n"
            "---\n"
            "Eu sou capaz. Eu sou forte. Eu consigo\n"
            "---\n"
            "Eu coloco limites com amor. Eu digo não com tranquilidade\n"
            "---\n"
            "Eu sou aceita. Eu me aceito. Não preciso de aprovação"
        ),
    },
    {
        "name": "07_visualiza_hoje",
        "start_ms": 14 * 60 * 1000,  # 14:00
        "text": (
            "Agora veja seu dia, na sua mente. <<5>>\n\n"
            "Você começa forte. <<3>> Movimento. Banho. Respiração. <<3>> Você sai pronta. <<5>>\n\n"
            "No meio do dia, você come bem. Você se move de novo. Você permanece clara. <<5>>\n\n"
            "Você lida com tudo o que vier com calma. <<3>> Gatilhos são sinais para respirar, não para reagir. <<5>>\n\n"
            "À noite, você fez o que importava. <<3>> Você sente um cansaço bom, não exaustão. <<5>>\n\n"
            "Você dorme bem esta noite, e amanhã você acorda pronta de novo. <<5>>\n\n"
            "Este é o seu dia. <<3>> Já em movimento. <<3>> Já inevitável."
        ),
    },
    {
        "name": "08_fechamento_centrado",
        "start_ms": 17 * 60 * 1000,  # 17:00
        "text": (
            "E antes de terminarmos, lembre-se: <<4>>\n\n"
            "Você é centrada. Mesmo quando o dia empurra. <<5>>\n\n"
            "Você é inabalável. Opiniões não te movem. Pressões não te dobram. <<5>>\n\n"
            "Você é a mulher que se cuida. Que se prioriza. Que se ama primeiro. <<5>>\n\n"
            "Mão no peito. Respiração. Palavras. <<3>> Sempre disponível."
        ),
    },
    {
        "name": "09_despertar",
        "start_ms": 19 * 60 * 1000,  # 19:00
        "use_wake_settings": True,
        "text": (
            "Agora, contando de um até cinco. A cada número, você fica mais alerta. Mais energizada. Mais pronta. <<4>>\n\n"
            "Um. Consciência voltando. Corpo acordando. <<4>>\n\n"
            "Dois. Mente clareando. Foco afiando. <<4>>\n\n"
            "Três. Você se sente forte. Confiante. Capaz. <<4>>\n\n"
            "Quatro. Olhos prontos para abrir. Corpo pronto para se mover. <<4>>\n\n"
            "Cinco. Olhos abertos. Acordada. Alerta. <<3>>\n\n"
            "Centrada. Clara. Pronta para o seu dia."
        ),
    },
]

PAUSE_RE = re.compile(r"<<(\d+(?:\.\d+)?)>>")


def _eleven_render_chunk(client, text, settings=VOICE_SETTINGS):
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


def render_text_with_pauses(client, text, cache_path, settings=VOICE_SETTINGS):
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return AudioSegment.from_file(cache_path, format="mp3").set_channels(2).set_frame_rate(SAMPLE_RATE)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    rendered = []
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


def render_dichotic_phrase_pair(client, l_text, r_text, cache_dir, idx):
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
    """Morning: alpha -> theta -> alpha -> beta (going UP for wake-up)"""
    print("[binaural] Synthesizing morning progression...")
    carrier = 200.0
    stages = [
        (0, 2, 10.0),
        (2, 11, 7.0),
        (11, 17, 10.0),
        (17, 19, 14.0),
        (19, 22, 18.0),
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
    progression_midi = [[48, 55, 60, 64], [43, 50, 55, 62], [45, 52, 57, 64], [41, 48, 53, 60]]
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
    print("Manuela Morning Hypnosis v1 (PT-BR, activation companion to bedtime v3)")
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
