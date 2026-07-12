"""
Bedtime Hypnosis Audio Generator - Manuela v2 (PT-BR, first-person).
- All affirmations / instructions self-spoken ("eu sou", "eu respiro", "eu volto")
- Anchor reversal core
- True dichotic listening with phrase-pair convergence
- Self-care drilling, family/support reinforcement, perfect-day visualization
- Soothing voice settings, finalised goodnight intonation
"""

import io
import os
import re
from pathlib import Path

import numpy as np
from pydub import AudioSegment

OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_FILE = OUTPUT_DIR / "bedtime_hypnosis_manuela_v2.mp3"
WORK_DIR = Path("/tmp/hypnosis_manuela_v2_build")
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
TOTAL_DURATION_MS = 36 * 60 * 1000  # 36 minutes total

VOICE_ID = "t9UJ0smqFgPZJnchMfob"  # Manuela cloned
MODEL_ID = "eleven_multilingual_v2"

# Standard soothing voice settings
VOICE_SETTINGS = {
    "stability": 0.7,
    "similarity_boost": 0.85,
    "style": 0.0,
    "speed": 0.85,
    "use_speaker_boost": True,
}

# Higher-stability settings for the final goodnight (forces falling/terminal intonation)
VOICE_SETTINGS_FINAL = {
    "stability": 0.9,
    "similarity_boost": 0.85,
    "style": 0.0,
    "speed": 0.8,
    "use_speaker_boost": True,
}

