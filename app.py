# Cargamos todos los modulos
import json
import argparse
import serial
import time
import spacy
#from kokoro_onnx import Kokoro
from misaki import en, espeak
import sys
import sounddevice as sd

# Cargamos el resto de archivos para utilizar sus funciones
import vozATexto as stt

# Listamos todos los dispositivos de audio disponibles
def listar_dispositivos():
    print(sd.query_devices())

# Funcion para el argumento del dispositivo
def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text

# Funcion principal
def main():
    try:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-l", "--listar", action="store_true",
            help="listar todos los dispositivos de audio")
        args, remaining = parser.parse_known_args()
        if args.listar:
            listar_dispositivos()
            parser.exit(0)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        parser.add_argument(
            "-d", "--dispositivo", type=int_or_str,
            help="dispositivo de entrada de audio (ID o nombre)")
        parser.add_argument(
            "-r", "--samplerate", type=int, help="sampling rate")
        parser.add_argument(
            "-m", "--modelo", type=str, help="lenguaje del modelo; e.j. en-us, fr, nl; por defecto español  ('es')")
        args = parser.parse_args(remaining)
        stt.capturar(args.samplerate,args.dispositivo,args.modelo,sd)
    except KeyboardInterrupt:
        print("\nParando captura de audio")
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ": " + str(e))

if __name__ == "__main__":
    main()
