import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd

st.title("Nomic Atlas → Google Sheets Sync Demo")

# =======================================
# 1️⃣ Nomic Settings
# =======================================
st.subheader("🔑 Nomic Connection Settings")

# Load token from secrets
default_token = st.secrets.get("NOMIC_TOKEN", "")

token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

df_data = None

if st.button("Fetch Dataset"):
    if not token:
        st.error("❌ Please provide API token first.")
    else:
        try:
            nomic.login(token=token, domain=domain)
            dataset = AtlasDataset(map_name)
            map_data = dataset.maps[0]

            df_data = map_data.data.df

            st.success(f"✅ Dataset fetched successfully! Rows: {len(df_data)}")

        except Exception as e:
            st.error(f"❌ Failed to fetch dataset: {e}")

# =======================================
# 2️⃣ Google Sheets Settings
# =======================================
st.subheader("📄 Google Sheets Settings")

spreadsheet_id = st.text_input(
    "Spreadsheet ID",
    value="1iPnaVVdUSC5BfNdxPVRSZAOiaCYWcMDYQWs5ps3AJsk"
)

worksheet_name = st.text_input("Worksheet Name", value="シート1")

# Load service account credentials
try:
    service_account_info = json.loads(st.secrets["google_service_account"]["value"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    st.success("✅ Google Service Account Loaded Successfully!")
except Exception as e:
    st.error(f"❌ Failed to load service account: {e}")
    client = None

# =======================================
# 3️⃣ Write to Google Sheets
# =======================================
if st.button("Write to Google Sheets"):
    if client is None:
        st.error("❌ Google client not initialized.")
    elif df_data is None or df_data.empty:
        st.error("⚠️ No dataset loaded to write.")
    else:
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)

            # Clear existing content
            worksheet.clear()

            # Write DataFrame
            worksheet.update(
                [df_data.columns.values.tolist()] + df_data.values.tolist()
            )

            st.success("✅ Data successfully written to Google Sheets!")

        except Exception as e:
            st.error(f"❌ Failed to write to Google Sheets: {e}")
