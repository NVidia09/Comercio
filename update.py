import requests
import os
import subprocess
from datetime import datetime, timedelta

# Configuración
REPO_URL = "https://api.github.com/repos/NVidia09/Comercio/commits"
LOCAL_VERSION_FILE = "version.txt"
GIT_CLONE_COMMAND = "git clone https://github.com/NVidia09/comercio.git"

def check_for_updates():
    # Leer la última fecha de actualización desde el archivo de versión local
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as file:
            last_update = datetime.strptime(file.read().strip(), "%Y-%m-%d")
    else:
        last_update = datetime.now() - timedelta(days=1)  # Por defecto, asume que la última actualización fue ayer

    # Consultar la API de GitHub para obtener el último commit
    response = requests.get(REPO_URL)
    if response.status_code == 200:
        latest_commit_date = datetime.strptime(response.json()[0]['commit']['committer']['date'], "%Y-%m-%dT%H:%M:%SZ")
        if latest_commit_date > last_update:
            print("Hay una nueva actualización disponible.")
            update_program()
        else:
            print("El programa está actualizado.")
    else:
        print("Error al consultar la API de GitHub.")

def update_program():
    repo_path = "comercio"  # Asegúrate de que esta sea la ruta correcta del repositorio local
    if os.path.isdir(repo_path):
        # Actualizar el repositorio existente
        subprocess.run(["git", "-C", repo_path, "pull"], check=True)
    else:
        # Clonar el repositorio porque no existe localmente
        subprocess.run(GIT_CLONE_COMMAND, shell=True, check=True)
    # Actualizar la fecha de la última actualización en el archivo de versión
    with open(LOCAL_VERSION_FILE, "w") as file:
        file.write(datetime.now().strftime("%Y-%m-%d"))
    print("El programa ha sido actualizado.")

if __name__ == "__main__":
    check_for_updates()