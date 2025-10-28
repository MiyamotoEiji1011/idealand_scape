import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from gspread_dataframe import set_with_dataframe
from data_processing import prepare_master_dataframe
import requests
import time


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
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        st.success("✅ Google Service Account Loaded Successfully!")
        return client
    except Exception as e:
        st.error(f"❌ Failed to load service account: {e}")
        return None


# =========================================================
# 📊 Google Sheetsへデータ書き込みのみ
# =========================================================
def write_to_google_sheet(client, spreadsheet_id: str, worksheet_name: str, map_data):
    """Googleスプレッドシートにデータのみ書き込む"""
    if client is None:
        st.error("❌ Google client not initialized.")
        return False

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        df_master = prepare_master_dataframe(map_data)

        worksheet.clear()
        set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)

        st.success("✅ Data successfully written to Google Sheet!")
        return True

    except Exception as e:
        st.error(f"❌ Failed to write sheet: {e}")
        return False


# =========================================================
# 🚀 GAS呼び出し処理
# =========================================================
def trigger_gas_dropdown_api(sheet_name: str, spreadsheet_id: str, gas_endpoint: str):
    """3分後にGASを呼び出してプルダウンUIを適用"""
    st.info("⏳ Waiting 3 minutes before calling GAS...")
    time.sleep(180)  # 3分待機

    try:
        payload = {
            "sheet_name": sheet_name,
            "spreadsheet_id": spreadsheet_id,
        }
        response = requests.post(gas_endpoint, data=payload, timeout=30)
        if response.status_code == 200:
            st.success("✅ GAS successfully triggered for dropdown setup!")
        else:
            st.warning(f"⚠️ GAS returned status {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"❌ Failed to call GAS: {e}")


# =========================================================
# 🏗️ Streamlit UI構築
# =========================================================
st.title("🧩 Dataset → Google Sheets Automation (No Design)")

# --- Nomic Atlas Settings ---
st.subheader("Nomic Atlas Settings")
default_token = st.secrets.get("NOMIC_TOKEN", "")
token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# --- Google Sheets Settings ---
st.subheader("Google Sheets Settings")
spreadsheet_id = st.text_input(
    "Spreadsheet ID", value="1XDAGnEjY8XpDC9ohtaHgo4ECZG8OgNUNJo-ZrCksRDI"
)
worksheet_name = st.text_input("Worksheet Name", value="シート1")

# --- GAS Settings ---
st.subheader("Apps Script Settings")
gas_endpoint = st.text_input(
    "GAS Web App URL",
    value="https://script.google.com/macros/s/AKfycbEXAMPLE_ID/exec",
    help="GASをWebアプリとしてデプロイしたURLを入力してください",
)

# --- Buttons ---
if st.button("Fetch Nomic Dataset"):
    map_data = fetch_nomic_dataset(token, domain, map_name)
    if map_data:
        st.session_state.map_data = map_data

if st.button("Google Login"):
    gclient = google_login()
    if gclient:
        st.session_state.gclient = gclient

if st.button("Create Sheet and Call GAS"):
    if "map_data" not in st.session_state:
        st.error("❌ Please fetch the Nomic dataset first.")
    elif "gclient" not in st.session_state:
        st.error("❌ Please log in to Google first.")
    else:
        success = write_to_google_sheet(
            st.session_state.gclient,
            spreadsheet_id,
            worksheet_name,
            st.session_state.map_data,
        )
        if success and gas_endpoint:
            trigger_gas_dropdown_api(worksheet_name, spreadsheet_id, gas_endpoint)
