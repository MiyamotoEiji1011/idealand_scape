import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json


# =========================================================
# 🔑 Google 認証
# =========================================================
def google_login():
    try:
        service_account_info = json.loads(st.secrets["google_service_account"]["value"])
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        st.success("✅ Google認証成功")
        return client, creds
    except Exception as e:
        st.error(f"❌ 認証失敗: {e}")
        return None, None


# =========================================================
# 📊 表（Tables）情報の確認
# =========================================================
def list_tables(creds, spreadsheet_id):
    try:
        service = build("sheets", "v4", credentials=creds)
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()

        if "sheets" not in meta:
            st.warning("⚠️ シート情報が取得できませんでした。")
            return

        for sheet in meta["sheets"]:
            title = sheet["properties"]["title"]
            sheet_id = sheet["properties"]["sheetId"]
            tables = sheet.get("basicFilter", None)
            st.write(f"🧾 シート名: {title}, ID: {sheet_id}")
            if tables:
                st.write("　┗ 既存 BasicFilter（旧式フィルター）あり。")
            else:
                st.write("　┗ BasicFilterなし or 新しいTables機能の可能性。")

    except HttpError as he:
        st.error(f"❌ HTTPエラー: {he}")
    except Exception as e:
        st.error(f"❌ list_tables中のエラー: {e}")


# =========================================================
# 🔧 BasicFilter設定をテスト的に追加 or 削除
# =========================================================
def test_set_basic_filter(creds, spreadsheet_id, sheet_name, rows=50, cols=20):
    try:
        service = build("sheets", "v4", credentials=creds)

        # sheetIdを取得
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = next(s["properties"]["sheetId"] for s in meta["sheets"] if s["properties"]["title"] == sheet_name)

        # 既存フィルターをクリア
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"clearBasicFilter": {"sheetId": sheet_id}}]},
        ).execute()

        # 新規フィルター設定を試す
        reqs = [{
            "setBasicFilter": {
                "filter": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": rows,
                        "startColumnIndex": 0,
                        "endColumnIndex": cols,
                    }
                }
            }
        }]

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": reqs}).execute()
        st.success(f"✅ フィルターを再設定しました (範囲: A1〜{cols}, 行数: {rows})")

    except HttpError as he:
        if "partially intersects a table" in str(he):
            st.warning("⚠️ 新しい '表 (Tables)' が存在しているため BasicFilter の再設定が禁止されています。")
        else:
            st.error(f"❌ APIエラー: {he}")
    except Exception as e:
        st.error(f"❌ test_set_basic_filter中のエラー: {e}")


# =========================================================
# 🧭 Streamlit UI
# =========================================================
st.title("🧪 Google Sheets Table Test")

spreadsheet_id = st.text_input("📄 スプレッドシートIDを入力")
sheet_name = st.text_input("🧾 シート名を入力", value="シート1")

if st.button("Google認証"):
    gclient, creds = google_login()
    if gclient:
        st.session_state.gclient = gclient
        st.session_state.creds = creds

if st.button("表の状態を確認"):
    if "creds" not in st.session_state:
        st.error("❌ まずGoogleログインしてください。")
    else:
        list_tables(st.session_state.creds, spreadsheet_id)

if st.button("BasicFilterを再設定してみる"):
    if "creds" not in st.session_state:
        st.error("❌ まずGoogleログインしてください。")
    else:
        test_set_basic_filter(st.session_state.creds, spreadsheet_id, sheet_name)
