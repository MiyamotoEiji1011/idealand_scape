# app.py
import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gspread_dataframe import set_with_dataframe
import json
import pandas as pd
from data_processing import prepare_master_dataframe


# =========================================================
# 🌍 Nomic Atlasデータ取得
# =========================================================
def fetch_nomic_dataset(token: str, domain: str, map_name: str):
    """Nomic Atlasからデータセットを取得"""
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
        sa_info = json.loads(st.secrets["google_service_account"]["value"])
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_info, scope)
        client = gspread.authorize(creds)
        st.success("✅ Google Service Account Loaded Successfully!")
        return client, creds
    except Exception as e:
        st.error(f"❌ Failed to load service account: {e}")
        return None, None


# =========================================================
# 🧱 テンプレートシートをターゲットへコピー
# =========================================================
def copy_template_sheet_to_target(
    client: gspread.Client,
    template_spreadsheet_id: str,
    template_sheet_name: str,
    target_spreadsheet_id: str,
    target_sheet_name: str,
):
    """テンプレートシートを別スプレッドシートにコピーして置き換え"""
    try:
        tpl_ss = client.open_by_key(template_spreadsheet_id)
        tpl_ws = tpl_ss.worksheet(template_sheet_name)

        # テンプレートをターゲットSSへコピー
        copied_info = tpl_ws.copy_to(target_spreadsheet_id)
        new_sheet_id = copied_info["sheetId"]

        tgt_ss = client.open_by_key(target_spreadsheet_id)

        # 同名シートがある場合削除
        try:
            old_ws = tgt_ss.worksheet(target_sheet_name)
            tgt_ss.del_worksheet(old_ws)
        except gspread.exceptions.WorksheetNotFound:
            pass

        # コピーしたシートをリネーム
        new_ws = None
        for ws in tgt_ss.worksheets():
            if ws.id == new_sheet_id:
                new_ws = ws
                break

        if not new_ws:
            st.error("❌ Copied sheet not found.")
            return None

        new_ws.update_title(target_sheet_name)
        st.success(f"✅ Copied '{template_sheet_name}' → '{target_sheet_name}'")
        return new_ws

    except Exception as e:
        st.error(f"❌ Failed to copy template sheet: {e}")
        return None


# =========================================================
# 🔧 テーブル範囲を自動調整（新旧UI対応）
# =========================================================
def adjust_table_range_safely(creds, spreadsheet_id, sheet_name, df_rows, df_cols, header_rows=1):
    """
    DFのサイズに合わせてシートの表範囲を調整。
    新しい「表（Tables）」が存在する場合はBasicFilter設定をスキップ。
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

        # sheetId取得
        sheet_id = None
        for s in meta["sheets"]:
            if s["properties"]["title"] == sheet_name:
                sheet_id = s["properties"]["sheetId"]
                break

        if sheet_id is None:
            st.error(f"❌ Target sheet '{sheet_name}' not found.")
            return

        # 行列数を十分に確保
        needed_rows = max(header_rows + df_rows, 200)
        needed_cols = max(df_cols, 26)

        requests = [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "rowCount": needed_rows,
                            "columnCount": needed_cols,
                        },
                    },
                    "fields": "gridProperties(rowCount,columnCount)",
                }
            }
        ]

        # BasicFilterの再設定を試す
        try:
            requests.append({"clearBasicFilter": {"sheetId": sheet_id}})
            requests.append({
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": header_rows + df_rows,
                            "startColumnIndex": 0,
                            "endColumnIndex": df_cols,
                        }
                    }
                }
            })

            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            st.info(f"🧩 BasicFilter resized to {df_rows} rows, {df_cols} cols")

        except HttpError as he:
            if "partially intersects a table" in str(he):
                st.warning("⚠️ テンプレートに新しい『表（Tables）』があるため、BasicFilter の再設定をスキップしました。")
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id, body={"requests": [requests[0]]}
                ).execute()
            else:
                raise he

    except Exception as e:
        st.error(f"❌ Failed to adjust table range: {e}")


# =========================================================
# 📊 データ書き込み処理
# =========================================================
def write_to_google_sheet(
    client,
    creds,
    spreadsheet_id: str,
    worksheet_name: str,
    map_data,
    template_spreadsheet_id: str,
    template_sheet_name: str,
):
    """1) テンプレートコピー → 2) 表範囲調整 → 3) データ挿入"""
    try:
        # 1️⃣ コピー
        worksheet = copy_template_sheet_to_target(
            client,
            template_spreadsheet_id,
            template_sheet_name,
            spreadsheet_id,
            worksheet_name,
        )
        if worksheet is None:
            return

        # 2️⃣ データ整形
        df_master = prepare_master_dataframe(map_data)
        df_rows = len(df_master)
        df_cols = len(df_master.columns)

        adjust_table_range_safely(
            creds,
            spreadsheet_id,
            worksheet_name,
            df_rows,
            df_cols,
        )

        # 3️⃣ データ挿入
        set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)
        st.success("✅ Data inserted successfully!")

    except Exception as e:
        st.error(f"❌ Failed to write sheet: {e}")


# =========================================================
# 🧭 Streamlit UI
# =========================================================
st.title("📋 Google Sheet Copier + Auto Table Resizer")

# --- Nomic Atlas Settings ---
st.subheader("Nomic Atlas Settings")
default_token = st.secrets.get("NOMIC_TOKEN", "")
token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# --- Google Sheets Settings ---
st.subheader("Google Sheets Settings")
spreadsheet_id = st.text_input("Target Spreadsheet ID", value="")
worksheet_name = st.text_input("Target Worksheet Name", value="メイン")

template_spreadsheet_id = st.text_input("Template Spreadsheet ID", value="")
template_sheet_name = st.text_input("Template Sheet Name", value="Table_2")

# --- Buttons ---
if st.button("Fetch Nomic Dataset"):
    data = fetch_nomic_dataset(token, domain, map_name)
    if data:
        st.session_state.map_data = data

if st.button("Google Login"):
    gclient, creds = google_login()
    if gclient:
        st.session_state.gclient = gclient
        st.session_state.creds = creds

if st.button("Copy Template → Resize Table → Insert Data"):
    if "map_data" not in st.session_state:
        st.error("❌ Please fetch the Nomic dataset first.")
    elif "gclient" not in st.session_state or "creds" not in st.session_state:
        st.error("❌ Please log in to Google first.")
    elif not template_spreadsheet_id or not template_sheet_name:
        st.error("❌ Please set template spreadsheet & sheet.")
    else:
        write_to_google_sheet(
            st.session_state.gclient,
            st.session_state.creds,
            spreadsheet_id,
            worksheet_name,
            st.session_state.map_data,
            template_spreadsheet_id,
            template_sheet_name,
        )
