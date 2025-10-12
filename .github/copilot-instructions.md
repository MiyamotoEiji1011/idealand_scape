# Copilot Instructions for `idealand_scape`

## Project Overview
- **Purpose:** Syncs datasets from Nomic Atlas to Google Sheets using a Streamlit UI.
- **Key File:** `app.py` (Streamlit app, all logic in one file)
- **External Services:**
  - [Nomic Atlas](https://atlas.nomic.ai) (API access via `nomic`)
  - Google Sheets (API via `gspread`)

## Architecture & Data Flow
- User provides Nomic API token, domain, and map name via Streamlit UI.
- App fetches dataset metadata from Nomic Atlas and stores it in `st.session_state`.
- Google Sheets credentials are loaded from `st.secrets` (JSON service account key).
- Data is written to a Google Sheet (ID and worksheet name are user inputs).
- DataFrame columns are project-specific and mostly Japanese-labeled.

## Developer Workflows
- **Run app:** `streamlit run app.py`
- **Dependencies:** See `requirements.txt` (pinned versions, use `pip install -r requirements.txt`).
- **Secrets:**
  - Place Nomic API token and Google service account JSON in `.streamlit/secrets.toml`:
    ```toml
    NOMIC_TOKEN = "..."
    [google_service_account]
    value = "{...json...}"
    ```
- **Testing:** No automated tests; manual validation via UI.

## Project Conventions
- All business logic is in `app.py` (no modules).
- Uses Streamlit session state for client and dataset caching.
- DataFrame columns are hardcoded and must match Google Sheet headers.
- Error handling is user-facing (Streamlit `st.error`, `st.success`).
- Japanese column names and worksheet names are common.

## Integration & Patterns
- Nomic Atlas: Authenticate with `nomic.login`, fetch with `AtlasDataset(map_name)`.
- Google Sheets: Use `gspread` with service account, write DataFrame with `set_with_dataframe`.
- All user input is via Streamlit widgets.

## Examples
- To add new columns, update both the `columns` list and Google Sheet headers.
- To change the data source, modify the Nomic Atlas fetch logic in `app.py`.

---
**Edit this file to update agent instructions as the project evolves.**
