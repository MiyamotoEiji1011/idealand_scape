import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from gspread_dataframe import set_with_dataframe
from googleapiclient.discovery import build
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
# 🎨 テンプレートデザインを既存シートに反映（PASTE_FORMAT）
# =========================================================
def apply_template_format_to_existing_sheet(
    client: gspread.Client,
    template_spreadsheet_id: str,
    template_sheet_name: str,
    target_spreadsheet_id: str,
    target_sheet_name: str,
):
    """
    テンプレートシートのフォーマットを既存シートにPASTE_FORMATで上書き反映する。
    ※ データは変更されず、見た目のみテンプレートと統一される。
    """
    try:
        # Sheets APIクライアント生成
        service = build("sheets", "v4", credentials=client.auth)

        # シート情報取得
        tpl_ss = client.open_by_key(template_spreadsheet_id)
        tpl_ws = tpl_ss.worksheet(template_sheet_name)
        tgt_ss = client.open_by_key(target_spreadsheet_id)
        tgt_ws = tgt_ss.worksheet(target_sheet_name)

        # batchUpdateでテンプレートのフォーマットをコピー
        body = {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": tpl_ws.id,
                            "startRowIndex": 0,
                            "startColumnIndex": 0,
                        },
                        "destination": {
                            "sheetId": tgt_ws.id,
                            "startRowIndex": 0,
                            "startColumnIndex": 0,
                        },
                        "pasteType": "PASTE_FORMAT",
                        "pasteOrientation": "NORMAL",
                    }
                }
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=target_spreadsheet_id, body=body
        ).execute()

        st.success(f"✅ Template format from '{template_sheet_name}' applied to '{target_sheet_name}' successfully!")
        return tgt_ws

    except Exception as e:
        st.error(f"❌ Failed to apply template format: {e}")
        return None


# =========================================================
# 📊 データ反映処理
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
    1) テンプレートシートの書式を既存シートに反映（PASTE_FORMAT）
    2) そのシートにデータを書き込む
    """
    if client is None:
        st.error("❌ Google client not initialized.")
        return

    try:
        # 1) テンプレート書式を既存シートに適用
        worksheet = apply_template_format_to_existing_sheet(
            client=client,
            template_spreadsheet_id=template_spreadsheet_id,
            template_sheet_name=template_sheet_name,
            target_spreadsheet_id=spreadsheet_id,
            target_sheet_name=worksheet_name,
        )
        if worksheet is None:
            return

        # 2) Nomicデータを反映
        df_master = prepare_master_dataframe(map_data)
        worksheet.clear()
        set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)

        st.success("✅ Template format applied and data written successfully!")
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
spreadsheet_id = st.text_input("Target Spreadsheet ID", value="")
worksheet_name = st.text_input("Target Worksheet Name", value="シート1")

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

if st.button("Apply Template Format & Write Data"):
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
