import cv2
import numpy as np
import pyautogui
import pytesseract
import pygame
import time
import json
import os
from mss import mss

# Configurar la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Cargar configuración desde un archivo JSON
CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    config_data = {
        "texto_objetivo_1": "is requesting a trade.",
        "sonido_alerta_1": "beep-104060.mp3",
        "intervalo_escaneo": 0.1,
        "texto_objetivo_2": "You have a new message!",
        "sonido_alerta_2": "alert-sound.mp3",
        "monitor_seleccionado": "ambos"  # Opciones: "1", "2", "ambos"
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

TEXTO_OBJETIVO_1 = config["texto_objetivo_1"]
SONIDO_ALERTA_1 = config["sonido_alerta_1"]
TEXTO_OBJETIVO_2 = config["texto_objetivo_2"]
SONIDO_ALERTA_2 = config["sonido_alerta_2"]
INTERVALO_ESCANEO = config["intervalo_escaneo"]
MONITOR_SELECCIONADO = config.get("monitor_seleccionado", "ambos")

pygame.mixer.init()

sct = mss()

# Obtener información de los monitores
displays = sct.monitors

# Muestra una captura de referencia
ref_capture = pyautogui.screenshot()
cv2.imshow("Captura de Referencia", np.array(ref_capture))
cv2.waitKey(10000)
cv2.destroyAllWindows()

def capturar_pantalla():
    if MONITOR_SELECCIONADO == "1":
        region = displays[1]  # Primer monitor
    elif MONITOR_SELECCIONADO == "2":
        region = displays[2]  # Segundo monitor
    else:
        region = {
            "left": 0,
            "top": 0,
            "width": displays[1]["width"] + displays[2]["width"],
            "height": max(displays[1]["height"], displays[2]["height"])
        }
    screenshot = sct.grab(region)
    frame = np.array(screenshot)
    return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

def preprocesar_imagen(frame):
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gris, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

def detectar_texto(frame):
    texto_extraido = pytesseract.image_to_string(frame).strip()

    if TEXTO_OBJETIVO_1.lower() in texto_extraido.lower():
        print(f"[ALERTA] '{TEXTO_OBJETIVO_1}' detectado!")
        pygame.mixer.Sound(SONIDO_ALERTA_1).play()

    if TEXTO_OBJETIVO_2.lower() in texto_extraido.lower():
        print(f"[ALERTA] '{TEXTO_OBJETIVO_2}' detectado!")
        pygame.mixer.Sound(SONIDO_ALERTA_2).play()

def main():
    print(f"Monitoreando en tiempo real: '{TEXTO_OBJETIVO_1}' y '{TEXTO_OBJETIVO_2}'")
    while True:
        frame = capturar_pantalla()
        frame_procesado = preprocesar_imagen(frame)
        detectar_texto(frame_procesado)
        time.sleep(INTERVALO_ESCANEO)

if __name__ == "__main__":
    main()
