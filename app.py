import json
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from nomic import AtlasDataset, cli

# ------------------------
# サービスアカウント認証
# ------------------------
service_account_info = json.loads(st.secrets["google_service_account"]["value"])
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

sheets_service = build("sheets", "v4", credentials=creds)
sheet_api = sheets_service.spreadsheets()

# ------------------------
# 固定設定（デモ用）
# ------------------------
NOMIC_TOKEN = st.secrets["nomic"]["token"]  # ← secrets.tomlに保存する想定
NOMIC_DOMAIN = "atlas.nomic.ai"
DATASET_NAME = "chizai-capcom-from-500"

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1iPnaVVdUSC5BfNdxPVRSZAOiaCYWcMDYQWs5ps3AJsk/edit?gid=0"
SHEET_NAME = "Sheet1"

# ------------------------
# Streamlit UI
# ------------------------
st.title("🔗 Nomic → Googleスプレッドシート 連携デモ")

st.write("Nomicのデータセット `chizai-capcom-from-500` を取得して、指定のスプレッドシートに反映します。")

# ==============================
# STEP 1. Nomicデータ取得
# ==============================
if st.button("① Nomicデータを取得"):
    try:
        cli.login(token=NOMIC_TOKEN, domain=NOMIC_DOMAIN)
        dataset = AtlasDataset(DATASET_NAME)
        atlas_map = dataset.maps[0]
        df = atlas_map.topics.df

        st.session_state["nomic_df"] = df
        st.success(f"データ取得成功！ {len(df)}件の行を取得しました。")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"データ取得エラー: {e}")

# ==============================
# STEP 2. スプレッドシート反映
# ==============================
if st.button("② スプレッドシートに反映"):
    if "nomic_df" not in st.session_state:
        st.warning("先に『① Nomicデータを取得』を押してください。")
    else:
        try:
            df = st.session_state["nomic_df"]

            # スプレッドシートID抽出
            import re
            m = re.search(r"/d/([a-zA-Z0-9-_]+)", SPREADSHEET_URL)
            spreadsheet_id = m.group(1)

            # 書き込みデータ準備
            values = [df.columns.tolist()] + df.astype(str).values.tolist()
            body = {"values": values}

            # 書き込み実行
            range_name = f"{SHEET_NAME}!A1"
            request = sheet_api.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            )
            response = request.execute()

            st.success("スプレッドシートへの反映が完了しました✨")
            st.json(response)
        except HttpError as he:
            st.error(f"Google Sheets APIエラー: {he}")
        except Exception as e:
            st.error(f"書き込み時エラー: {e}")
