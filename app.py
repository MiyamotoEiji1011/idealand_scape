import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile
import json

st.title("Google Drive CSVアップロードアプリ 🌸")

# --- 1. サービスアカウント情報をStreamlit Secretsから読み込む ---
# Secrets.tomlに以下のように保存しておく
# [google_service_account]
# value = """ {...JSON内容...} """
service_account_info = json.loads(st.secrets["google_service_account"]["value"])

creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/drive']
)

drive_service = build('drive', 'v3', credentials=creds)

# --- 2. ファイルアップロードUI ---
uploaded_file = st.file_uploader("アップロードするCSVファイルを選択してください", type=["csv"])

# --- 3. アップロード先フォルダID入力 ---
folder_id = st.text_input("アップロード先フォルダID", value="")  # 例: 共有フォルダID

# --- 4. アップロード処理 ---
if uploaded_file and folder_id:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    file_metadata = {
        'name': uploaded_file.name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(tmp_file_path, mimetype='application/csv')
    try:
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True  # 共有ドライブにも対応
        ).execute()
        st.success(f"アップロード成功！ファイルID: {file.get('id')}")
    except Exception as e:
        st.error(f"アップロード中にエラーが発生しました: {e}")

# --- 5. 注意 ---
st.info("⚠️ フォルダIDはDrive上で対象フォルダを開いたときのURL末尾のIDを使用してください。")
