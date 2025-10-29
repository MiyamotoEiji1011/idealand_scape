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
    "nomic": "Nomic",
    "output": "Output",
    "design": "Design",
    "setting": "Setting",
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
        st.markdown("<h2>Nomic</h2>", unsafe_allow_html=True)
        st.text_input("API Token")
        st.text_input("Domain")
        st.text_input("Map URL")

    elif page == "output":
        st.markdown("<h2>Output</h2>", unsafe_allow_html=True)
        st.text_input("sheet URL")
        st.text_input("sheet name")

        if st.button("Go output!"):
            st.success("Succes ooutput sheet!")

    elif page == "design":
        st.markdown("<h2>Design</h2>", unsafe_allow_html=True)
        st.text_input("スプレッドシートID")
        st.text_input("シート名")

    elif page == "setting":
        st.markdown("<h2>Setting</h2>", unsafe_allow_html=True)
        st.text_input("カテゴリ列名")

    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 💅 外部CSSを読み込む
# ================================
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
