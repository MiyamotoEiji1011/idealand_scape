import json
from google.oauth2 import service_account
import streamlit as st

service_account_info = json.loads(st.secrets["google_service_account"]["value"])
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/drive']
)
