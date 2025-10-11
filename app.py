import streamlit as st

st.title("Secrets テスト")

if "nomic" in st.secrets:
    st.success(f"Nomic Token: {st.secrets['nomic']['token'][:10]}...")
else:
    st.error("❌ [nomic] セクションが見つかりません")

if "google_service_account" in st.secrets:
    st.success("✅ Google サービスアカウント 読み込み成功")
else:
    st.error("❌ Google サービスアカウントが読み込まれていません")
