import os
import zipfile
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# Función para comprimir el proyecto
def comprimir_proyecto(ruta_proyecto, nombre_archivo_zip):
    with zipfile.ZipFile(nombre_archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ruta_proyecto):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(ruta_proyecto, '..')))

# Función para subir el archivo a Google Drive
def subir_a_google_drive(nombre_archivo_zip, credentials_path):
    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': nombre_archivo_zip, 'parents': ['1HEuZ4ylWo55b2RkoOKdcigW7J6dj2vMv']}
    media = MediaFileUpload(nombre_archivo_zip, mimetype='application/zip')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Archivo {nombre_archivo_zip} subido con éxito, ID: {file.get('id')}")

# Ruta del proyecto a comprimir
ruta_proyecto = 'C:/Cursos/Python/Cursos/Comercio/Comercio'
nombre_archivo_zip = 'backup_proyecto.zip'
credentials_path = 'C:/Cursos/Python/Cursos/Comercio/Comercio/Backup/credentials.json'

comprimir_proyecto(ruta_proyecto, nombre_archivo_zip)
subir_a_google_drive(nombre_archivo_zip, credentials_path)