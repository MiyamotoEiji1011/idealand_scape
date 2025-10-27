# app.py
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ==============================
# 🔐 Google 認証（Service Account）
# ==============================
def google_login():
    try:
        info = json.loads(st.secrets["google_service_account"]["value"])
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        st.success("✅ Google Service Account Loaded Successfully!")
        return client
    except Exception as e:
        st.error(f"❌ Failed to load service account: {e}")
        return None

# ============================================
# 📄 コピー元シート → コピー先に反映（置き換え）
# ============================================
def copy_template_sheet_to_target(
    client: gspread.Client,
    template_spreadsheet_id: str,
    template_sheet_name: str,
    target_spreadsheet_id: str,
    target_sheet_name: str,
):
    """
    1) テンプレートSS内の指定シートをコピーしてターゲットSSへ追加
    2) ターゲットSSに同名のシートがあれば削除
    3) コピーしたシートを target_sheet_name にリネーム
    """
    try:
        # コピー元
        tpl_ss = client.open_by_key(template_spreadsheet_id)
        tpl_ws = tpl_ss.worksheet(template_sheet_name)

        # まずコピーを作る（←これで「最後の1枚を削除できない」問題を回避）
        copied_info = tpl_ws.copy_to(target_spreadsheet_id)  # returns {"sheetId": ...}
        new_sheet_id = copied_info.get("sheetId")
        if not new_sheet_id:
            st.error("❌ Failed to copy template sheet (no sheetId returned).")
            return None

        # コピー先
        tgt_ss = client.open_by_key(target_spreadsheet_id)

        # 既存の同名シートがあれば削除（この時点ではシートが2枚以上あるので安全に削除可）
        try:
            old_ws = tgt_ss.worksheet(target_sheet_name)
            tgt_ss.del_worksheet(old_ws)
        except gspread.exceptions.WorksheetNotFound:
            pass  # 無ければスキップ

        # 追加されたシートを取得してリネーム
        new_ws = None
        for ws in tgt_ss.worksheets():
            if ws.id == new_sheet_id:
                new_ws = ws
                break

        if new_ws is None:
            st.error("❌ Copied sheet not found in target spreadsheet.")
            return None

        new_ws.update_title(target_sheet_name)
        st.success(f"✅ Copied '{template_sheet_name}' → '{target_sheet_name}'")
        return new_ws

    except Exception as e:
        st.error(f"❌ Failed to copy/replace sheet: {e}")
        return None

# ============
# 🧪 UI
# ============
st.title("Sheet Copier (テンプレ反映だけ版)")

st.subheader("Google Login")
if st.button("Google Login"):
    gclient = google_login()
    if gclient:
        st.session_state.gclient = gclient

st.subheader("Copy Settings")
template_spreadsheet_id = st.text_input("Template Spreadsheet ID", value="")
template_sheet_name     = st.text_input("Template Sheet Name", value="Template")
target_spreadsheet_id   = st.text_input("Target Spreadsheet ID", value="")
target_sheet_name       = st.text_input("Target Sheet Name", value="シート1")

if st.button("Copy → Reflect to Target"):
    if "gclient" not in st.session_state:
        st.error("❌ Please log in first.")
    elif not (template_spreadsheet_id and template_sheet_name and target_spreadsheet_id and target_sheet_name):
        st.error("❌ Please fill all fields.")
    else:
        copy_template_sheet_to_target(
            client=st.session_state.gclient,
            template_spreadsheet_id=template_spreadsheet_id,
            template_sheet_name=template_sheet_name,
            target_spreadsheet_id=target_spreadsheet_id,
            target_sheet_name=target_sheet_name,
        )
