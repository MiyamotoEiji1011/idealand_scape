import streamlit as st

st.set_page_config(page_title="Nomic Map to Sheet", layout="wide")

# ================================
# 🌱 初期ページ
# ================================
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
# 🔶 タブメニュー
# ================================
tabs = {
    "nomic": "🧬 Nomic設定",
    "google": "🔑 Google認証",
    "sheet": "📊 スプレッドシート",
    "data": "🧠 データ設定",
    "export": "🚀 出力・実行",
}

cols = st.columns(len(tabs))
for i, (key, label) in enumerate(tabs.items()):
    with cols[i]:
        active = st.session_state.page == key
        bg = "#ff7f32" if active else "#ffffff"
        color = "#fff" if active else "#333"
        shadow = "0 3px 8px rgba(0,0,0,0.08)" if active else "0 2px 6px rgba(0,0,0,0.05)"
        if st.button(label, key=f"tab_{key}", use_container_width=True):
            st.session_state.page = key
        st.markdown(
            f"<style>div[data-testid='stButton'][key='tab_{key}'] button {{background:{bg};color:{color};border:none;border-radius:8px;padding:10px 0;font-weight:600;box-shadow:{shadow};transition:all 0.25s;}}</style>",
            unsafe_allow_html=True,
        )

st.markdown("<hr class='tab-line'>", unsafe_allow_html=True)

# ================================
# 🪟 メインコンテンツ
# ================================
st.markdown("<div class='content'>", unsafe_allow_html=True)
page = st.session_state.page

if page == "nomic":
    st.markdown("<h2 class='section-title'>🧬 Nomic設定</h2>", unsafe_allow_html=True)
    st.text_input("APIトークン")
    st.text_input("ドメイン")
    st.text_input("マップ名")

elif page == "google":
    st.markdown("<h2 class='section-title'>🔑 Google認証</h2>", unsafe_allow_html=True)
    st.file_uploader("Service Account JSONファイルをアップロード")

elif page == "sheet":
    st.markdown("<h2 class='section-title'>📊 スプレッドシート設定</h2>", unsafe_allow_html=True)
    st.text_input("スプレッドシートID")
    st.text_input("シート名")

elif page == "data":
    st.markdown("<h2 class='section-title'>🧠 データ設定</h2>", unsafe_allow_html=True)
    st.checkbox("カテゴリごとに色を自動付与")
    st.text_input("カテゴリ列名")

elif page == "export":
    st.markdown("<h2 class='section-title'>🚀 出力・実行</h2>", unsafe_allow_html=True)
    st.button("スプレッドシートへ書き出す", use_container_width=True)
    st.info("ここに出力結果を表示予定。")

st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 💅 CSS — スタイリッシュ最小構成
# ================================
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    color: #222;
    font-family: 'Noto Sans JP', sans-serif;
}

/* ヘッダー */
.header {
    display: flex;
    align-items: center;
    padding: 16px 40px;
    border-bottom: 1px solid #eee;
    background-color: #fff;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.logo {
    height: 48px;
    width: auto;
    object-fit: contain;
}
.title {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* コンテンツエリア */
.content {
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px 60px;
}

/* タブ下ライン */
.tab-line {
    border: none;
    border-bottom: 1px solid #ddd;
    margin: 1rem 0 2rem;
}

/* セクションタイトル */
.section-title {
    border-left: 4px solid #ff7f32;
    padding-left: 10px;
    margin-bottom: 1.5rem;
    font-weight: 700;
    color: #222;
}
</style>
""", unsafe_allow_html=True)
