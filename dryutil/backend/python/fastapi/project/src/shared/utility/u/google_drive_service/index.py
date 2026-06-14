import os, sys, subprocess
# ------------------------
# Auto-install prerequisites
# ------------------------
def install_libs(_v={
    "l": []
}):
    for lib in _v['l']:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing {lib} via Poetry ...")
            subprocess.check_call(["poetry", "add", lib])
#set..
install_libs({
    "l": [
    "google-api-python-client",
    "google-auth",
    "google-auth-httplib2",
    "google-auth-oauthlib",
   ]
})




#set..
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service(_v={
    'cred': dict
}):
    #print(_v)
    #creds = service_account.Credentials.from_service_account_file(
        #SERVICE_ACCOUNT_FILE, scopes=SCOPES
    #)
    creds = service_account.Credentials.from_service_account_info(
        _v['cred'], scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

# ✅ Upload file
def upload_file(file_path: str, file_name: str, mime_type: str, folder_id: Optional[str] = None):
    service = get_drive_service()
    file_metadata = {"name": file_name}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(
        body=file_metadata, media_body=media, fields="id, name, webViewLink"
    ).execute()

    return file

# ✅ List files
def list_files(_v={
    'cred': dict,
    'page_size': None,
    'folder_id': None,
    }) -> List[dict]:
    service = get_drive_service({'cred':_v['cred']})
    query = f"'{_v["folder_id"]}' in parents" if _v["folder_id"] else None

    results = service.files().list(
        pageSize=_v["page_size"],
        q=query,
        fields="files(id, name, mimeType, webViewLink, createdTime)"
    ).execute()

    return results.get("files", [])

# ✅ Download file
def download_file(_v={
    'cred': dict,
    'file_id': str,
    'destination': str,
    }):
    service = get_drive_service({'cred':_v['cred']})
    request = service.files().get_media(fileId=_v["file_id"])
    fh = io.FileIO(_v["destination"], "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
    return _v["destination"]

# ✅ Delete file
def delete_file(file_id: str):
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()
    return {"status": "deleted", "file_id": file_id}

# ✅ Find folder
def find_folder(_v={
    'cred': dict,
    'folder_name': str,
    'parent_id': str,
    }):
    service = get_drive_service({'cred':_v['cred']})

    # Build query
    query = f"name = '{_v["folder_name"]}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if _v["parent_id"]:
        query += f" and '{_v["parent_id"]}' in parents"
    

    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name, webViewLink)",
        pageSize=10
    ).execute()


    folders = results.get("files", [])
    return folders  # list of matching folders

# ✅ Create folder
def create_folder(_v={
    'cred': dict,
    'folder_name': str,
    'parent_id': str,
    }):
    service = get_drive_service({'cred':_v['cred']})

    file_metadata = {
        "name": _v["folder_name"],
        "mimeType": "application/vnd.google-apps.folder"
    }

    if _v["parent_id"]:  # Optional: create inside another folder
        file_metadata["parents"] = [_v["parent_id"]]

    folder = service.files().create(
        body=file_metadata,
        fields="id, name, webViewLink"
    ).execute()

    """ Sample
    {'id': '14FAKMXPGzIQDqapYvP8lPlq6U0qmlAsg', 'name': 'dryutil-174a3734-093b-4f51-803b-63c14be0bed7', 'webViewLink': 'https://drive.google.com/drive/folders/14FAKMXPGzIQDqapYvP8lPlq6U0qmlAsg'}
    """

    return folder
