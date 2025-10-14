import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from gspread_dataframe import set_with_dataframe
from gspread_formatting import CellFormat, format_cell_range, TextFormat
from data_processing import prepare_master_dataframe

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
# 📊 Google Sheets書き込み処理
# =========================================================

def format_sheet_header_bold(worksheet, df):
    if df.empty:
        return

    num_cols = len(df.columns)

    # 1行目の最後の列を取得（A-Z, AA, AB対応）
    if num_cols <= 26:
        last_col_letter = chr(64 + num_cols)
    else:
        last_col_letter = ""
        n = num_cols
        while n > 0:
            n, remainder = divmod(n-1, 26)
            last_col_letter = chr(65 + remainder) + last_col_letter

    # まず全体を通常書式に戻す
    total_range = f"A1:{last_col_letter}{worksheet.row_count}"
    normal_format = CellFormat(textFormat=TextFormat(bold=False))
    format_cell_range(worksheet, total_range, normal_format)

    # 1行目だけ太字にする
    header_range = f"A1:{last_col_letter}1"
    header_format = CellFormat(textFormat=TextFormat(bold=True))
    format_cell_range(worksheet, header_range, header_format)


def write_to_google_sheet(client, spreadsheet_id: str, worksheet_name: str, map_data):
    """Googleスプレッドシートにデータを書き込む"""
    if client is None:
        st.error("❌ Google client not initialized.")
        return

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        df_master = prepare_master_dataframe(map_data)

        worksheet.clear()
        set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)
        format_sheet_header_bold(worksheet, df_master)

        st.success("✅ Successfully wrote data to Google Sheet!")
    except Exception as e:
        st.error(f"❌ Failed to write sheet: {e}")


# =========================================================
# 🏗️ Streamlit UI構築
# =========================================================
st.title("Demo App")

# --- Nomic Atlas Settings ---
st.subheader("Nomic Atlas Settings")
default_token = st.secrets.get("NOMIC_TOKEN", "")
token = st.text_input("API Token", value="", type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="")

# --- Google Sheets Settings ---
st.subheader("Google Sheets Settings")
spreadsheet_id = st.text_input("Spreadsheet ID", value="")
worksheet_name = st.text_input("Worksheet Name", value="シート1")

# --- Buttons ---
if st.button("Fetch Nomic Dataset"):
    map_data = fetch_nomic_dataset(token, domain, map_name)
    if map_data:
        st.session_state.map_data = map_data

if st.button("Google Login"):
    gclient = google_login()
    if gclient:
        st.session_state.gclient = gclient

if st.button("Create / Update Google Sheet"):
    if "map_data" not in st.session_state:
        st.error("❌ Please fetch the Nomic dataset first.")
    elif "gclient" not in st.session_state:
        st.error("❌ Please log in to Google first.")
    else:
        write_to_google_sheet(
            st.session_state.gclient,
            spreadsheet_id,
            worksheet_name,
            st.session_state.map_data,
        )
