import streamlit as st
import nomic
from nomic import AtlasDataset

def fetch_nomic_dataset(st, token, domain, map_name):
    """Nomic Atlasデータセットを取得"""
    if not token:
        st.error("❌ Please provide API token first.")
        return
    try:
        nomic.login(token=token, domain=domain)
        dataset = AtlasDataset(map_name)
        st.session_state.map_data = dataset.maps[0]
        st.success("✅ Dataset fetched successfully!")
    except Exception as e:
        st.error(f"❌ Failed to fetch dataset: {e}")