SEGMENTS = [
    {
        "name": "01_boas_vindas",
        "start_ms": 0,
        "text": (
            "Aqui estou eu. <<2>>\n\n"
            "Em uma posição confortável, deitada, meu corpo relaxado, meus braços soltos ao lado do corpo. <<3>>\n\n"
            "Não preciso fazer nada. Apenas ouvir minha própria voz. <<2>>\n\n"
            "Esse é o meu momento. Enquanto eu descanso, minha mente se reorganiza. Cada palavra que eu digo vai sendo absorvida bem fundo, no lugar onde as mudanças acontecem de verdade."
        ),
    },
    {
        "name": "02_relaxamento",
        "start_ms": 70 * 1000,
        "text": (
            "Eu respiro fundo, bem fundo, pelo nariz. <<4>> Encho completamente meus pulmões. <<3>> E solto o ar bem devagar pela boca. Bem devagar. <<5>>\n\n"
            "Mais uma vez. Inspiro profundamente. <<4>> Sinto o ar entrando, expandindo o meu peito. <<3>> Expiro devagar, soltando tudo o que eu não preciso mais. <<5>>\n\n"
            "Mais uma. Inspiro. <<4>> Seguro por um momento. <<2>> Expiro, deixando meu corpo afundar mais na cama. <<5>>\n\n"
            "Mais uma. Bem fundo. <<3>> Ao soltar, percebo como meu corpo já está mais pesado. Como se cada exhalação me levasse mais fundo. <<5>>\n\n"
            "A cada respiração agora, mais profundo. Mais solta. Mais entregue. <<5>>\n\n"
            "Trago minha atenção para os meus pés. <<3>> Sinto cada dedo. <<3>> Meus pés ficam pesados, soltos, quentinhos. Como se estivessem afundando suavemente. <<4>>\n\n"
            "Subo a sensação para as minhas panturrilhas, para as minhas canelas. <<3>> Minhas pernas relaxam. Ficam macias, pesadas. <<4>>\n\n"
            "Subo até os meus joelhos e as minhas coxas. <<2>> Minhas pernas inteiras se entregam. Pesadas. Sem força. Apenas descansando. <<4>>\n\n"
            "Indo mais fundo. <<3>>\n\n"
            "Sinto o meu quadril e a parte de baixo das minhas costas. <<2>> Solto qualquer tensão acumulada ali. <<3>> Meu quadril desce mais. Confortável. <<4>>\n\n"
            "Subo até a minha barriga. O meu peito. <<2>> Minha respiração fica mais lenta. Mais leve. Mais natural. <<4>>\n\n"
            "Cada respiração me leva mais fundo. <<5>>\n\n"
            "Solto os meus ombros. Deixo os ombros caírem, longe das orelhas. <<3>> Meus braços ficam pesados, sem peso. Minhas mãos descansam totalmente. <<4>>\n\n"
            "Solto o meu pescoço. Solto a minha mandíbula. <<3>> Deixo a mandíbula bem solta, a língua relaxada. <<3>>\n\n"
            "Solto os músculos ao redor dos meus olhos. Solto a minha testa. <<3>> Meu rosto inteiro fica sereno. <<4>>\n\n"
            "Meu corpo inteiro agora está pesado, quente, totalmente em paz. <<3>>\n\n"
            "Estou indo cada vez mais fundo, com cada respiração. Mais e mais profundo."
        ),
    },
    {
        "name": "03_contagem",
        "start_ms": 5 * 60 * 1000 + 30 * 1000,  # 5:30
        "text": (
            "Daqui a pouco eu vou contar de dez até um. <<3>> A cada número, eu vou duas vezes mais fundo do que estava antes. <<4>>\n\n"
            "Duas vezes mais profunda. Duas vezes mais relaxada. Duas vezes mais aberta. <<5>>\n\n"
            "Dez. Descendo agora. Soltando completamente. Como se estivesse descendo uma escada suave. <<4>>\n\n"
            "Nove. Mais fundo. Mais pesada. Meu corpo afunda mais. <<4>>\n\n"
            "Oito. Duas vezes mais fundo do que no número anterior. Minha mente fica suave, leve, tranquila. <<4>>\n\n"
            "Sete. O mundo lá fora vai ficando longe. Os sons distantes. Apenas a minha voz importa agora. <<4>>\n\n"
            "Seis. Metade do caminho. Profundamente relaxada. Respirando devagar, naturalmente. <<4>>\n\n"
            "Cinco. Ainda mais fundo. Meu subconsciente está aberto, receptivo, pronto. <<4>>\n\n"
            "Quatro. Tão relaxada que parece que estou flutuando. Leve. Sem peso. <<4>>\n\n"
            "Três. O nível mais profundo de descanso que eu já conheci. Mais profundo do que o sono. <<4>>\n\n"
            "Dois. Sem pensamento. Sem esforço. Apenas estar. Apenas ouvir. <<4>>\n\n"
            "Um. <<3>> Estou no estado perfeito. <<3>>\n\n"
            "Tudo o que eu disser daqui pra frente entra direto onde precisa. Direto no lugar profundo onde as mudanças acontecem. E fica."
        ),
    },
    {
        "name": "04_lugar_seguro",
        "start_ms": 9 * 60 * 1000 + 30 * 1000,  # 9:30
        "text": (
            "Agora, na minha mente, eu vou para um lugar lindo. <<5>>\n\n"
            "Esse lugar é meu. Só meu. <<3>>\n\n"
            "Vejo um jardim aberto, cercado de árvores antigas que sussurram com o vento. <<4>>\n\n"
            "O céu é azul, limpo, com algumas nuvens leves passando devagar. <<4>>\n\n"
            "Sinto o sol quente nos meus ombros. Uma luz dourada que toca minha pele e me aquece por dentro. <<5>>\n\n"
            "O ar é puro. Cheira a flores, a terra molhada, a vida. <<4>>\n\n"
            "Eu respiro fundo, e cada inspiração me preenche de paz. <<5>>\n\n"
            "Caminho devagar pelo jardim. Sinto a grama macia debaixo dos meus pés. <<4>>\n\n"
            "Cada passo me deixa mais leve. Mais firme. Mais centrada. <<5>>\n\n"
            "Vejo um banco de pedra. Sento ali. <<3>>\n\n"
            "Olho para minhas mãos e percebo que elas estão calmas. <<3>>\n\n"
            "Olho para o meu peito e percebo que minha respiração está tranquila. <<4>>\n\n"
            "Esse é o meu lugar. Aqui eu sou inteira. Aqui eu sou forte. Aqui eu sou eu mesma. <<5>>\n\n"
            "Sinto uma sensação morna no peito. Essa é a minha paz. <<3>>\n\n"
            "Sinto uma firmeza nas minhas pernas. Essa é a minha força. <<3>>\n\n"
            "Sinto uma clareza na minha cabeça. Esse é o meu controle. <<4>>\n\n"
            "Paz. Força. Controle. Tudo isso vive dentro de mim. <<5>>\n\n"
            "A cada respiração, esse lugar fica mais real. Mais nítido. Mais meu. <<5>>\n\n"
            "E eu sei que esse lugar mora dentro de mim. Posso voltar pra cá em uma respiração, em qualquer momento, em qualquer lugar."
        ),
    },
    {
        "name": "05_ancoragem",
        "start_ms": 13 * 60 * 1000 + 30 * 1000,  # 13:30
        "text": (
            "Agora levo uma das minhas mãos para o meu peito. <<3>>\n\n"
            "Sinto minha mão ali. O calor. A presença. <<4>>\n\n"
            "Respiro devagar. <<3>> E digo, em silêncio: <<3>>\n\n"
            "Eu estou aqui. Eu estou segura. Eu sou forte. <<5>>\n\n"
            "De novo. Eu estou aqui. Eu estou segura. Eu sou forte. <<5>>\n\n"
            "Esse gesto, minha mão no peito, junto com essa frase, traz uma onda de calma pelo meu corpo. <<4>>\n\n"
            "Esse é o meu botão. Minha âncora. <<3>>\n\n"
            "Toda vez que eu colocar a mão no peito, e respirar, e disser essas palavras, meu corpo entra automaticamente nesse estado de calma. De força. De presença."
        ),
    },
    {
        "name": "06_inversao_gatilho",
        "start_ms": 15 * 60 * 1000,  # 15:00
        "text": (
            "E agora, meu subconsciente está aprendendo uma coisa nova. <<4>>\n\n"
            "Aquela sensação antiga, que às vezes chegava... aquele sinal que meu corpo conhece... a partir de hoje significa algo diferente. <<5>>\n\n"
            "Toda vez que aquele sinal aparecer... meu corpo automaticamente responde de outra forma. <<4>>\n\n"
            "Em vez de descer, eu subo. <<3>>\n\n"
            "Em vez de apertar, eu abro. <<3>>\n\n"
            "Em vez de ficar pequena, eu fico forte. <<5>>\n\n"
            "O mesmo sinal que antes me puxava pra baixo... agora me leva direto pra minha força. <<5>>\n\n"
            "Eu não preciso lembrar de nada. Eu não preciso pensar. <<3>>\n\n"
            "Meu corpo já sabe o caminho novo. <<5>>\n\n"
            "Cada vez que aquele sinal vier, ele dispara uma onda de calma, de centro, de presença em mim. <<4>>\n\n"
            "Como se alguém acendesse uma luz dentro de mim. <<5>>\n\n"
            "O sinal antigo virou meu professor. O que antes me derrubava, agora me fortalece."
        ),
    },
    {
        "name": "07_dichotic_inversao",
        "start_ms": 17 * 60 * 1000,  # 17:00
        "repeat": 4,
        "repeat_gap_ms": 3000,
        "left_text": (
            "Quando aquele sinal vier, eu fico mais forte\n"
            "---\n"
            "Meu corpo aprendeu a usar tudo a meu favor\n"
            "---\n"
            "Eu confio no meu instinto, no meu corpo, no meu centro\n"
            "---\n"
            "Tenho dentro de mim toda a calma que preciso\n"
            "---\n"
            "Cada respiração me devolve para o meu eixo"
        ),
        "right_text": (
            "A onda antiga agora me deixa mais forte\n"
            "---\n"
            "Tudo o que era contra mim agora trabalha a meu favor\n"
            "---\n"
            "Sou psicóloga, sou mãe, sou mulher, e estou no meu centro\n"
            "---\n"
            "Tudo o que eu sinto, e tudo o que eu sei, é o que preciso\n"
            "---\n"
            "Estou de volta. Eu sei voltar para o meu eixo"
        ),
    },
    {
        "name": "08_auto_cuidado",
        "start_ms": 21 * 60 * 1000,  # 21:00
        "text": (
            "E agora meu corpo está aprendendo uma nova prioridade. <<4>>\n\n"
            "Meu corpo gosta de se mover. <<3>> Meu corpo precisa de movimento. <<3>> Cada vez que eu me movo, meu corpo agradece. <<4>>\n\n"
            "Aquelas atividades que me fazem bem... aquelas que eu sei que me trazem leveza... meu corpo agora pede por elas, naturalmente. <<5>>\n\n"
            "Pode ser caminhar. Pode ser ioga. Pode ser alongar. Pode ser respirar ao ar livre. Pode ser qualquer coisa que meu corpo pedir. <<4>>\n\n"
            "Cada vez que eu cuido de mim, eu fico mais forte. <<3>> Cada vez que eu me movo, minha mente fica mais leve. <<3>> Cada vez que eu respiro ar puro, o sinal antigo perde força. <<4>>\n\n"
            "Eu não preciso de força de vontade. <<3>> Eu simplesmente sinto vontade. <<3>> E eu atendo, porque eu me amo. <<5>>\n\n"
            "Cuidar de mim é o meu remédio. <<3>> É o meu antídoto. <<3>> É a minha proteção. <<5>>\n\n"
            "A partir de hoje, todo dia, eu me movo. Todo dia, eu respiro fundo. Todo dia, eu me priorizo. <<4>>\n\n"
            "Não como sacrifício. Como prazer. Como amor próprio. <<5>>\n\n"
            "Meu corpo agradece. Minha mente agradece. Minha vida agradece. Toda vez que eu cuido de mim."
        ),
    },
    {
        "name": "09_dia_ideal",
        "start_ms": 24 * 60 * 1000,  # 24:00
        "text": (
            "Agora, na minha mente, vejo um dia comum daqui pra frente. <<5>>\n\n"
            "Acordo de manhã. Antes de qualquer coisa, sinto meu corpo descansado. <<3>> Meu peito está leve. <<3>> Minha respiração já é calma. <<5>>\n\n"
            "Levanto sem pressa. <<3>> Bebo água. Sinto a luz da manhã no meu rosto. <<4>>\n\n"
            "Faço algo que cuida de mim. Pode ser uma caminhada. Pode ser alguns minutos de alongamento. Pode ser apenas uma respiração profunda no ar fresco. <<5>>\n\n"
            "Sinto meu corpo agradecendo. <<4>>\n\n"
            "Quando o dia começa a se mover... quando as coisas começam a acontecer... eu permaneço inteira. <<5>>\n\n"
            "Se algo me toca, eu sinto. E sigo. <<3>> Se algo me desafia, eu respiro. E sigo. <<3>> Se aquele sinal antigo tenta começar... minha mão vai pro peito... e eu volto pro centro em segundos. <<5>>\n\n"
            "Vejo a mim mesma cuidando dos meus filhos com presença. <<4>> Vejo a mim mesma trabalhando com clareza. <<4>> Vejo a mim mesma rindo, abraçando, vivendo. <<5>>\n\n"
            "No final do dia, eu deito sabendo que fiz o suficiente. Que cuidei de mim. Que cuidei dos meus. Que estive presente. <<5>>\n\n"
            "Esse é o meu dia. <<3>> Esse é o meu padrão novo. <<3>> Essa sou eu, agora."
        ),
    },
    {
        "name": "10_familia",
        "start_ms": 27 * 60 * 1000,  # 27:00
        "text": (
            "Eu sou amada. <<4>>\n\n"
            "Tenho ao meu redor pessoas que me amam. Pessoas que me apoiam. Pessoas que torcem por mim. <<5>>\n\n"
            "Minha família me ama. <<3>> Eles veem em mim o que eu nem sempre consigo ver. <<5>>\n\n"
            "Eu não estou sozinha. Eu nunca estou sozinha. <<5>>\n\n"
            "Quando eu preciso, eu posso pedir. <<3>> Quando eu peço, eles estão ali. <<3>> E quando eu não consigo pedir, eles também estão ali. <<5>>\n\n"
            "Eu permito ser cuidada. <<3>> Eu permito ser amada. <<3>> Eu permito receber. <<5>>\n\n"
            "Sou parte de algo maior do que eu mesma. Uma rede de amor que me sustenta, mesmo quando eu não percebo. <<5>>\n\n"
            "E essa rede está sempre comigo. <<3>> No coração. <<3>> Na minha história. <<3>> No meu agora."
        ),
    },
    {
        "name": "11_dichotic_identidade",
        "start_ms": 29 * 60 * 1000,  # 29:00
        "repeat": 3,
        "repeat_gap_ms": 3000,
        "left_text": (
            "Eu sou inteira, sou mãe, sou mulher, vivo em paz\n"
            "---\n"
            "Confio no meu corpo, na minha história, no meu agora\n"
            "---\n"
            "Escolho o que entra, escolho o que fica, sigo o meu caminho"
        ),
        "right_text": (
            "Cada inspiração me devolve para o lugar da paz\n"
            "---\n"
            "Meu corpo me responde, minha mente me obedece, eu vivo no agora\n"
            "---\n"
            "Sigo onde meu coração aponta, eu sigo o meu caminho"
        ),
    },
    {
        "name": "12_compromisso_diario",
        "start_ms": 31 * 60 * 1000,  # 31:00
        "text": (
            "E essa gravação... essa minha voz... esse momento... <<3>> Eu amo ouvir. <<4>>\n\n"
            "Cada noite, antes de dormir, sinto vontade de voltar aqui. <<3>> De ouvir de novo. De me sentir assim. <<4>>\n\n"
            "Toda vez que eu escuto, algo dentro de mim fica mais forte. <<3>> Mais centrada. Mais inteira. <<4>>\n\n"
            "Eu espero por esse momento durante o dia. <<3>> É o meu presente. É o meu refúgio. É o meu remédio. <<5>>\n\n"
            "A cada noite que eu ouço, a transformação se aprofunda. <<3>> A cada noite, o caminho novo se solidifica. <<3>> A cada noite, eu me sinto mais eu. <<5>>\n\n"
            "Quando termina, eu adormeço com facilidade, com paz, com confiança. <<4>>\n\n"
            "Amanhã, na hora certa, meu corpo vai me lembrar. <<3>> Eu vou querer voltar. Como quem volta para um lugar querido. <<5>>\n\n"
            "Esse é o meu hábito. <<3>> Meu prazer. <<3>> Meu compromisso de amor comigo mesma."
        ),
    },
    {
        "name": "13_sono",
        "start_ms": 33 * 60 * 1000 + 30 * 1000,  # 33:30
        "text": (
            "Agora meu corpo fica cada vez mais pesado. Minha mente vai mais fundo. <<4>>\n\n"
            "Tudo o que eu disse esta noite está se assentando dentro de mim. <<4>>\n\n"
            "Enquanto eu durmo, meu subconsciente vai ensaiar, organizar, reforçar. Cada palavra. Cada caminho novo. <<4>>\n\n"
            "Vou acordar amanhã mais leve. Mais clara. Mais forte. <<4>>\n\n"
            "Apenas me entrego. <<3>> Em um sono profundo, restaurador, perfeito. <<5>>\n\n"
            "Agora eu durmo."
        ),
        # Final goodnight rendered separately with high stability for terminal intonation
        "final_phrase": "Boa noite.",
    },
]

