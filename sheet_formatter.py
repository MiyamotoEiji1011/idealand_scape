from gspread_formatting import (
    CellFormat,
    format_cell_range,
    TextFormat,
    Color,
)
from googleapiclient.discovery import build
import colorsys


# ===============================
# 🟩 1行目ヘッダーを#356854背景＋白文字＋太字にする
# ===============================
def apply_header_style_green(worksheet, df):
    """1行目を#356854背景・白文字・太字にする"""
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
        backgroundColor=Color(
            red=0x35 / 255, green=0x68 / 255, blue=0x54 / 255
        ),  # #356854
        textFormat=TextFormat(bold=True, foregroundColor=Color(1, 1, 1)),
        verticalAlignment="MIDDLE",
        horizontalAlignment="CENTER",
    )
    format_cell_range(worksheet, header_range, header_format)


# ===============================
# 🎨 表全体のデザイン調整
# ===============================
def apply_sheet_design(worksheet, df):
    """外枠のみ枠線、交互色、中央揃えを設定"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    creds = spreadsheet.client.auth
    service = build("sheets", "v4", credentials=creds)

    num_rows = len(df) + 1  # ヘッダー含む
    num_cols = len(df.columns)

    green = {"red": 0x35 / 255, "green": 0x68 / 255, "blue": 0x54 / 255}
    light_gray = {"red": 0.95, "green": 0.95, "blue": 0.95}
    white = {"red": 1, "green": 1, "blue": 1}

    requests = []

    # --- 1) 外枠だけ描画 ---
    requests.append({
        "updateBorders": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 0,
                "endRowIndex": num_rows,
                "startColumnIndex": 0,
                "endColumnIndex": num_cols,
            },
            "top": {"style": "SOLID", "width": 2, "color": green},
            "bottom": {"style": "SOLID", "width": 2, "color": green},
            "left": {"style": "SOLID", "width": 2, "color": green},
            "right": {"style": "SOLID", "width": 2, "color": green},
            # 👇 内側の線を消す
            "innerHorizontal": {"style": "NONE"},
            "innerVertical": {"style": "NONE"},
        }
    })

    # --- 2) 全体を縦中央揃え（E列以外）---
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 1,
                "endRowIndex": num_rows,
                "startColumnIndex": 0,
                "endColumnIndex": num_cols,
            },
            "cell": {
                "userEnteredFormat": {
                    "verticalAlignment": "MIDDLE",
                }
            },
            "fields": "userEnteredFormat.verticalAlignment",
        }
    })

    # --- 3) 交互の背景色（E列除く）---
    # 偶数行（2,4,6...）を薄い灰色に
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
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": light_gray
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor",
                }
            })
    # 4) E列の背景色上書きを防ぐため、E列全体を白でリセットしない
    # （上のforでE列にも反映されるときは後で条件書式が勝つ）

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()


# ===============================
# 🟢 C列プルダウン（前回のものを統合）
# ===============================
def apply_dropdown_with_color_to_column_C(worksheet, df):
    """C列の実データからカテゴリを自動抽出してプルダウン＋背景色を付ける"""
    if df.empty:
        return

    spreadsheet = worksheet.spreadsheet
    spreadsheet_id = spreadsheet.id
    creds = spreadsheet.client.auth
    service = build("sheets", "v4", credentials=creds)

    try:
        c_series = df.iloc[:, 2]
    except Exception:
        return

    categories = sorted(set([str(v).strip() for v in c_series.dropna() if str(v).strip() != ""]))
    if not categories:
        categories = []

    num_rows = len(df) + 1
    col_index = 2  # C列

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
                    "values": [{"userEnteredValue": v} for v in categories],
                },
                "showCustomUi": True,
                "strict": True,
            },
        }
    }

    requests = [dropdown_request]

    # 条件付き書式で背景色
    def hsl_to_rgb(h, s, l):
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return {"red": r, "green": g, "blue": b}

    n = max(1, len(categories))
    palette = [hsl_to_rgb(i / n, 0.5, 0.85) for i in range(n)]

    for idx, cat in enumerate(categories):
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": num_rows,
                        "startColumnIndex": col_index,
                        "endColumnIndex": col_index + 1,
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": cat}]
                        },
                        "format": {
                            "backgroundColor": palette[idx]
                        }
                    }
                },
                "index": 0
            }
        })

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()
