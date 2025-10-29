import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import sheet_formatter
import data_processing

import re
import json

# ===================================
# 関数
# ===================================
def nomic_dataset(api_token: str, domain: str, map_url: str):
    # URLから map_name を抽出
    match = re.search(r"/data/[^/]+/([^/]+)/map", map_url or "")
    if not match:
        st.error("Invalid map URL format. Please check your Nomic map link.")
        return None

    map_name = match.group(1)
    st.info(f"Extracted map name: {map_name}")

    try:
        # Nomicログイン
        nomic.login(token=api_token, domain=domain)
        # データセット取得
        dataset = AtlasDataset(map_name)
        st.success("Dataset fetched successfully.")
        return dataset.maps[0]

    except Exception as e:
        st.error(f"Failed to fetch dataset: {e}")
        return None


def google_login():
    try:
        service_account_info = json.loads(st.secrets["google_service_account"]["value"])
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        st.success("Google Service Account Loaded Successfully.")
        return client
    except Exception as e:
        st.error(f"Failed to load service account: {e}")
        return None
    

def write_sheet(client, spreadsheet_id: str, worksheet_name: str, map_data):
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)

        # ワークシート取得。無ければ作成
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)

        # --- データ整形 ---
        # プロジェクト内の処理を想定。存在しない場合はエラーにします。
        import data_processing
        df_master = data_processing.prepare_master_dataframe(map_data)

        # --- 書き込み前に初期化 ---
        worksheet.clear()

        # --- データフレーム書き込み ---
        import sheet_formatter
        sheet_formatter.set_with_dataframe(worksheet, df_master, include_column_header=True, row=1, col=1)

        # いったん全リセット
        sheet_formatter.reset_sheet_formatting(worksheet)

        # --- フォーマット適用 ---
        sheet_formatter.apply_header_style_green(worksheet, df_master)
        sheet_formatter.apply_filter_to_header(worksheet, df_master)
        sheet_formatter.apply_green_outer_border(worksheet, df_master)
        sheet_formatter.apply_wrap_text_to_header_row(worksheet, df_master)
        sheet_formatter.apply_wrap_text_to_column_E(worksheet, df_master)
        sheet_formatter.set_custom_column_widths(worksheet)
        sheet_formatter.apply_dropdowns_for_columns_C_and_D(worksheet, df_master)
        sheet_formatter.apply_sheet_design(worksheet, df_master)

        st.success("Successfully wrote data to Google Sheet.")
    except Exception as e:
        st.error(f"Failed to write sheet: {e}")


def output_sheet():
    # 入力チェック
    required_fields = {
        "API Token": st.session_state.nomic_api_token,
        "Domain": st.session_state.nomic_domain,
        "Map URL": st.session_state.nomic_map_url,
        "Output Sheet URL": st.session_state.output_sheet_url,
        "Output Sheet Name": st.session_state.output_sheet_name,
    }

    missing = [key for key, val in required_fields.items() if not val]
    if missing:
        st.error("Missing required fields: " + ", ".join(missing))
        return None

    # Nomicデータ取得
    dataset = nomic_dataset(
        api_token=st.session_state.nomic_api_token,
        domain=st.session_state.nomic_domain,
        map_url=st.session_state.nomic_map_url,
    )
    st.session_state.map_data = dataset
    
    # Google 認証
    gclient = google_login()
    st.session_state.gclient = gclient

    # スプレッドシートのIDを抽出
    url = st.session_state.output_sheet_url.strip()
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)

    spreadsheet_id = match.group(1)

    worksheet_name = st.session_state.output_sheet_name

    # 書き込み
    write_sheet(
        st.session_state.gclient,
        spreadsheet_id=spreadsheet_id,
        worksheet_name=worksheet_name,
        map_data=st.session_state.map_data,
    )



# ===================================
# ページ設定
# ===================================
st.set_page_config(page_title="Nomic Map to Sheet", layout="wide")

# ===================================
# 初期ページ設定
# ===================================
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# ===================================
# 初期変数（入力データの初期化）
# ===================================
default_state = {
    "nomic_api_token": st.secrets.get("NOMIC_TOKEN", ""),
    "nomic_domain": "atlas.nomic.ai",
    "nomic_map_url": "chizai-capcom-from-500",
    "output_sheet_url": "1pt9jeFguPEjw_aWGpHoGVPx4YV49Qp_ngURRK17926M",
    "output_sheet_name": "シート1",
    "design_sheet_id": "",
    "design_sheet_name": "",
    "setting_category_col": ""
}

for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ===================================
# ヘッダー
# ===================================
logo_url = "https://prcdn.freetls.fastly.net/release_image/52909/36/52909-36-dd1d67cb4052a579b0c29e32c84fa9bf-2723x945.png?width=1950&height=1350&quality=85%2C65&format=jpeg&auto=webp&fit=bounds&bg-color=fff"

st.markdown(f"""
    <div class="header">
        <div class="header-left">
            <img src="{logo_url}" class="logo" alt="App Logo">
            <span class="title">Nomic Map to Sheet</span>
        </div>
    </div>
""", unsafe_allow_html=True)


# ===================================
# サイドメニュー
# ===================================
tabs = {
    "nomic": "Nomic",
    "output": "Output",
    "design": "Design",
    "setting": "Setting",
}

spacer1, col1, spacer2, col2, spacer3 = st.columns([0.5, 1, 0.1, 3, 0.5])

with col1:
    st.markdown("<div class='side-menu'>", unsafe_allow_html=True)
    for key, label in tabs.items():
        if st.button(label, key=f"tab_{key}", use_container_width=True):
            st.session_state.page = key
    st.markdown("</div>", unsafe_allow_html=True)


# ===================================
# メインコンテンツ
# ===================================
with col2:
    st.markdown("<div class='content'>", unsafe_allow_html=True)
    page = st.session_state.page

    # ---- Nomicタブ ----
    if page == "nomic":
        st.markdown("<h2>Nomic</h2>", unsafe_allow_html=True)
        st.session_state.nomic_api_token = st.text_input("API Token", value=st.session_state.nomic_api_token)
        st.session_state.nomic_domain = st.text_input("Domain", value=st.session_state.nomic_domain)
        st.session_state.nomic_map_url = st.text_input("Map URL", value=st.session_state.nomic_map_url)

    # ---- Outputタブ ----
    elif page == "output":
        st.markdown("<h2>Output</h2>", unsafe_allow_html=True)
        st.session_state.output_sheet_url = st.text_input("Sheet URL", value=st.session_state.output_sheet_url)
        st.session_state.output_sheet_name = st.text_input("Sheet Name", value=st.session_state.output_sheet_name)

        if st.button("Run Output"):
            output_sheet()
            st.success(f"Exported to {st.session_state.output_sheet_name or 'Sheet not specified'}")

    # ---- Designタブ ----
    elif page == "design":
        st.markdown("<h2>Design</h2>", unsafe_allow_html=True)
        st.session_state.design_sheet_id = st.text_input("Sheet ID", value=st.session_state.design_sheet_id)
        st.session_state.design_sheet_name = st.text_input("Sheet Name", value=st.session_state.design_sheet_name)

    # ---- Settingタブ ----
    elif page == "setting":
        st.markdown("<h2>Setting</h2>", unsafe_allow_html=True)
        st.session_state.setting_category_col = st.text_input("Category Column", value=st.session_state.setting_category_col)

    st.markdown("</div>", unsafe_allow_html=True)


# ===================================
# 外部CSSを読み込む
# ===================================
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
