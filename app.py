import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- APP INTERFACE ---
st.set_page_config(page_title="Permanent Delivery Log", layout="wide")

st.title("📦 Delivery Management System (Permanent)")

# 1. Create a connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Fetch existing data from your sheet
try:
    data = conn.read(worksheet="Sheet1")
except:
    # If the sheet is empty, create a starting point
    data = pd.DataFrame(columns=["Date", "Client", "LPO", "Product", "Quantity"])

# --- FORM SECTION ---
with st.container():
    st.subheader("Log New Entry")
    with st.form("delivery_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            client = st.text_input("Client / Recipient")
            lpo = st.text_input("LPO Number")
            
        with col2:
            product = st.text_input("Product Name")
            qty = st.number_input("Quantity", min_value=0.0, step=1.0)
            
        submit_button = st.form_submit_button("Submit Delivery")

# --- SAVING DATA TO GOOGLE SHEETS ---
if submit_button:
    if client and product:
        # Create new row
        new_row = pd.DataFrame([{
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "Client": client,
            "LPO": lpo,
            "Product": product,
            "Quantity": qty
        }])
        
        # Combine with old data
        updated_df = pd.concat([data, new_row], ignore_index=True)
        
        # PUSH TO GOOGLE SHEETS
        conn.update(worksheet="Sheet1", data=updated_df)
        
        st.success(f"✅ Saved permanently to Google Sheets!")
        st.rerun() # Refresh to show new data
    else:
        st.warning("Please enter a Client and Product.")

# --- DISPLAYING DATA ---
st.divider()
st.subheader("Recent Reports")
st.dataframe(data, use_container_width=True)
