import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from gspread_dataframe import set_with_dataframe
from data_processing import prepare_master_dataframe

# =========================================================
# 🌍 Nomic Atlasデータ取得
# =========================================================
def fetch_nomic_dataset(token: str, domain: str, map_name: str):
    """Nomic Atlasからデータセットを取得"""
    if not token:
        st.error("❌ Please provide API token first.")
        return None

    try:
        nomic.login(token=token, domain=domain)
        dataset = AtlasDataset(map_name)
        st.success("✅ Dataset fetched successfully!")
        return dataset.maps[0]
    except Exception as e:
        st.error(f"❌ Failed to fetch dataset: {e}")
        return None


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
# 🧱 テンプレートコピー
# =========================================================
def _find_worksheet_by_id(spreadsheet: gspread.Spreadsheet, sheet_id: int):
    """worksheet.id を見て一致するワークシートを返す（互換用）"""
    for ws in spreadsheet.worksheets():
        if ws.id == sheet_id:
            return ws
    return None

def copy_template_to_target(
    client: gspread.Client,
    template_spreadsheet_id: str,
    template_sheet_name: str,
    target_spreadsheet_id: str,
    target_sheet_name: str,
):
    """
    テンプレートSS内の指定シートを、ターゲットSSへコピーして target_sheet_name にリネーム。
    既に同名シートがあれば削除してから差し替え。
    戻り値: コピー後の gspread.Worksheet
    """
    # テンプレート取得
    tpl_ss = client.open_by_key(template_spreadsheet_id)
    try:
        tpl_ws = tpl_ss.worksheet(template_sheet_name)
    except Exception as e:
        st.error(f"❌ Template sheet not found: {template_sheet_name} ({e})")
        return None

    # ターゲット取得
    tgt_ss = client.open_by_key(target_spreadsheet_id)

    # 既存の同名シートがあれば削除
    try:
        old = tgt_ss.worksheet(target_sheet_name)
        tgt_ss.del_worksheet(old)
    except gspread.exceptions.WorksheetNotFound:
        pass  # 無ければOK

    # テンプレをターゲットへコピー
    resp = tpl_ws.copy_to(target_spreadsheet_id)  # dict {sheetId: int, ...}
    new_sheet_id = resp.get("sheetId")
    if new_sheet_id is None:
        st.error("❌ Failed to copy template sheet (no sheetId returned).")
        return None

    # コピーされたシートを取得してリネーム
    new_ws = _find_worksheet_by_id(tgt_ss, new_sheet_id)
    if new_ws is None:
        st.error("❌ Copied sheet not found in target spreadsheet.")
        return None

    new_ws.update_title(target_sheet_name)
    return new_ws


# =========================================================
# 📊 データ反映（装飾ナシ）
# =========================================================
def write_to_google_sheet(
    client,
    spreadsheet_id: str,
    worksheet_name: str,
    map_data,
    template_spreadsheet_id: str,
    template_sheet_name: str,
):
    """
    1) テンプレートシートをコピーしてターゲットに適用
    2) そのシートへデータを書き込む
    """
    if client is None:
        st.error("❌ Google client not initialized.")
        return

    try:
        # 1) テンプレートコピー
        worksheet = copy_template_to_target(
            client=client,
            template_spreadsheet_id=template_spreadsheet_id,
            template_sheet_name=template_sheet_name,
            target_spreadsheet_id=spreadsheet_id,
            target_sheet_name=worksheet_name,
        )
        if worksheet is None:
            return

        # 2) データ生成 & 反映
        df_master = prepare_master_dataframe(map_data)

        # テンプレートの既存データ領域をクリア（必要なら）
        worksheet.clear()

        # 見出し込みでA1から書き込み
        set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)

        st.success("✅ Template copied and data written successfully!")
    except Exception as e:
        st.error(f"❌ Failed to write sheet: {e}")


# =========================================================
# 🏗️ Streamlit UI構築
# =========================================================
st.title("Demo App")

# --- Nomic Atlas Settings ---
st.subheader("Nomic Atlas Settings")
default_token = st.secrets.get("NOMIC_TOKEN", "")
token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# --- Google Sheets Settings ---
st.subheader("Google Sheets Settings")
# 出力先
spreadsheet_id = st.text_input("Target Spreadsheet ID", value="")  # 例: 出力先
worksheet_name = st.text_input("Target Worksheet Name", value="シート1")

# テンプレート
template_spreadsheet_id = st.text_input("Template Spreadsheet ID", value="1DJbrC0fGpVcPrHrTlDyzTZdt2K1lmm_2QJJVI8fqoIY")
template_sheet_name = st.text_input("Template Sheet Name", value="Template")

# --- Buttons ---
if st.button("Fetch Nomic Dataset"):
    map_data = fetch_nomic_dataset(token, domain, map_name)
    if map_data:
        st.session_state.map_data = map_data

if st.button("Google Login"):
    gclient = google_login()
    if gclient:
        st.session_state.gclient = gclient

if st.button("Copy Template & Write Data"):
    if "map_data" not in st.session_state:
        st.error("❌ Please fetch the Nomic dataset first.")
    elif "gclient" not in st.session_state:
        st.error("❌ Please log in to Google first.")
    elif not template_spreadsheet_id or not template_sheet_name:
        st.error("❌ Please set template spreadsheet & sheet.")
    else:
        write_to_google_sheet(
            client=st.session_state.gclient,
            spreadsheet_id=spreadsheet_id,
            worksheet_name=worksheet_name,
            map_data=st.session_state.map_data,
            template_spreadsheet_id=template_spreadsheet_id,
            template_sheet_name=template_sheet_name,
        )
