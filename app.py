import json
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Nomic 関連インポート ---
from nomic import AtlasDataset, cli  # こういう形で使えるはず

# ------------------------------
# サービスアカウントでの認証
# ------------------------------
service_account_info = json.loads(st.secrets["google_service_account"]["value"])
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
sheets_service = build("sheets", "v4", credentials=creds)
sheet_api = sheets_service.spreadsheets()

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("Nomic → スプレッドシート反映アプリ")

# Nomic API や対象データ入力
nomic_token = st.text_input("Nomic API トークン", type="password")
nomic_domain = st.text_input("Nomic ドメイン (例: atlas.nomic.ai)")
dataset_name = st.text_input("データセット名 (map 名もこの中)", value="chizai-capcom-from-500")
map_index = st.number_input("マップ番号 (0 から始まる)", min_value=0, step=1)

# スプレッドシート反映用
sheet_url = st.text_input("反映先スプレッドシートの URL")
worksheet_name = st.text_input("ワークシート名 (タブ名)", value="Sheet1")

# ボタン①：データ取得
if st.button("データを取得"):
    try:
        # Nomic にログイン
        cli.login(token=nomic_token, domain=nomic_domain)
        dataset = AtlasDataset(dataset_name)
        atlas_map = dataset.maps[map_index]
        # データフレーム（topics や map.data など、利用したい属性による）
        df = atlas_map.topics.df  # 例：topic データを取得
        st.dataframe(df)
        # 保存しておく（セッションステートに）
        st.session_state["nomic_df"] = df
        st.success("データ取得成功！")
    except Exception as e:
        st.error(f"Nomic データ取得でエラー: {e}")

# ボタン②：スプレッドシートに反映
if st.button("スプレッドシートに反映"):
    if "nomic_df" not in st.session_state:
        st.error("まず「データを取得」を押してください")
    else:
        try:
            df = st.session_state["nomic_df"]
            # URL からスプレッドシートID を抜き出す関数
            def get_spreadsheet_id(url):
                import re
                m = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
                return m.group(1) if m else None

            spreadsheet_id = get_spreadsheet_id(sheet_url)
            if spreadsheet_id is None:
                st.error("スプレッドシート URL から ID を取得できませんでした")
            else:
                # 書き込む範囲を自動で決める（たとえばタブ名 + “!A1”）
                range_name = f"{worksheet_name}!A1"
                # DataFrame をリストのリストに変換
                values = [df.columns.tolist()] + df.values.tolist()
                body = {"values": values}

                request = sheet_api.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body
                )
                response = request.execute()
                st.success("スプレッドシート反映完了！")
                st.json(response)
        except HttpError as he:
            st.error(f"Sheets API エラー: {he}")
        except Exception as e:
            st.error(f"反映処理でエラー: {e}")
