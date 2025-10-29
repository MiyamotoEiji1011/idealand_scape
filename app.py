import streamlit as st

# ================================
# 🪄 ページ設定
# ================================
st.set_page_config(page_title="Nomic Map to Sheet", layout="wide")

# 初期ページ設定
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# ================================
# 🧭 ヘッダー（ロゴ＋タイトル）
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
        style = "background-color:#ff6a00;color:#fff;" if active else "background-color:#f5f5f5;color:#333;"
        if st.button(label, key=f"tab_{key}", use_container_width=True):
            st.session_state.page = key
        st.markdown(
            f"<style>div[data-testid='stButton'][key='tab_{key}'] button {{{style} border:none;border-radius:6px;padding:8px 0;font-weight:500;}}</style>",
            unsafe_allow_html=True,
        )

st.markdown("<hr>", unsafe_allow_html=True)

# ================================
# 🪟 メインコンテンツ
# ================================
st.markdown("<div class='content'>", unsafe_allow_html=True)

page = st.session_state.page

if page == "nomic":
    st.header("🧬 Nomic設定")
    st.text_input("APIトークン")
    st.text_input("ドメイン")
    st.text_input("マップ名")

elif page == "google":
    st.header("🔑 Google認証")
    st.file_uploader("Service Account JSONファイルをアップロード")

elif page == "sheet":
    st.header("📊 スプレッドシート設定")
    st.text_input("スプレッドシートID")
    st.text_input("シート名")

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
# 💅 シンプルCSS
# ================================
st.markdown("""
<style>
body, .stApp {
    background-color: #fff;
    color: #222;
    font-family: 'Noto Sans JP', sans-serif;
}

/* ヘッダー */
.header {
    display: flex;
    align-items: center;
    padding: 16px 40px;
    border-bottom: 1px solid #eee;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.logo {
    height: 48px;
    width: auto;
    object-fit: contain;
}
.title {
    font-size: 20px;
    font-weight: 600;
}

/* コンテンツ中央寄せ */
.content {
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
}

/* 見出し */
h1, h2, h3 {
    color: #222;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)
