import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# --- DATABASE SETUP ---
# We use a simple SQLite file. 
# Note: On Streamlit Cloud's free tier, this resets if the app is idle.
conn = sqlite3.connect('deliveries.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs 
             (Date TEXT, Client TEXT, LPO TEXT, Product TEXT, Quantity REAL)''')
conn.commit()

# --- APP INTERFACE ---
st.set_page_config(page_title="Delivery Log", layout="wide")

st.title("📦 Delivery Management System")

# This creates the "Form" layout you liked
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

# --- SAVING DATA ---
if submit_button:
    if client and product:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO logs (Date, Client, LPO, Product, Quantity) VALUES (?, ?, ?, ?, ?)",
                  (current_time, client, lpo, product, qty))
        conn.commit()
        st.success(f"Done! Logged {product} for {client}")
    else:
        st.warning("Please enter at least a Client and Product name.")

# --- DISPLAYING DATA ---
st.divider()
st.subheader("Recent Reports")

# Load data into a nice table
df = pd.read_sql_query("SELECT * FROM logs ORDER BY Date DESC", conn)

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No logs found yet. Start by adding one above!")
