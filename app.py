import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import json

st.title("Google Drive & Sheets Demo")

# --- Secretsから認証情報を取得 ---
client_id = st.secrets["google_oauth"]["client_id"]
client_secret = st.secrets["google_oauth"]["client_secret"]
redirect_uri = st.secrets["google_oauth"]["redirect_uri"]

# --- OAuthフロー設定 ---
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": [redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=[
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets"
    ],
    redirect_uri=redirect_uri,
)

# --- 認可URL生成 ---
if "credentials" not in st.session_state:
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.write("🔐 Google認証を行ってください:")
    st.markdown(f"[認証する]({auth_url})")
else:
    st.success("✅ 認証済みです！")

# --- 認可コード処理 ---
code = st.experimental_get_query_params().get("code")
if code and "credentials" not in st.session_state:
    flow.fetch_token(code=code[0])
    creds = flow.credentials
    st.session_state["credentials"] = creds_to_dict(creds)
    st.rerun()

# --- スプレッドシート作成 ---
if "credentials" in st.session_state:
    creds = Credentials.from_authorized_user_info(st.session_state["credentials"])
    drive_service = build("drive", "v3", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)

    if st.button("📄 スプレッドシートを作成"):
        file_metadata = {
            "name": "自動作成テスト",
            "mimeType": "application/vnd.google-apps.spreadsheet",
        }
        sheet = drive_service.files().create(body=file_metadata, fields="id").execute()
        st.success(f"✨ 作成しました！ → ID: {sheet['id']}")
