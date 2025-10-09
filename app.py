import streamlit as st
from nomic import AtlasDataset
import nomic

st.title("🔗 Nomic Atlas Login & Map Fetcher")

# --- 入力欄 ---
token = st.text_input("Nomic Atlas Token", type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")

# --- ボタン ---
if st.button("Login & Fetch Map"):
    if not token or not map_name:
        st.warning("TokenとMap名を入力してください。")
    else:
        try:
            nomic.cli.login(token=token, domain=domain)
            dataset = AtlasDataset(map_name)
            map_obj = dataset.maps[0]
            df_topics = map_obj.topics.df

            st.success("✅ Login & Fetch Success!")
            st.dataframe(df_topics.head())  # データの一部を表示

        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
