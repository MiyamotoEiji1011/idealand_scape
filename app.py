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
    st.markdown("<h2 class='sidebar-title'>設定メニュー</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    pages = {
        "nomic": "🧬 Nomic設定",
        "google": "🔑 Google認証",
        "sheet": "📊 スプレッドシート設定",
        "data": "🧠 データ設定",
        "export": "🚀 出力・実行"
    }

    for key, label in pages.items():
        is_active = st.session_state.page == key
        button_class = "active-button" if is_active else "sidebar-button"
        if st.button(label, key=f"btn_{key}", use_container_width=True):
            st.session_state.page = key
        st.markdown(
            f"<style>div[data-testid='stButton'][key='btn_{key}'] button {{{'background-color:#ff4b4b; color:white;' if is_active else ''}}}</style>",
            unsafe_allow_html=True
        )

# ================================
# 🪟 メイン画面
# ================================
st.markdown("<h1 class='main-title'>データ連携アプリケーション</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>NomicやGoogleと連携してデータを自動処理します。</p>", unsafe_allow_html=True)
st.markdown("<hr class='divider'>", unsafe_allow_html=True)

page = st.session_state.page

if page == "nomic":
    st.subheader("🧬 Nomic設定")
    st.text_input("APIトークン", key="nomic_token")
    st.text_input("ドメイン", key="nomic_domain")
    st.text_input("マップ名", key="nomic_map")
    st.text_input("マップ名", key="nomic_map")
    st.text_input("マップ名", key="nomic_map")
    st.text_input("マップ名", key="nomic_map")
    st.text_input("マップ名", key="nomic_map")
    st.text_input("マップ名", key="nomic_map")
    st.text_input("マップ名", key="nomic_map")
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
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")
    st.text_input("カテゴリ列名")

elif page == "export":
    st.subheader("🚀 出力・実行")
    st.button("スプレッドシートへ書き出す", use_container_width=True)
    st.info("ここに出力結果を表示予定。")

# ================================
# 💅 CSSを外部から読み込み
# ================================
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
