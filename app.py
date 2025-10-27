from googleapiclient.discovery import build

def expand_table_range(creds, spreadsheet_id: str, sheet_name: str, start_row: int, end_row: int, start_col: int, end_col: int):
    """
    シートの表範囲を擬似的に拡張（BasicFilterの再設定で代替）
    """
    try:
        service = build("sheets", "v4", credentials=creds)

        # sheetIdを取得
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = None
        for s in meta["sheets"]:
            if s["properties"]["title"] == sheet_name:
                sheet_id = s["properties"]["sheetId"]
                break

        if sheet_id is None:
            print("❌ Sheet not found.")
            return

        # 既存フィルターを削除して新しい範囲で再設定
        requests = [
            {"clearBasicFilter": {"sheetId": sheet_id}},
            {
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row - 1,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col - 1,
                            "endColumnIndex": end_col,
                        }
                    }
                }
            },
        ]

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()
        print(f"✅ 表範囲を {start_row}:{end_row}, {start_col}:{end_col} に再設定しました。")

    except Exception as e:
        print(f"❌ Failed to expand table range: {e}")
