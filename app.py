import json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urlparse, parse_qs

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
st.title("ユーザーのスプレッドシートに書き込みデモ")

sheet_url = st.text_input("スプレッドシートの URL を入力してください")
worksheet_name = st.text_input("ワークシート名 (タブ名)", value="Sheet1")
row_values = st.text_input("追加する行の値 (カンマ区切り)", value="A,B,C")

def get_spreadsheet_id(url):
    """
    スプレッドシートのURLからIDを取得
    """
    try:
        parsed = urlparse(url)
        if "spreadsheets" in parsed.path:
            return parsed.path.split("/d/")[1].split("/")[0]
        # fallback
        query = parse_qs(parsed.query)
        return query.get("id", [None])[0]
    except Exception:
        return None

if st.button("行を追加"):
    if not sheet_url:
        st.error("スプレッドシートの URL を入力してください")
    else:
        try:
            spreadsheet_id = get_spreadsheet_id(sheet_url)
            if not spreadsheet_id:
                st.error("URL からスプレッドシートIDを取得できませんでした")
            else:
                # スプレッドシート取得
                spreadsheet = client.open_by_key(spreadsheet_id)
                worksheet = spreadsheet.worksheet(worksheet_name)

                # 入力値をリストに変換
                values = [v.strip() for v in row_values.split(",")]

                # 末尾に追加
                worksheet.append_row(values)

                st.success(f"{values} を {worksheet_name} に追加しました！")
        except gspread.exceptions.WorksheetNotFound:
            st.error(f"ワークシート '{worksheet_name}' が見つかりません。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
