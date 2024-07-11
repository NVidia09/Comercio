from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

# Obtener la ruta base del directorio actual
basedir = os.path.dirname(os.path.abspath(__file__))
# Replace 'YOUR_CLIENT_SECRETS_FILE.json' with the path to the JSON file you downloaded
#CLIENT_SECRETS_FILE = 'C:/Cursos/Python/Cursos/Comercio/Comercio/credentials.json'
CLIENT_SECRETS_FILE = os.path.join(basedir, 'credentials.json')

# This scope will allow the script to access and modify files in your Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print("Your refresh token has been saved in token.json. Use this file for your API calls.")

if __name__ == '__main__':
    main()