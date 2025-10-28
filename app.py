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
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        service = build("sheets", "v4", credentials=creds)
        st.success("✅ Google Service Account Loaded Successfully!")
        return client, service
    except Exception as e:
        st.error(f"❌ Failed to load service account: {e}")
        return None, None


# =========================================================
# 📋 プルダウン設定＋フォーマットコピー
# =========================================================
def copy_cell_with_dropdown(service, source_id: str, dest_id: str):
    try:
        # ① コピー元のA1セルのdataValidationを取得
        src = service.spreadsheets().get(
            spreadsheetId=source_id,
            ranges=["シート1!A1"],
            fields="sheets.data.rowData.values.dataValidation",
            includeGridData=True
        ).execute()

        # データ検証ルールの取得
        validation = None
        try:
            validation = src["sheets"][0]["data"][0]["rowData"][0]["values"][0]["dataValidation"]
        except KeyError:
            st.warning("⚠️ コピー元A1にプルダウン設定がありません。")

        # ② 値とフォーマットをコピー
        requests = []
        for i in range(10):
            requests.append({
                "copyPaste": {
                    "source": {
                        "sheetId": 0,
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
            })

        # ③ プルダウン設定をA1〜A10に適用
        if validation:
            requests.append({
                "setDataValidation": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 0,
                        "endRowIndex": 10,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "rule": validation
                }
            })

        # ④ API実行
        service.spreadsheets().batchUpdate(
            spreadsheetId=dest_id, body={"requests": requests}
        ).execute()

        st.success("✅ プルダウン設定を含むセルコピーが完了しました！ (A1 → A1:A10)")

    except Exception as e:
        st.error(f"❌ コピーに失敗しました: {e}")


# =========================================================
# 🏗️ Streamlit UI
# =========================================================
st.title("プルダウン付きセルコピー ツール")

if st.button("Google Login"):
    gclient, gservice = google_login()
    if gclient:
        st.session_state.gclient = gclient
        st.session_state.gservice = gservice

st.subheader("スプレッドシート設定")
source_id = st.text_input("コピー元スプレッドシートID")
dest_id = st.text_input("コピー先スプレッドシートID")

if st.button("A1セルをA1〜A10にコピー（プルダウン付き）"):
    if "gservice" not in st.session_state:
        st.error("❌ 先にGoogleログインしてください。")
    elif not source_id or not dest_id:
        st.error("❌ スプレッドシートIDを入力してください。")
    else:
        copy_cell_with_dropdown(st.session_state.gservice, source_id, dest_id)