PAUSE_RE = re.compile(r"<<(\d+(?:\.\d+)?)>>")


def _eleven_render_chunk(client, text: str, settings=VOICE_SETTINGS) -> AudioSegment:
    audio_iter = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        text=text,
        output_format="mp3_44100_128",
        voice_settings=settings,
    )
    audio_bytes = b"".join(audio_iter)
    return AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3").set_channels(2).set_frame_rate(SAMPLE_RATE)


def render_text_with_pauses(client, text: str, cache_path: Path,
                            final_phrase: str | None = None) -> AudioSegment:
    """Generate text with `<<N>>` pause markers handled. Optional final_phrase rendered with terminal-tone settings."""
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
                rendered.append(_eleven_render_chunk(client, clean))
            else:
                pause_ms = int(float(part) * 1000)
                rendered.append(AudioSegment.silent(duration=pause_ms, frame_rate=SAMPLE_RATE).set_channels(2))
        if not paragraphs[p_idx].rstrip().endswith(">>"):
            rendered.append(AudioSegment.silent(duration=600, frame_rate=SAMPLE_RATE).set_channels(2))

    if final_phrase:
        # Long pause before goodnight, then high-stability render so it lands as a final exhale
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
            voice = render_text_with_pauses(client, seg["text"], cache_path,
                                            final_phrase=seg.get("final_phrase"))
            voice = voice.set_channels(2).set_frame_rate(SAMPLE_RATE)
            lead_in = AudioSegment.silent(duration=1000, frame_rate=SAMPLE_RATE).set_channels(2)
            voice = lead_in + voice
            full = full.overlay(voice, position=seg["start_ms"])
            print(f"[voice]   {seg['name']} placed at {seg['start_ms']/1000:.0f}s, length {len(voice)/1000:.1f}s")

    return full[:TOTAL_DURATION_MS]


