import os
import io
from google.oauth2 import service_account
from collections import deque
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from rich.progress import track
from settings import Settings

CONTENT_DIR = 'src/content'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
settings = Settings()

def authenticate_service_account():    
    credentials = service_account.Credentials.from_service_account_info(
        settings.service_account_key, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def fetch_markdown_folders_and_files(service):
    folders = deque([(settings.blog_folder_id, "root")])
    while folders:
        folder_id, folder_name = folders.popleft()
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        for file in results.get('files', []):
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                folders.append((file['id'], file['name']))
            elif file['mimeType'] == 'text/markdown':
                yield (folder_name, file)            

def download_file(service, file_id, folder, filename):
    request = service.files().get_media(fileId=file_id)
    filepath = os.path.join(CONTENT_DIR, folder, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with io.FileIO(filepath, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

def main():
    service = authenticate_service_account()
    folder_and_files = list(fetch_markdown_folders_and_files(service))
    print(f"Found {len(folder_and_files)} markdown files.")
    for folder, file in track(folder_and_files, description="Downloading files...", total=len(folder_and_files)):
        print(f"Downloading {file['name']}...")
        download_file(service, file['id'], folder.lower(), file['name'])

if __name__ == '__main__':
    main()
