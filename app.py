import streamlit as st
import nomic
from nomic import AtlasDataset
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import sheet_formatter
import nomic_module

import re
import json

# ===================================
# 関数
# ===================================


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
            df_master, err = nomic_module.create_nomic_dataset(
                st.session_state.nomic_api_token,
                st.session_state.nomic_domain,
                st.session_state.nomic_map_url
            )

            if err or df_master is None:
                st.error(f"❌ データ取得に失敗しました: {err}")
            else:
                st.success(f"✅ Exported to {st.session_state.output_sheet_name or 'Sheet not specified'}")

                # --- DataFrameをCSVとしてダウンロード可能に ---
                csv_data = df_master.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="📥 CSVとしてダウンロード",
                    data=csv_data,
                    file_name="nomic_master_data.csv",
                    mime="text/csv",
                )

                # --- 画面にプレビューを表示 ---
                st.dataframe(df_master.head(20))

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
