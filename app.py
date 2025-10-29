import streamlit as st

st.set_page_config(page_title="データ連携アプリ", layout="wide")

# ================================
# 🌱 初期化
# ================================
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# ================================
# 🌆 ヘッダー（ロゴ＋アプリ名）
# ================================
logo_url = "https://prcdn.freetls.fastly.net/release_image/52909/36/52909-36-dd1d67cb4052a579b0c29e32c84fa9bf-2723x945.png?width=1950&height=1350&quality=85%2C65&format=jpeg&auto=webp&fit=bounds&bg-color=fff"

st.markdown(
    f"""
    <div class="header">
        <div class="header-left">
            <img src="{logo_url}" class="logo" alt="App Logo">
            <span class="app-title">Nomic Map to sheet</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ================================
# 🔶 タブ（上部水平ボタン）
# ================================
tabs = {
    "nomic": "🧬 Nomic設定",
    "google": "🔑 Google認証",
    "sheet": "📊 スプレッドシート",
    "data": "🧠 データ設定",
    "export": "🚀 出力・実行",
}

tab_cols = st.columns(len(tabs))

for i, (key, label) in enumerate(tabs.items()):
    with tab_cols[i]:
        is_active = st.session_state.page == key
        btn_label = f"**{label}**" if is_active else label
        if st.button(btn_label, key=f"tab_{key}", use_container_width=True):
            st.session_state.page = key

st.markdown("<div class='tab-underline'></div>", unsafe_allow_html=True)

# ================================
# 🪟 メインコンテンツ
# ================================
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

# ================================
# 💅 CSS — 白背景＆ライン強調スタイル
# ================================
st.markdown("""
<style>
/* 全体背景を白に */
.stApp {
    background-color: #ffffff !important;
}

/* ヘッダー */
.header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    background-color: #ffffff;
    border-bottom: 2px solid #f0f0f0;
    padding: 12px 40px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
            /* ロゴ画像をきれいにスケーリング */
.logo {
    height: 100px;                /* 高さを固定（ここを変えれば調整可能） */
    width: auto;                 /* 横幅は自動で比率維持 */
    object-fit: contain;         /* トリミングせず全体を収める */
    display: block;
    margin-right: 12px;
}

/* ロゴとタイトルの位置を微調整 */
.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-shrink: 0;
}

/* タイトルとのバランス */
.app-title {
    font-size: 22px;
    font-weight: 600;
    color: #222;
    letter-spacing: 0.5px;
}

/* タブ群 */
div[data-testid="column"] button {
    background-color: #fff;
    border: none;
    border-bottom: 3px solid transparent;
    color: #333;
    font-size: 15px;
    font-weight: 500;
    padding: 10px 0;
    transition: all 0.2s ease;
}
div[data-testid="column"] button:hover {
    color: #ff6a00;
    border-bottom: 3px solid #ff6a00;
    background-color: #fafafa;
}
div[data-testid="column"] button:focus {
    outline: none;
}
div[data-testid="column"] button:has(strong) {
    color: #ff6a00 !important;
    border-bottom: 3px solid #ff6a00 !important;
    font-weight: 600;
}

/* タブ下のライン */
.tab-underline {
    height: 1px;
    background-color: #ddd;
    margin-bottom: 1.5rem;
}

/* 見出し */
h1, h2, h3 {
    color: #222;
    font-family: 'Helvetica Neue', 'Noto Sans JP', sans-serif;
}

/* 入力フォーム */
input, textarea, select {
    background-color: #ffffff !important;
    border: 1px solid #ccc !important;
    color: #111 !important;
    border-radius: 4px !important;
    transition: 0.2s ease-in-out;
}
input:focus, textarea:focus, select:focus {
    border-color: #ff6a00 !important;
    box-shadow: 0 0 4px rgba(255, 106, 0, 0.3);
}

/* ボタン */
button[kind="primary"] {
    background-color: #ff6a00 !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(255, 106, 0, 0.3);
}
button[kind="primary"]:hover {
    background-color: #e85c00 !important;
}

/* 情報ボックス */
[data-testid="stAlert"] {
    background-color: #fafafa !important;
    border-left: 4px solid #ff6a00 !important;
    color: #333 !important;
}

/* 区切り */
hr {
    border: none;
    border-bottom: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)
