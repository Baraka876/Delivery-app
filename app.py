import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from PIL import Image
import io

# Database Setup
conn = sqlite3.connect('delivery_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs 
             (id INTEGER PRIMARY KEY, date TEXT, client TEXT, product TEXT, 
              lpo TEXT, qty REAL, transport REAL, bites REAL, total REAL, 
              status TEXT, driver TEXT, notes TEXT, photo BLOB)''')
conn.commit()

st.set_page_config(page_title="Delivery Tracker", layout="wide")

# Sidebar Search
st.sidebar.header("🔍 Search")
search_lpo = st.sidebar.text_input("Find LPO Number")

# --- APP LOGIC ---
tab1, tab2 = st.tabs(["📝 Log Delivery", "📊 Reports & Search"])

with tab1:
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        client = st.text_input("Client/Recipient")
        lpo = st.text_input("LPO Number")
        product = st.text_input("Product Name")
        qty = st.number_input("Quantity", min_value=0.0)
        
        st.subheader("Expenses")
        col1, col2 = st.columns(2)
        transport = col1.number_input("Transport", min_value=0.0)
        bites = col2.number_input("Small Bites", min_value=0.0)
        
        status = st.selectbox("Status", ["Credit", "Paid"])
        driver = st.text_input("Delivered By")
        
        uploaded_file = st.file_uploader("Scan/Photo of Signed Invoice", type=['jpg', 'jpeg', 'png'])
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Save Entry"):
            total = transport + bites
            img_byte_arr = uploaded_file.getvalue() if uploaded_file else None
            
            c.execute("INSERT INTO logs (date, client, product, lpo, qty, transport, bites, total, status, driver, notes, photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                      (str(date), client, product, lpo, qty, transport, bites, total, status, driver, notes, img_byte_arr))
            conn.commit()
            st.success(f"Saved! Total: {total}")

with tab2:
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    
    if search_lpo:
        df = df[df['lpo'].str.contains(search_lpo, case=False, na=False)]

    if not df.empty:
        st.subheader("💰 Financial Summary")
        m1, m2 = st.columns(2)
        m1.metric("Total Expenses", f"{df['total'].sum():,.2f}")
        m2.metric("Total in Credit", f"{df[df['status']=='Credit']['total'].sum():,.2f}")
        
        st.divider()
        st.dataframe(df.drop(columns=['photo']), use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📩 Download Report for WhatsApp", data=csv, file_name="delivery_report.csv", mime="text/csv")
    else:
        st.info("No records found.")
