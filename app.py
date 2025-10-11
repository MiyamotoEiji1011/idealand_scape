import streamlit as st
import nomic
from nomic import AtlasDataset

st.title("Nomic Atlas Login Test")

# --- Load token from secrets ---
default_token = st.secrets.get("NOMIC_TOKEN", "")

# --- Input fields ---
st.subheader("Connection Settings")
token = st.text_input("API Token", value=default_token, type="password")
domain = st.text_input("Domain", value="atlas.nomic.ai")
map_name = st.text_input("Map Name", value="chizai-capcom-from-500")


# --- Fetch dataset button ---
if st.button("Fetch Dataset"):
    if not token:
        st.error("❌ Please login first.")
    else:
        try:
            nomic.cli.login(token=token, domain=domain)
            dataset = AtlasDataset(map_name)
            map_data = dataset.maps[0]
            df_topics = map_data.topics.df

            st.success("✅ Dataset fetched successfully!")

        except Exception as e:
            st.error(f"❌ Failed to fetch dataset: {e}")
