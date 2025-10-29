# sheets_writer.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from googleapiclient.discovery import build
from gspread_formatting import (
    CellFormat,
    format_cell_range,
    TextFormat,
    Color,
)

import json
import re
import pandas as pd
import colorsys

def extract_spreadsheet_id(url) -> str:
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    return m.group(1) if m else url


def write_sheet(spreadsheet_url, sheet_name, service_account_info, df_master):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)

        # --- Open spreadsheet and worksheet ---
        spreadsheet_id = extract_spreadsheet_id(spreadsheet_url)
        spreadsheet = client.open_by_key(spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=26)

        # --- Clear and write DataFrame ---
        worksheet.clear()
        set_with_dataframe(worksheet, df_master, include_column_header=True, resize=True)
        reset_sheet(worksheet)

        print(f"✅ Successfully wrote data to '{sheet_name}' in spreadsheet {spreadsheet_id}")
        return worksheet.url, None

    except Exception as e:
        print(f"❌ Failed to write to sheet: {e}")
        return None, str(e)


def reset_sheet(worksheet):
    """
    シート全体をリセットし、標準フォントとテキストカラーを設定。
    - 既存の書式・プルダウン・条件付き書式・罫線などを全削除
    - ベースフォント: Roboto
    - テキストカラー: #434343 (67/255, 67/255, 67/255)
    """
    spreadsheet = worksheet.spreadsheet
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)
    spreadsheet_id = spreadsheet.id
    sheet_id = worksheet.id

    # 現在の範囲サイズを取得
    data = worksheet.get_all_values()
    num_rows = max(1, len(data))
    num_cols = max(1, len(data[0]) if data else 1)

    # --- 1️⃣ データ検証削除 ---
    clear_data_validation = {"clearBasicFilter": {"sheetId": sheet_id}}

    # --- 2️⃣ 条件付き書式削除 ---
    try:
        rules = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id, fields="sheets.conditionalFormats"
        ).execute()
        num_rules = 0
        for s in rules.get("sheets", []):
            if "conditionalFormats" in s:
                num_rules += len(s["conditionalFormats"])
    except Exception:
        num_rules = 0

    delete_rules = []
    for _ in range(num_rules):
        delete_rules.append({
            "deleteConditionalFormatRule": {"sheetId": sheet_id, "index": 0}
        })

    # --- 3️⃣ 全書式クリア + ベースフォント/カラー設定 ---
    base_text_color = {"red": 67/255, "green": 67/255, "blue": 67/255}
    base_text_format = {
        "fontFamily": "Roboto",
        "fontSize": 10,
        "foregroundColor": base_text_color,
        "bold": False,
        "italic": False,
    }

    clear_and_set_format = {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": num_rows,
                "startColumnIndex": 0,
                "endColumnIndex": num_cols,
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": base_text_format,
                    "horizontalAlignment": "LEFT",
                    "verticalAlignment": "MIDDLE",
                    "backgroundColor": {"red": 1, "green": 1, "blue": 1},  # 白背景で統一
                    "wrapStrategy": "OVERFLOW_CELL"  # テキスト折返しをリセット
                }
            },
            "fields": "userEnteredFormat",
        }
    }

    # --- 4️⃣ 枠線リセット ---
    clear_borders = {
        "updateBorders": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": num_rows,
                "startColumnIndex": 0,
                "endColumnIndex": num_cols,
            },
            "top": {"style": "NONE"},
            "bottom": {"style": "NONE"},
            "left": {"style": "NONE"},
            "right": {"style": "NONE"},
            "innerHorizontal": {"style": "NONE"},
            "innerVertical": {"style": "NONE"},
        }
    }

    # 一括実行
    requests = [clear_data_validation, clear_and_set_format, clear_borders] + delete_rules

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()

    print("✅ Sheet formatting reset + base style applied (Roboto + #434343)")
