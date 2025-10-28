import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# =========================================================
# 🔑 Google Sheets認証
# =========================================================
def google_login():
    """Google Service Accountで認証"""
    try:
        service_account_info = json.loads(st.secrets["google_service_account"]["value"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        st.success("✅ Google Service Account Loaded Successfully!")
        return client
    except Exception as e:
        st.error(f"❌ Failed to load service account: {e}")
        return None


# =========================================================
# 📋 コピー処理
# =========================================================
def copy_a_column_data(client, source_id: str, dest_id: str):
    """スプレッドシート間でA列の1〜10行をコピー"""
    try:
        # コピー元とコピー先のシートを開く
        src_spreadsheet = client.open_by_key(source_id)
        dest_spreadsheet = client.open_by_key(dest_id)

        src_sheet = src_spreadsheet.sheet1
        dest_sheet = dest_spreadsheet.sheet1

        # A1〜A10のデータを取得
        data = src_sheet.get('A1:A10')

        if not data:
            st.warning("⚠️ コピー元にデータがありません。")
            return

        # コピー先に書き込み
        dest_sheet.update('A1', data)
        st.success("✅ コピー完了！A1〜A10をコピーしました。")

    except Exception as e:
        st.error(f"❌ コピーに失敗しました: {e}")


# =========================================================
# 🏗️ Streamlit UI
# =========================================================
st.title("Google Sheets Copy Tool")

# --- Google Login ---
if st.button("Google Login"):
    gclient = google_login()
    if gclient:
        st.session_state.gclient = gclient

# --- Spreadsheet IDs ---
st.subheader("スプレッドシート設定")
source_id = st.text_input("コピー元スプレッドシートID")
dest_id = st.text_input("コピー先スプレッドシートID")

# --- Copy Button ---
if st.button("A列をコピー"):
    if "gclient" not in st.session_state:
        st.error("❌ 先にGoogleログインしてください。")
    elif not source_id or not dest_id:
        st.error("❌ スプレッドシートIDを入力してください。")
    else:
        copy_a_column_data(st.session_state.gclient, source_id, dest_id)
