import json
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ------------------------
# サービスアカウント認証
# ------------------------
service_account_info = json.loads(st.secrets["google_service_account"]["value"])
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# ------------------------
# Streamlit UI
# ------------------------
st.title("Google Drive ファイルアップローダー")

folder_name = st.text_input("作成するフォルダ名", value="MyFolder")
file_to_upload = st.file_uploader("アップロードするファイルを選択", type=["csv", "txt", "xlsx"])

if st.button("フォルダ作成 & アップロード"):

    # 1. フォルダ作成
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = drive_service.files().create(
        body=folder_metadata,
        fields="id"
    ).execute()
    folder_id = folder.get("id")
    st.success(f"フォルダ作成完了！ID: {folder_id}")

    # 2. ファイルアップロード
    if file_to_upload is not None:
        # Streamlit UploadedFile から直接アップロード
        media = MediaFileUpload(file_to_upload.name, mimetype=file_to_upload.type)
        file_metadata = {
            "name": file_to_upload.name,
            "parents": [folder_id]
        }
    
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True  # ← ここを忘れずに
        ).execute()
    
        st.success(f"ファイルアップロード完了！ID: {uploaded_file.get('id')}")

