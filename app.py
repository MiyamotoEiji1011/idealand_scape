import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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
# 📊 表の内部（ヘッダー検出して自動挿入）
# =========================================================
def write_data_inside_table_auto(client, spreadsheet_id: str, worksheet_name: str, map_data):
    """
    コピーされたシート内の「表(Table_○)」を壊さずに、
    ヘッダー行を自動検出し、その下のデータ行をすべて置き換える。
    """
    try:
        worksheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
        df_master = prepare_master_dataframe(map_data)

        # === 1️⃣ ヘッダー位置の自動検出 ===
        header_row_index = None
        header_values = []
        all_rows = worksheet.get_all_values()

        for i, row in enumerate(all_rows[:10]):  # 上から10行以内にヘッダーがある前提
            if any(cell.strip() for cell in row):  # 空行でない
                header_row_index = i + 1
                header_values = row
                break

        if not header_row_index:
            st.error("❌ ヘッダー行を検出できませんでした。テンプレートを確認してください。")
            return

        st.info(f"🧭 ヘッダー行を自動検出: {header_row_index}行目")

        num_cols = len(header_values)
        num_rows = len(df_master)

        # === 2️⃣ データ範囲を算出 ===
        from gspread.utils import rowcol_to_a1

        start_row = header_row_index + 1
        start_col = 1
        end_row = start_row + num_rows - 1
        end_col = num_cols

        range_a1 = f"{rowcol_to_a1(start_row, start_col)}:{rowcol_to_a1(end_row, end_col)}"

        # === 3️⃣ 書き込み前に旧データクリア（テーブル内部のみ） ===
        worksheet.batch_clear([range_a1])

        # === 4️⃣ 新データ挿入 ===
        values = df_master.values.tolist()
        worksheet.update(range_a1, values)

        st.success(f"✅ {num_rows} 行のデータを表内に挿入しました！ (範囲: {range_a1})")

    except Exception as e:
        st.error(f"❌ Failed to write inside table: {e}")


# =========================================================
# 📋 メイン処理
# =========================================================
def main():
    st.title("📊 Google Sheet Template Copier + Table Inserter")

    # --- Nomic設定 ---
    st.subheader("Nomic Atlas Settings")
    default_token = st.secrets.get("NOMIC_TOKEN", "")
    token = st.text_input("API Token", value=default_token, type="password")
    domain = st.text_input("Domain", value="atlas.nomic.ai")
    map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

    # --- Google Sheets設定 ---
    st.subheader("Google Sheets Settings")
    spreadsheet_id = st.text_input("Target Spreadsheet ID", value="1XDAGnEjY8XpDC9ohtaHgo4ECZG8OgNUNJo-ZrCksRDI")
    worksheet_name = st.text_input("Target Worksheet Name", value="シート1")

    template_spreadsheet_id = st.text_input("Template Spreadsheet ID", value="1DJbrC0fGpVcPrHrTlDyzTZdt2K1lmm_2QJJVI8fqoIY")
    template_sheet_name = st.text_input("Template Sheet Name", value="シート1")

    # --- ボタン群 ---
    if st.button("Fetch Nomic Dataset"):
        data = fetch_nomic_dataset(token, domain, map_name)
        if data:
            st.session_state.map_data = data

    if st.button("Google Login"):
        gclient, creds = google_login()
        if gclient:
            st.session_state.gclient = gclient
            st.session_state.creds = creds

    if st.button("Copy Template & Insert Data into Table"):
        if "map_data" not in st.session_state:
            st.error("❌ Please fetch the Nomic dataset first.")
        elif "gclient" not in st.session_state:
            st.error("❌ Please log in to Google first.")
        elif not template_spreadsheet_id or not template_sheet_name:
            st.error("❌ Please set template spreadsheet & sheet.")
        else:
            worksheet = copy_template_sheet_to_target(
                client=st.session_state.gclient,
                template_spreadsheet_id=template_spreadsheet_id,
                template_sheet_name=template_sheet_name,
                target_spreadsheet_id=spreadsheet_id,
                target_sheet_name=worksheet_name,
            )

            if worksheet:
                write_data_inside_table_auto(
                    client=st.session_state.gclient,
                    spreadsheet_id=spreadsheet_id,
                    worksheet_name=worksheet_name,
                    map_data=st.session_state.map_data,
                )


if __name__ == "__main__":
    main()
