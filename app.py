import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

st.title("📄 Google Drive スプレッドシート自動作成")

# -------------------------
# 関数定義
# -------------------------
def creds_to_dict(creds):
    """Credentialsオブジェクトを辞書に変換"""
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }

def get_credentials():
    """OAuth認証を行いCredentialsを取得"""
    if "credentials" in st.session_state:
        creds = Credentials(**st.session_state["credentials"])
        return creds

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets"
        ],
        redirect_uri=st.secrets["google_oauth"]["redirect_uri"],
    )

    # 認証URL生成
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.write("🔐 Googleアカウント認証を行ってください:")
    st.markdown(f"[認証する]({auth_url})")

    # 認可コード取得
    code = st.experimental_get_query_params().get("code")
    if code:
        flow.fetch_token(code=code[0])
        creds = flow.credentials
        st.session_state["credentials"] = creds_to_dict(creds)
        st.experimental_rerun()

    return None

# -------------------------
# メイン処理
# -------------------------
creds = get_credentials()
if creds:
    drive_service = build("drive", "v3", credentials=creds)

    # UI
    folder_id = st.text_input("📁 作成先フォルダID（空欄ならマイドライブ）", "")
    sheet_name = st.text_input("📄 作成するスプレッドシート名", "MyAutoSheet")

    if st.button("作成！"):
        file_metadata = {
            "name": sheet_name,
            "mimeType": "application/vnd.google-apps.spreadsheet",
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]

        file = drive_service.files().create(body=file_metadata, fields="id, name").execute()
        st.success(f"✨ 作成しました！: {file['name']}")
        st.markdown(f"[開く ▶️](https://docs.google.com/spreadsheets/d/{file['id']}/edit)")
