import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Delivery & Expense Log", layout="wide")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Load data (Safe error handling)
try:
    data = conn.read(worksheet="Sheet1")
except Exception:
    data = pd.DataFrame(columns=["Date", "Client", "LPO", "Product", "Qty", "Transport", "Bites", "Total", "Status", "Staff", "Notes"])

st.title("🚚 Delivery Management & Bookkeeping")

# 3. New Entry Form
with st.expander("📝 Log New Delivery & Expenses", expanded=True):
    with st.form("delivery_form", clear_on_submit=True):
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

# 4. Save Logic
if submit:
    total_exp = trans_exp + bites_exp
    new_entry = pd.DataFrame([{
        "Date": date.strftime("%Y-%m-%d"),
        "Client": client,
        "LPO": lpo,
        "Product": product,
        "Qty": qty,
        "Transport": trans_exp,
        "Bites": bites_exp,
        "Total": total_exp,
        "Status": status,
        "Staff": staff,
        "Notes": notes
    }])
    
    updated_df = pd.concat([data, new_entry], ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_df)
    st.success(f"✅ Saved! Total Expense: {total_exp}")
    st.rerun()

# 5. Monthly Reporting Section
st.divider()
st.header("📊 Monthly Bookkeeping Report")

if not data.empty:
    data['Date'] = pd.to_datetime(data['Date'])
    current_month = datetime.now().strftime("%m")
    month_df = data[data['Date'].dt.strftime('%m') == current_month]

    # Dashboard Totals
    m1, m2, m3 = st.columns(3)
    m1.metric("Month Total Expenses", f"{month_df['Total'].sum():,.2f}")
    m2.metric("Total Qty Delivered", f"{month_df['Qty'].sum():,.2f}")
    m3.metric("Pending Credits", len(month_df[month_df['Status'] == "Credit"]))

    st.subheader("Detailed Monthly Log")
    st.dataframe(month_df, use_container_width=True)

    # Export for WhatsApp
    csv = month_df.to_csv(index=False).encode('utf-8')
    st.download_button("📩 Download Report for WhatsApp", data=csv, file_name="monthly_report.csv", mime="text/csv")
else:
    st.info("No data recorded yet.")
