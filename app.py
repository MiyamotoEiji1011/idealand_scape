import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from gspread_dataframe import set_with_dataframe

st.title("Nomic Atlas → Google Sheets Sync Demo (Data Hold & Export)")

# =======================================
# 1️⃣ Nomic Settings
# =======================================
st.subheader("🔑 Nomic Connection Settings")

default_token = st.secrets.get("NOMIC_TOKEN", "")
token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

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
if "gclient" not in st.session_state:
    try:
        service_account_info = json.loads(st.secrets["google_service_account"]["value"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        st.session_state.gclient = gspread.authorize(creds)
        st.success("✅ Google Service Account Loaded Successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load service account: {e}")
        st.session_state.gclient = None

# =======================================
# 3️⃣ Fetch Dataset from Nomic Atlas
# =======================================
if st.button("Fetch Dataset"):
    if not token:
        st.error("❌ Please provide API token first.")
    else:
        try:
            nomic.login(token=token, domain=domain)
            dataset = AtlasDataset(map_name)
            st.session_state.map_data = dataset.maps[0]
            st.success("✅ Dataset fetched successfully!")
        except Exception as e:
            st.error(f"❌ Failed to fetch dataset: {e}")

# =======================================
# 4️⃣ Prepare empty DataFrame for Google Sheets
# =======================================
columns = [
    "depth", "topic_id", "Nomic Topic: Broad", "Nomic Topic: Medium", "キーワード",
    "アイデア数", "平均スコア", "新規性平均スコア", "市場性平均スコア", "実現性平均スコア",
    "優秀アイデア数(12点以上)", "優秀アイデアの比率(12点以上)",
    "novelty_score(新規性)平均スコア", "novelty_score(新規性)優秀アイデア数(4点以上)",
    "novelty_score(新規性)優秀アイデア比率(4点以上)",
    "feasibility_score(実現可能性)平均スコア", "feasibility_score(実現可能性)優秀アイデア数(4点以上)",
    "feasibility_score(実現可能性)優秀アイデア比率(4点以上)",
    "marketability_score(市場性)平均スコア", "marketability_score(市場性)優秀アイデア数(4点以上)",
    "marketability_score(市場性)優秀アイデア比率(4点以上)",
    "アイデア名", "Summary", "カテゴリー", "合計スコア", "新規性スコア", "市場性スコア", "実現性スコア"
]
df_master = pd.DataFrame(columns=columns)

# =======================================
# 5️⃣ Initialize Google Sheet
# =======================================
st.subheader("📝 Initialize Google Sheet")
if st.button("Clear & Initialize Sheet"):
    client = st.session_state.gclient
    if client is None:
        st.error("❌ Google client not initialized.")
    else:
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            worksheet.clear()
            set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)
            st.success("✅ Google Sheet cleared and initialized with column headers!")
        except Exception as e:
            st.error(f"❌ Failed to initialize Google Sheet: {e}")

# =======================================
# 6️⃣ Write Metadata to Google Sheet
# =======================================
st.subheader("📤 Write Metadata to Google Sheet")
if st.button("Write Metadata to Sheet"):
    client = st.session_state.gclient
    if client is None:
        st.error("❌ Google client not initialized.")
    elif "map_data" not in st.session_state:
        st.error("⚠️ No dataset loaded yet. Please fetch dataset first.")
    else:
        try:
            map_data = st.session_state.map_data
            df_metadata = map_data.topics.metadata

            df_master["depth"] = df_metadata["depth"].astype(str)
            df_master["topic_id"] = df_metadata["topic_id"].astype(str)
            df_master["Nomic Topic: Broad"] = df_metadata["topic_depth_1"].astype(str)
            df_master["Nomic Topic: Medium"] = df_metadata["topic_depth_2"].astype(str)
            df_master["キーワード"] = df_metadata["topic_description"].astype(str)

            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            worksheet.clear()
            set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)
            st.success("✅ Metadata successfully written to Google Sheet!")
        except Exception as e:
            st.error(f"❌ Failed to write metadata: {e}")
