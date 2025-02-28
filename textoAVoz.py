#TTS
from kokoro import KPipeline
from misaki import en, espeak

pipe_audio = ''
sd = ''

def generar_voz(texto):
    print("Generando voz")
    phonemes, _ = g2p(texto)
    # Create
    samples, sample_rate = kokoro.create(phonemes, voice="ef_dora", is_phonemes=True)

    # Play
    print("Playing audio...")
    sd.play(samples, sample_rate)
    sd.wait()

def inicializarModelo(sounddevice):
    fallback = espeak.EspeakFallback(british=False)
    g2p = en.G2P(trf=False, british=False, fallback=fallback)
    pipe_audio = KPipeline(lang_code='e')
    sd = sounddevice
