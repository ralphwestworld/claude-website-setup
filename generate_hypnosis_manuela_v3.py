"""
Bedtime Hypnosis - Manuela v3 (Brazilian Portuguese).
Built from her actual answers in the June 30 2026 self-reflection session.
Uses her own cloned voice (t9UJ0smqFgPZJnchMfob).

Core belief installed: "Eu venho em primeiro lugar. Esse espaço é meu."
Trigger reversed: "Eu não sou capaz" -> "Eu sou capaz. Eu reconheço. Eu volto."
Past reframe: rejection -> "Eu sou aceita. Eu me aceito."
Internal voice mirrored back (her own words): "Você é capaz. Você é forte. Você é o Rock Balboa."
"""

import io
import os
import re
import time
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "bedtime_hypnosis_manuela_v3.mp3"
WORK_DIR = Path("/tmp/hypnosis_manuela_v3_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 48 * 60 * 1000  # 48 min

VOICE_ID = "t9UJ0smqFgPZJnchMfob"  # Manuela cloned
MODEL_ID = "eleven_multilingual_v2"

VOICE_SETTINGS_INTRO = {
    "stability": 0.78,
    "similarity_boost": 0.85,
    "style": 0.05,
    "speed": 0.8,
    "use_speaker_boost": True,
}

VOICE_SETTINGS = {
    "stability": 0.72,
    "similarity_boost": 0.85,
    "style": 0.08,
    "speed": 0.85,
    "use_speaker_boost": True,
}

VOICE_SETTINGS_FINAL = {
    "stability": 0.9,
    "similarity_boost": 0.85,
    "style": 0.0,
    "speed": 0.78,
    "use_speaker_boost": True,
}

SEGMENTS = [
    {
        "name": "00_boas_vindas",
        "start_ms": 0,
        "use_intro_settings": True,
        "text": (
            "Olá. <<3>>\n\n"
            "Encontre uma posição confortável. Deitada. Braços relaxados. Pernas descruzadas. <<3>> Você não precisa fazer nada além de ouvir. <<5>>\n\n"
            "Esta experiência ainda não é o sono. <<3>> Você ainda tem consciência. Você ouve tudo o que eu digo. <<4>>\n\n"
            "Mas haverá mudanças. Mudanças gentis. <<3>> Em como você se sente. Como você pensa. Como você age amanhã. <<5>>\n\n"
            "É como sonhar acordada. <<3>> Tudo que você precisa fazer é relaxar. Deixar os sons te envolverem. <<5>>\n\n"
            "Esta noite, seu subconsciente assume. <<3>> Cada palavra que eu digo vai ser absorvida bem fundo, no lugar onde as verdadeiras mudanças acontecem."
        ),
    },
    {
        "name": "01_respiracao",
        "start_ms": 90 * 1000,  # 1:30
        "use_intro_settings": True,
        "text": (
            "Preste atenção à sua respiração. <<3>> A subida suave. <<3>> E a descida suave. <<3>> Acontecendo por si só. <<5>>\n\n"
            "Antes de relaxar mais profundamente, respire mais fundo algumas vezes. <<4>>\n\n"
            "Solte todo o ar. <<5>> E inspire suavemente. <<5>>\n\n"
            "Solte todo o ar. <<5>> E inspire suavemente. <<5>>\n\n"
            "Mais uma vez. Solte todo o ar. <<4>> E inspire suavemente."
        ),
    },
    {
        "name": "02_relaxamento",
        "start_ms": 3 * 60 * 1000,  # 3:00
        "use_intro_settings": True,
        "text": (
            "Agora, faça um varredura pelo seu corpo. <<3>> Sinta seus pés. Seus pés relaxam. <<3>>\n\n"
            "Suas panturrilhas e canelas. Soltas. <<3>>\n\n"
            "Seus joelhos e coxas. Pesados. <<3>>\n\n"
            "Seus quadris e a parte de baixo das costas. Liberam. <<3>>\n\n"
            "Sua barriga e seu peito. Amolecem. <<3>>\n\n"
            "Seus ombros. Solta os ombros. <<3>> Para longe das orelhas. Braços pesados. Mãos relaxadas. <<3>>\n\n"
            "Seu pescoço e sua mandíbula. Macios. <<3>> Seus olhos imóveis. Sua testa lisa. <<4>>\n\n"
            "Seu corpo inteiro está pesado, aquecido, em paz. <<3>> E você vai mais fundo a cada respiração."
        ),
    },
    {
        "name": "03_contagem",
        "start_ms": 5 * 60 * 1000 + 30 * 1000,  # 5:30
        "use_intro_settings": True,
        "text": (
            "Daqui a pouco eu vou contar de dez até um. <<3>> A cada número, você vai duas vezes mais fundo. <<3>>\n\n"
            "Duas vezes mais profunda. Duas vezes mais aberta. <<5>>\n\n"
            "Dez. Descendo agora. Soltando. <<3>>\n\n"
            "Nove. Mais fundo. Mais pesada. <<3>>\n\n"
            "Oito. O dobro mais profundo do que antes. <<3>>\n\n"
            "Sete. O mundo lá fora se afastando. Apenas a minha voz. <<3>>\n\n"
            "Seis. Meio caminho. Profundamente relaxada. <<3>>\n\n"
            "Cinco. Ainda mais fundo. Seu subconsciente aberto. <<3>>\n\n"
            "Quatro. Tão relaxada que parece que você está flutuando. <<3>>\n\n"
            "Três. O nível mais profundo de transe que você já experimentou. <<3>>\n\n"
            "Dois. Além do pensamento. Além do esforço. <<3>>\n\n"
            "Um. Você está agora no estado perfeito para receber tudo o que eu disser. <<3>> Cada palavra entra direto no lugar profundo onde as crenças vivem, e fica."
        ),
    },
    {
        "name": "04_lugar_seguro",
        "start_ms": 8 * 60 * 1000,  # 8:00
        "use_intro_settings": True,
        "text": (
            "E agora, na sua mente, imagine um lugar seu. <<5>>\n\n"
            "Pode ser real, pode ser imaginário. Mas é seu. <<3>>\n\n"
            "Uma luz dourada. Quente. <<3>> Tocando sua pele. <<5>>\n\n"
            "O ar é puro. Você respira fácil. <<3>>\n\n"
            "Aqui, seu corpo se sente forte. Estável. Inteira. <<5>>\n\n"
            "Seus pés tocam o chão. Você sente a firmeza. <<3>>\n\n"
            "Este é o lugar onde você sempre sabe voltar. <<3>> Em uma respiração, você está aqui de novo. <<5>>\n\n"
            "Esse lugar mora dentro de você. <<3>> Você nunca está longe dele."
        ),
    },
    {
        "name": "05_ancoragem",
        "start_ms": 10 * 60 * 1000,  # 10:00
        "text": (
            "Agora coloque uma das mãos no seu peito. <<3>> Sinta o calor. A presença. <<4>>\n\n"
            "Respire. <<3>> E diga, em silêncio: <<3>>\n\n"
            "Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<5>>\n\n"
            "De novo. Eu venho em primeiro lugar. Eu estou bem. Eu sou capaz. <<5>>\n\n"
            "Este é o seu botão. A sua âncora. <<3>>\n\n"
            "Toda vez que você colocar a mão no peito, e respirar, e disser estas palavras, seu corpo entra automaticamente neste estado de calma, de força, de presença. <<5>>\n\n"
            "Em qualquer momento do dia, em qualquer momento da vida, você sempre tem este botão. <<3>> Mão. Respiração. Palavras. E você volta."
        ),
    },
    {
        "name": "06_inversao_gatilho",
        "start_ms": 12 * 60 * 1000,  # 12:00
        "text": (
            "E agora, seu subconsciente está aprendendo uma coisa nova. <<5>>\n\n"
            "Aquele primeiro pensamento que às vezes vem. Aquele pensamento de que você não é capaz. <<4>>\n\n"
            "A partir de hoje, esse pensamento significa algo diferente. <<5>>\n\n"
            "Quando vier o pensamento eu não sou capaz, ele vira o seu sinal. <<3>> O sinal para você fazer uma pausa. E lembrar. <<5>>\n\n"
            "Eu sou capaz. Eu reconheço. Eu volto pro meu centro. <<5>>\n\n"
            "Olhe tudo o que você já fez. Olhe tudo o que você sustenta. <<3>> Olhe o seu trabalho, olhe os seus filhos, olhe a mulher que você é. <<5>>\n\n"
            "Você é mais do que capaz. Você é mais do que suficiente. <<5>>\n\n"
            "O mesmo pensamento que antes te puxava pra baixo, agora te puxa pra cima. <<3>> Ele te traz de volta pra você. <<5>>\n\n"
            "E quando esse pensamento vier, seu corpo sabe o que fazer. <<3>> Mão no peito. Respiração. Palavras. Você volta. Sempre. <<5>>\n\n"
            "Não importa quantas vezes ele tente voltar, você volta primeiro."
        ),
    },
    {
        "name": "07_aceitacao",
        "start_ms": 15 * 60 * 1000,  # 15:00
        "text": (
            "E agora, uma parte mais profunda. <<5>>\n\n"
            "Há memórias do passado que ainda tentam te puxar pra baixo. Memórias de rejeição. De não ser aceita por quem deveria te aceitar. <<5>>\n\n"
            "Essas memórias existiram. Elas foram reais. <<3>> Mas elas não são você. <<5>>\n\n"
            "A partir de hoje, você instala uma verdade nova, mais profunda do que qualquer memória antiga: <<5>>\n\n"
            "Eu sou aceita. <<3>> Eu me aceito. <<3>> Eu não preciso da aceitação de ninguém. <<5>>\n\n"
            "O amor que você procurou em outras pessoas, você se dá agora. <<3>> A aprovação que você esperou de outros, você dá pra você mesma. <<5>>\n\n"
            "Você não precisa colar nos outros. Você não precisa da aprovação deles. <<3>> Você vive a sua vida, sustentada por você mesma. <<5>>\n\n"
            "E quando alguém te aceitar, é bônus. Quando alguém não te aceitar, não muda nada. <<3>> Porque a sua aceitação não está nas mãos de ninguém. Está dentro de você. <<5>>\n\n"
            "Você é aceita. Você é amada. Você é inteira. <<3>> Por você. <<3>> Para você."
        ),
    },
    {
        "name": "08_dichotic_identidade",
        "start_ms": 18 * 60 * 1000,  # 18:00
        "repeat": 4,
        "repeat_gap_ms": 3000,
        "left_text": (
            "Você é capaz, você é forte, você é o Rock Balboa\n"
            "---\n"
            "Você é maravilhosa, você é bonita, você aguenta\n"
            "---\n"
            "Você é estável, você é saudável, você é inteira\n"
            "---\n"
            "Você vem primeiro, esse espaço é seu, você se cuida\n"
            "---\n"
            "Você coloca limites com amor, e os limites te protegem"
        ),
        "right_text": (
            "Eu sou capaz. Eu sou forte. Eu sou o Rock Balboa\n"
            "---\n"
            "Eu sou maravilhosa. Eu sou bonita. Eu aguento\n"
            "---\n"
            "Eu sou estável, saudável, inteira\n"
            "---\n"
            "Eu venho primeiro. Esse espaço é meu. Eu me cuido\n"
            "---\n"
            "Eu coloco limites com amor. Meus limites me protegem"
        ),
    },
    {
        "name": "08b_dichotic_core",
        "start_ms": 22 * 60 * 1000 + 30 * 1000,  # 22:30
        "repeat": 3,
        "repeat_gap_ms": 3000,
        "left_text": (
            "Você vem em primeiro lugar, esse espaço é seu, você se cuida\n"
            "---\n"
            "Quando o pensamento vier, você respira, você volta\n"
            "---\n"
            "Você é aceita, você se aceita, você não precisa de aprovação\n"
            "---\n"
            "Você é estável, você é saudável, você é uma mãe presente\n"
            "---\n"
            "Você acorda bem, você se cuida primeiro, você está em paz"
        ),
        "right_text": (
            "Eu venho em primeiro lugar. Esse espaço é meu. Eu me cuido\n"
            "---\n"
            "Quando o pensamento vem, eu respiro, eu volto\n"
            "---\n"
            "Eu sou aceita. Eu me aceito. Não preciso de aprovação\n"
            "---\n"
            "Eu sou estável, saudável, uma mãe presente\n"
            "---\n"
            "Eu acordo bem. Eu me cuido primeiro. Eu estou em paz"
        ),
    },
    {
        "name": "09_limites",
        "start_ms": 26 * 60 * 1000,  # 26:00
        "text": (
            "Você está aprendendo a colocar limites. <<5>>\n\n"
            "Os mesmos relacionamentos que te nutrem podem te esgotar. <<3>> Seu marido. Seus filhos. Seu trabalho. Sua família. <<5>>\n\n"
            "Você ama todos eles. <<3>> E justamente por amar, você coloca limites. <<5>>\n\n"
            "Limites não são parede. Limites são proteção. <<3>> Para você. E para eles. <<5>>\n\n"
            "Quando você se esgota tentando estar para todo mundo, ninguém tem o seu melhor. <<3>> Quando você se cuida primeiro, todo mundo recebe a sua melhor versão. <<5>>\n\n"
            "Você diz não quando precisa dizer não. <<3>> Sem culpa. Com amor. <<5>>\n\n"
            "Você se prioriza. <<3>> Não como egoísmo. Como sabedoria. <<5>>\n\n"
            "Porque você sabe agora: você só pode dar do que tem dentro. E para ter dentro, você precisa se nutrir primeiro."
        ),
    },
    {
        "name": "10_dia_perfeito",
        "start_ms": 28 * 60 * 1000 + 30 * 1000,  # 28:30
        "text": (
            "Agora, veja na sua mente o seu dia perfeito. <<5>>\n\n"
            "Você acorda bem. <<3>> Grata. Estável. Levemente feliz por acordar. <<5>>\n\n"
            "Você se levanta com energia. <<3>> Você se move. Pode ser musculação, pode ser ioga, pode ser uma corrida. <<3>> O movimento te dá adrenalina. Te acorda por inteiro. <<5>>\n\n"
            "Depois, um banho longo. Sozinha. Sem pressa. <<3>> Esse momento é seu. <<5>>\n\n"
            "Você se troca, se prepara, e vai para o seu trabalho. <<3>> Você chega com presença. <<3>> Conexão com o seu time. <<3>> Sua voz nas reuniões. Sua marca no que você faz. <<3>> Você dá suporte ao negócio e às pessoas, porque esse é o seu papel, e você é boa nisso. <<5>>\n\n"
            "Você busca seus filhos na escola. <<3>> Você está presente com eles, de verdade. <<5>>\n\n"
            "Um jantar em família. <<3>> Calmo. Conectado. <<5>>\n\n"
            "E uma noite tranquila. <<3>> Você se prepara para dormir. <<3>> Você dorme bem. <<3>> E amanhã, você acorda assim de novo. <<5>>\n\n"
            "Este é o seu padrão. <<3>> Estabilidade emocional e física. Todos os dias."
        ),
    },
    {
        "name": "11_filhos",
        "start_ms": 32 * 60 * 1000 + 30 * 1000,  # 32:30
        "text": (
            "E seus filhos. <<5>>\n\n"
            "Quando eles crescerem e olharem para você, eles vão se lembrar de uma mãe estável. <<3>> Saudável. Feliz. Profunda. <<5>>\n\n"
            "Eles vão se lembrar da mãe que estava presente. <<3>> Que se cuidou. Que respeitou sua própria vida. <<3>> E que, por isso, conseguiu estar inteira para eles. <<5>>\n\n"
            "Essa é a herança que você dá pra eles. <<3>> Não só amor. Mas o exemplo de uma mulher inteira. <<5>>\n\n"
            "Cada vez que você se cuida, você cuida deles também. <<3>> Cada vez que você se prioriza, você ensina a eles a se priorizarem. <<3>> Cada vez que você coloca limites, você mostra a eles que é possível amar e ter limites ao mesmo tempo."
        ),
    },
    {
        "name": "12_autocuidado",
        "start_ms": 35 * 60 * 1000,  # 35:00
        "text": (
            "E seu corpo gosta de se mover. <<3>> Seu corpo precisa de movimento. <<5>>\n\n"
            "Treinar te faz bem. <<3>> Musculação, ioga, corrida, alongamento. Qualquer movimento que seu corpo pede. <<5>>\n\n"
            "E você tem outros prazeres que estavam adormecidos. <<5>>\n\n"
            "Desenhar. <<3>> Você desenhava muito. Você resgatou esse amor no hospital. <<3>> Agora você desenha de novo, na sua vida. <<5>>\n\n"
            "Trabalhos manuais. Cerâmica. Miçangas. Pintura. <<3>> Tudo o que suas mãos sabem fazer e gostam de fazer. <<5>>\n\n"
            "Você dedica tempo para essas coisas. <<3>> Não como obrigação. Como prazer. Como reencontro com você. <<5>>\n\n"
            "Cada momento que você dedica a essas atividades, seu corpo se cura, sua mente se acalma, sua alma se expande."
        ),
    },
    {
        "name": "13_cura_corpo",
        "start_ms": 38 * 60 * 1000,  # 38:00
        "use_intro_settings": True,
        "text": (
            "E agora, com seu corpo profundamente relaxado, vamos para a cura. <<5>>\n\n"
            "Seu corpo é inteligente. <<3>> Ele sabe como se curar. <<3>> Cada célula. Cada órgão. Cada sistema. <<3>> Sabe exatamente o que fazer. <<5>>\n\n"
            "Sua tireoide se equilibra. Seus hormônios fluem corretamente. <<3>> Seu sistema endócrino encontra seu ritmo natural. <<5>>\n\n"
            "Seu coração desacelera para o seu ritmo natural. Calmo. <<3>> Seus pulmões respiram fundo, fácil. <<5>>\n\n"
            "Seu sistema nervoso encontra calma. <<3>> O lado da luta cede. O lado do descanso se eleva. <<3>> Você sai do estado de alerta e entra no estado de cura. <<5>>\n\n"
            "Cortisol baixa. Melatonina sobe. <<3>> Seu corpo sabe o tempo. <<5>>\n\n"
            "Seu apetite se equilibra. Você come o que serve a você. Você se nutre. <<5>>\n\n"
            "E seu sono esta noite repara. <<3>> Sono profundo, mais profundo. <<3>> REM mais claro. <<3>> A arquitetura do seu sono, restaurada. <<5>>\n\n"
            "Cada noite você se cura mais. <<3>> Cada manhã você acorda mais forte. <<5>>\n\n"
            "Essa é você, cuidando de você, no nível mais profundo."
        ),
    },
    {
        "name": "14_compromisso_diario",
        "start_ms": 43 * 60 * 1000,  # 43:00
        "text": (
            "E esta gravação. Esta voz. Este momento. <<3>> Você ama ouvir. <<5>>\n\n"
            "Toda noite, antes de dormir, você quer voltar aqui. <<3>> Toda noite, algo dentro de você fica mais forte. <<5>>\n\n"
            "Você espera por esse momento. <<3>> É o seu presente. É o seu refúgio. É o seu tempo só seu. <<5>>\n\n"
            "Cada noite que você ouve, a transformação vai mais fundo. <<3>> Cada noite, você se sente mais você."
        ),
    },
    {
        "name": "15_sono",
        "start_ms": 45 * 60 * 1000 + 30 * 1000,  # 45:30
        "text": (
            "E agora, seu corpo fica cada vez mais pesado. Sua mente vai mais fundo. <<4>>\n\n"
            "Tudo o que eu disse esta noite está se acomodando dentro de você. <<3>> No lugar onde a identidade se forma. <<4>>\n\n"
            "Enquanto você dorme, seu subconsciente vai ensaiar, organizar, reforçar. <<3>> Cada palavra. Cada caminho novo. <<4>>\n\n"
            "Você vai acordar amanhã mais clara. Mais leve. Mais forte. <<4>>\n\n"
            "Não há nada para fazer agora. <<3>> Apenas se entregar ao sono. <<5>>\n\n"
            "Mais fundo. <<3>> E mais fundo. <<3>> Em um sono perfeito, curativo, restaurador."
        ),
        "final_phrase": "Boa noite.",
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
            rendered.append(AudioSegment.silent(duration=600, frame_rate=SAMPLE_RATE).set_channels(2))
    if final_phrase:
        rendered.append(AudioSegment.silent(duration=4000, frame_rate=SAMPLE_RATE).set_channels(2))
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


def render_dichotic_segment(client, seg):
    l_phrases = [p.strip() for p in seg["left_text"].split("---") if p.strip()]
    r_phrases = [p.strip() for p in seg["right_text"].split("---") if p.strip()]
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
            voice = render_text_with_pauses(client, seg["text"], cache_path, settings=settings,
                                            final_phrase=seg.get("final_phrase"))
            voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
            lead_in = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
            voice = lead_in + voice
            full = full.overlay(voice, position=seg["start_ms"])
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, length {len(voice)/1000:.1f}s")
    return full[:TOTAL_DURATION_MS]


def generate_binaural_track():
    """Sleep-bound progression."""
    print("[binaural] Synthesizing sleep-bound progression...")
    carrier = 200.0
    stages = [
        (0, 3, 10.0),
        (3, 8, 7.0),
        (8, 38, 4.0),
        (38, 45, 3.0),
        (45, 48, 2.0),
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


def _note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def generate_ambient_track():
    """Am-F-C-G evening pad."""
    print("[ambient] Synthesizing evening music pad (Am-F-C-G)...")
    progression_midi = [[45, 48, 52, 57], [41, 45, 48, 53], [48, 52, 55, 60], [43, 47, 50, 55]]
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
    print("Bedtime Hypnosis - Manuela v3 (PT-BR, from her June 30 answers)")
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