def generate_binaural_track() -> AudioSegment:
    print("[binaural] Synthesizing...")
    carrier = 200.0
    # scaled to 36 minutes: alpha 0-3, theta 3-9, delta 9-30, deep delta 30-36
    stages = [
        (0, 3, 10.0),
        (3, 9, 7.0),
        (9, 30, 4.0),
        (30, 36, 2.0),
    ]
    total_samples = int(SAMPLE_RATE * (TOTAL_DURATION_MS / 1000.0))
    t = np.arange(total_samples) / SAMPLE_RATE
    beat_curve = np.zeros(total_samples, dtype=np.float64)
    crossfade_s = 5.0
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
    print("[ambient] Synthesizing music pad...")
    progression_midi = [
        [45, 48, 52, 57],  # Am
        [41, 45, 48, 53],  # F
        [48, 52, 55, 60],  # C
        [43, 47, 50, 55],  # G
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
    print("Bedtime Hypnosis Audio Generator - Manuela v2 (PT-BR)")
    print("=" * 70)

    voice_track = build_voice_track()
    binaural_track = generate_binaural_track()
    ambient_track = generate_ambient_track()

    voice_track = voice_track[:TOTAL_DURATION_MS]
    binaural_track = binaural_track[:TOTAL_DURATION_MS]
    ambient_track = ambient_track[:TOTAL_DURATION_MS]

    print("[mix] Layering tracks...")
    binaural_track = binaural_track - 22
    ambient_track = ambient_track - 8

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
    print(f"Output:        {OUTPUT_FILE}")
    print(f"Duration:      {len(mixed)/1000/60:.2f} min")
    print(f"Size:          {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
