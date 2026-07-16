import os
import requests
from requests.auth import HTTPBasicAuth

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES DE ZOOM
# ==========================================
# Para obtener esto debes crear una App "Server-to-Server OAuth" en el Zoom App Marketplace.
# Opcionalmente, si ya tienes un TOKEN de acceso temporal, puedes ponerlo directamente abajo.

ZOOM_ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID", "TU_ACCOUNT_ID_AQUI")
ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID", "TU_CLIENT_ID_AQUI")
ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET", "TU_CLIENT_SECRET_AQUI")

# Si pegas un token manual de Postman o n8n aquí, ignorará la autenticación y usará este.
MANUAL_ACCESS_TOKEN = "" 

# El ID de la reunión que quieres revisar (ej: 89312345678). Si lo dejas vacío, buscará la última reunión grabada.
MEETING_ID = ""

def get_access_token():
    if MANUAL_ACCESS_TOKEN:
        return MANUAL_ACCESS_TOKEN
        
    print("Obteniendo Access Token de Zoom...")
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ZOOM_ACCOUNT_ID}"
    response = requests.post(url, auth=HTTPBasicAuth(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET))
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo token: {response.text}")
        exit(1)
        
    token = response.json().get("access_token")
    print("✅ Token obtenido con éxito.")
    return token

def check_recordings(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    if MEETING_ID:
        # Busca una reunión en específico
        url = f"https://api.zoom.us/v2/meetings/{MEETING_ID}/recordings"
        print(f"Consultando grabaciones para la reunión {MEETING_ID}...")
    else:
        # Busca las últimas grabaciones del usuario (me)
        url = "https://api.zoom.us/v2/users/me/recordings?page_size=5"
        print("Consultando las últimas grabaciones de tu cuenta...")
        
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error al consultar la API: {response.text}")
        exit(1)
        
    data = response.json()
    
    # Si usamos la ruta de "users/me/recordings", los datos vienen en una lista 'meetings'
    meetings_to_check = [data] if MEETING_ID else data.get("meetings", [])
    
    if not meetings_to_check:
        print("⚠️ No se encontraron grabaciones en la nube en tu cuenta de Zoom.")
        return

    encontro_vtt = False

    for meeting in meetings_to_check:
        m_id = meeting.get("id")
        m_topic = meeting.get("topic")
        print(f"\nRevisando reunión: [{m_id}] - {m_topic}")
        
        archivos = meeting.get("recording_files", [])
        for file in archivos:
            tipo = file.get("file_type")
            ext = file.get("file_extension")
            r_type = file.get("recording_type")
            
            print(f"  -> Archivo encontrado: {tipo} (.{ext}) - {r_type}")
            
            if tipo == "TRANSCRIPT" or ext == "VTT":
                print("     ✅ ¡TRANSCRIPT ENCONTRADO! Esta cuenta soporta y genera VTTs.")
                encontro_vtt = True

    if not encontro_vtt:
        print("\n❌ CONCLUSIÓN: No se encontró ningún archivo .vtt (TRANSCRIPT) en las grabaciones revisadas.")
        print("Asegúrate de que en el panel de Zoom (Account Settings > Recording) la opción 'Audio Transcript' esté activada.")

if __name__ == "__main__":
    token = get_access_token()
    check_recordings(token)
