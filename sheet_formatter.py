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
        backgroundColor=Color(red=0.36, green=0.66, blue=0.38),
        textFormat=TextFormat(bold=True, foregroundColor=Color(1, 1, 1)),
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
# 🟩 外枠のみを緑色で描画
# ===============================
def apply_green_outer_border(worksheet, df, start_row=1, start_col=1):
    """表の外枠だけを緑色線で描画"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    num_rows = len(df)
    num_cols = len(df.columns)

    green = {"red": 0.36, "green": 0.66, "blue": 0.38}

    request_body = {
        "requests": [
            {
                "updateBorders": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": start_row - 1,
                        "endRowIndex": start_row - 1 + num_rows + 1,
                        "startColumnIndex": start_col - 1,
                        "endColumnIndex": start_col - 1 + num_cols,
                    },
                    "top": {"style": "SOLID", "width": 2, "color": green},
                    "bottom": {"style": "SOLID", "width": 2, "color": green},
                    "left": {"style": "SOLID", "width": 2, "color": green},
                    "right": {"style": "SOLID", "width": 2, "color": green},
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=request_body
    ).execute()


# ===============================
# 🔤 E列を折り返し表示
# ===============================
def apply_wrap_text_to_column_E(worksheet, df):
    """E列全体のテキストを折り返し表示"""
    if df.empty:
        return

    num_rows = len(df)
    # E列 → インデックス4（A=0）
    start_col = 4
    end_col = 5

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    request_body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": 0,
                        "endRowIndex": num_rows + 1,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields": "userEnteredFormat.wrapStrategy",
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
    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    column_widths = {
        "A": 80,
        "B": 80,
        "C": 165,
        "D": 165,
        "E": 550,
        **{chr(c): 150 for c in range(ord("F"), ord("J") + 1)},
        **{chr(c): 220 for c in range(ord("K"), ord("U") + 1)},
        "V": 300,
        "W": 300,
        "X": 150,
        **{col: 110 for col in ["Y", "Z", "AA", "AB"]},
    }

    requests = []
    for col_letter, width in column_widths.items():
        col_index = (
            (ord(col_letter[-1]) - 65)
            if len(col_letter) == 1
            else (ord(col_letter[-1]) - 65 + 26)
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
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()


# ===============================
# 🔤 1行目すべてのセルを折り返し表示
# ===============================
def apply_wrap_text_to_header_row(worksheet, df):
    """1行目（ヘッダー行）の全列に折り返し設定を適用"""
    if df.empty:
        return

    num_cols = len(df.columns)

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    request_body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": 0,      # 1行目（0始まり）
                        "endRowIndex": 1,        # 1行目だけ
                        "startColumnIndex": 0,
                        "endColumnIndex": num_cols,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields": "userEnteredFormat.wrapStrategy",
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=request_body
    ).execute()

# ===============================
# 🟩 列グループ間に縦の区切り線を描画
# ===============================
def apply_vertical_group_borders(worksheet, df):
    """
    列グループの境界に緑色の縦線を描画。
    グループ範囲：
    A〜E | F〜J | K〜L | M〜O | P〜R | S〜U | V〜AB
    """
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    num_rows = len(df) + 1  # ヘッダー含む
    green = {"red": 0.36, "green": 0.66, "blue": 0.38}

    # 各グループの「右端列インデックス」を定義（A=0始まり）
    # 例：E列=4, J列=9, L列=11 ...
    group_right_edges = [4, 9, 11, 14, 17, 20, 27]  # AB=27

    requests = []
    for edge_index in group_right_edges:
        requests.append({
            "updateBorders": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": num_rows,
                    "startColumnIndex": edge_index,
                    "endColumnIndex": edge_index + 1,
                },
                "left": {"style": "SOLID", "width": 2, "color": green},
            }
        })

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()

# ===============================
# 🎨 C列をカテゴリ別プルダウン＋色付き表示にする
# ===============================
def apply_dropdown_with_color_to_column_C(worksheet, df):
    """
    C列にプルダウンを設定し、選択肢ごとに背景色を変更する。
    """
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    gclient = spreadsheet.client
    creds = gclient.auth
    service = build("sheets", "v4", credentials=creds)

    num_rows = len(df) + 1  # ヘッダー含む
    col_index = 2  # C列（A=0, B=1, C=2）

    # プルダウンに表示するカテゴリーと色
    category_colors = {
        "Entertainment": {"red": 0.98, "green": 0.86, "blue": 0.50},   # 黄色
        "Agriculture": {"red": 1.0, "green": 0.70, "blue": 0.70},      # ピンク
        "Disaster Management": {"red": 1.0, "green": 0.80, "blue": 0.60}, # オレンジ
        "Local Revitalization": {"red": 0.75, "green": 0.85, "blue": 1.0}, # 水色
        "Personalized Learning": {"red": 0.80, "green": 0.90, "blue": 0.90}, # 薄青緑
        "Healthcare": {"red": 0.80, "green": 1.0, "blue": 0.80},        # 緑
        "VR Education": {"red": 0.90, "green": 0.85, "blue": 1.0},      # 紫
    }

    # 1️⃣ プルダウン（データ検証）を設定
    dropdown_request = {
        "setDataValidation": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 1,
                "endRowIndex": num_rows,
                "startColumnIndex": col_index,
                "endColumnIndex": col_index + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in category_colors.keys()],
                },
                "showCustomUi": True,
                "strict": True,
            },
        }
    }

    # 2️⃣ 条件付き書式ルールを設定（選択肢ごとに背景色変更）
    rules_requests = []
    for label, color in category_colors.items():
        rules_requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": worksheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": num_rows,
                            "startColumnIndex": col_index,
                            "endColumnIndex": col_index + 1,
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": label}],
                        },
                        "format": {
                            "backgroundColor": color,
                            "textFormat": {"bold": True},
                        },
                    },
                },
                "index": 0,
            }
        })

    # 3️⃣ APIリクエストまとめて送信
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [dropdown_request] + rules_requests},
    ).execute()
