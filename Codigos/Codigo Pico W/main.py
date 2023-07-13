"""
main.py

Este programa realiza la lectura de datos de un sensor BME280 y la información de GPS. Luego, envía los datos a través de UDP a una dirección IP y puerto específicos.

Requiere las siguientes bibliotecas y módulos:
- machine: módulo para controlar periféricos en microcontroladores.
- Pin: módulo para controlar pines de E/S en microcontroladores.
- I2C: módulo para comunicación I2C en microcontroladores.
- UART: módulo para comunicación UART en microcontroladores.
- time: módulo para funciones relacionadas con el tiempo.
- bme280: módulo para interactuar con el sensor BME280.
- socket: módulo para comunicación de red a través de sockets.
- network: módulo para configuración y administración de redes.
- micropyGPS: módulo para decodificar datos NMEA de un módulo GPS.

"""

from machine import Timer
from machine import Pin, I2C, UART
import time
import bme280
import socket
import network
from micropyGPS import MicropyGPS

# Configura los detalles de la conexión UDP
UDP_IP = '0.0.0.0'  # Dirección IP de destino para enviar los datos por UDP
UDP_PORT = 5005           # Puerto UDP de destino

# Configura los detalles de la red Wi-Fi
SSID = 'NOMBRE_DE_RED'    # Nombre de la red Wi-Fi (SSID)
PASSWORD = 'CONTRASEÑA'   # Contraseña de la red Wi-Fi

# Inicializa el adaptador Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

# Conéctate a la red Wi-Fi
wifi.connect(SSID, PASSWORD)

# Espera a que se establezca la conexión Wi-Fi
while not wifi.isconnected():
    pass

# Muestra la dirección IP asignada
print("Conexión Wi-Fi establecida")
print("Dirección IP:", wifi.ifconfig()[0])

# Crea un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Configuración del bus I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
bme = bme280.BME280(i2c=i2c)

# Configuración del GPS
gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
my_gps = MicropyGPS(5)  # Ajusta el valor de TIMEZONE según tu ubicación

# Valores iniciales de latitud y longitud (valores constantes)
initial_latitude = "0.000000"
initial_longitude = "0.000000"

def convert(parts):
    """
    Convierte las partes de coordenadas GPS (grados, minutos, dirección) a un valor decimal.

    Args:
        parts (tuple): Tupla con las partes de la coordenada (grados, minutos, dirección).

    Returns:
        str: Coordenada convertida a valor decimal con 6 decimales.

    """
    if parts[0] == 0:
        return None

    data = parts[0] + (parts[1] / 60.0)
    # parts[2] contiene 'E' o 'W' o 'N' o 'S'
    if parts[2] == 'S':
        data = -data
    if parts[2] == 'W':
        data = -data

    data = '{0:.6f}'.format(data)  # con 6 decimales
    return str(data)

def leer_sensor():
    """
    Lee los valores del sensor BME280 y envía los datos junto con la información del GPS por UDP.

    """
    temp = bme.values[0]
    pres = bme.values[1]
    hum = bme.values[2]

    # Leer datos del GPS
    length = gps_module.any()
    if length > 0:
        b = gps_module.read(length)
        for x in b:
            msg = my_gps.update(chr(x))

    # Obtener latitud y longitud
    latitude = convert(my_gps.latitude)
    longitude = convert(my_gps.longitude)

    if latitude is None or longitude is None:
        # Usar los valores iniciales si no hay datos del GPS
        latitude = initial_latitude
        longitude = initial_longitude

    message = f"Temperatura: {temp}   Presion: {pres}   Humedad: {hum}   Latitud: {latitude}   Longitud: {longitude}"
    print(message)
    sock.sendto(bytes(message, "utf-8"), (UDP_IP, UDP_PORT))

while True:
    leer_sensor()
    time.sleep(1)

