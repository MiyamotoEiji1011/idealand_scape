import streamlit as st
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

st.title("🔍 Nomic Dataset → Google Sheets Exporter")

# === 入力フォーム ===
token = st.text_input("🔑 Nomic API Token", type="password")
dataset_name = st.text_input("📦 Dataset name (例: chizai-capcom-from-500)")

if st.button("🚀 データを取得してスプレッドシートに出力"):
    if not token or not dataset_name:
        st.error("トークンとデータセット名を入力してください！")
    else:
        try:
            with st.spinner("Nomic APIからデータを取得中..."):
                url = f"https://api.atlas.nomic.ai/v1/dataset/{dataset_name}"
                headers = {"Authorization": f"Bearer {token}"}
                res = requests.get(url, headers=headers)

                if res.status_code != 200:
                    st.error(f"APIエラー: {res.status_code}")
                    st.stop()

                data = res.json()
                df = pd.json_normalize(data)

            # === Google Sheetsに書き込み ===
            st.info("Googleスプレッドシートに書き込み中...")

            creds_dict = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )

            client = gspread.authorize(creds)

            sheet_title = f"NomicExport_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            spreadsheet = client.create(sheet_title)
            sheet = spreadsheet.sheet1

            # DataFrame → Sheet
            sheet.update([df.columns.values.tolist()] + df.values.tolist())

            # 公開設定
            spreadsheet.share(None, perm_type="anyone", role="reader")

            st.success("✅ スプレッドシートを作成しました！")
            st.write(f"[🔗 スプレッドシートを開く]({spreadsheet.url})")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
