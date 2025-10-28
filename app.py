import streamlit as st

# =========================================
# 🧩 ページ設定
# =========================================
st.set_page_config(
    page_title="データ管理アプリ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# 🌿 初期化
# =========================================
if "page" not in st.session_state:
    st.session_state.page = "nomic"

# =========================================
# 🎛️ サイドバー（業務アプリ風）
# =========================================
with st.sidebar:
    st.markdown("<h2 style='color:#1e1e1e; font-weight:600;'>設定メニュー</h2>", unsafe_allow_html=True)
    st.markdown("---")

    menu_items = {
        "nomic": "🧬 Nomic設定",
        "google": "🔑 Google認証",
        "sheet": "📊 スプレッドシート設定",
        "data": "🧠 データ設定",
        "export": "🚀 出力・実行",
    }

    for key, label in menu_items.items():
        button_style = f"""
            background-color: {'#e8eef5' if st.session_state.page == key else '#f8f9fa'};
            color: {'#1f1f1f' if st.session_state.page == key else '#333'};
            border: none;
            text-align: left;
            padding: 10px 16px;
            border-radius: 4px;
            width: 100%;
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
        """
        if st.button(label, key=f"btn_{key}"):
            st.session_state.page = key
        st.markdown(f"<style>div[data-testid='stButton'] > button#{key} {{ {button_style} }}</style>", unsafe_allow_html=True)

# =========================================
# 🪟 メイン画面
# =========================================
st.markdown("<h1 style='color:#2d3436; font-weight:600;'>データ連携アプリケーション</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>データ連携設定を行い、スプレッドシートに出力します。</p>", unsafe_allow_html=True)
st.markdown("---")

page = st.session_state.page

if page == "nomic":
    st.subheader("🧬 Nomic設定")
    st.text_input("APIトークン", key="nomic_token")
    st.text_input("ドメイン", key="nomic_domain")
    st.text_input("マップ名", key="nomic_map")

elif page == "google":
    st.subheader("🔑 Google認証")
    st.file_uploader("Service Account JSONファイルをアップロード")

elif page == "sheet":
    st.subheader("📊 スプレッドシート設定")
    st.text_input("スプレッドシートID", key="sheet_id")
    st.text_input("シート名", key="sheet_name")

elif page == "data":
    st.subheader("🧠 データ設定")
    st.checkbox("カテゴリごとに色を自動付与")
    st.text_input("カテゴリ列名")
    st.number_input("最大行数", min_value=1, max_value=10000, value=1000)

elif page == "export":
    st.subheader("🚀 出力・実行")
    st.button("スプレッドシートへ書き出す", use_container_width=True)
    st.info("出力結果はここに表示されます。")

# =========================================
# 💅 CSS: 業務アプリ風の落ち着いた配色
# =========================================
st.markdown("""
<style>
    /* 全体背景 */
    .stApp {
        background-color: #fafafa;
    }

    /* サイドバー */
    section[data-testid="stSidebar"] {
        background-color: #f2f3f5;
        border-right: 1px solid #d0d0d0;
        padding-top: 1rem;
    }

    /* ボタン */
    .stButton > button {
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        background-color: #f8f9fa;
        color: #333;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #e8eef5;
        border-color: #aabbee;
    }

    /* ヘッダー */
    h1, h2, h3 {
        font-family: "Segoe UI", "Hiragino Kaku Gothic ProN", sans-serif;
    }

    /* テキスト入力 */
    div[data-baseweb="input"] > div {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)
