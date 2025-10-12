import streamlit as st
import pandas as pd
import json
from google_utils import init_gspread, clear_and_init_sheet, write_metadata_to_sheet
from nomic_utils import fetch_nomic_dataset
from data_utils import create_master_dataframe

st.title("Nomic Atlas → Google Sheets Sync Demo (with Secrets)")

# =======================================
# 1️⃣ Load Secrets
# =======================================
# NOMIC Token（自動入力）
try:
    default_token = st.secrets["NOMIC_TOKEN"]
except KeyError:
    default_token = ""

# Googleサービスアカウント（JSON文字列 → dict変換）
try:
    google_service_info = json.loads(st.secrets["google_service_account"]["value"])
except KeyError:
    google_service_info = None

# =======================================
# 2️⃣ Settings UI
# =======================================
st.subheader("🔑 Connection Settings")

# Nomic
token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# Google Sheets
spreadsheet_id = st.text_input("Spreadsheet ID", value="1iPnaVVdUSC5BfNdxPVRSZAOiaCYWcMDYQWs5ps3AJsk")
worksheet_name = st.text_input("Worksheet Name", value="シート1")

# =======================================
# 3️⃣ Initialize Google Client
# =======================================
client = init_gspread(st, google_service_info)

# =======================================
# 4️⃣ Buttons
# =======================================
if st.button("Fetch Dataset"):
    fetch_nomic_dataset(st, token, domain, map_name)

df_master = create_master_dataframe()

if st.button("Clear & Initialize Sheet"):
    clear_and_init_sheet(st, client, spreadsheet_id, worksheet_name, df_master)

if st.button("Write Metadata to Sheet"):
    write_metadata_to_sheet(st, client, spreadsheet_id, worksheet_name, df_master)
