import serial

def enviarSenal(texto):
    ser = serial.Serial("/dev/ttyACM0", 9600)
    byte_data = bytearray(texto, "utf-8")
    ser.write(byte_data)  # Enciende el LED
    ser.close()
