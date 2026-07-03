"""
Manuela tapes v4 - SHORT versions per her 7/3 feedback:
- Morning: ~10 min (was 22)
- Night: ~20 min (was 48)
- Pauses cut roughly in half (was too slow)
- Whole-paragraph rendering: fewer pause markers inside paragraphs so ElevenLabs
  keeps natural prosody/breathing (fixes "dry, cut off" delivery)
- 250ms padding around each chunk (fixes clipped word edges)
- Slightly livelier voice settings (fixes dry delivery)

Generates BOTH tapes in one run.
"""

import io
import os
import re
import time
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
VOICE_ID = "t9UJ0smqFgPZJnchMfob"  # Manuela cloned
MODEL_ID = "eleven_multilingual_v2"

# Livelier than before: lower stability + a touch more style = natural inflection
VOICE_SETTINGS = {
    "stability": 0.62,
    "similarity_boost": 0.85,
    "style": 0.18,
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

VOICE_SETTINGS_FINAL = {
    "stability": 0.85,
    "similarity_boost": 0.85,
    "style": 0.05,
    "speed": 0.82,
    "use_speaker_boost": True,
}

PAUSE_RE = re.compile(r"<<(\d+(?:\.\d+)?)>>")

# ============ NIGHT TAPE (~20 min) ============
NIGHT_SEGMENTS = [
    {
        "name": "01_boas_vindas",
        "start_ms": 0,
        "text": (
            "Olá. Encontre uma posição confortável, deitada, braços relaxados. Você não precisa fazer nada além de ouvir. "
            "Esta experiência ainda não é o sono. Você ouve tudo o que eu digo, e tudo que você precisa fazer é relaxar e deixar os sons te envolverem. <<2>>\n\n"
            "Preste atenção à sua respiração. A subida suave, e a descida suave, acontecendo por si só. <<2>>\n\n"
            "Agora respire fundo. Solte todo o ar. <<2>> E inspire suavemente. <<2>> Mais uma vez. Solte todo o ar. <<2>> E inspire. <<2>>\n\n"
            "Esta noite, seu subconsciente assume. Cada palavra vai ser absorvida bem fundo, no lugar onde as verdadeiras mudanças acontecem."
        ),
    },
    {
        "name": "02_relaxamento",
        "start_ms": 2 * 60 * 1000,  # 2:00
        "text": (
            "Sinta seus pés relaxarem. Suas pernas ficam soltas e pesadas. Seus quadris liberam. Sua barriga e seu peito amolecem. <<2>>\n\n"
            "Solte os ombros, para longe das orelhas. Braços pesados, mãos relaxadas. Pescoço macio, mandíbula solta, testa lisa. <<2>>\n\n"
            "Seu corpo inteiro está pesado, aquecido, em paz. E você vai mais fundo a cada respiração."
        ),
    },
    {
        "name": "03_contagem",
        "start_ms": 3 * 60 * 1000 + 30 * 1000,  # 3:30
        "text": (
            "Agora eu vou contar de dez até um, e a cada número você vai duas vezes mais fundo. <<2>>\n\n"
            "Dez, descendo agora. Nove, mais pesada. Oito, o dobro mais profunda. <<1.5>>\n\n"
            "Sete, o mundo lá fora se afastando. Seis, meio caminho. Cinco, seu subconsciente aberto. <<1.5>>\n\n"
            "Quatro, flutuando. Três, o nível mais profundo que você já experimentou. Dois, além do pensamento. <<1.5>>\n\n"
            "Um. Você está no estado perfeito. Cada palavra entra direto no lugar onde as crenças vivem, e fica."
        ),
    },
    {
        "name": "04_ancora",
        "start_ms": 5 * 60 * 1000 + 30 * 1000,  # 5:30
        "text": (
            "Coloque uma das mãos no seu peito. Sinta o calor, a presença. <<2>>\n\n"
            "Respire, e diga em silêncio: Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<3>>\n\n"
            "De novo. Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<3>>\n\n"
            "Este é o seu botão. Toda vez que você colocar a mão no peito, respirar, e dizer estas palavras, seu corpo entra automaticamente neste estado de calma e força. Em qualquer momento, em qualquer lugar, você volta."
        ),
    },
    {
        "name": "05_inversao",
        "start_ms": 7 * 60 * 1000 + 30 * 1000,  # 7:30
        "text": (
            "E agora seu subconsciente está aprendendo uma coisa nova. <<2>>\n\n"
            "Aquele primeiro pensamento que às vezes vem, o pensamento de que você não é capaz. A partir de hoje, ele significa algo diferente. <<2>>\n\n"
            "Quando ele vier, ele vira o seu sinal para pausar e lembrar: eu sou capaz. Olha tudo o que eu já fiz. Olha tudo o que eu sustento. Meu trabalho, meus filhos, a mulher que eu sou. <<2>>\n\n"
            "O mesmo pensamento que antes te puxava pra baixo, agora te traz de volta pra você. Mão no peito, respiração, palavras. Você volta. Sempre."
        ),
    },
    {
        "name": "06_aceitacao",
        "start_ms": 9 * 60 * 1000 + 30 * 1000,  # 9:30
        "text": (
            "Há memórias antigas que tentam te puxar pra baixo. Elas existiram, mas elas não são você. <<2>>\n\n"
            "A partir de hoje, uma verdade nova, mais profunda que qualquer memória: eu sou aceita. Eu me aceito. Eu não preciso da aceitação de ninguém. <<2>>\n\n"
            "O amor que você procurou em outras pessoas, você se dá agora. Você vive a sua vida sustentada por você mesma. <<2>>\n\n"
            "Você é aceita. Você é amada. Você é inteira. Por você, e para você."
        ),
    },
    {
        "name": "07_dichotic",
        "start_ms": 11 * 60 * 1000 + 30 * 1000,  # 11:30
        "repeat": 3,
        "repeat_gap_ms": 2000,
        "left_text": (
            "Você é capaz, você é forte, você é o Rock Balboa\n"
            "---\n"
            "Você vem primeiro, esse espaço é seu, você se cuida\n"
            "---\n"
            "Você é aceita, você coloca limites com amor, você é inteira"
        ),
        "right_text": (
            "Eu sou capaz. Eu sou forte. Eu sou o Rock Balboa\n"
            "---\n"
            "Eu venho primeiro. Esse espaço é meu. Eu me cuido\n"
            "---\n"
            "Eu sou aceita. Eu coloco limites com amor. Eu sou inteira"
        ),
    },
    {
        "name": "08_dia_perfeito",
        "start_ms": 14 * 60 * 1000,  # 14:00
        "text": (
            "Veja seu dia perfeito. Você acorda grata, estável, levemente feliz por acordar. <<2>>\n\n"
            "Você se move de manhã, e o movimento te dá energia. Um banho longo, sozinha, sem pressa. <<2>>\n\n"
            "No trabalho, sua voz nas reuniões, sua marca no que você faz, conexão com o seu time. <<2>>\n\n"
            "Você busca seus filhos, está presente de verdade. Um jantar em família, calmo. Uma noite tranquila. <<2>>\n\n"
            "E seus filhos, quando crescerem, vão se lembrar de uma mãe estável, saudável, feliz, profunda. Cada vez que você se cuida, você cuida deles também."
        ),
    },
    {
        "name": "09_cura",
        "start_ms": 16 * 60 * 1000 + 30 * 1000,  # 16:30
        "text": (
            "E agora, com seu corpo profundamente relaxado, a cura. <<2>>\n\n"
            "Seu corpo é inteligente. Ele sabe como se curar. Sua tireoide se equilibra, seus hormônios fluem corretamente, seu coração desacelera para o ritmo natural. <<2>>\n\n"
            "Seu sistema nervoso encontra calma. O alerta cede, o descanso se eleva. Cortisol baixa, melatonina sobe. <<2>>\n\n"
            "Seu sono esta noite repara. Sono profundo, mais profundo. E cada manhã você acorda mais forte. Essa é você, cuidando de você, no nível mais profundo."
        ),
    },
    {
        "name": "10_sono",
        "start_ms": 18 * 60 * 1000 + 30 * 1000,  # 18:30
        "text": (
            "Agora seu corpo fica cada vez mais pesado, sua mente vai mais fundo. <<2>>\n\n"
            "Enquanto você dorme, seu subconsciente vai ensaiar, organizar e reforçar cada palavra, cada caminho novo. Você vai acordar amanhã mais clara, mais leve, mais forte. <<2>>\n\n"
            "Não há nada para fazer agora. Apenas se entregar ao sono. Mais fundo, e mais fundo, em um sono perfeito, curativo, restaurador."
        ),
        "final_phrase": "Boa noite.",
    },
]

NIGHT_DURATION_MS = 21 * 60 * 1000
NIGHT_OUTPUT = OUTPUT_DIR / "bedtime_hypnosis_manuela_v4_short.mp3"
NIGHT_WORK = Path("/tmp/hypnosis_manuela_v4_night_build")

# ============ MORNING TAPE (~10 min) ============
MORNING_SEGMENTS = [
    {
        "name": "01_bom_dia",
        "start_ms": 0,
        "text": (
            "Bom dia. Sente ou deite, olhos podem fechar. Isto é curto e focado, e define o seu dia. <<2>>\n\n"
            "Respire fundo. Solte todo o ar. <<2>> E inspire. <<2>> Mais uma vez. Solte. <<2>> E inspire. <<2>>\n\n"
            "Contando de três até um, você vai apenas fundo o suficiente para receber. Três, mais leve. Dois, aberta e receptiva. Um. Estado perfeito."
        ),
    },
    {
        "name": "02_ancora",
        "start_ms": 2 * 60 * 1000,  # 2:00
        "text": (
            "Mão no peito. Sinta o calor. <<2>>\n\n"
            "Diga na sua mente: Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<2.5>>\n\n"
            "De novo. Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<2.5>>\n\n"
            "Esta é a sua âncora para hoje. Em qualquer momento, mão no peito, respiração, palavras, e você volta."
        ),
    },
    {
        "name": "03_hoje",
        "start_ms": 3 * 60 * 1000 + 30 * 1000,  # 3:30
        "text": (
            "Hoje você é capaz, forte, o Rock Balboa. Estável, saudável, inteira. Uma mulher que vem em primeiro lugar. <<2>>\n\n"
            "Hoje você acorda grata e se move. O movimento te dá energia. Um banho com calma, e você sai pronta. <<2>>\n\n"
            "No trabalho, sua voz, sua marca, sua presença. Com seus filhos, presença de verdade. <<2>>\n\n"
            "Você coloca limites com amor. Você diz não sem culpa quando precisa. Você se prioriza, não como egoísmo, mas como sabedoria. <<2>>\n\n"
            "Se o pensamento eu não sou capaz tentar aparecer, mão no peito, respiração, e você volta em segundos."
        ),
    },
    {
        "name": "04_dichotic",
        "start_ms": 6 * 60 * 1000,  # 6:00
        "repeat": 2,
        "repeat_gap_ms": 2000,
        "left_text": (
            "Você vem primeiro hoje, você se cuida, você está bem\n"
            "---\n"
            "Você é capaz, você é forte, você consegue"
        ),
        "right_text": (
            "Eu venho primeiro hoje. Eu me cuido. Eu estou bem\n"
            "---\n"
            "Eu sou capaz. Eu sou forte. Eu consigo"
        ),
    },
    {
        "name": "05_despertar",
        "start_ms": 8 * 60 * 1000,  # 8:00
        "use_wake_settings": True,
        "text": (
            "Agora, contando de um até cinco, você fica mais alerta a cada número. <<2>>\n\n"
            "Um, corpo acordando. Dois, mente clareando. Três, forte e confiante. <<1.5>>\n\n"
            "Quatro, olhos prontos para abrir. Cinco. Olhos abertos, acordada, alerta. <<1.5>>\n\n"
            "Centrada, clara, pronta para o seu dia."
        ),
    },
]

MORNING_DURATION_MS = 10 * 60 * 1000
MORNING_OUTPUT = OUTPUT_DIR / "morning_hypnosis_manuela_v2_short.mp3"
MORNING_WORK = Path("/tmp/hypnosis_manuela_v2_morning_build")


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
            seg = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3").set_channels(2).set_frame_rate(SAMPLE_RATE)
            # 250ms padding both sides prevents clipped word edges when concatenating
            pad = AudioSegment.silent(duration=250, frame_rate=SAMPLE_RATE).set_channels(2)
            return pad + seg + pad
        except Exception as e:
            last_err = e
            wait = 2 ** attempt
            print(f"  [retry {attempt+1}/5 after {wait}s] {type(e).__name__}: {str(e)[:120]}")
            time.sleep(wait)
    raise last_err


def render_text_with_pauses(client, text, cache_path, settings=VOICE_SETTINGS, final_phrase=None):
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
            rendered.append(AudioSegment.silent(duration=400, frame_rate=SAMPLE_RATE).set_channels(2))
    if final_phrase:
        rendered.append(AudioSegment.silent(duration=2500, frame_rate=SAMPLE_RATE).set_channels(2))
        rendered.append(_eleven_render_chunk(client, final_phrase, settings=VOICE_SETTINGS_FINAL))
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


def render_dichotic_segment(client, seg, work_dir):
    l_phrases = [p.strip() for p in seg["left_text"].split("---") if p.strip()]
    r_phrases = [p.strip() for p in seg["right_text"].split("---") if p.strip()]
    cache_dir = work_dir / seg["name"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    l_full = AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2)
    r_full = AudioSegment.silent(duration=0, frame_rate=SAMPLE_RATE).set_channels(2)
    gap = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
    for i, (l_text, r_text) in enumerate(zip(l_phrases, r_phrases)):
        l_a, r_a = render_dichotic_phrase_pair(client, l_text, r_text, cache_dir, i)
        l_full += l_a
        r_full += r_a
        if i < len(l_phrases) - 1:
            l_full += gap
            r_full += gap
    return l_full, r_full


def pan_segment(seg, pan):
    if seg.channels == 1:
        seg = seg.set_channels(2)
    return seg.pan(pan)


def build_voice_track(client, segments, total_ms, work_dir):
    full = AudioSegment.silent(duration=total_ms, frame_rate=SAMPLE_RATE).set_channels(2)
    for seg in segments:
        if "left_text" in seg and "right_text" in seg:
            print(f"[voice]   {seg['name']} (dichotic)")
            l_audio, r_audio = render_dichotic_segment(client, seg, work_dir)
            l_audio = pan_segment(l_audio, -1.0)
            r_audio = pan_segment(r_audio, 1.0)
            repeat = seg.get("repeat", 1)
            gap_ms = seg.get("repeat_gap_ms", 2000)
            unit_len = len(l_audio)
            lead_in = AudioSegment.silent(duration=600, frame_rate=SAMPLE_RATE).set_channels(2)
            for r in range(repeat):
                offset = seg["start_ms"] + r * (unit_len + gap_ms)
                full = full.overlay(lead_in + l_audio, position=offset)
                full = full.overlay(lead_in + r_audio, position=offset)
            total_len = repeat * unit_len + (repeat - 1) * gap_ms
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, total {total_len/1000:.1f}s ({repeat}x)")
        else:
            cache_path = work_dir / f"{seg['name']}.mp3"
            print(f"[voice]   {seg['name']} (mono)")
            settings = VOICE_SETTINGS_WAKE if seg.get("use_wake_settings") else VOICE_SETTINGS
            voice = render_text_with_pauses(client, seg["text"], cache_path, settings=settings,
                                            final_phrase=seg.get("final_phrase"))
            voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
            lead_in = AudioSegment.silent(duration=600, frame_rate=SAMPLE_RATE).set_channels(2)
            voice = lead_in + voice
            full = full.overlay(voice, position=seg["start_ms"])
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, length {len(voice)/1000:.1f}s")
    return full[:total_ms]


def generate_binaural(total_ms, stages):
    carrier = 200.0
    total_samples = int(SAMPLE_RATE * (total_ms / 1000.0))
    t = np.arange(total_samples) / SAMPLE_RATE
    beat_curve = np.zeros(total_samples, dtype=np.float64)
    crossfade_s = 5.0
    for i, (s_min, e_min, beat) in enumerate(stages):
        s = int(s_min * 60 * SAMPLE_RATE)
        e = min(int(e_min * 60 * SAMPLE_RATE), total_samples)
        beat_curve[s:e] = beat
        if i > 0:
            cf = int(crossfade_s * SAMPLE_RATE)
            cs = max(0, s - cf // 2)
            ce = min(total_samples, s + cf // 2)
            beat_curve[cs:ce] = np.linspace(stages[i-1][2], beat, ce - cs)
    left_phase = 2 * np.pi * carrier * t
    right_phase = 2 * np.pi * np.cumsum(carrier + beat_curve) / SAMPLE_RATE
    stereo = np.empty((total_samples, 2), dtype=np.float32)
    stereo[:, 0] = np.sin(left_phase) * 0.6
    stereo[:, 1] = np.sin(right_phase) * 0.6
    int16 = (stereo * 32767).astype(np.int16)
    return AudioSegment(int16.tobytes(), frame_rate=SAMPLE_RATE, sample_width=2, channels=2)


def _note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def generate_ambient(total_ms, progression):
    chord_duration_s = 14.0
    crossfade_s = 3.5
    n_samples = int(SAMPLE_RATE * (total_ms / 1000.0))
    t_full = np.arange(n_samples) / SAMPLE_RATE
    out_l = np.zeros(n_samples, dtype=np.float32)
    out_r = np.zeros(n_samples, dtype=np.float32)
    cs = int(chord_duration_s * SAMPLE_RATE)
    cf = int(crossfade_s * SAMPLE_RATE)
    step = cs - cf
    env = np.ones(cs, dtype=np.float32)
    env[:cf] = np.linspace(0.0, 1.0, cf)
    env[-cf:] = np.linspace(1.0, 0.0, cf)
    n_chords = (n_samples // step) + 2
    for i in range(n_chords):
        chord = progression[i % len(progression)]
        start = i * step
        if start >= n_samples:
            break
        end = min(start + cs, n_samples)
        length = end - start
        lt = np.arange(length) / SAMPLE_RATE
        wl = np.zeros(length, dtype=np.float32)
        wr = np.zeros(length, dtype=np.float32)
        for j, midi in enumerate(chord):
            freq = _note_hz(midi)
            d = (j - 1.5) * 2.5
            fl = freq * 2 ** (d / 1200.0)
            fr = freq * 2 ** (-d / 1200.0)
            amp = 0.30 if j == 0 else (0.22 if j == 1 else 0.18)
            wl += amp * np.sin(2 * np.pi * fl * lt + j * 1.7).astype(np.float32)
            wr += amp * np.sin(2 * np.pi * fr * lt + j * 0.9).astype(np.float32)
        wl = np.tanh(wl * 0.9) * env[:length]
        wr = np.tanh(wr * 0.9) * env[:length]
        out_l[start:end] += wl
        out_r[start:end] += wr
    lfo = 0.12 * np.sin(2 * np.pi * 0.05 * t_full).astype(np.float32)
    out_l *= (1.0 - lfo)
    out_r *= (1.0 + lfo)
    peak = max(np.max(np.abs(out_l)), np.max(np.abs(out_r))) or 1.0
    out_l = out_l / peak * 0.85
    out_r = out_r / peak * 0.85
    stereo = np.empty((n_samples, 2), dtype=np.float32)
    stereo[:, 0] = out_l
    stereo[:, 1] = out_r
    int16 = (stereo * 32767).astype(np.int16)
    return AudioSegment(int16.tobytes(), frame_rate=SAMPLE_RATE, sample_width=2, channels=2)


def build_tape(client, name, segments, total_ms, work_dir, output, binaural_stages, progression, fade_out_ms):
    print("=" * 60)
    print(f"Building {name}")
    print("=" * 60)
    work_dir.mkdir(parents=True, exist_ok=True)
    voice = build_voice_track(client, segments, total_ms, work_dir)
    print("[binaural] Synthesizing...")
    binaural = generate_binaural(total_ms, binaural_stages) - 22
    print("[ambient] Synthesizing...")
    ambient = generate_ambient(total_ms, progression) - 10
    base = AudioSegment.silent(duration=total_ms, frame_rate=SAMPLE_RATE).set_channels(2)
    mixed = base.overlay(ambient).overlay(binaural).overlay(voice)
    mixed = mixed.fade_in(2000).fade_out(fade_out_ms)
    print(f"[export] {output}")
    mixed.export(str(output), format="mp3", bitrate="192k",
                 parameters=["-ar", str(SAMPLE_RATE), "-ac", "2"])
    print(f"  Duration: {len(mixed)/1000/60:.2f} min | Size: {output.stat().st_size/1024/1024:.1f} MB")


def main():
    from elevenlabs.client import ElevenLabs
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set")
    client = ElevenLabs(api_key=api_key)

    # Night: sleep-bound binaural, Am-F-C-G pad, long fade
    build_tape(
        client, "NIGHT v4 short (~21 min)",
        NIGHT_SEGMENTS, NIGHT_DURATION_MS, NIGHT_WORK, NIGHT_OUTPUT,
        binaural_stages=[(0, 2, 10.0), (2, 5, 7.0), (5, 16, 4.0), (16, 19, 3.0), (19, 21, 2.0)],
        progression=[[45, 48, 52, 57], [41, 45, 48, 53], [48, 52, 55, 60], [43, 47, 50, 55]],
        fade_out_ms=30000,
    )

    # Morning: rising binaural, C-G-Am-F pad, short fade
    build_tape(
        client, "MORNING v2 short (~10 min)",
        MORNING_SEGMENTS, MORNING_DURATION_MS, MORNING_WORK, MORNING_OUTPUT,
        binaural_stages=[(0, 1, 10.0), (1, 5, 7.0), (5, 7, 10.0), (7, 8, 14.0), (8, 10, 18.0)],
        progression=[[48, 55, 60, 64], [43, 50, 55, 62], [45, 52, 57, 64], [41, 48, 53, 60]],
        fade_out_ms=4000,
    )

    print()
    print("=" * 60)
    print("ALL DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
