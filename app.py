import streamlit as st

st.set_page_config(page_title="データ連携アプリ", layout="wide")

# ================================
# 🌱 初期化
# ================================
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# ================================
# 🧭 サイドバー（ツールバー）
# ================================
with st.sidebar:
    st.title("⚙️ 設定メニュー")

    if st.button("🧬 Nomic設定", use_container_width=True):
        st.session_state.page = "nomic"

    if st.button("🔑 Google認証", use_container_width=True):
        st.session_state.page = "google"

    if st.button("📊 スプレッドシート設定", use_container_width=True):
        st.session_state.page = "sheet"

    if st.button("🧠 データ設定", use_container_width=True):
        st.session_state.page = "data"

    if st.button("🚀 出力・実行", use_container_width=True):
        st.session_state.page = "export"

st.markdown("---")

# ================================
# 🪟 メイン画面（切り替え表示）
# ================================
st.title("📁 データ管理アプリケーション")

if st.session_state.page == "nomic":
    st.header("🧬 Nomic設定")
    st.text_input("APIトークン", key="nomic_token")
    st.text_input("ドメイン", key="nomic_domain")
    st.text_input("マップ名", key="nomic_map")

elif st.session_state.page == "google":
    st.header("🔑 Google認証")
    st.file_uploader("Service Account JSONファイルをアップロード")

elif st.session_state.page == "sheet":
    st.header("📊 スプレッドシート設定")
    st.text_input("スプレッドシートID", key="sheet_id")
    st.text_input("シート名", key="sheet_name")

elif st.session_state.page == "data":
    st.header("🧠 データ設定")
    st.checkbox("カテゴリごとに色を自動付与")
    st.text_input("カテゴリ列名")

elif st.session_state.page == "export":
    st.header("🚀 出力・実行")
    st.button("スプレッドシートへ書き出す", use_container_width=True)
    st.info("ここに出力結果を表示予定。")

# ================================
# 💅 スタイル調整（CSSで見た目整える）
# ================================
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
            border-right: 1px solid #ddd;
        }
        div.block-container {
            padding-top: 1rem;
            padding-left: 2rem;
        }
        h1 {
            color: #2c3e50;
        }
        .stButton > button {
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 6px;
            color: #333;
        }
        .stButton > button:hover {
            background-color: #e6f0ff;
            border-color: #4a90e2;
            color: #000;
        }
    </style>
""", unsafe_allow_html=True)
