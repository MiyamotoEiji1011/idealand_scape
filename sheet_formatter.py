# sheet_formatter.py
from gspread_formatting import CellFormat, format_cell_range, TextFormat

def format_sheet_header_bold(worksheet, df):
    """Googleシートの1行目を太字にし、全体の見た目を整える"""
    if df.empty:
        return

    num_cols = len(df.columns)

    # 最終列の文字（A-Z, AA, AB...対応）
    if num_cols <= 26:
        last_col_letter = chr(64 + num_cols)
    else:
        last_col_letter = ""
        n = num_cols
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            last_col_letter = chr(65 + remainder) + last_col_letter

    # 全体をリセット（太字解除など）
    total_range = f"A1:{last_col_letter}{worksheet.row_count}"
    normal_format = CellFormat(textFormat=TextFormat(bold=False))
    format_cell_range(worksheet, total_range, normal_format)

    # 1行目だけ太字
    header_range = f"A1:{last_col_letter}1"
    header_format = CellFormat(textFormat=TextFormat(bold=True))
    format_cell_range(worksheet, header_range, header_format)
