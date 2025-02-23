import pyaudio
import json
import argparse
from vosk import Model, KaldiRecognizer
import serial
import time
import spacy
import sounddevice as sd
from kokoro_onnx import Kokoro
from misaki import en, espeak

def accion_jugar():
    print("El usuario quiere jugar")
    #ser.write("1".encode("utf-8"))
    generar_voz("Muy bien, ¿qué quieres jugar?")

def accion_saludo():
    print("Saludar al usuario")
    #ser.write("2".encode("utf-8"))
    generar_voz("Hola usuario, ¿cómo estás?")

def accion_sentarse():
    print("El usuario quiere que me siente")
    #ser.write("3".encode("utf-8"))
    generar_voz("Está bien, te espero aquí")

def accion_despido():
    print("El usuario se despide")
    #ser.write("4".encode("utf-8"))
    generar_voz("Hasta luego, espero vernos pronto")

def accion_aprender():
    print("El usuario quiere aprender")
    #ser.write("5".encode("utf-8"))
    generar_voz("Entendido, vamos a aprender")

def palabras(texto):
    texto = "".join(texto)
    palabras_acciones = {
        "hola": accion_saludo,
        "saludar": accion_saludo,
        "buenas": accion_saludo,
        "adios": accion_despido,
        "hasta luego": accion_despido,
        "nos vemos": accion_despido,
        "despido": accion_despido,
        "siéntate": accion_sentarse,
        "sentarnos": accion_sentarse,
        "sentar": accion_sentarse,
        "jugar": accion_jugar,
        "juguemos": accion_jugar,
        "aprender": accion_aprender
    }

    # Buscar coincidencias y ejecutar la acción correspondiente
    for palabra, accion in palabras_acciones.items():
        #print(palabra)
        doc = nlp(palabra)
        #for token in doc:
            #print(token.text, token.lemma_)
        coincidencias = [token.text for token in doc if token.lemma_ in texto]
        if coincidencias:
                print(f"Formas encontradas: {coincidencias}")
                accion()
                break  # Opcional: Detenerse tras la primera coincidencia
    else:
        print("Ninguna palabra clave encontrada")

def generar_voz(texto):
    print("Generando voz")
    phonemes, _ = g2p(texto)
    # Create
    samples, sample_rate = kokoro.create(phonemes, voice="ef_dora", is_phonemes=True)

    # Play
    print("Playing audio...")
    sd.play(samples, sample_rate)
    sd.wait()



def lecturaStream():
    # Configurar PyAudio para capturar audio en tiempo real
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=4000)
    stream.start_stream()

    print("Escuchando...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break
            # Procesar el bloque de audio
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print("Transcripción:", result.get("text", ""))
                palabras(result.get("text", ""))
            else:
                partial = json.loads(rec.PartialResult())
                print("Parcial:", partial.get("partial", ""))
                palabras(partial.get("partial", ""))
    except KeyboardInterrupt:
        print("Detenido por el usuario.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def lecturaArchivo(archivo):
    print(f"Procesando {archivo}...")
    # Leer un archivo .wav para el reconocimiento
    with open(archivo, "rb") as wav_file:
        wav_data = wav_file.read()

    texto_final = []
    chunk_size = 4096
    for i in range(0, len(wav_data), chunk_size):
        chunk = wav_data[i:i+chunk_size]
        if rec.AcceptWaveform(chunk):
            result = json.loads(rec.Result())
            texto_final.append(result.get("text", ""))

    final_result = json.loads(rec.FinalResult())
    texto_final.append(final_result.get("text", ""))

    print("Texto reconocido ", texto_final)

    palabras(texto_final)

# Configurar el puerto serial
#ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600, timeout=1)

# Cargar y configurar el modelo TTS
fallback = espeak.EspeakFallback(british=False)
g2p = en.G2P(trf=False, british=False, fallback=fallback)

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

# Cargar el modelo en español para el reconocimiento de voz
model = Model("./vosk-model-small-es-0.42")
rec = KaldiRecognizer(model, 16000)

# Cargar el modelo para los sinonimos
nlp = spacy.load("es_core_news_sm")

#Leer los argumentos (el archivo de voz lo recibo por argumentos)
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lectura", help="Forma de recibir el audio [stream/archivo]")
parser.add_argument("-a", "--archivo", help="Ruta del archivo a procesar")
args = parser.parse_args()

if args.lectura == "archivo":
    lecturaArchivo(args.archivo)
else:
    lecturaStream()

#print(texto_final)

#ser.close()
