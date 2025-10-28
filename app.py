import streamlit as st

st.set_page_config(page_title="データ連携アプリ", layout="wide")

# ================================
# 🌱 初期化
# ================================
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# ================================
# 🧭 サイドバー
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
# 🪟 メイン画面
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
# 💅 外部CSS読み込み
# ================================
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 例: プロジェクト直下に style.css がある場合
local_css("style.css")
