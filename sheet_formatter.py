from gspread_formatting import (
    CellFormat,
    format_cell_range,
    TextFormat,
    Color,
)
from googleapiclient.discovery import build
import colorsys


# ===============================
# 🟩 1行目ヘッダーを緑背景＋白文字＋太字にする
# ===============================
def apply_header_style_green(worksheet, df):
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
        horizontalAlignment="CENTER",
        verticalAlignment="MIDDLE",
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
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

    num_cols = len(df.columns)
    request_body = {
        "requests": [
            {
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": worksheet.id,
                            "startRowIndex": 0,
                            "endRowIndex": len(df) + 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": num_cols,
                        }
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id, body=request_body
    ).execute()


# ===============================
# 🟩 外枠のみを緑色で描画
# ===============================
def apply_green_outer_border(worksheet, df):
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

    num_rows = len(df)
    num_cols = len(df.columns)

    green = {"red": 0.36, "green": 0.66, "blue": 0.38}
    white = {"red": 1, "green": 1, "blue": 1}

    request_body = {
        "requests": [
            {
                "updateBorders": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": 0,
                        "endRowIndex": num_rows + 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": num_cols,
                    },
                    "top": {"style": "SOLID", "width": 2, "color": green},
                    "bottom": {"style": "SOLID", "width": 2, "color": green},
                    "left": {"style": "SOLID", "width": 2, "color": green},
                    "right": {"style": "SOLID", "width": 2, "color": green},
                    "innerHorizontal": {"style": "SOLID", "width": 1, "color": white},
                    "innerVertical": {"style": "SOLID", "width": 1, "color": white},
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id, body=request_body
    ).execute()


# ===============================
# 🔤 E列を折り返し表示
# ===============================
def apply_wrap_text_to_column_E(worksheet, df):
    """E列全体のテキストを折り返し表示"""
    if df.empty:
        return

    num_rows = len(df)
    start_col, end_col = 4, 5  # E列

    spreadsheet = worksheet.spreadsheet
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

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
                    "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}},
                    "fields": "userEnteredFormat.wrapStrategy",
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id, body=request_body
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
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

    request_body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": num_cols,
                    },
                    "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}},
                    "fields": "userEnteredFormat.wrapStrategy",
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id, body=request_body
    ).execute()


# ===============================
# 📏 各列の幅を細かく設定
# ===============================
def set_custom_column_widths(worksheet):
    spreadsheet = worksheet.spreadsheet
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

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

    def col_to_index(col):
        """列文字→インデックス"""
        col = col.upper()
        index = 0
        for c in col:
            index = index * 26 + (ord(c) - 64)
        return index - 1

    requests = []
    for col_letter, width in column_widths.items():
        col_index = col_to_index(col_letter)
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
        spreadsheetId=spreadsheet.id, body={"requests": requests}
    ).execute()


# ===============================
# 🟩 列グループ間に縦の区切り線を描画
# ===============================
def apply_vertical_group_borders(worksheet, df):
    """列グループの境界に緑色の縦線を描画"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

    num_rows = len(df) + 1
    green = {"red": 0.36, "green": 0.66, "blue": 0.38}

    group_right_edges = [5, 10, 11, 15, 18, 21, 28]  # A〜E | F〜J | ... | V〜AB
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
        spreadsheetId=spreadsheet.id, body={"requests": requests}
    ).execute()


# ===============================
# 🟢 C列のプルダウンをデータから自動生成＋条件付き書式で色付け
# ===============================
def apply_dropdown_with_color_to_column_C(worksheet, df):
    """C列のカテゴリを抽出してプルダウン＋背景色を自動設定
       D列にも同様のプルダウンを設定（薄灰色固定）"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

    # --- C列カテゴリ抽出 ---
    try:
        c_series = df.iloc[:, 2]
    except Exception:
        return

    categories = sorted(
        set(
            [
                str(v).strip()
                for v in c_series.dropna()
                if str(v).strip() != "" and str(v).lower() != "none"
            ]
        )
    )
    num_rows = len(df) + 1

    # ========= C列 =========
    col_index_c = 2
    dropdown_c = {
        "setDataValidation": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 1,
                "endRowIndex": num_rows,
                "startColumnIndex": col_index_c,
                "endColumnIndex": col_index_c + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in categories],
                },
                "strict": True,
            },
        }
    }

    requests = [dropdown_c]

    # C列 色分け（カテゴリ別）
    n = max(1, len(categories))
    palette = [_hsl_to_rgb(i / n, 0.5, 0.85) for i in range(n)]

    for idx, cat in enumerate(categories):
        requests.append(
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": worksheet.id,
                                "startRowIndex": 1,
                                "endRowIndex": num_rows,
                                "startColumnIndex": col_index_c,
                                "endColumnIndex": col_index_c + 1,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": cat}],
                            },
                            "format": {"backgroundColor": palette[idx]},
                        },
                    },
                    "index": 0,
                }
            }
        )

    # ========= D列 =========
    col_index_d = 3
    dropdown_d = {
        "setDataValidation": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 1,
                "endRowIndex": num_rows,
                "startColumnIndex": col_index_d,
                "endColumnIndex": col_index_d + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in categories],
                },
                "strict": True,
            },
        }
    }

    requests.append(dropdown_d)

    # D列：すべて薄灰色背景に統一
    light_gray = {"red": 0.95, "green": 0.95, "blue": 0.95}
    requests.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": col_index_d,
                    "endColumnIndex": col_index_d + 1,
                },
                "cell": {"userEnteredFormat": {"backgroundColor": light_gray}},
                "fields": "userEnteredFormat.backgroundColor",
            }
        }
    )

    # --- リクエスト送信 ---
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id, body={"requests": requests}
    ).execute()


def _hsl_to_rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return {"red": r, "green": g, "blue": b}

# ===============================
# 🎨 シート全体デザイン適用
# ===============================
def apply_sheet_design(worksheet, df):
    """全体の背景・縦揃え・交互色設定"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    service = build("sheets", "v4", credentials=spreadsheet.client.auth)

    num_rows = len(df) + 1
    num_cols = len(df.columns)

    light_gray = {"red": 0.95, "green": 0.95, "blue": 0.95}
    white = {"red": 1, "green": 1, "blue": 1}

    requests = []

    # 縦中央揃え
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 1,
                "endRowIndex": num_rows,
                "startColumnIndex": 0,
                "endColumnIndex": num_cols,
            },
            "cell": {"userEnteredFormat": {"verticalAlignment": "MIDDLE"}},
            "fields": "userEnteredFormat.verticalAlignment",
        }
    })

    # 交互の背景色
    for i in range(1, num_rows):
        if i % 2 == 0:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": i,
                        "endRowIndex": i + 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": num_cols,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": light_gray}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            })

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id, body={"requests": requests}
    ).execute()
