import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import json

# =========================================================
# 🔑 Google Sheets認証
# =========================================================
def google_login():
    """Google Service Accountで認証"""
    try:
        service_account_info = json.loads(st.secrets["google_service_account"]["value"])
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)

        # Sheets APIクライアントも作る
        service = build("sheets", "v4", credentials=creds)
        st.success("✅ Google Service Account Loaded Successfully!")
        return client, service
    except Exception as e:
        st.error(f"❌ Failed to load service account: {e}")
        return None, None


# =========================================================
# 📋 セルごとコピー処理
# =========================================================
def copy_cell_format_and_value(service, source_id: str, dest_id: str):
    """コピー元A1セルを、コピー先A1〜A10にフォーマット付きでコピー"""
    try:
        # copyPasteリクエストを作成
        requests = [
            {
                "copyPaste": {
                    "source": {
                        "sheetId": 0,  # デフォルトシート（シート1）のID=0
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "destination": {
                        "sheetId": 0,
                        "startRowIndex": i,
                        "endRowIndex": i + 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "pasteType": "PASTE_NORMAL",
                    "pasteOrientation": "NORMAL",
                }
            }
            for i in range(10)
        ]

        # リクエスト送信
        body = {"requests": requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=dest_id, body=body
        ).execute()

        st.success("✅ セル本体のコピー完了！(A1 → A1:A10 に複製)")
    except Exception as e:
        st.error(f"❌ セルコピーに失敗しました: {e}")


# =========================================================
# 🏗️ Streamlit UI
# =========================================================
st.title("セルごとコピーするツール")

# --- Google Login ---
if st.button("Google Login"):
    gclient, gservice = google_login()
    if gclient:
        st.session_state.gclient = gclient
        st.session_state.gservice = gservice

# --- Spreadsheet IDs ---
st.subheader("スプレッドシート設定")
source_id = st.text_input("コピー元スプレッドシートID")
dest_id = st.text_input("コピー先スプレッドシートID")

# --- Copy Button ---
if st.button("A1セルをA1〜A10にコピー"):
    if "gservice" not in st.session_state:
        st.error("❌ 先にGoogleログインしてください。")
    elif not source_id or not dest_id:
        st.error("❌ スプレッドシートIDを入力してください。")
    else:
        copy_cell_format_and_value(
            st.session_state.gservice, source_id, dest_id
        )
