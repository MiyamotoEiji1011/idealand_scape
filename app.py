import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from gspread_dataframe import set_with_dataframe


# =========================================================
# 🧩 Nomic Atlas関連処理
# =========================================================
def fetch_nomic_dataset(token: str, domain: str, map_name: str):
    """Nomic Atlasからデータセットを取得する"""
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
def write_to_google_sheet(client, spreadsheet_id: str, worksheet_name: str, map_data):
    """Googleスプレッドシートにデータを書き込む"""
    if client is None:
        st.error("❌ Google client not initialized.")
        return

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # メタデータの抽出
        df_metadata = map_data.topics.metadata

        # カラム構造を定義
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

        # データフレームを作成
        df_master = pd.DataFrame(columns=columns)
        df_master["depth"] = df_metadata["depth"].astype(str)
        df_master["topic_id"] = df_metadata["topic_id"].astype(str)
        df_master["Nomic Topic: Broad"] = df_metadata["topic_depth_1"].astype(str)
        df_master["Nomic Topic: Medium"] = df_metadata["topic_depth_2"].astype(str)
        df_master["キーワード"] = df_metadata["topic_description"].astype(str)

        # シートに書き込み
        worksheet.clear()
        set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)
        st.success("✅ Successfully wrote data to Google Sheet!")
    except Exception as e:
        st.error(f"❌ Failed to write sheet: {e}")


# =========================================================
# treamlit UI構築
# =========================================================
st.title("Nomic Atlas → Google Sheets Sync Demo (Data Hold & Export)")

# --- Nomic Atlas Settings ---
st.subheader("Nomic Atlas Settings")
default_token = st.secrets.get("NOMIC_TOKEN", "")
token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# --- Google Sheets Settings ---
st.subheader("Google Sheets Settings")
spreadsheet_id = st.text_input("Spreadsheet ID", value="1iPnaVVdUSC5BfNdxPVRSZAOiaCYWcMDYQWs5ps3AJsk")
worksheet_name = st.text_input("Worksheet Name", value="シート1")

# --- Buttons ---
if st.button("🔍 Fetch Nomic Dataset"):
    map_data = fetch_nomic_dataset(token, domain, map_name)
    if map_data:
        st.session_state.map_data = map_data

if st.button("🔑 Google Login"):
    gclient = google_login()
    if gclient:
        st.session_state.gclient = gclient

if st.button("📤 Create / Update Google Sheet"):
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
