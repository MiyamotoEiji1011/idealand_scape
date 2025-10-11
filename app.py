import json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------
# サービスアカウント認証
# ------------------------
service_account_info = json.loads(st.secrets["google_service_account"]["value"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)

client = gspread.authorize(creds)

# ------------------------
# Streamlit UI
# ------------------------
st.title("既存スプレッドシート 書き込みデモ")

spreadsheet_name = st.text_input("スプレッドシート名", value="Your Spreadsheet Name")
worksheet_name = st.text_input("ワークシート名", value="Sheet1")
row_values = st.text_input("追加する行の値 (カンマ区切り)", value="A,B,C")

if st.button("行を追加"):
    try:
        # スプレッドシートとワークシートを取得
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # 入力値をリストに変換
        values = [v.strip() for v in row_values.split(",")]

        # 末尾に追加
        worksheet.append_row(values)

        st.success(f"{values} を {worksheet_name} に追加しました！")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
