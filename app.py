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

# ================================
# 🪟 メインコンテンツ
# ================================
st.markdown("<div class='content-area'>", unsafe_allow_html=True)

page = st.session_state.page

if page == "nomic":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("🧬 Nomic設定")
    st.text_input("APIトークン", key="nomic_token")
    st.text_input("ドメイン", key="nomic_domain")
    st.text_input("マップ名", key="nomic_map")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "google":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("🔑 Google認証")
    st.file_uploader("Service Account JSONファイルをアップロード")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "sheet":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("📊 スプレッドシート設定")
    st.text_input("スプレッドシートID", key="sheet_id")
    st.text_input("シート名", key="sheet_name")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "data":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("🧠 データ設定")
    st.checkbox("カテゴリごとに色を自動付与")
    st.text_input("カテゴリ列名")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "export":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("🚀 出力・実行")
    st.button("スプレッドシートへ書き出す", use_container_width=True)
    st.info("ここに出力結果を表示予定。")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ================================
# 💅 外部CSSを読み込む
# ================================
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
