import streamlit as st
from nomic import AtlasDataset
import nomic

st.set_page_config(page_title="Nomic Atlas Viewer", layout="wide")
st.title("Nomic Atlas")

# --- 入力欄 ---
token = st.text_input("Nomic Atlas Token", type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# --- ボタン ---
if st.button("Login & Fetch Map"):
    if not token or not map_name:
        st.warning("⚠️ TokenとMap名を入力してください。")
    else:
        try:
            nomic.cli.login(token=token, domain=domain)
            dataset = AtlasDataset(map_name)
            map_obj = dataset.maps[0]

            # --- 各データフレームを取得 ---
            df_metadata = map_obj.topics.metadata
            df_topics = map_obj.topics.df
            df_data = map_obj.data.df

            st.success("✅ Login & Fetch Success!")

            # --- タブでデータを切り替え ---
            tab1, tab2, tab3 = st.tabs(["🧩 Metadata", "📚 Topics", "📊 Data"])

            with tab1:
                st.markdown("### 🧩 Metadata")
                st.dataframe(df_metadata, use_container_width=True, height=600)

            with tab2:
                st.markdown("### 📚 Topics")
                st.dataframe(df_topics, use_container_width=True, height=600)

            with tab3:
                st.markdown("### 📊 Data")
                st.dataframe(df_data, use_container_width=True, height=600)

        except Exception as e:
            st.error(f"❌ エラーが発生しました:\n\n{e}")
