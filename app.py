import streamlit as st
import pandas as pd
from nomic import AtlasDataset
import gspread
from google.oauth2.service_account import Credentials
import io

# --- Streamlit Secrets ---
NOMIC_TOKEN = st.secrets["NOMIC_TOKEN"]
SERVICE_ACCOUNT = st.secrets["GOOGLE_SERVICE_ACCOUNT"]

# --- タイトル ---
st.title("🌏 Nomic → Google Sheets 連携デモ")

# --- 固定値 ---
MAP_NAME = "chizai-capcom-from-500"
DOMAIN = "atlas.nomic.ai"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iPnaVVdUSC5BfNdxPVRSZAOiaCYWcMDYQWs5ps3AJsk/edit?gid=0"

# --- 認証 ---
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT)
gc = gspread.authorize(creds)

try:
    st.info("🔄 Nomic Atlas からデータ取得中…")

    dataset = AtlasDataset(map_name=MAP_NAME, token=NOMIC_TOKEN, domain=DOMAIN)
    csv_data = dataset.export_data(format="csv")  # Nomicのエクスポート機能（仮想例）
    
    # pandasで読み込み
    df = pd.read_csv(io.StringIO(csv_data))

    st.success(f"✅ {len(df)}件のデータを取得しました！")

    # Google Sheets へアップロード
    sheet = gc.open_by_url(SHEET_URL).sheet1
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    st.success("📝 Googleスプレッドシートにデータを反映しました！")
    st.dataframe(df)

except Exception as e:
    st.error(f"⚠️ エラーが発生しました: {e}")
