import streamlit as st
import pandas as pd
from modules.google_utils import init_gspread, clear_and_init_sheet, write_metadata_to_sheet
from modules.nomic_utils import fetch_nomic_dataset
from modules.data_utils import create_master_dataframe

st.title("Nomic Atlas → Google Sheets Sync Demo (Modular Version)")

# =======================================
# 1️⃣ Settings
# =======================================
st.subheader("🔑 Connection Settings")

# Nomic
token = st.text_input("API Token", type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# Google Sheets
spreadsheet_id = st.text_input("Spreadsheet ID", value="xxxxxx")
worksheet_name = st.text_input("Worksheet Name", value="シート1")

# =======================================
# 2️⃣ Load Google Client
# =======================================
client = init_gspread(st)

# =======================================
# 3️⃣ Buttons
# =======================================
if st.button("Fetch Dataset"):
    fetch_nomic_dataset(st, token, domain, map_name)

df_master = create_master_dataframe()

if st.button("Clear & Initialize Sheet"):
    clear_and_init_sheet(st, client, spreadsheet_id, worksheet_name, df_master)

if st.button("Write Metadata to Sheet"):
    write_metadata_to_sheet(st, client, spreadsheet_id, worksheet_name, df_master)
