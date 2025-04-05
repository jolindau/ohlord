import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

SHEET_ID = '1QxDWmTzj6LM4ipierMGsLNlcJh5J2eUe_gF_IK3rceY'
SHEET_NAME = 'Sheet1'
TOTAL_MINUTES = 24 * 60

@st.cache_resource
def get_worksheet():
    # Define the scope for Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Load credentials from Streamlit's secrets
    creds_json = st.secrets["google"]["credentials"]
    creds_dict = json.loads(creds_json)
    
    # Use credentials to authorize with Google Sheets API
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    # Authorize and get the worksheet
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.worksheet(SHEET_NAME)


ws = get_worksheet()

def load_data():
    records = ws.get_all_records()
    return {row["name"]: row for row in records}

def update_value(name, field, delta):
    records = ws.get_all_records()
    for i, row in enumerate(records):
        if row["name"] == name:
            new_val = max(0, int(row[field]) + delta)
            cell = f"{chr(ord('C') + ['beers', 'hotdogs'].index(field))}{i+2}"
            ws.update_acell(cell, new_val)

def time_remaining(start_time_str, beers, hotdogs):
    start = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    minutes_elapsed = int((datetime.now() - start).total_seconds() // 60)
    time_saved = beers * 60 + hotdogs * 30
    return max(TOTAL_MINUTES - minutes_elapsed - time_saved, 0)

st.title("Fantasy Football Punishment Tracker")
data = load_data()

for name in data:
    row = data[name]
    start_time = row["start_time"]
    beers = int(row["beers"])
    hotdogs = int(row["hotdogs"])
    remaining = time_remaining(start_time, beers, hotdogs)
    progress = 1 - (remaining / TOTAL_MINUTES)

    st.subheader(name.capitalize())
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(f"**Start Time:** {datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')}")
        st.markdown(f"**Time Left:** {remaining // 60}h {remaining % 60}m")
        st.progress(progress, text=f"{int(progress * 100)}% complete")

    with col2:
        st.markdown("**Beers**")
        if st.button(f"➕ Beer ({beers})", key=f"{name}_add_beer"):
            update_value(name, "beers", 1)
        if st.button(f"➖ Beer", key=f"{name}_sub_beer"):
            update_value(name, "beers", -1)

    with col3:
        st.markdown("**Hotdogs**")
        if st.button(f"➕ Dog ({hotdogs})", key=f"{name}_add_dog"):
            update_value(name, "hotdogs", 1)
        if st.button(f"➖ Dog", key=f"{name}_sub_dog"):
            update_value(name, "hotdogs", -1)

    st.markdown("---")