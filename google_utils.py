import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

def init_gspread(st):
    """Googleサービスアカウントを初期化"""
    if "gclient" not in st.session_state:
        try:
            service_account_info = json.loads(st.secrets["google_service_account"]["value"])
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
            st.session_state.gclient = gspread.authorize(creds)
            st.success("✅ Google Service Account Loaded Successfully!")
        except Exception as e:
            st.error(f"❌ Failed to load service account: {e}")
            st.session_state.gclient = None
    return st.session_state.gclient


def clear_and_init_sheet(st, client, spreadsheet_id, worksheet_name, df):
    """シートを初期化してカラムを書き込み"""
    if client is None:
        st.error("❌ Google client not initialized.")
        return
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)
        worksheet.clear()
        set_with_dataframe(worksheet, df, include_column_header=True, row=1, col=1)
        st.success("✅ Google Sheet cleared and initialized!")
    except Exception as e:
        st.error(f"❌ Failed to initialize Google Sheet: {e}")


def write_metadata_to_sheet(st, client, spreadsheet_id, worksheet_name, df):
    """Nomicから取得したデータをGoogle Sheetsに書き込む"""
    if client is None:
        st.error("❌ Google client not initialized.")
        return
    elif "map_data" not in st.session_state:
        st.error("⚠️ No dataset loaded yet. Please fetch dataset first.")
        return

    try:
        map_data = st.session_state.map_data
        df_metadata = map_data.topics.metadata

        df["depth"] = df_metadata["depth"].astype(str)
        df["topic_id"] = df_metadata["topic_id"].astype(str)
        df["Nomic Topic: Broad"] = df_metadata["topic_depth_1"].astype(str)
        df["Nomic Topic: Medium"] = df_metadata["topic_depth_2"].astype(str)
        df["キーワード"] = df_metadata["topic_description"].astype(str)

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)
        worksheet.clear()
        set_with_dataframe(worksheet, df, include_column_header=True, row=1, col=1)
        st.success("✅ Metadata successfully written to Google Sheet!")
    except Exception as e:
        st.error(f"❌ Failed to write metadata: {e}")
