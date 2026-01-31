import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- APP SETUP ---
st.set_page_config(page_title="Delivery Management", layout="wide", page_icon="🚚")

st.title("🚚 Delivery Management & Bookkeeping")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Fetch Data
try:
    data = conn.read(worksheet="Sheet1")
except:
    data = pd.DataFrame(columns=["Date", "Client", "LPO", "Product", "Qty", "Staff", "Status", "Transport", "Bites", "Total", "Notes"])

# --- FORM SECTION ---
with st.expander("📝 Log New Delivery & Expenses", expanded=False):
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            client = st.text_input("Company / Person Delivered To")
            lpo = st.text_input("LPO Number")
            product = st.text_input("Product Name")
            qty = st.number_input("Quantity Delivered", min_value=0.0)
        with col2:
            staff = st.text_input("Delivered By")
            status = st.selectbox("Payment Status", ["Credit", "Paid", "Partial"])
            trans_exp = st.number_input("Transport Expense", min_value=0.0)
            bites_exp = st.number_input("Small Bites Expense", min_value=0.0)
            notes = st.text_area("Notes")
            invoice_photo = st.file_uploader("Upload Signed Invoice Photo", type=['jpg', 'png', 'jpeg'])

        submit = st.form_submit_button("Submit & Save Entry")

if submit:
    total_calculated = trans_exp + bites_exp
    new_entry = pd.DataFrame([{
        "Date": date.strftime("%Y-%m-%d"),
        "Client": client,
        "LPO": lpo,
        "Product": product,
        "Qty": qty,
        "Staff": staff,
        "Status": status,
        "Transport": trans_exp,
        "Bites": bites_exp,
        "Total": total_calculated,
        "Notes": notes
    }])
    updated_df = pd.concat([data, new_entry], ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_df)
    st.success(f"✅ Saved! Total: {total_calculated}")
    st.rerun()

# --- SEARCH & FILTER SECTION ---
st.divider()
st.header("🔎 Search & Filter Records")
search_query = st.text_input("Search by Client Name, LPO, or Product", placeholder="Type here to filter...")

# Filter logic
if search_query:
    filtered_df = data[
        data['Client'].astype(str).str.contains(search_query, case=False) | 
        data['LPO'].astype(str).str.contains(search_query, case=False) |
        data['Product'].astype(str).str.contains(search_query, case=False)
    ]
else:
    # Default to current month if no search
    data['Date'] = pd.to_datetime(data['Date'])
    current_month = datetime.now().strftime("%Y-%m")
    filtered_df = data[data['Date'].dt.strftime('%Y-%m') == current_month]

# --- BOOKKEEPING & REPORTS ---
st.header("📊 Bookkeeping Summary")

if not filtered_df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Selected Total Expenses", f"{filtered_df['Total'].sum():,.2f}")
    m2.metric("Selected Total Qty", f"{filtered_df['Qty'].sum():,.2f}")
    m3.metric("Records Found", len(filtered_df))

    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📩 Export These Results for WhatsApp",
        data=csv,
        file_name=f"Delivery_Export_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime='text/csv',
    )
else:
    st.info("No matching records found.")
