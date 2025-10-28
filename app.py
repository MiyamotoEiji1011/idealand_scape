import streamlit as st

st.set_page_config(page_title="データ連携アプリ", layout="wide")

# ================================
# 🌱 初期化
# ================================
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# ================================
# 🌆 ヘッダー（ロゴ＋アプリ名＋上部タブ）
# ================================
logo_url = "https://upload.wikimedia.org/wikipedia/commons/4/4f/Orange_logo.svg"  # 仮ロゴ（後で置き換え可能）

st.markdown(f"""
    <div class="header">
        <div class="header-left">
            <img src="{logo_url}" class="logo">
            <span class="app-title">DataSync Hub</span>
        </div>
        <div class="header-tabs">
            <a class="tab {'active' if st.session_state.page=='nomic' else ''}" href="?page=nomic">Nomic設定</a>
            <a class="tab {'active' if st.session_state.page=='google' else ''}" href="?page=google">Google認証</a>
            <a class="tab {'active' if st.session_state.page=='sheet' else ''}" href="?page=sheet">スプレッドシート</a>
            <a class="tab {'active' if st.session_state.page=='data' else ''}" href="?page=data">データ設定</a>
            <a class="tab {'active' if st.session_state.page=='export' else ''}" href="?page=export">出力・実行</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# ================================
# 🪟 メイン画面（タブ切り替え）
# ================================
st.markdown("<div class='content'>", unsafe_allow_html=True)

page = st.session_state.page

if page == "nomic":
    st.header("🧬 Nomic設定")
    st.text_input("APIトークン", key="nomic_token")
    st.text_input("ドメイン", key="nomic_domain")
    st.text_input("マップ名", key="nomic_map")

elif page == "google":
    st.header("🔑 Google認証")
    st.file_uploader("Service Account JSONファイルをアップロード")

elif page == "sheet":
    st.header("📊 スプレッドシート設定")
    st.text_input("スプレッドシートID", key="sheet_id")
    st.text_input("シート名", key="sheet_name")

elif page == "data":
    st.header("🧠 データ設定")
    st.checkbox("カテゴリごとに色を自動付与")
    st.text_input("カテゴリ列名")

elif page == "export":
    st.header("🚀 出力・実行")
    st.button("スプレッドシートへ書き出す", use_container_width=True)
    st.info("ここに出力結果を表示予定。")

st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 💅 CSS（白黒＋オレンジのideaflow風テーマ）
# ================================
st.markdown("""
<style>
body {
    background-color: #fff;
    color: #111;
    font-family: 'Helvetica Neue', 'Noto Sans JP', sans-serif;
}

/* ヘッダー全体 */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    padding: 10px 40px;
    position: sticky;
    top: 0;
    z-index: 100;
}

/* ロゴとアプリ名 */
.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.logo {
    width: 36px;
    height: 36px;
}
.app-title {
    font-size: 20px;
    font-weight: 600;
    color: #111;
}

/* タブ部分 */
.header-tabs {
    display: flex;
    gap: 20px;
}
.tab {
    text-decoration: none;
    color: #333;
    font-weight: 500;
    font-size: 15px;
    padding: 6px 10px;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}
.tab:hover {
    color: #ff6a00;
    border-bottom: 2px solid #ff6a00;
}
.tab.active {
    color: #ff6a00;
    border-bottom: 2px solid #ff6a00;
    font-weight: 600;
}

/* メインコンテンツ */
.content {
    padding: 40px 60px;
}

/* 入力要素 */
input, textarea, select {
    background-color: #fafafa !important;
    border: 1px solid #ccc !important;
    color: #111 !important;
}
input:focus {
    border-color: #ff6a00 !important;
    outline: none !important;
}
button[kind="primary"] {
    background-color: #ff6a00 !important;
    color: white !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)
