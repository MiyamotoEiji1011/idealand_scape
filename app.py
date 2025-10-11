import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
import math

st.title("Nomic Atlas → Google Sheets Sync Demo (Safe for Large Data)")

# =======================================
# 1️⃣ Nomic Settings
# =======================================
st.subheader("🔑 Nomic Connection Settings")
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

            # 分割して取得
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
# 3️⃣ Write to Google Sheets (Chunked)
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
            worksheet.clear()  # 既存データ削除

            # chunk size を指定して分割書き込み
            chunk_size = 100  # 1回に書き込む行数
            total_rows = len(df_data)
            num_chunks = math.ceil(total_rows / chunk_size)

            progress_bar = st.progress(0)

            # 最初にヘッダー書き込み
            worksheet.update([df_data.columns.values.tolist()])

            for i in range(num_chunks):
                start = i * chunk_size
                end = min((i + 1) * chunk_size, total_rows)
                chunk_values = df_data.iloc[start:end].values.tolist()
                worksheet.append_rows(chunk_values)
                progress_bar.progress((i + 1) / num_chunks)

            st.success(f"✅ Data successfully written! Total rows: {total_rows}")

        except Exception as e:
            st.error(f"❌ Failed to write to Google Sheets: {e}")
