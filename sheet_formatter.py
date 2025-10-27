# sheet_formatter.py
from gspread_formatting import (
    CellFormat,
    format_cell_range,
    TextFormat,
    Color,
)
from googleapiclient.discovery import build


# ===============================
# 🟩 1行目ヘッダーを緑背景＋白文字＋太字にする
# ===============================
def apply_header_style_green(worksheet, df):
    """1行目を緑色背景・白文字・太字にする"""
    if df.empty:
        return

    num_cols = len(df.columns)

    # 最終列を算出
    if num_cols <= 26:
        last_col_letter = chr(64 + num_cols)
    else:
        last_col_letter = ""
        n = num_cols
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            last_col_letter = chr(65 + remainder) + last_col_letter

    header_range = f"A1:{last_col_letter}1"
    header_format = CellFormat(
        backgroundColor=Color(red=0.36, green=0.66, blue=0.38),  # 少し深めの緑
        textFormat=TextFormat(bold=True, foregroundColor=Color(1, 1, 1)),  # 白文字＋太字
    )
    format_cell_range(worksheet, header_range, header_format)


# ===============================
# 🔍 フィルターを1行目に適用
# ===============================
def apply_filter_to_header(worksheet, df):
    """シートの1行目にフィルターを設定"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id

    # gspreadの内部認証情報を取り出してGoogle Sheets APIを直接利用
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    num_cols = len(df.columns)
    request_body = {
        "requests": [
            {
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": worksheet.id,
                            "startRowIndex": 0,
                            "endRowIndex": 1 + len(df),
                            "startColumnIndex": 0,
                            "endColumnIndex": num_cols,
                        }
                    }
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=request_body
    ).execute()

# ===============================
# ⬛ 表全体に枠線をつける
# ===============================
def apply_borders_to_range(worksheet, df, start_row=1, start_col=1):
    """表全体に罫線（外枠＋内線）を描画する"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    num_rows = len(df)
    num_cols = len(df.columns)

    request_body = {
        "requests": [
            {
                "updateBorders": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": start_row - 1,
                        "endRowIndex": start_row - 1 + num_rows + 1,  # +1 for header
                        "startColumnIndex": start_col - 1,
                        "endColumnIndex": start_col - 1 + num_cols,
                    },
                    "top": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "left": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "right": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "innerHorizontal": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "innerVertical": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=request_body
    ).execute()


# ===============================
# 📏 各列の幅を細かく設定（A〜AB列）
# ===============================
def set_custom_column_widths(worksheet):
    """
    各列の幅をピクセル単位で設定。
    A〜AB列の幅を固定値で指定。
    """
    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    # 列ごとの幅指定（ピクセル）
    column_widths = {
        # A〜D
        "A": 80,
        "B": 80,
        "C": 150,
        "D": 150,

        # E
        "E": 600,

        # F〜J → 150
        **{chr(c): 150 for c in range(ord("F"), ord("J") + 1)},

        # K〜U → 200
        **{chr(c): 200 for c in range(ord("K"), ord("U") + 1)},

        # V・W
        "V": 300,
        "W": 300,

        # X
        "X": 150,

        # Y〜AB → 110
        **{col: 110 for col in ["Y", "Z", "AA", "AB"]},
    }

    # 変換してAPIリクエストを作成
    requests = []
    for col_letter, width in column_widths.items():
        # 列インデックスを0始まりで計算（A=0, B=1...）
        col_index = (
            (ord(col_letter[-1]) - 65) if len(col_letter) == 1
            else (ord(col_letter[-1]) - 65 + 26)  # AA, ABなど
        )

        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": worksheet.id,
                    "dimension": "COLUMNS",
                    "startIndex": col_index,
                    "endIndex": col_index + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # API実行
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()
