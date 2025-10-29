import streamlit as st

# ================================
# 🪄 ページ設定
# ================================
st.set_page_config(page_title="Nomic Map to Sheet", layout="wide")

# 初期ページ設定
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# ================================
# 🌆 ヘッダー
# ================================
logo_url = "https://prcdn.freetls.fastly.net/release_image/52909/36/52909-36-dd1d67cb4052a579b0c29e32c84fa9bf-2723x945.png?width=1950&height=1350&quality=85%2C65&format=jpeg&auto=webp&fit=bounds&bg-color=fff"

st.markdown(f"""
    <div class="header">
        <div class="header-left">
            <img src="{logo_url}" class="logo" alt="App Logo">
            <span class="title">Nomic Map to Sheet</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ================================
# 🔳 タブメニュー（横サイドバー風）
# ================================
tabs = {
    "nomic": "🧬 Nomic設定",
    "google": "🔑 Google認証",
    "sheet": "📊 スプレッドシート",
    "data": "🧠 データ設定",
    "export": "🚀 出力・実行",
}

# 2カラムレイアウト
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("<div class='side-menu'>", unsafe_allow_html=True)
    for key, label in tabs.items():
        active = st.session_state.page == key
        style = "active-tab" if active else "tab-btn"
        if st.button(label, key=f"tab_{key}", use_container_width=True):
            st.session_state.page = key
        st.markdown(f"<style>div[data-testid='stButton'][key='tab_{key}'] button{{}} </style>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 🪟 メインコンテンツ
# ================================
with col2:
    st.markdown("<div class='content'>", unsafe_allow_html=True)
    page = st.session_state.page

    if page == "nomic":
        st.markdown("<h2>🧬 Nomic設定</h2>", unsafe_allow_html=True)
        st.text_input("APIトークン")
        st.text_input("ドメイン")
        st.text_input("マップ名")

    elif page == "google":
        st.markdown("<h2>🔑 Google認証</h2>", unsafe_allow_html=True)
        st.file_uploader("Service Account JSONファイルをアップロード")

    elif page == "sheet":
        st.markdown("<h2>📊 スプレッドシート設定</h2>", unsafe_allow_html=True)
        st.text_input("スプレッドシートID")
        st.text_input("シート名")

    elif page == "data":
        st.markdown("<h2>🧠 データ設定</h2>", unsafe_allow_html=True)
        st.checkbox("カテゴリごとに色を自動付与")
        st.text_input("カテゴリ列名")

    elif page == "export":
        st.markdown("<h2>🚀 出力・実行</h2>", unsafe_allow_html=True)
        st.button("スプレッドシートへ書き出す", use_container_width=True)
        st.info("ここに出力結果を表示予定。")

    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 💅 CSS — 黒×白ベース、横タブ構成
# ================================
st.markdown("""
<style>
/* ===== 全体 ===== */
body, .stApp {
    background-color: #111 !important;
    color: #fff !important;
    font-family: 'Noto Sans JP', sans-serif;
}

/* ===== ヘッダー ===== */
.header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    border-bottom: 1px solid #333;
    padding: 16px 40px;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.logo {
    height: 40px;
    width: auto;
    object-fit: contain;
}
.title {
    font-size: 20px;
    font-weight: 600;
    color: #fff;
}

/* ===== 左側タブメニュー ===== */
.side-menu {
    display: flex;
    flex-direction: column;
    gap: 30px;
    padding: 20px 10px;
    height: 100%;
}
div[data-testid="stButton"] button {
    background-color: #222;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 10px;
    font-weight: 500;
    transition: all 0.2s ease;
}
div[data-testid="stButton"] button:hover {
    background-color: #333;
}
div[data-testid="stButton"] button:focus {
    outline: none;
}
div[data-testid="stButton"] button:has(strong) {
    background-color: #fff;
    color: #000;
}

/* アクティブなタブ */
.active-tab {
    background-color: #fff !important;
    color: #000 !important;
}

/* ===== メインエリア ===== */
.content {
    padding: 40px;
    background-color: #111;
}
h2 {
    border-left: 4px solid #fff;
    padding-left: 12px;
    margin-bottom: 20px;
    color: #fff;
}

/* ===== 入力エリア ===== */
input, textarea {
    background-color: #000 !important;
    color: #fff !important;
    border: 1px solid #444 !important;
    border-radius: 4px;
    transition: 0.2s ease-in-out;
}
input:focus, textarea:focus {
    border-color: #fff !important;
    box-shadow: 0 0 4px rgba(255,255,255,0.4);
}

/* ===== ボタン ===== */
button[kind="primary"] {
    background-color: #fff !important;
    color: #000 !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 600;
}
button[kind="primary"]:hover {
    background-color: #ddd !important;
}
</style>
""", unsafe_allow_html=True)
