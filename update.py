import sys

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


# # Determinar si el script se ejecuta como un archivo .py o como un ejecutable .exe
# if getattr(sys, 'frozen', False):
#     # Si se ejecuta como un ejecutable .exe, el directorio base es el directorio del ejecutable
#     basedir = sys._MEIPASS
# else:
#     # Si se ejecuta como un archivo .py, el directorio base es el directorio del script
#     basedir = os.path.dirname(os.path.abspath(__file__))
#
# # Configurar el repo_path para que apunte al subdirectorio _internal dentro del basedir
# repo_path = os.path.join(basedir, "_internal")

def update_program():
    # Determinar si el script se ejecuta como un archivo .py o como un ejecutable .exe
    if getattr(sys, 'frozen', False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(os.path.abspath(__file__))

    # Verificar si basedir ya termina con "_internal"
    if basedir.endswith("_internal"):
        repo_path = basedir
    else:
        repo_path = os.path.join(basedir, "_internal")

    if not os.path.isdir(repo_path):
        os.makedirs(repo_path)

    current_dir = os.getcwd()
    os.chdir(repo_path)

    try:
        if os.path.isdir(".git"):
            # Actualizar el repositorio existente
            subprocess.run(["git", "pull"], check=True)
        else:
            # Clonar el repositorio porque no existe localmente, sin crear un subdirectorio adicional
            subprocess.run(["git", "clone", GIT_CLONE_COMMAND.split()[-1], "."], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al actualizar el repositorio: {e}")
    finally:
        os.chdir(current_dir)

    with open(LOCAL_VERSION_FILE, "w") as file:
        file.write(datetime.now().strftime("%Y-%m-%d"))
    print("El programa ha sido actualizado.")

    return

if __name__ == "__main__":
    check_for_updates()