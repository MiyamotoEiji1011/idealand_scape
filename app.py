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

map_data = None
df_metadata = None
df_topics = None
df_data = None

if st.button("Fetch Dataset"):
    if not token:
        st.error("❌ Please provide API token first.")
    else:
        try:
            nomic.login(token=token, domain=domain)
            dataset = AtlasDataset(map_name)
            map_data = dataset.maps[0]

            # --- Hold Data ---
            df_metadata = map_data.topics.metadata
            df_topics = map_data.topics.df
            df_data = map_data.data.df

            st.success(f"✅ Dataset fetched successfully! Metadata rows: {len(df_metadata)}, Topics rows: {len(df_topics)}, Data rows: {len(df_data)}")

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
# 3️⃣ Download CSVs for local backup
# =======================================
if map_data is not None:
    st.subheader("💾 Download Raw Data")
    if st.button("Download metadata CSV"):
        csv = df_metadata.to_csv(index=False)
        st.download_button("Download Metadata", csv, file_name="metadata.csv", mime="text/csv")
    if st.button("Download topics CSV"):
        csv = df_topics.to_csv(index=False)
        st.download_button("Download Topics", csv, file_name="topics.csv", mime="text/csv")
    if st.button("Download data CSV"):
        csv = df_data.to_csv(index=False)
        st.download_button("Download Data", csv, file_name="data.csv", mime="text/csv")

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


