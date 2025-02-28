import queue
import sys
import ast
import spacy
from spacy.matcher import PhraseMatcher
from unidecode import unidecode
#from kokoro_onnx import Kokoro
from kokoro import KPipeline
from misaki import en, espeak

from vosk import Model, KaldiRecognizer

#import textoAVoz as tts
import comunicacion_serial as serial

q = queue.Queue()

def accion_jugar():
    print("El usuario quiere jugar")
    #ser.write("1".encode("utf-8"))
    serial.enviarSenal("2")
    #tts.generar_voz("Muy bien, ¿qué quieres jugar?")

def accion_saludo():
    print("Saludar al usuario")
    #ser.write("2".encode("utf-8"))
    serial.enviarSenal("b")
    #tts.generar_voz("Hola usuario, ¿cómo estás?")

def accion_sentarse():
    print("El usuario quiere que me siente")
    #ser.write("3".encode("utf-8"))
    serial.enviarSenal("s")
    #tts.generar_voz("Está bien, te espero aquí")

def accion_despido():
    print("El usuario se despide")
    #ser.write("4".encode("utf-8"))
    serial.enviarSenal("4")
    #tts.generar_voz("Hasta luego, espero vernos pronto")

def accion_aprender():
    print("El usuario quiere aprender")
    #ser.write("5".encode("utf-8"))
    serial.enviarSenal("d")
    #tts.generar_voz("Entendido, vamos a aprender")

def comando(texto, nlp):
    frases = PhraseMatcher(nlp.vocab, attr="LOWER")
    texto = ast.literal_eval(texto)
    #if (len(str(texto['text'])) > 1):
        #print(texto['text'])
    doc = nlp(unidecode(str(texto['text'])))
    variantes = {
        "saludo" : ["hola", "buenos días", "buenos dias", "buen dia", "buen día", "buenas tardes", "buena tarde", "buenas noches", "buena noche", "saludos", "saludo"],
        "despido" : ["adios", "hasta luego", "nos vemos", "despido"],
        "sentar" : ["sientate", "sentarse", "sientate", "siéntate"],
        "jugar" : ["juguemos", "jugar"],
        "captura" :  ["toma foto", "toma captura", "tomame una foto"],
        "aprender" : ["aprender"]
    }

    palabras_acciones = {
        "saludo" : accion_saludo,
        "despido": accion_despido,
        "sentar": accion_sentarse,
        "jugar": accion_jugar,
        "aprender": accion_aprender
    }

    for palabra, variante in variantes.items():
        pattern = [nlp(unidecode(v).lower()) for v in variante]
        frases.add(palabra, pattern)

    coincidencias = frases(doc)

    # Mostrar resultados
    for match_id, start, end in coincidencias:
        frase_base = nlp.vocab.strings[match_id]  # Obtener el ID de la frase base
        span = doc[start:end]  # Obtener el fragmento del texto que coincide
        print(f"Frase detectada: {frase_base} (texto: '{span.text}')")
        print("Frase base: " , frase_base)
        for palabra, accion in palabras_acciones.items():
            accion()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def capturar(samplerate, dispositivo, lenguaje, sd):
    #tts.inicializarModelo(sd)
    #clasificador = pipeline('text-classification', model='distilbert-base-uncased')
    #kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    nlp = spacy.load('es_core_news_md')
    # Cargar y configurar el modelo TTS
    #fallback = espeak.EspeakFallback(british=False)
    #g2p = en.G2P(trf=False, british=False, fallback=fallback)
    #pipe_audio = KPipeline(lang_code='e')
    if samplerate is None:
        device_info = sd.query_devices(dispositivo, "input")
        print(device_info.values())
        # soundfile expects an int, sounddevice provides a float:
        samplerate = int(device_info["default_samplerate"])

    if lenguaje is None:
        model = Model(lang="es")
    else:
        model = Model(lang=lenguaje)

    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=dispositivo, dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Ctrl+C para parar el programa")
        print("Escuchando...")
        print("#" * 80)

        rec = KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = rec.Result()
                print(text)
                comando(text, nlp)
