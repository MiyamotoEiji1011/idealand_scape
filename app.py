import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from nomic import AtlasDataset
import io

# ======================================
# 🔐 Secretsから読み込み
# ======================================
SERVICE_ACCOUNT = st.secrets["google_service_account"]["value"]
NOMIC_TOKEN = st.secrets["nomic"]["token"]
DOMAIN = st.secrets["nomic"]["domain"]

# JSON文字列を辞書に変換
import json
SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT)

# ======================================
# ⚙️ 設定値
# ======================================
MAP_NAME = "chizai-capcom-from-500"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iPnaVVdUSC5BfNdxPVRSZAOiaCYWcMDYQWs5ps3AJsk/edit?gid=0"

st.title("🌏 Nomic → Google Sheets 連携デモ")
st.write("固定マップ:", MAP_NAME)
st.write("ドメイン:", DOMAIN)

# ======================================
# 🔑 Google認証
# ======================================
try:
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO)
    gc = gspread.authorize(creds)
    st.success("✅ Googleサービスアカウントの認証成功！")
except Exception as e:
    st.error(f"Google認証エラー: {e}")

# ======================================
# 📤 Nomicデータ取得
# ======================================
try:
    st.info("🔄 Nomic Atlas からデータ取得中…")
    dataset = AtlasDataset(map_name=MAP_NAME, token=NOMIC_TOKEN, domain=DOMAIN)
    
    # CSVデータのダウンロード
    csv_data = dataset.export_data(format="csv")  # Nomic SDKが対応している場合
    df = pd.read_csv(io.StringIO(csv_data))

    st.success(f"✅ Nomicから {len(df)} 件のデータを取得しました！")
    st.dataframe(df.head())
except Exception as e:
    st.error(f"Nomicデータ取得エラー: {e}")

# ======================================
# 📊 Googleスプレッドシート更新
# ======================================
if st.button("📤 スプレッドシートに反映"):
    try:
        sheet = gc.open_by_url(SHEET_URL).sheet1
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("📝 スプレッドシートに反映完了！")
    except Exception as e:
        st.error(f"スプレッドシート更新エラー: {e}")
