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
            <p>Nomic Map to Sheet</p>
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

# 3カラム構成（左右スペース・中央）
spacer1, col1, spacer2, col2, spacer3 = st.columns([0.5, 1, 0.1, 3, 0.5])

with col1:
    st.markdown("<div class='side-menu'>", unsafe_allow_html=True)
    for key, label in tabs.items():
        if st.button(label, key=f"tab_{key}", use_container_width=True):
            st.session_state.page = key
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
# 💅 外部CSSを読み込む
# ================================
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
