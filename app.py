import json
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import ioimport json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------
# サービスアカウント認証
# ------------------------
service_account_info = json.loads(st.secrets["google_service_account"]["value"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)

client = gspread.authorize(creds)

# ------------------------
# Streamlit UI
# ------------------------
st.title("既存スプレッドシート 書き込みデモ")

spreadsheet_name = st.text_input("スプレッドシート名", value="Your Spreadsheet Name")
worksheet_name = st.text_input("ワークシート名", value="Sheet1")
row_values = st.text_input("追加する行の値 (カンマ区切り)", value="A,B,C")

if st.button("行を追加"):
    try:
        # スプレッドシートとワークシートを取得
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # 入力値をリストに変換
        values = [v.strip() for v in row_values.split(",")]

        # 末尾に追加
        worksheet.append_row(values)

        st.success(f"{values} を {worksheet_name} に追加しました！")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")


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
        fields="id",
        supportsAllDrives=True  # 共有ドライブ対応
    ).execute()
    folder_id = folder.get("id")
    st.success(f"フォルダ作成完了！ID: {folder_id}")

    # 2. ファイルアップロード
    if file_to_upload is not None:
        # UploadedFile をバイナリで読み込む
        file_bytes = file_to_upload.read()
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=file_to_upload.type, resumable=True)

        file_metadata = {
            "name": file_to_upload.name,
            "parents": [folder_id]
        }

        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True  # ← ここも忘れずに
        ).execute()

        st.success(f"ファイルアップロード完了！ID: {uploaded_file.get('id')}")
