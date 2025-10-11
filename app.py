import streamlit as st
import gspread
import pandas as pd
import os
from google.oauth2.service_account import Credentials
from nomic import AtlasDataset
import json

# ======================================
# 🔐 Secrets読み込み
# ======================================
SERVICE_ACCOUNT = st.secrets["google_service_account"]["value"]
NOMIC_TOKEN = st.secrets["nomic"]["token"]
DOMAIN = st.secrets["nomic"]["domain"]

SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT)

MAP_NAME = "chizai-capcom-from-500"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iPnaVVdUSC5BfNdxPVRSZAOiaCYWcMDYQWs5ps3AJsk/edit?gid=0#gid=0"

st.title("🧭 Nomic → Googleスプレッドシート 反映デモ")
st.write(f"対象マップ: `{MAP_NAME}`")

# ======================================
# 🔑 Google認証
# ======================================
try:
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO)
    gc = gspread.authorize(creds)
    st.success("✅ Googleサービスアカウント認証成功！")
except Exception as e:
    st.error(f"Google認証エラー: {e}")

# ======================================
# 🌐 Nomic API設定（CLI経由ではなく環境変数で）
# ======================================
os.environ["NOMIC_API_KEY"] = NOMIC_TOKEN
os.environ["NOMIC_DOMAIN"] = DOMAIN

# ======================================
# 🗺️ Nomic データ取得
# ======================================
if st.button("🔄 Nomicデータを取得"):
    try:
        dataset = AtlasDataset(MAP_NAME)
        map = dataset.maps[0]
        df_topics = map.topics.df

        st.session_state["df"] = df_topics
        st.success(f"✅ データ取得成功！ {len(df_topics)} 件のトピックを取得しました。")
        st.dataframe(df_topics.head())

    except Exception as e:
        st.error(f"データ取得エラー: {e}")

# ======================================
# 📊 スプレッドシートに反映
# ======================================
if "df" in st.session_state and st.button("📤 スプレッドシートに反映"):
    try:
        df = st.session_state["df"]
        sheet = gc.open_by_url(SHEET_URL).sheet1
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("📝 スプレッドシートにデータを反映しました！")
    except Exception as e:
        st.error(f"スプレッドシート更新エラー: {e}")
