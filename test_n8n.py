import requests
import json
import time
import os

url = "https://jeanc.app.n8n.cloud/webhook/crear-reunion-chat"
payload = {
    "creador_id": "test-id",
    "mensaje": "Crear reunión de prueba para mañana a las 10am de tipo virtual"
}

try:
    print(f"Enviando request a n8n: {url}")
    resp = requests.post(url, json=payload, timeout=90)
    print(f"Status: {resp.status_code}")
    print(f"Response text: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
